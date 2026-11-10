"""“每日一读”单页视频的朗读：沿用工具包 西班牙语/tools/make_audio.py 的整条处理链（Qwen3 固定种子、电平、压缩、
去电磁音、-16 LUFS、限幅、成品独立核查），只改时间安排以贴近参考视频：先读标题，句间 1.0 秒，片头 0.5 秒、结尾 1.2 秒。
（参考视频句间约 1.3 秒；试过 1.3/1.2/1.1 秒，3 秒短时响度波动 1.34/1.24/1.13 LU，超过工具包上限 1.0——窗口里静音占比变大造成的，
 朗读本身句间偏差只有 0.44 LU；1.0 秒 0.95 LU 通过，不改核查标准，所以取 1.0 秒。）

    cd <工具包根目录> && python <本文件> <文章.json> <输出目录> [音色名] [句间停顿秒数]

输出：<输出目录>/<id>.mp3、<id>_timings.json（每句起止时间、朗读文字、响度核查报告）。不改工具包里的任何文件
（合成缓存仍写在工具包的 西班牙语/audio/_合成缓存/，同一句文字再跑直接用缓存）。
"""
import importlib.util
import json
import sys
from pathlib import Path

ART, OUT = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
VOICE = sys.argv[3] if len(sys.argv) > 3 else 'qwen3_M1F5_25'
PAUSE = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0                       # 句间停顿（秒）
TOOLS = Path('西班牙语/tools').resolve()
sys.path.insert(0, str(TOOLS))
spec = importlib.util.spec_from_file_location('es_make_audio', TOOLS / 'make_audio.py')
MA = importlib.util.module_from_spec(spec)
spec.loader.exec_module(MA)

art = json.loads(ART.read_text('utf-8'))
title = art['title_es'] + '.'
p = {'id': art['id'],
     'paras': [[{'es': title, 'zh': art['title_zh']}]] + art['paras'],     # 第 1 句 = 标题（参考视频先读标题）
     'no_pause_commas': art.get('no_pause_commas', {})}
base = MA.VOICES[VOICE]
cfg0 = dict(base, lead_in=0.5, sentence_pause=PAUSE, tail=1.2)
eng = MA.engine_for(cfg0)
safe = cfg0.get('safe_short_term')
ladder = [(cfg0.get('leveler_win', 1.0), cfg0.get('leveler_rng', 4.0))] + [tuple(x) for x in cfg0.get('leveler_ladder', [])]
tried = []
for win, rng in ladder:
    c = dict(cfg0, leveler_win=win, leveler_rng=rng)
    a48, items = MA.build(p, c, eng, None, log=print if not tried else (lambda *_: None))
    mp3 = MA.G.encode_mp3(a48, kbps=c.get('kbps', 128))
    rep, errs = MA.verify(mp3, items, c.get('lufs', -16.0))
    tried.append((not errs, rep['short_term_std_lu'], win, rng, c, a48, items, mp3, rep, errs))
    if safe is None or (not errs and rep['short_term_std_lu'] <= safe):
        break
    print(f"  慢速电平 {win} 秒 ±{rng:g} dB：短时波动 {rep['short_term_std_lu']} LU"
          + (f"，{'；'.join(errs)}" if errs else f'，高于安全线 {safe}') + '，加强一档再试')
ok_runs = [t for t in tried if t[0]]
pick = (next((t for t in ok_runs if safe is None or t[1] <= safe), None)
        or min(ok_runs, key=lambda t: t[1], default=None) or tried[0])
_, _, win, rng, cfg, a48, items, mp3, rep, errs = pick
print(f"  响度：整体 {rep['integrated_lufs']} LUFS，句间最大偏差 {rep['sentence_max_dev_lu']} LU，短时波动 {rep['short_term_std_lu']} LU，"
      f"峰值 {rep['peak_dbfs']} dBFS；电磁音：梳状线 {rep['comb_db']:+.2f} dB，全频段最强 {rep['buzz_hz']:.0f} Hz {rep['buzz_db']:+.1f} dB")
if errs:
    raise SystemExit('检查未通过，未输出文件：' + '；'.join(errs))
OUT.mkdir(parents=True, exist_ok=True)
(OUT / f"{art['id']}.mp3").write_bytes(mp3)
dur = round(len(a48) / MA.OUT_SR, 3)
(OUT / f"{art['id']}_timings.json").write_text(json.dumps(
    {'voice': VOICE, 'file': f"{art['id']}.mp3", 'duration': dur, 'loudness': rep,
     'voice_cfg': {k: v for k, v in cfg.items() if k != 'ref_text'}, 'sentences': items},
    ensure_ascii=False, indent=1), 'utf-8')
print(f"已生成 {art['id']}.mp3（{dur:.1f} 秒），检查全部通过")
