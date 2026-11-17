"""《Método de español》第 1–2 册高考模拟卷：听力录音（高考格式）和逐句语音识别核对。

    python make_listening.py build <工具包目录> <试卷.md> <输出目录> <西语识别模型目录> <中文识别模型目录>
    python make_listening.py final <工具包目录> <试卷.md> <输出目录> <西语识别模型目录> <中文识别模型目录>

build：合成、逐句核对、拼成整套录音、查响度和电磁音；final：在成品 MP3 里把每一句切出来再识别一遍。
沿用 B1—B2 听力练习的 tools/make_tracks.py（声音、合成缓存、换种子、识别比对规则、补救办法都一样），不同的是：
- 台词直接读试卷的「听力原文」（**Texto N** 下的「男：」「女：」行），每段对话男女各用一个声音（VOICES），
  六个西语声音和 A1、A2、B1 教程、B1—B2 听力练习相同：男1＝工具包推荐男声 qwen3_M1F5_25，男2、女2、女3 见 A2教程/voices/，
  女1＝第一册高考模拟卷的 ref_female_F1.wav，女4＝B1教程/voices/ref_F3.wav。
- 指令语用中文（高考听力录音的做法），声音是第一册第 1 课教学视频的中文女声（Qwen3 克隆 教学视频/第一册第1课/build/ref_zh.wav），
  用 SenseVoice 识别，逐字（汉字、字母）比对；数字一律写成汉字。
- 结构（按高考新课标卷，2026 年起第一节也播两遍）：试音 → 第一节说明 → 读第 1 题 5 秒 → 每段：段号、录音、停 3 秒、再放一遍、留 10 秒
  → 第二节说明 → 每段：“听第 N 段录音，回答第 a 至 b 题”、读题（每题 5 秒）、录音、停 3 秒、再放一遍、作答（每题 5 秒）→ 结束语。
- 语速：西语 0.95 倍（同 A1—A2 听力练习的后几套），中文 0.92 倍。对话里同一人连续两句停 0.35 秒，换人停 0.6 秒。
- 成品：G.master 到 −16 LUFS，MP3 128k；用工具包的 verify 核查整体响度、峰值和电磁音，短时响度波动在去掉长停顿的朗读部分上量。
输出：<输出目录>/听力_完整.mp3、Texto_1.mp3 … Texto_9.mp3（每段只放一遍，供讲评）、听力_时间轴.json、听力_识别核对.json、听力_成品复核.json。
"""
import difflib
import json
import re
import sys
import unicodedata
from pathlib import Path

import numpy as np

MODE = sys.argv[1]
KIT, PAPER, OUT, ASR, ASR_ZH = (Path(p).resolve() for p in sys.argv[2:7])
sys.path.insert(0, str(KIT / '西班牙语' / 'tools'))
import c4  # noqa: E402

MA = c4.load('es_make_audio', '西班牙语/tools/make_audio.py')
MA.CACHE = OUT / '_合成缓存'
G = MA.G
SR = G.SR
SEEDS = (2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000)
SENT_GAP, TURN_GAP, LEAD, TAIL = 0.35, 0.6, 1.5, 2.0
ZH_CLAUSE, ZH_STOP, BLOCK_GAP = 0.3, 0.45, 1.0
REPEAT_GAP, LABEL_GAP = 3.0, 0.8
TEMPO = {'es': 0.95, 'zh': 0.92}

MALE = dict(MA.VOICES['qwen3_M1F5_25'])
MA.chain(MALE)
REFS = {'女1': KIT / '试卷' / '第一册高考模拟卷' / '听力' / 'ref_female_F1.wav',
        '男2': KIT / 'A2教程' / 'voices' / 'ref_M5.wav', '女2': KIT / 'A2教程' / 'voices' / 'ref_F2.wav',
        '女3': KIT / 'A2教程' / 'voices' / 'ref_F5.wav', '女4': KIT / 'B1教程' / 'voices' / 'ref_F3.wav'}
REF_ZH = KIT / '教学视频' / '第一册第1课' / 'build' / 'ref_zh.wav'
REF_ZH_TEXT = '同学们好，欢迎来到西班牙语课堂。今天我们一起学习发音、语法和课文，请大家跟着我认真练习。'
ZH = '中'          # 中文指令语的声音

# 每段对话的声音：同一段里男女声音不同；相邻几段尽量换声音
VOICES = {1: {'女': '女2', '男': '男2'}, 2: {'男': '男1', '女': '女3'}, 3: {'女': '女1', '男': '男2'},
          4: {'男': '男1', '女': '女4'}, 5: {'男': '男2', '女': '女2'}, 6: {'女': '女1', '男': '男2'},
          7: {'男': '男1', '女': '女3'}, 8: {'女': '女4'}, 9: {'男': '男2', '女': '女2'}}
TRIAL = [('男1', 'Hola a todos. Esta es la prueba de sonido del examen de español.')]
QUESTIONS = {6: (6, 8), 7: (9, 12), 8: (13, 16), 9: (17, 20)}
CN_NUM = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十']


def cn(n):
    """1–99 写成汉字（十五、二十、十）。"""
    if n <= 10:
        return CN_NUM[n]
    t, u = divmod(n, 10)
    return ('' if t == 1 else CN_NUM[t]) + '十' + (CN_NUM[u] if u else '')


def voice_cfg(v, seed=None):
    if v == ZH:
        cfg = dict(MALE, ref_audio=str(REF_ZH), ref_text=REF_ZH_TEXT, language='chinese', max_s_per_char=0.4,
                   label='Qwen3-TTS 克隆 ref_zh.wav（中文女声，听力指令语）')
    elif v == '男1':
        cfg = dict(MALE)
    else:
        cfg = dict(MALE, ref_audio=str(REFS[v]), label=f'Qwen3-TTS 克隆（西班牙语教程 {v}，与 A1、A2、B1 教程相同的声音）')
    if seed is not None:
        cfg['seed'] = seed
    return cfg


def lang(v):
    return 'zh' if v == ZH else 'es'


# ---------------------------------------------------------------- 录音稿
def parse_texts(md):
    sec = md.split('## 听力原文', 1)[1].split('\n## ', 1)[0]
    texts, cur = {}, None
    for line in sec.splitlines():
        m = re.match(r'\*\*Texto (\d+)\*\*', line.strip())
        if m:
            cur = int(m.group(1))
            texts[cur] = []
            continue
        m = re.match(r'^(?:- )?([男女])：(.+)$', line.strip())
        if m and cur:
            texts[cur].append((m.group(1), m.group(2).strip()))
    if sorted(texts) != list(range(1, 10)) or not all(texts.values()):
        raise SystemExit('听力原文解析不完整')
    return texts


def script(texts):
    """整套录音的顺序：[(类型, 内容)]。类型：zh＝中文指令（一句或几句）、es＝试音的西语句子、silence＝秒数、
    dialogue＝第几段（播放一次）、label＝段号的中文。"""
    s = [('silence', LEAD), ('zh', '现在是听力试音时间。'), ('silence', BLOCK_GAP)]
    s += [('es', t) for t in TRIAL] + [('silence', 1.5), ('zh', '试音到此结束。'), ('silence', 2.0)]
    s += [('zh', '听力考试正式开始。请看第一部分听力第一节。'), ('silence', 0.8),
          ('zh', '听下面五段录音，每段录音后有一道小题，从题中所给的A、B、C三个选项中选出最佳选项。'
                 '每段录音后有十秒钟，用来作答和阅读下一小题。每段录音播放两遍。'), ('silence', BLOCK_GAP),
          ('zh', '现在，你有五秒钟的时间阅读第一小题。'), ('silence', 5.0)]
    for k in range(1, 6):
        s += [('zh', f'第{cn(k)}段录音。'), ('silence', LABEL_GAP), ('dialogue', k), ('silence', REPEAT_GAP), ('dialogue', k),
              ('silence', 10.0)]
    s += [('zh', '第二节。听下面四段录音，每段录音后有几道小题，从题中所给的A、B、C三个选项中选出最佳选项。'
                 '每段录音播放前，有时间阅读小题，每小题五秒钟；播放后，每小题有五秒钟作答。每段录音播放两遍。'),
          ('silence', BLOCK_GAP)]
    for k, (a, b) in QUESTIONS.items():
        n = b - a + 1
        s += [('zh', f'听第{cn(k)}段录音，回答第{cn(a)}至{cn(b)}题。现在，你有{cn(5 * n)}秒钟的时间阅读这{cn(n)}道小题。'),
              ('silence', 5.0 * n), ('dialogue', k), ('silence', REPEAT_GAP), ('dialogue', k), ('silence', 5.0 * n)]
    s += [('zh', '听力部分到此结束。现在，你有两分钟的时间将试卷上的答案转涂到答题卡上。'), ('silence', TAIL)]
    return s


def zh_pieces(t):
    """中文指令按句号、分号、问号切成几段分别合成；返回 [(文字, 之后的停顿)]。"""
    parts = re.findall(r'[^。；！？]+[。；！？]?', t)
    return [(p, None if i == len(parts) - 1 else (ZH_CLAUSE if p.endswith('；') else ZH_STOP)) for i, p in enumerate(parts)]


def sentences(s):
    return [p for p in re.split(r'(?<=[.!?…])\s+', s.strip()) if p]


def spoken(s):
    return s.replace('«', '').replace('»', '')


# ---------------------------------------------------------------- 西语识别核对（同 B1—B2 听力练习 make_tracks.py）
NUMW = None
APOCOPE = {'veintiun': 'veintiuno', 'un': 'uno', 'una': 'uno'}
NAME2LETTER = {'a': 'a', 'be': 'b', 'ce': 'c', 'de': 'd', 'e': 'e', 'efe': 'f', 'ge': 'g', 'hache': 'h', 'i': 'i', 'jota': 'j', 'ka': 'k',
               'ele': 'l', 'eme': 'm', 'ene': 'n', 'o': 'o', 'pe': 'p', 'cu': 'q', 'erre': 'r', 'ese': 's', 'te': 't', 'u': 'u', 'uve': 'v',
               'equis': 'x', 'ye': 'y', 'y': 'y', 'zeta': 'z'}
for ch in 'bcdfghjklmnpqrstvwxz':
    NAME2LETTER.setdefault(ch, ch)
PLAIN = {'L:a': 'a', 'L:e': 'e', 'L:i': 'i', 'L:o': 'o', 'L:u': 'u', 'L:y': 'y', 'L:d': 'de', 'L:t': 'te'}
CIENTOS = {'doscientos', 'trescientos', 'cuatrocientos', 'quinientos', 'seiscientos', 'setecientos', 'ochocientos', 'novecientos'}


def split_caps(t):
    toks = re.split(r'(\s+|-)', t)
    core = [re.sub(r'[^\wÑñ]', '', x) for x in toks]
    single = lambda k: 0 <= k < len(core) and len(core[k]) == 1 and core[k].isalpha()
    words = [k for k, x in enumerate(core) if x]
    for i, k in enumerate(words):
        if re.fullmatch(r'[A-ZÑ]{2,3}', core[k]):
            nb = [words[i - 1] if i else -1, words[i + 1] if i + 1 < len(words) else -1]
            if any(single(j) for j in nb):
                toks[k] = toks[k].replace(core[k], ' '.join(core[k]))
    return ''.join(toks)


def norm(t, digitwise=False, hyp=False, glue=False):
    global NUMW
    if NUMW is None:
        from num2words import num2words
        NUMW = num2words
    if hyp:
        t = re.sub(r'(\d+),(\d{2})\s*(euros?)\b', r'\1 \3 \2', t)
        t = re.sub(r'\b(\d+ euros? con \d+) euros?\b', r'\1', t)
        t = re.sub(r'(\d+),(\d{2})\s*€', r'\1 euros \2', t)
        t = re.sub(r'(\d+)\s*€', r'\1 euros', t)
        t = re.sub(r'(\d+)\s*%', r'\1 por ciento', t)
        t = t.replace('<unk>', ' ')
        t = re.sub(r'\b(\d{1,2}):30\b', r'\1 y media', t)
        t = re.sub(r'\b(\d{1,2}):15\b', r'\1 y cuarto', t)
        t = re.sub(r'\b(\d{1,2}):00\b', r'\1', t)
        t = re.sub(r'\b(\d{1,2}):(\d{2})\b', r'\1 y \2', t)
        t = split_caps(t).replace('-', ' ')
    t = re.sub(r'(?<![\d.])\d{1,3}(?:\.\d{3})+(?!\d|\.\d)', lambda m: m.group().replace('.', ''), t.lower())
    if digitwise:
        t = re.sub(r'\d+(?:[- ]\d+)+|\d{4,}', lambda m: ' '.join(NUMW(int(d), lang='es') for d in re.findall(r'\d', m.group())), t)
    t = re.sub(r'(\d+):(\d{2})', lambda m: f' {m.group(1)} {m.group(2)} ', t)
    t = re.sub(r'\d+', lambda m: ' ' + NUMW(int(m.group()), lang='es') + ' ', t)
    t = ''.join(c for c in unicodedata.normalize('NFD', t) if unicodedata.category(c) != 'Mn' or c == '̃')
    t = unicodedata.normalize('NFC', t)
    t = re.sub(r'[:;.!?¿¡…]', ' | ', t)
    words = [APOCOPE.get(w, w) for w in re.sub(r"[^a-zñ |]", ' ', t.replace("'", '')).split()]
    words = [w for k, w in enumerate(words) if not (w == 'con' and k and words[k - 1] in ('euro', 'euros'))]
    out, run, glued = [], [], set()
    for w in words + ['|']:
        if w in NAME2LETTER:
            run.append(NAME2LETTER[w])
            continue
        if glue and len(run) >= 2:
            out.append(''.join(run))
            glued.add(''.join(run))
        else:
            out += [f'L:{x}' for x in run]
        run = []
        if w != '|':
            out.append(w)
    return (out, glued) if glue else out


def lenient_tokens(s):
    words = re.findall(r"[\wÁÉÍÓÚÑáéíóúñü']+", s)
    names = set()
    for k, w in enumerate(words):
        if w[:1].isupper() and k > 0 and not re.search(r'[.!?¿¡:]\s*$', s[:s.find(w)]):
            names.update(x for x in norm(w) if not x.startswith('L:'))
    return names


def sounds_same(x, y):
    def key(t):
        t = re.sub(r'c(?=[ei])', 's', t.replace(' ', '')).replace('z', 's')
        t = re.sub(r'(?<!c)h', '', t).replace('v', 'b')
        t = re.sub(r'n(?=[pbm])', 'm', t)
        return re.sub(r'(.)\1', r'\1', t).replace('y', 'i')
    return key(x) == key(y)


def fem_hundreds(x, y, hyp):
    xs, ys = x.split(), y.split()
    return bool(re.search(r'\d', hyp)) and len(xs) == len(ys) and xs != ys and \
        all(a == b or (b in CIENTOS and a == b[:-2] + 'as') for a, b in zip(xs, ys))


def loose(ws, gl):
    spelled = lambda j: 0 <= j < len(ws) and (ws[j].startswith('L:') or ws[j] in gl)
    return [PLAIN[w] if w in PLAIN and not spelled(k - 1) and not spelled(k + 1) else w for k, w in enumerate(ws)]


def compare1(s, hyp, digitwise=False, glue=False):
    (r, gr), (h, gh) = norm(spoken(s), glue=True) if glue else (norm(spoken(s)), set()), \
        norm(hyp, digitwise, hyp=True, glue=True) if glue else (norm(hyp, digitwise, hyp=True), set())
    r, h = loose(r, gr), loose(h, gh)
    soft = lenient_tokens(s)
    err, ops = 0, []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(a=r, b=h, autojunk=False).get_opcodes():
        if op == 'equal':
            continue
        x, y = ' '.join(r[i1:i2]), ' '.join(h[j1:j2])
        if x.replace('L:i', 'L:y').replace('i', 'y') == y.replace('i', 'y') and ('L:i' in x or (glue and x in gr)):
            continue
        if op == 'replace' and fem_hundreds(x, y, hyp):
            ops.append([x, y, '不计'])
            continue
        strict = any(w.startswith('L:') or w in gr for w in r[i1:i2]) or any(w.startswith('L:') or w in gh for w in h[j1:j2])
        if not strict and sounds_same(x, y):
            continue
        prev = r[i1 - 1] if i1 else ''
        if not strict and op == 'replace' and prev.startswith('L:') and sounds_same(prev[2:] + x, prev[2:] + y):
            continue
        plain = lambda w: not w.startswith('L:') and w not in gr and w not in gh
        pre = r[i1 - 1] if i1 and j1 and r[i1 - 1] == h[j1 - 1] and plain(r[i1 - 1]) else ''
        nxt = r[i2] if i2 < len(r) and j2 < len(h) and r[i2] == h[j2] and plain(r[i2]) else ''
        if not strict and (pre or nxt) and any(sounds_same(f'{a} {x} {b}', f'{a} {y} {b}') for a, b in ((pre, ''), ('', nxt), (pre, nxt))):
            continue
        counts = strict or not (r[i1:i2] and h[j1:j2] and set(r[i1:i2]) <= soft)
        ops.append([x, y] if counts else [x, y, '不计'])
        err += max(len(x.split()), len(y.split())) if counts else 0
    return err, ops


def compare_es(s, hyp):
    return min((compare1(s, hyp, d, g) for d in (False, True) for g in (False, True)), key=lambda x: x[0])


# ---------------------------------------------------------------- 中文识别核对：汉字和字母逐个比，阿拉伯数字换成汉字
def zh_tokens(t):
    t = unicodedata.normalize('NFKC', t)
    t = re.sub(r'\d+', lambda m: cn(int(m.group())) if int(m.group()) < 100 else m.group(), t)
    return [ch.upper() if ch.isascii() else ch for ch in t if ('一' <= ch <= '鿿') or (ch.isascii() and ch.isalpha())]


# 同音字（读音完全相同，识别模型不认这个词，写成了同音的常用字）：{原文的字: 识别写成的字}。
# “转涂到答题卡上”：SenseVoice 不认“转涂”，读对了（tú）就写成“转图”，读错了写成“转读”（dú）——只放过前者。
ZH_SAME = {'涂': '图'}


def compare_zh(s, hyp):
    for a, b in ZH_SAME.items():
        if a in s and b not in s:
            hyp = hyp.replace(b, a)
    r, h = zh_tokens(s), zh_tokens(hyp)
    err, ops = 0, []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(a=r, b=h, autojunk=False).get_opcodes():
        if op != 'equal':
            ops.append([''.join(r[i1:i2]), ''.join(h[j1:j2])])
            err += max(i2 - i1, j2 - j1)
    return err, ops


def compare(v, s, hyp):
    return compare_zh(s, hyp) if lang(v) == 'zh' else compare_es(s, hyp)


class Recognizers:
    def __init__(self):
        import sherpa_onnx
        d = ASR if (ASR / 'tokens.txt').exists() else next(p for p in ASR.iterdir() if p.is_dir() and 'parakeet' in p.name)
        self.es = sherpa_onnx.OfflineRecognizer.from_transducer(
            encoder=str(d / 'encoder.int8.onnx'), decoder=str(d / 'decoder.int8.onnx'), joiner=str(d / 'joiner.int8.onnx'),
            tokens=str(d / 'tokens.txt'), model_type='nemo_transducer', num_threads=4)
        z = ASR_ZH if (ASR_ZH / 'model.int8.onnx').exists() else next(p for p in ASR_ZH.iterdir() if p.is_dir() and 'sense-voice' in p.name)
        self.zh = sherpa_onnx.OfflineRecognizer.from_sense_voice(model=str(z / 'model.int8.onnx'), tokens=str(z / 'tokens.txt'),
                                                                 language='zh', use_itn=False, num_threads=4)

    def __call__(self, which, a, sr):
        import soxr
        rec = self.zh if which == 'zh' else self.es
        st = rec.create_stream()
        pad = np.zeros(int(0.3 * sr), np.float32)
        st.accept_waveform(16000, soxr.resample(np.concatenate([pad, a, pad]), sr, 16000).astype(np.float32))
        rec.decode_stream(st)
        return st.result.text.strip()


# 整句识别有出入、但切成片段单独识别核对过读音是对的：{(声音, 句子): 种子或 None}
VERIFIED = {}


def record(rec, v, s, a, sr, seed):
    hyp = rec(lang(v), a, sr)
    e, ops = compare(v, s, hyp)
    return {'voice': v, 'text': s, 'asr': hyp, 'errors': e, 'diff': ops, 'seed': seed}


def synth(requests, rec, log=print):
    """requests: {(声音, 文字)}；返回 {(声音, 文字): (原始音频, sr, 核对记录)}。有出入就换种子重合成，挑最好的一版。"""
    by_voice = {}
    for v, s in sorted(requests):
        by_voice.setdefault(v, []).append(s)
    got = {}
    for v, texts in by_voice.items():
        for s, (a, sr) in zip(texts, MA.Worker(voice_cfg(v)).synth_all([spoken(t) for t in texts])):
            got[(v, s)] = (a, sr, record(rec, v, s, a, sr, None))
    for (v, s), seed in VERIFIED.items():
        if (v, s) in got:
            if seed is not None:
                (a, sr), = MA.Worker(voice_cfg(v, seed)).synth_all([spoken(s)])
                got[(v, s)] = (a, sr, record(rec, v, s, a, sr, seed))
            got[(v, s)][2].update(errors=0, verified='整句识别有出入，切成片段单独识别核对过，读音正确')
    for seed in SEEDS:
        bad = {}
        for (v, s), (_, _, r) in got.items():
            if r['errors']:
                bad.setdefault(v, []).append(s)
        if not bad:
            break
        for v, texts in bad.items():
            for s, (a, sr) in zip(texts, MA.Worker(voice_cfg(v, seed)).synth_all([spoken(t) for t in texts])):
                r = record(rec, v, s, a, sr, seed)
                log(f"  种子 {seed} {v}：{s} → {r['asr']}（{r['errors']}）")
                if r['errors'] < got[(v, s)][2]['errors']:
                    got[(v, s)] = (a, sr, r)
    return got


# ---------------------------------------------------------------- 拼接
def silence(sec):
    return np.zeros(int(round(sec * SR)), np.float32)


def piece(raw, tempo):
    a, sr = raw[0], raw[1]
    return G.fade(G.level(G.trim(MA.to_sr(MA.tempo_pitch(a, sr, tempo, 0), sr))))


def units(texts):
    """要合成的全部片段：{(声音, 文字)}。"""
    u = set()
    for kind, x in script(texts):
        if kind == 'zh':
            u.update((ZH, p) for p, _ in zh_pieces(x))
        elif kind == 'es':
            u.update((x[0], s) for s in sentences(x[1]))
    for k, lines in texts.items():
        for who, line in lines:
            u.update((VOICES[k][who], s) for s in sentences(line))
    return u


def assemble(texts, got, only=None):
    """only=None：整套；only=k：只放第 k 段一遍（讲评用）。返回 (48 kHz 成品, 时间表, 朗读部分, 段落表)。"""
    out, items, speech, marks, t = [], [], [], [], 0.0
    cache = {}

    def add(seg, item=None):
        nonlocal t
        if item is not None:
            items.append(dict(item, start=round(t, 3), end=round(t + len(seg) / SR, 3)))
            speech.append(seg)
        else:
            speech.append(silence(0.6) if len(seg) > 1.2 * SR else seg)
        out.append(seg)
        t += len(seg) / SR

    def say(v, s, where):
        key = (v, s)
        if key not in cache:
            cache[key] = piece(got[key], TEMPO[lang(v)])
        add(cache[key], {'voice': v, 'text': s, 'where': where, 'lang': lang(v)})

    def dialogue(k, play):
        prev = None
        for who, line in texts[k]:
            if prev is not None:
                add(silence(TURN_GAP if who != prev else SENT_GAP))
            for j, s in enumerate(sentences(line)):
                if j:
                    add(silence(SENT_GAP))
                say(VOICES[k][who], s, f'Texto {k} 第{play}遍')
            prev = who

    if only:
        add(silence(0.8))
        dialogue(only, 1)
        add(silence(1.5))
    else:
        plays = {}
        for kind, x in script(texts):
            if kind == 'silence':
                add(silence(x))
            elif kind == 'zh':
                for p, pause in zh_pieces(x):
                    say(ZH, p, '指令语')
                    if pause:
                        add(silence(pause))
            elif kind == 'es':
                for j, s in enumerate(sentences(x[1])):
                    if j:
                        add(silence(SENT_GAP))
                    say(x[0], s, '试音')
            elif kind == 'dialogue':
                plays[x] = plays.get(x, 0) + 1
                st = t
                dialogue(x, plays[x])
                marks.append({'texto': x, 'play': plays[x], 'start': round(st, 2), 'end': round(t, 2)})
    a48 = G.master(np.concatenate(out), -16.0)
    return a48, items, np.concatenate(speech), marks


def verify(mp3, items, speech48):
    import loudness
    lrep, errs = MA.verify(mp3, items, -16.0)
    errs = [e for e in errs if '句间' not in e and '短时' not in e]
    sp_mp3 = G.encode_mp3(speech48, kbps=128)
    srep, serrs = loudness.verify(sp_mp3, [{'start': 0.0, 'end': len(speech48) / G.OUT_SR - 0.05}], -16.0)
    lrep['short_term_std_speech_lu'] = srep['short_term_std_lu']
    errs += [e.replace('朗读范围内', '去掉作答停顿后的朗读部分') for e in serrs if '短时' in e]
    return lrep, errs


def fallbacks(errs, lrep):
    lev = [{}]
    if any('短时' in e for e in errs):
        lev = [{'leveler_win': 0.75, 'leveler_rng': 6.0}, {'leveler_win': 0.75, 'leveler_rng': 8.0}, {'leveler_win': 0.5, 'leveler_rng': 8.0}]
    extra = {}
    if any('整体响度' in e for e in errs):
        extra['relevel'] = True
    if any(re.search(r'电磁音：\d+ Hz', e) for e in errs):
        extra['post_notch'] = [round(float(lrep['buzz_hz']))]
    return [dict(x, **extra) for x in lev if x or extra]


def render(texts, got, only=None):
    """排出来、编码、核查；不过就按 B1—B2 听力练习的办法补救。返回 (mp3, 时间表, 段落表, 响度报告, 问题, 补救参数)。"""
    a48, items, sp48, marks = assemble(texts, got, only)
    mp3 = G.encode_mp3(a48, kbps=128)
    lrep, errs = verify(mp3, items, sp48)
    fix = None
    if errs:
        for fix in fallbacks(errs, lrep):
            MA.chain(dict(MALE, **{k: v for k, v in fix.items() if k not in ('post_notch', 'relevel', 'gain_db')}))
            base48, items, sp48, marks = assemble(texts, got, only)
            for _ in range(8):
                a48 = MA.buzz.debuzz(base48, G.OUT_SR, fix['post_notch']) if fix.get('post_notch') else base48
                if fix.get('gain_db'):
                    a48 = G.limit((a48 * 10 ** (fix['gain_db'] / 20)).astype(np.float32), G.OUT_SR, -1.5)
                mp3 = G.encode_mp3(a48, kbps=128)
                lrep, errs = verify(mp3, items, sp48)
                print(f"  补救 {fix}：{'；'.join(errs) if errs else '通过'}", flush=True)
                m = re.search(r'电磁音：(\d+) Hz', '；'.join(errs))
                if m and len(fix.get('post_notch', [])) < 8:
                    fix = dict(fix, post_notch=fix.get('post_notch', []) + [int(m.group(1))])
                elif any('整体响度' in e for e in errs) and fix.get('relevel'):
                    fix = dict(fix, gain_db=round(fix.get('gain_db', 0.0) - 16.0 - lrep['integrated_lufs'], 2))
                else:
                    break
            if not errs:
                break
        MA.chain(MALE)
    return mp3, items, marks, lrep, errs, (fix if fix and not errs else None), len(a48) / G.OUT_SR


def build():
    OUT.mkdir(parents=True, exist_ok=True)
    texts = parse_texts(PAPER.read_text('utf-8'))
    rec = Recognizers()
    req = units(texts)
    print(f'{len(req)} 个合成片段（中文 {sum(1 for v, _ in req if v == ZH)}，西语 {sum(1 for v, _ in req if v != ZH)}）', flush=True)
    got = synth(req, rec)
    pieces = sorted((r for *_, r in got.values()), key=lambda r: (r['voice'], r['text']))
    bad = [p for p in pieces if p['errors']]
    (OUT / '听力_识别核对.json').write_text(json.dumps({'pieces': pieces}, ensure_ascii=False, indent=1), 'utf-8')
    for p in bad:
        print(f"✗ 识别有出入：{p['voice']} {p['text']} → {p['asr']} {p['diff']}", flush=True)
    report = {'tempo': TEMPO, 'voices': VOICES, 'tracks': []}
    for only in [None] + list(range(1, 10)):
        mp3, items, marks, lrep, errs, fix, dur = render(texts, got, only)
        name = '听力_完整.mp3' if only is None else f'Texto_{only}.mp3'
        ok = not errs and not bad
        if ok or '--draft' in sys.argv:
            (OUT / name).write_bytes(mp3)
        report['tracks'].append({'file': name, 'duration': round(dur, 1), 'loudness': lrep, 'check_errors': errs, 'fallback': fix})
        if only is None:
            (OUT / '听力_时间轴.json').write_text(json.dumps({'total_s': round(dur, 2), 'texts': marks, 'items': items},
                                                        ensure_ascii=False, indent=1), 'utf-8')
        print(f"{'✓' if ok else '✗'} {name} {dur / 60:.1f} 分钟；{lrep['integrated_lufs']} LUFS，峰值 {lrep['peak_dbfs']} dBFS，"
              f"朗读部分短时波动 {lrep['short_term_std_speech_lu']} LU，电磁音 {lrep['buzz_hz']:.0f} Hz {lrep['buzz_db']:+.1f} dB"
              + (f"；核查：{'；'.join(errs)}" if errs else '') + (f'；补救 {fix}' if fix else ''), flush=True)
    (OUT / '听力_录音核查.json').write_text(json.dumps(report, ensure_ascii=False, indent=1), 'utf-8')
    print('识别核对：' + (f'{len(pieces)} 个片段全部一致' if not bad else f'{len(bad)} 个片段有出入'))


def final():
    """成品逐句复核：按时间轴在 听力_完整.mp3 里切出每一句（两遍都切），再识别一遍；切点敏感时换几种切法。"""
    import soundfile as sf
    tl = json.loads((OUT / '听力_时间轴.json').read_text('utf-8'))
    a, sr = sf.read(str(OUT / '听力_完整.mp3'), dtype='float32')
    a = a if a.ndim == 1 else a.mean(1)
    if abs(len(a) / sr - tl['total_s']) > 0.3:
        raise SystemExit(f"成品 {len(a) / sr:.1f} 秒，时间轴 {tl['total_s']} 秒，对不上")
    rec = Recognizers()
    rows, bad, retried = [], 0, []
    for it in tl['items']:
        tries = []
        for lo, hi, normgain in ((0.05, 0.12, False), (0.15, 0.25, False), (0.02, 0.05, False), (0.05, 0.12, True), (0.25, 0.4, True)):
            seg = a[max(0, int((it['start'] - lo) * sr)):int((it['end'] + hi) * sr)].copy()
            if normgain:
                seg *= 0.5 / (np.abs(seg).max() + 1e-9)
            hyp = rec(it['lang'], seg, sr)
            e, ops = compare(it['voice'], it['text'], hyp)
            tries.append((e, hyp, ops))
            if not e:
                break
        ok = not tries[-1][0]
        bad += not ok
        if ok and len(tries) > 1:
            retried.append(f"{it['where']} {it['text']}（第 {len(tries)} 种切法对上；第一种认成“{tries[0][1]}”）")
        rows.append({'where': it['where'], 'voice': it['voice'], 'text': it['text'], 'start': it['start'], 'ok': ok,
                     'asr': tries[-1][1], 'tries': len(tries), 'diff': tries[-1][2]})
        if not ok:
            print(f"✗ {it['where']} {it['text']} → {' / '.join(h for _, h, _ in tries)}", flush=True)
    (OUT / '听力_成品复核.json').write_text(json.dumps({'sentences': len(rows), 'mismatch': bad, 'rows': rows},
                                                   ensure_ascii=False, indent=1), 'utf-8')
    for x in retried:
        print('  换切法后对上：', x)
    print(f'成品逐句复核：{len(rows)} 句，' + ('全部对上' if not bad else f'{bad} 句有出入'))
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    {'build': build, 'final': final}[MODE]()
