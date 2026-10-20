"""HSK1 中文阅读：合成逐句朗读音频（沿用西班牙语分级阅读的做法和核查）。

    python make_audio.py <工具包根目录> <文章 JSON> <输出目录> <SenseVoice 模型目录>

- 声音：Qwen3-TTS 1.7B 克隆 教学视频/第一册第1课/build/ref_zh.wav（工具包女声说的一段中文，第一课教学视频的中文讲解用的就是它），
  language=chinese。合成后放慢到 0.85 倍（tempo；0.8 倍时电磁音核查在 3.7 kHz 处超限），音高不变，吐字更清楚，适合 HSK1 初学者。
- 分段：每句在句中的 ，、；： 处停 0.35 秒，在句中的 ！？。 处停 0.5 秒；句间 0.8 秒；片头 1.5 秒、结尾 2 秒静音（和西语分级阅读一样）。
- 核对：每段用 SenseVoice 识别，转成带声调拼音和原文比（同音字不算错）；有出入的段换种子重合成，挑最准的一版。
  任何一段最后仍有出入就不输出（--draft 除外）。
- 响度：西语那条处理链（K 加权电平、压缩、慢速电平、-16 LUFS），用 loudness.verify 核查四项。
输出：<输出目录>/<id>.mp3、<id>.srt、<id>_timings.json、<id>_识别核对.json。
"""
import argparse
import difflib
import json
import os
import re
import sys
from pathlib import Path

import numpy as np

if os.environ.get('PYLIB'):                                  # pypinyin 装在别处时用 PYLIB 指定
    sys.path.insert(0, os.environ['PYLIB'])

REF_ZH_TEXT = '同学们好，欢迎来到西班牙语课堂。今天我们一起学习发音、语法和课文，请大家跟着我认真练习。'
SEEDS = (2000, 3000, 4000, 5000, 6000)
CLAUSE, STOP = 0.35, 0.5
TEMPO = 0.85
PARTICLES = {'de2', 'de5', 'di4'}


def segments(zh):
    """'我是学生，我学习中文。' → [('我是学生，', 0.35), ('我学习中文。', None)]：(文字, 之后的停顿)。"""
    parts = re.findall(r'[^，、；：！？。]+[，、；：！？。]?', zh)
    out = []
    for i, t in enumerate(parts):
        last = i == len(parts) - 1
        out.append((t, None if last else (STOP if t[-1] in '！？。' else CLAUSE)))
    return out


def pinyin(t):
    from pypinyin import Style, lazy_pinyin
    t = ''.join(ch for ch in t if '一' <= ch <= '鿿')
    return lazy_pinyin(t, style=Style.TONE3, neutral_tone_with_five=True)


def diff(r, h):
    ops, err = [], 0
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(a=r, b=h, autojunk=False).get_opcodes():
        if op == 'equal':
            continue
        x, y = r[i1:i2], h[j1:j2]
        ok = bool(x and y and set(x) | set(y) <= PARTICLES)
        ops.append((' '.join(x), ' '.join(y)))
        err += 0 if ok else max(i2 - i1, j2 - j1)
    return err, ops


class ASR:
    def __init__(self, d):
        import sherpa_onnx
        d = Path(d)
        if not (d / 'model.int8.onnx').exists():
            d = next(p for p in d.iterdir() if p.is_dir() and 'sense-voice' in p.name)
        self.rec = sherpa_onnx.OfflineRecognizer.from_sense_voice(
            model=str(d / 'model.int8.onnx'), tokens=str(d / 'tokens.txt'), language='zh', use_itn=False, num_threads=4)

    def check(self, text, a, sr):
        import soxr
        st = self.rec.create_stream()
        st.accept_waveform(16000, soxr.resample(a, sr, 16000).astype(np.float32))
        self.rec.decode_stream(st)
        hyp = st.result.text.strip()
        err, ops = diff(pinyin(text), pinyin(hyp))
        return err, hyp, ops


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('kit')
    ap.add_argument('article')
    ap.add_argument('out')
    ap.add_argument('asr')
    ap.add_argument('--draft', action='store_true')
    a = ap.parse_args()
    kit, out = Path(a.kit), Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    sys.path.insert(0, str(kit / '西班牙语' / 'tools'))
    import c4
    MA = c4.load('es_make_audio', '西班牙语/tools/make_audio.py')
    MA.CACHE = out / '_合成缓存'
    G, SR = MA.G, MA.SR
    p = json.loads(Path(a.article).read_text('utf-8'))

    cfg = dict(MA.VOICES['qwen3_M1F5_25'], label='Qwen3-TTS 克隆 ref_zh.wav（中文女声），0.85 倍速',
               ref_audio=str(kit / '教学视频' / '第一册第1课' / 'build' / 'ref_zh.wav'), ref_text=REF_ZH_TEXT,
               language='chinese', max_s_per_char=0.4, tempo=TEMPO, pitch_cents=0, clause_pause=CLAUSE)
    MA.chain(cfg)

    plan = [(k, s, segments(s['zh'])) for k, s in enumerate(p['sents'], 1)]
    texts = list(dict.fromkeys(t for *_, segs in plan for t, _ in segs))
    raw = dict(zip(texts, MA.Worker(cfg).synth_all(texts)))
    asr = ASR(a.asr)
    rep = {t: asr.check(t, *raw[t]) for t in texts}
    seeds = {}
    for seed in SEEDS:
        bad = [t for t in texts if rep[t][0]]
        if not bad:
            break
        for t, res in zip(bad, MA.Worker(dict(cfg, seed=seed)).synth_all(bad)):
            r = asr.check(t, *res)
            print(f'  种子 {seed}：{t} → {r[1]}（{r[0]} 处出入）', flush=True)
            if r[0] < rep[t][0]:
                rep[t], raw[t], seeds[t] = r, res, seed
    rows = [{'text': t, 'errors': rep[t][0], 'asr': rep[t][1], 'diff': rep[t][2], 'seed': seeds.get(t, cfg['seed'])} for t in texts]
    (out / f'{p["id"]}_识别核对.json').write_text(json.dumps(rows, ensure_ascii=False, indent=1), 'utf-8')
    left = [x for x in rows if x['errors']]
    print(f'识别核对：{len(texts)} 段，' + ('全部一致' if not left else f'仍有出入 {len(left)} 段：' + '；'.join(f"{x['text']}→{x['asr']}" for x in left)))
    if left and not a.draft:
        raise SystemExit('识别核对未通过，未输出音频')

    pieces = [np.zeros(int(round(cfg['lead_in'] * SR)), np.float32)]
    t = len(pieces[0]) / SR
    items = []
    for n, (k, s, segs) in enumerate(plan):
        st, parts = t, []
        for txt, pause in segs:
            a0, sr = raw[txt]
            seg = G.fade(G.level(G.trim(MA.to_sr(MA.tempo_pitch(a0, sr, TEMPO, 0), sr))))
            parts.append([round(t, 3), round(t + len(seg) / SR, 3)])
            pieces.append(seg)
            t += len(seg) / SR
            if pause:
                pieces.append(np.zeros(int(round(pause * SR)), np.float32))
                t += pause
        items.append({'k': k, 'para': 1, 'start': round(st, 3), 'end': round(t, 3), 'parts': parts,
                      'segments': [x for x, _ in segs], 'text': s['zh'], 'read': s['zh']})
        g = cfg['tail'] if n == len(plan) - 1 else cfg['sentence_pause']
        pieces.append(np.zeros(int(round(g * SR)), np.float32))
        t += g
    a48 = G.master(np.concatenate(pieces), cfg.get('lufs', -16.0))
    mp3 = G.encode_mp3(a48, kbps=cfg.get('kbps', 128))
    lrep, errs = MA.verify(mp3, items, cfg.get('lufs', -16.0))
    print(f"响度：整体 {lrep['integrated_lufs']} LUFS，句间最大偏差 {lrep['sentence_max_dev_lu']} LU，短时波动 {lrep['short_term_std_lu']} LU，"
          f"峰值 {lrep['peak_dbfs']} dBFS；电磁音：梳状线 {lrep['comb_db']:+.2f} dB")
    if errs and not a.draft:
        raise SystemExit('响度核查未通过：' + '；'.join(errs))
    (out / f'{p["id"]}.mp3').write_bytes(mp3)
    srt = []
    for i, it in enumerate(items, 1):
        srt += [str(i), f"{G.fmt_ts(it['start'])} --> {G.fmt_ts(it['end'])}", it['text'], p['sents'][i - 1]['es'], '']
    (out / f'{p["id"]}.srt').write_text('\n'.join(srt), 'utf-8')
    dur = len(a48) / MA.OUT_SR
    (out / f'{p["id"]}_timings.json').write_text(json.dumps(
        {'file': f'{p["id"]}.mp3', 'duration': round(dur, 3), 'loudness': lrep,
         'voice_cfg': dict(cfg, ref_audio=str(Path(cfg['ref_audio']).relative_to(kit))), 'sentences': items,
         'draft_issues': errs}, ensure_ascii=False, indent=1), 'utf-8')
    print(f'已生成 {out / (p["id"] + ".mp3")}（{dur:.1f} 秒）')


if __name__ == '__main__':
    main()
