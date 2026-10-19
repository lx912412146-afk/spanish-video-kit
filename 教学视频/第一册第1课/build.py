"""第一课教学视频：合成 → 语音识别核对 → 画面 → 视频。

    python build.py synth  工具包目录 西语识别模型目录 中文识别模型目录   # 合成全部讲解和示范、逐句识别核对、换种子重试，生成时间轴和音轨
    python build.py render 工具包目录                                    # 用 Chromium 把每个画面状态截成 PNG（要在普通终端运行）
    python build.py video                                                 # ffmpeg 拼成 MP4

- 中文讲解：Qwen3-TTS 克隆 build/ref_zh.wav（工具包女声说的一段中文，见 make_zh_ref.py），language=chinese。
- 西语示范：男声 qwen3_M1F5_25，女声是它克隆 Supertonic 3 F1（build/ref_female_F1.wav，和模拟卷听力同一个）。
- 核对：西语用 Parakeet-TDT 0.6B v3，中文用 SenseVoice（比带声调的拼音，同音字不算错）。
  有出入的句子换种子 2000…5000 重新合成，挑最准的一版，记在 build/seed_overrides.json。
"""
import difflib
import json
import re
import shutil
import subprocess
import sys
import unicodedata
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
B = HERE / 'build'
sys.path.insert(0, str(HERE))
from lesson1 import SCENES, TITLE  # noqa: E402

REF_ZH_TEXT = '同学们好，欢迎来到西班牙语课堂。今天我们一起学习发音、语法和课文，请大家跟着我认真练习。'
LEAD, ZH_GAP, ES_GAP, TAIL = 0.6, 0.35, 0.55, 0.9
SEEDS = (2000, 3000, 4000, 5000)
FPS = 30


# ---------------------------------------------------------------- 脚本展开
def scenes():
    out = []
    for i, sc in enumerate(SCENES):
        sc = dict(sc)
        if 'same_cards_as' in sc:
            sc['cards'] = out[i + sc['same_cards_as']]['cards']
        out.append(sc)
    return out


def card(sc, cid):
    return next(c for c in sc['cards'] if c['id'] == cid)


def tts_text(c):
    t = c.get('tts') or c.get('es') or ''
    t = t.replace('‿', ' ').replace('·', '')
    return t if re.search(r'[.!?…]$', t) else t + '.'


def lines():
    """[(声音, 文本)]：全部要合成的句子（去重前）。"""
    out = []
    for sc in scenes():
        for st in sc['steps']:
            if st[0] == 'zh':
                out.append(('ZH', st[1]))
            elif st[0] == 'es':
                out.append(('ES_' + st[2], tts_text(card(sc, st[1]))))
    return out


# ---------------------------------------------------------------- 声音
def load_kit(kit):
    sys.path.insert(0, str(kit / '西班牙语' / 'tools'))
    import c4
    MA = c4.load('es_make_audio', '西班牙语/tools/make_audio.py')
    MA.CACHE = B / '_合成缓存'
    return MA


def voices(MA):
    ref_f = B / 'ref_female_F1.wav'
    shared = HERE.parent.parent / '试卷' / '第一册高考模拟卷' / '听力' / 'ref_female_F1.wav'   # 仓库里和模拟卷共用
    if not ref_f.exists() and shared.exists():
        shutil.copyfile(shared, ref_f)
    male = dict(MA.VOICES['qwen3_M1F5_25'])
    female = dict(male, ref_audio=str(B / 'ref_female_F1.wav'))
    zh = dict(male, ref_audio=str(B / 'ref_zh.wav'), ref_text=REF_ZH_TEXT, language='chinese',
              max_s_per_char=0.4)                     # 中文每字的时长比西语字母长，放宽时长检查
    MA.chain(male)
    return {'ES_M': male, 'ES_F': female, 'ZH': zh}


def overrides():
    f = B / 'seed_overrides.json'
    return json.loads(f.read_text('utf-8')) if f.exists() else {}


def worker(MA, cfgs, v, seed=None):
    return MA.Worker(cfgs[v] if seed is None else dict(cfgs[v], seed=seed))


def synth(MA, cfgs, items):
    """items: [(声音, 文本)] → {(声音, 文本): (音频, 采样率)}，按种子覆盖分组合成。"""
    ov, groups, out = overrides(), {}, {}
    for v, t in dict.fromkeys(items):
        groups.setdefault((v, ov.get(f'{v}|{t}')), []).append(t)
    for (v, seed), ts in groups.items():
        for t, res in zip(ts, worker(MA, cfgs, v, seed).synth_all(ts)):
            out[(v, t)] = res
    return out


# ---------------------------------------------------------------- 识别核对
APOCOPE = {'veintiun': 'veintiuno', 'un': 'uno', 'una': 'uno'}
HOMOPHONES = {('si', 'c'), ('ah', 'a'), ('tambien', 'tan bien'), ('ana', 'anna')}
PARTICLES = {'de2', 'de5', 'di4'}                 # 结构助词“得、地”：拼音库按 de2 / di4 注音，识别常写成“的”
NAMES = {'xin', 'li'}


def norm_es(t):
    from num2words import num2words
    t = re.sub(r'\d+', lambda m: ' ' + num2words(int(m.group()), lang='es') + ' ', t.lower())
    t = ''.join(c for c in unicodedata.normalize('NFD', t) if unicodedata.category(c) != 'Mn')
    return [APOCOPE.get(w, w) for w in re.sub(r"[^a-zñ ]", ' ', t.replace("'", '')).split()]


def pinyin(t):
    from pypinyin import Style, lazy_pinyin
    t = ''.join(ch for ch in t if '一' <= ch <= '鿿')
    return lazy_pinyin(t, style=Style.TONE3, neutral_tone_with_five=True)


def diff(r, h):
    ops, err = [], 0
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(a=r, b=h, autojunk=False).get_opcodes():
        if op == 'equal':
            continue
        x, y = ' '.join(r[i1:i2]), ' '.join(h[j1:j2])
        ok = (x.replace(' ', '') == y.replace(' ', '') or (x, y) in HOMOPHONES or bool(r[i1:i2] and set(r[i1:i2]) <= NAMES)
              or bool(r[i1:i2] and h[j1:j2] and set(r[i1:i2]) | set(h[j1:j2]) <= PARTICLES))
        ops.append((x, y))
        err += 0 if ok else max(i2 - i1, j2 - j1)
    return err, ops


class Checker:
    def __init__(self, asr_es, asr_zh):
        import sherpa_onnx
        d = next(p for p in Path(asr_es).iterdir() if p.is_dir() and 'parakeet' in p.name)
        self.es = sherpa_onnx.OfflineRecognizer.from_transducer(
            encoder=str(d / 'encoder.int8.onnx'), decoder=str(d / 'decoder.int8.onnx'), joiner=str(d / 'joiner.int8.onnx'),
            tokens=str(d / 'tokens.txt'), model_type='nemo_transducer', num_threads=4)
        d = next(p for p in Path(asr_zh).iterdir() if p.is_dir() and 'sense-voice' in p.name) \
            if not (Path(asr_zh) / 'model.int8.onnx').exists() else Path(asr_zh)
        self.zh = sherpa_onnx.OfflineRecognizer.from_sense_voice(
            model=str(d / 'model.int8.onnx'), tokens=str(d / 'tokens.txt'), language='zh', use_itn=False, num_threads=4)

    def text(self, rec, a, sr):
        import soxr
        st = rec.create_stream()
        st.accept_waveform(16000, soxr.resample(a, sr, 16000).astype(np.float32))
        rec.decode_stream(st)
        return st.result.text.strip()

    def check(self, v, t, a, sr):
        if v == 'ZH':
            hyp = self.text(self.zh, a, sr)
            err, ops = diff(pinyin(t), pinyin(hyp))
        else:
            hyp = self.text(self.es, a, sr)
            err, ops = diff(norm_es(t), norm_es(hyp))
        return err, hyp, ops


def do_synth(kit, asr_es, asr_zh):
    MA = load_kit(Path(kit))
    G = MA.G
    cfgs = voices(MA)
    items = list(dict.fromkeys(lines()))
    audio = synth(MA, cfgs, items)
    chk = Checker(asr_es, asr_zh)
    report = {}
    for v, t in items:
        report[(v, t)] = chk.check(v, t, *audio[(v, t)])
    bad = [k for k, r in report.items() if r[0]]
    print(f'首轮：{len(items)} 句，有出入 {len(bad)} 句', flush=True)
    ov = overrides()
    for seed in SEEDS:
        bad = [k for k in bad if report[k][0]]
        if not bad:
            break
        for v in sorted({k[0] for k in bad}):
            ts = [t for vv, t in bad if vv == v]
            for t, (a, sr) in zip(ts, worker(MA, cfgs, v, seed).synth_all(ts)):
                r = chk.check(v, t, a, sr)
                print(f'  种子 {seed} {v} {r[0]} 处：{t} → {r[1]}', flush=True)
                if r[0] < report[(v, t)][0]:
                    report[(v, t)], audio[(v, t)] = r, (a, sr)
                    ov[f'{v}|{t}'] = seed
    (B / 'seed_overrides.json').write_text(json.dumps(ov, ensure_ascii=False, indent=1), 'utf-8')
    rows = [{'voice': v, 'text': t, 'errors': r[0], 'asr': r[1], 'diff': r[2], 'seed': ov.get(f'{v}|{t}')}
            for (v, t), r in report.items()]
    (B / '识别核对.json').write_text(json.dumps(rows, ensure_ascii=False, indent=1), 'utf-8')
    left = [x for x in rows if x['errors']]
    near = [x for x in rows if x['diff'] and not x['errors']]
    for x in left:
        print(f'✗ {x["voice"]} {x["text"]} → {x["asr"]}  {x["diff"]}')
    for x in near:
        print(f'≈ {x["voice"]} {x["text"]} → {x["asr"]}')
    print(f'核对：{len(rows)} 句；仍有出入 {len(left)} 句；只差空格、同音或人名 {len(near)} 句')

    # ---- 时间轴和音轨
    clip = {k: G.fade(G.level(G.trim(MA.to_sr(a, sr)))) for k, (a, sr) in audio.items()}
    SR = G.SR
    parts, states, t = [], [], 0.0

    def add(sec, **state):
        nonlocal t
        if sec <= 0:
            return
        parts.append(np.zeros(int(round(sec * SR)), np.float32))
        states.append(dict(state, t0=round(t, 4), dur=round(sec, 4)))
        t += sec

    def add_audio(a, **state):
        nonlocal t
        parts.append(a.astype(np.float32))
        states.append(dict(state, t0=round(t, 4), dur=round(len(a) / SR, 4)))
        t += len(a) / SR

    for si, sc in enumerate(scenes()):
        rev = []
        add(LEAD, scene=si, hl=None, sub='', rev=list(rev), badge=None)
        for st in sc['steps']:
            if st[0] == 'zh':
                add_audio(clip[('ZH', st[1])], scene=si, hl=None, sub=st[1], rev=list(rev), badge=None)
                add(ZH_GAP, scene=si, hl=None, sub=st[1], rev=list(rev), badge=None)
            elif st[0] == 'es':
                c = card(sc, st[1])
                a = clip[('ES_' + st[2], tts_text(c))]
                add_audio(a, scene=si, hl=st[1], sub='', es=st[1], rev=list(rev), badge='listen')
                if st[3]:
                    add(max(1.6, 1.4 * len(a) / SR) + 0.3, scene=si, hl=st[1], sub='', rev=list(rev), badge='repeat')
                else:
                    add(ES_GAP, scene=si, hl=st[1], sub='', rev=list(rev), badge=None)
            elif st[0] == 'reveal':
                rev.append(st[1])
            elif st[0] == 'pause':
                add(st[1], scene=si, hl=None, sub='', rev=list(rev), badge='think')
        add(TAIL, scene=si, hl=None, sub='', rev=list(rev), badge=None)
    mix = G.master(np.concatenate(parts), -16.0)
    import soundfile as sf
    sf.write(str(B / 'audio.wav'), mix, G.OUT_SR, subtype='PCM_16')
    (B / 'timeline.json').write_text(json.dumps({'total_s': round(t, 3), 'states': states}, ensure_ascii=False, indent=0), 'utf-8')
    print(f'音轨 {t / 60:.1f} 分钟，{len(states)} 个画面状态')


# ---------------------------------------------------------------- 画面
def merged_states():
    """把相邻、画面完全相同的状态合并。"""
    st = json.loads((B / 'timeline.json').read_text('utf-8'))['states']
    out = []
    for s in st:
        key = {k: v for k, v in s.items() if k not in ('t0', 'dur', 'es')}
        if out and out[-1]['key'] == key:
            out[-1]['dur'] += s['dur']
        else:
            out.append({'key': key, 't0': s['t0'], 'dur': s['dur']})
    return out


def do_render(kit):
    from playwright.sync_api import sync_playwright
    fonts = Path(kit) / '背景样式（6种）' / 'fonts' / 'fonts.css'
    page_html = (HERE / 'template.html').read_text('utf-8').replace('FONTS_CSS', fonts.as_uri())
    (B / 'page.html').write_text(page_html, 'utf-8')
    data = {'title': TITLE, 'scenes': scenes()}
    states = merged_states()
    fr = B / 'frames'
    shutil.rmtree(fr, ignore_errors=True)
    fr.mkdir(parents=True)
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        pg = br.new_page(viewport={'width': 1920, 'height': 1080})
        pg.goto((B / 'page.html').as_uri())
        pg.evaluate('d => window.setData(d)', data)
        pg.wait_for_timeout(800)
        cache = {}
        for i, s in enumerate(states):
            k = json.dumps(s['key'], sort_keys=True, ensure_ascii=False)
            f = fr / f'{i:05d}.png'
            if k in cache:
                shutil.copyfile(cache[k], f)
            else:
                pg.evaluate('s => window.render(s)', s['key'])
                pg.evaluate('document.fonts.ready')
                pg.screenshot(path=str(f))
                cache[k] = f
        br.close()
    (B / 'frames.json').write_text(json.dumps([round(s['dur'], 4) for s in states]), 'utf-8')
    print(f'画面：{len(states)} 张（不同的 {len(cache)} 张）')


def do_preview(kit):
    """每屏一张样图（高亮第一张卡片、带第一句讲解字幕），排版检查用：build/preview/。"""
    from playwright.sync_api import sync_playwright
    fonts = Path(kit) / '背景样式（6种）' / 'fonts' / 'fonts.css'
    (B / 'page.html').write_text((HERE / 'template.html').read_text('utf-8').replace('FONTS_CSS', fonts.as_uri()), 'utf-8')
    out = B / 'preview'
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True)
    scs = scenes()
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        pg = br.new_page(viewport={'width': 1920, 'height': 1080})
        pg.goto((B / 'page.html').as_uri())
        pg.evaluate('d => window.setData(d)', {'title': TITLE, 'scenes': scs})
        pg.wait_for_timeout(800)
        for i, sc in enumerate(scs):
            zh = next((s[1] for s in sc['steps'] if s[0] == 'zh'), '')
            hl = sc['cards'][min(1, len(sc.get('cards') or [0]) - 1)]['id'] if sc.get('cards') else None
            rev = [c['id'] for c in sc.get('cards', [])][:2] if sc['layout'] == 'quiz' else []
            for j, key in enumerate(({'scene': i, 'hl': None, 'sub': zh, 'rev': rev, 'badge': None},
                                     {'scene': i, 'hl': hl, 'sub': '', 'rev': rev, 'badge': 'repeat'})):
                pg.evaluate('s => window.render(s)', key)
                pg.evaluate('document.fonts.ready')
                pg.screenshot(path=str(out / f'{i:02d}_{j}.png'))
        br.close()
    print('PREVIEW_DONE', len(scs))


def do_video():
    durs = json.loads((B / 'frames.json').read_text('utf-8'))
    frames = sorted((B / 'frames').glob('*.png'))
    assert len(frames) == len(durs)
    # 累计时间取整到帧，避免长片误差累积
    lines_, cum, prev = [], 0.0, 0
    for f, d in zip(frames, durs):
        cum += d
        n = round(cum * FPS) - prev
        prev += n
        lines_ += [f"file '{f.as_posix()}'", f'duration {n / FPS:.6f}']
    lines_.append(f"file '{frames[-1].as_posix()}'")
    (B / 'concat.txt').write_text('\n'.join(lines_) + '\n', 'utf-8')
    out = HERE / '第1课_Quién_es_él_教学视频.mp4'
    ff = shutil.which('ffmpeg') or str(Path(sys.executable).parent / 'ffmpeg')
    subprocess.run([ff, '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', str(B / 'concat.txt'),
                    '-i', str(B / 'audio.wav'), '-vf', f'fps={FPS},format=yuv420p', '-c:v', 'libx264', '-preset', 'medium',
                    '-crf', '18', '-tune', 'stillimage', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart',
                    '-shortest', str(out)], check=True)
    print(out.name, f'{out.stat().st_size / 1e6:.1f} MB')


if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'synth':
        do_synth(*sys.argv[2:5])
    elif cmd == 'render':
        do_render(sys.argv[2])
    elif cmd == 'preview':
        do_preview(sys.argv[2])
    elif cmd == 'video':
        do_video()
