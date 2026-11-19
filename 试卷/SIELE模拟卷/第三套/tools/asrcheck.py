"""SIELE 模拟卷录音用的合成、逐句识别核对和成品核查。

除开头这几十行外，代码原样摘自《西班牙语 B1—B2 听力练习》的 tools/make_tracks.py
（送进合成的写法、识别核对、换种子重合成、拼接、成品核查、补救办法），所以核对标准和那套听力完全一样。

环境变量：SIELE_KIT（工具包目录）、SIELE_ASR（Parakeet 识别模型目录）、SIELE_ROOT（本卷工作目录，合成缓存放在 audio_build/_合成缓存）。
声音：播音员男1（工具包推荐男声 qwen3_M1F5_25）；男2、女1、女2、女3、女4 是 Qwen3-TTS 克隆，参考录音同 A2、B1 教程。
"""
import difflib
import os
import re
import sys
import unicodedata
from pathlib import Path

import numpy as np

KIT = Path(os.environ['SIELE_KIT']).resolve()
ASR = Path(os.environ['SIELE_ASR']).resolve()
ROOT = Path(os.environ['SIELE_ROOT']).resolve()
sys.path.insert(0, str(KIT / '西班牙语' / 'tools'))
import c4  # noqa: E402

MA = c4.load('es_make_audio', '西班牙语/tools/make_audio.py')
MA.CACHE = ROOT / 'audio_build' / '_合成缓存'
G = MA.G
SR = G.SR
SEEDS = (2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000)

MALE = dict(MA.VOICES['qwen3_M1F5_25'])
MA.chain(MALE)
VOICE_DIR = KIT / 'A2教程' / 'voices'
B1_VOICES = KIT / 'B1教程' / 'voices'
REFS = {'女1': KIT / '试卷' / '第一册高考模拟卷' / '听力' / 'ref_female_F1.wav',
        '男2': VOICE_DIR / 'ref_M5.wav', '女2': VOICE_DIR / 'ref_F2.wav', '女3': VOICE_DIR / 'ref_F5.wav', '女4': B1_VOICES / 'ref_F3.wav'}


def voice_cfg(v, seed=None):
    cfg = dict(MALE) if v == '男1' else dict(MALE, ref_audio=str(REFS[v]), label=f'Qwen3-TTS 克隆（西班牙语教程 {v}，与 A1、A2、B1 教程相同的声音）')
    if seed is not None:
        cfg['seed'] = seed
    return cfg


# ---------------------------------------------------------------- 送进合成的写法（印出来的还是原文）
LETTER_NAME = {'B': 'be', 'C': 'ce', 'D': 'de', 'F': 'efe', 'G': 'ge', 'H': 'hache', 'J': 'jota', 'K': 'ka', 'L': 'ele', 'M': 'eme',
               'N': 'ene', 'P': 'pe', 'Q': 'cu', 'R': 'erre', 'S': 'ese', 'T': 'te', 'V': 'uve', 'W': 'uve doble', 'X': 'equis', 'Z': 'zeta'}


def spoken(s):
    """“la puerta B”里单独的大写字母读字母名称；书名号不送进合成。"""
    s = s.replace('«', '').replace('»', '')
    return re.sub(r'\b(puerta|letra|vía|aula) ([B-DF-HJ-NP-TV-Z])\b', lambda m: f'{m.group(1)} {LETTER_NAME[m.group(2)]}', s)


def sentences(s):
    return [p for p in re.split(r'(?<=[.!?…])\s+', s.strip()) if p]


# ---------------------------------------------------------------- 识别核对
NUMW = None
APOCOPE = {'veintiun': 'veintiuno', 'un': 'uno', 'una': 'uno'}
# 字母名称 → 字母（两边都换，所以 de、te、a、y 这些普通词换了也一致）
NAME2LETTER = {'a': 'a', 'be': 'b', 'ce': 'c', 'de': 'd', 'e': 'e', 'efe': 'f', 'ge': 'g', 'hache': 'h', 'i': 'i', 'jota': 'j', 'ka': 'k',
               'ele': 'l', 'eme': 'm', 'ene': 'n', 'o': 'o', 'pe': 'p', 'cu': 'q', 'erre': 'r', 'ese': 's', 'te': 't', 'u': 'u', 'uve': 'v',
               'equis': 'x', 'ye': 'y', 'y': 'y', 'zeta': 'z'}
for ch in 'bcdfghjklmnpqrstvwxz':
    NAME2LETTER.setdefault(ch, ch)


def split_caps(t):
    """识别结果拼读时常把两三个字母连成大写块（P-A-U-LA、G-O-ME Z）：旁边是单个字母的大写块拆开；“la letra CE”里的 CE 不拆。"""
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
    """小写、去重音、数字换成西语读法；字母名称和单个字母都换成“字母”记号 L:x。
    glue：两个以上连着的字母拼成一个词（H U G O ＝ hugo；冒号、句号处断开，逗号不断），返回 (词表, 拼出来的词)。
    hyp：识别结果，另外把 12,90€ 换成 12 euros 90，拆开拼读时连在一起的大写字母块。"""
    global NUMW
    if NUMW is None:
        from num2words import num2words
        NUMW = num2words
    if hyp:
        t = re.sub(r'(\d+),(\d{2})\s*(euros?)\b', r'\1 \3 \2', t)              # 识别结果写成 1,20 euro（＝un euro con veinte）
        t = re.sub(r'\b(\d+ euros? con \d+) euros?\b', r'\1', t)               # 写成 1 euro con 20 euro：后面的 euro 是识别补的单位
        t = re.sub(r'(\d+),(\d{2})\s*€', r'\1 euros \2', t)
        t = re.sub(r'(\d+)\s*€', r'\1 euros', t)
        t = re.sub(r'(\d+)\s*%', r'\1 por ciento', t)
        # 识别结果把单位写成符号（30 km/h、5 km、40 kg、100 m、8 °C、$100）：换回录音稿里的读法
        t = re.sub(r'(\d+)\s*km\s*/\s*h\b', r'\1 kilómetros por hora', t, flags=re.I)
        t = re.sub(r'\b1\s*km\b', 'un kilómetro', t, flags=re.I)
        t = re.sub(r'(\d+)\s*km\b', r'\1 kilómetros', t, flags=re.I)
        t = re.sub(r'(\d+)\s*kg\b', r'\1 kilos', t, flags=re.I)
        t = re.sub(r'(\d+)\s*m\b', r'\1 metros', t)
        t = re.sub(r'(\d+)\s*°\s*C?(?![A-Za-z])', r'\1 grados', t)
        t = re.sub(r'\$\s*(\d+)|(\d+)\s*\$', lambda m: f'{m.group(1) or m.group(2)} pesos', t)
        t = t.replace('<unk>', ' ')
        t = re.sub(r'\b(\d{1,2}):30\b', r'\1 y media', t)              # 识别结果写成 8:30 的钟点
        t = re.sub(r'\b(\d{1,2}):15\b', r'\1 y cuarto', t)
        t = re.sub(r'\b(\d{1,2}):00\b', r'\1', t)
        t = re.sub(r'\b(\d{1,2}):(\d{2})\b', r'\1 y \2', t)
        t = split_caps(t).replace('-', ' ')
    t = re.sub(r'(?<![\d.])\d{1,3}(?:\.\d{3})+(?!\d|\.\d)', lambda m: m.group().replace('.', ''), t.lower())
    if digitwise:
        t = re.sub(r'\d+(?:[- ]\d+)+|\d{4,}', lambda m: ' '.join(NUMW(int(d), lang='es') for d in re.findall(r'\d', m.group())), t)
    t = re.sub(r'(\d+):(\d{2})', lambda m: f' {m.group(1)} {m.group(2)} ', t)
    t = re.sub(r'\d+', lambda m: ' ' + NUMW(int(m.group()), lang='es') + ' ', t)
    t = ''.join(c for c in unicodedata.normalize('NFD', t) if unicodedata.category(c) != 'Mn' or c == '\u0303')
    t = unicodedata.normalize('NFC', t)
    t = re.sub(r'[:;.!?¿¡…]', ' | ', t)
    words = [APOCOPE.get(w, w) for w in re.sub(r"[^a-zñ |]", ' ', t.replace("'", '')).split()]
    words = [w for k, w in enumerate(words) if not (w == 'con' and k and words[k - 1] in ('euro', 'euros'))]   # “dos euros con cincuenta”＝“dos euros cincuenta”
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
    """句中大写的专有名词（人名、地名）：识别模型拼不准（Ximena 和 Jimena 读音一样），出入只记录。拼读的字母不在内。"""
    words = re.findall(r"[\wÁÉÍÓÚÑáéíóúñü']+", s)
    names = set()
    for k, w in enumerate(words):
        if w[:1].isupper() and k > 0 and not re.search(r'[.!?¿¡:]\s*$', s[:s.find(w)]):
            names.update(x for x in norm(w) if not x.startswith('L:'))
    return names


def sounds_same(x, y):
    """读音相同、只是写法或词界不同（同 A2 的 make_tracks.py）：连写分写、双写字母、词尾 y 和 i、不发音的 h、b 和 v、seseo。
    拼读的字母（L:x 和连起来的字母词）不用这条放宽。"""
    def key(t):
        t = re.sub(r'c(?=[ei])', 's', t.replace(' ', '')).replace('z', 's')
        t = re.sub(r'(?<!c)h', '', t).replace('v', 'b')
        t = re.sub(r'n(?=[pbm])', 'm', t)
        return re.sub(r'(.)\1', r'\1', t).replace('y', 'i')
    return key(x) == key(y)


# 识别结果常把整百的数写成阿拉伯数字（doscientas cartas → 200 cartas），换回西语读法时只有阳性（doscientos）：
# 只差这一点、识别结果里确实有数字时不计（写成数字就听不出阴阳性），核对记录里注明
CIENTOS = {'doscientos', 'trescientos', 'cuatrocientos', 'quinientos', 'seiscientos', 'setecientos', 'ochocientos', 'novecientos'}


def fem_hundreds(x, y, hyp):
    xs, ys = x.split(), y.split()
    return bool(re.search(r'\d', hyp)) and len(xs) == len(ys) and xs != ys and \
        all(a == b or (b in CIENTOS and a == b[:-2] + 'as') for a, b in zip(xs, ys))


def compare(s, hyp):
    """数字有两种读法（整数、逐位的号码），字母有两种比法（一个个比、连起来比），取出入最少的。"""
    return min((compare1(s, hyp, d, g) for d in (False, True) for g in (False, True)), key=lambda x: x[0])


# 单独出现（前后都不是字母）的 a、e、i、o、u、y、de、te 是普通词（介词、连词、语气词），不是拼读：换回原词，可以按读音放宽
PLAIN = {'L:a': 'a', 'L:e': 'e', 'L:i': 'i', 'L:o': 'o', 'L:u': 'u', 'L:y': 'y', 'L:d': 'de', 'L:t': 'te'}


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
        # 拼读里的 i 和 y 同音（识别模型常把字母 i 写成 Y，就像连词 y）：只有这一处出入时不算
        if x.replace('L:i', 'L:y').replace('i', 'y') == y.replace('i', 'y') and ('L:i' in x or (glue and x in gr)):
            continue
        if op == 'replace' and fem_hundreds(x, y, hyp):
            ops.append([x, y, '不计'])
            continue
        strict = any(w.startswith('L:') or w in gr for w in r[i1:i2]) or any(w.startswith('L:') or w in gh for w in h[j1:j2])
        if not strict and sounds_same(x, y):
            continue
        # 连上前面一个相同的词再比：seseo 里 va a hacer 和 va a ser 读音一样（a＋hacer → aser）
        prev = r[i1 - 1] if i1 else ''
        if not strict and op == 'replace' and prev.startswith('L:') and sounds_same(prev[2:] + x, prev[2:] + y):
            continue
        # 连上前后相同的词再比：词界不同、读音一样（pilates son ＝ Pilate son，normalmente salgo ＝ normalmente es algo，
        # a Cádiz en ＝ acá dicen，busca monitores ＝ buscan monitores）；拼读的字母不放宽
        plain = lambda w: not w.startswith('L:') and w not in gr and w not in gh
        pre = r[i1 - 1] if i1 and j1 and r[i1 - 1] == h[j1 - 1] and plain(r[i1 - 1]) else ''
        nxt = r[i2] if i2 < len(r) and j2 < len(h) and r[i2] == h[j2] and plain(r[i2]) else ''
        if not strict and (pre or nxt) and any(sounds_same(f'{a} {x} {b}', f'{a} {y} {b}') for a, b in ((pre, ''), ('', nxt), (pre, nxt))):
            continue
        # 专有名词只放宽拼法（Li Mei 识别成 Lee May）；整个漏掉（识别结果里没有）照样算错——名字常常就是答案
        counts = strict or not (r[i1:i2] and h[j1:j2] and set(r[i1:i2]) <= soft)
        ops.append([x, y] if counts else [x, y, '不计'])
        err += max(len(x.split()), len(y.split())) if counts else 0
    return err, ops


class Recognizer:
    def __init__(self):
        import sherpa_onnx
        d = ASR if (ASR / 'tokens.txt').exists() else next(p for p in ASR.iterdir() if p.is_dir() and 'parakeet' in p.name)
        self.rec = sherpa_onnx.OfflineRecognizer.from_transducer(
            encoder=str(d / 'encoder.int8.onnx'), decoder=str(d / 'decoder.int8.onnx'), joiner=str(d / 'joiner.int8.onnx'),
            tokens=str(d / 'tokens.txt'), model_type='nemo_transducer', num_threads=4)

    def __call__(self, a, sr):
        import soxr
        st = self.rec.create_stream()
        pad = np.zeros(int(0.3 * sr), np.float32)
        st.accept_waveform(16000, soxr.resample(np.concatenate([pad, a, pad]), sr, 16000).astype(np.float32))
        self.rec.decode_stream(st)
        return st.result.text.strip()


# 整句识别有出入、但切成片段单独识别核对过读音是对的：用核对过的那一版（种子，None 是不加种子的第一版），出入不计，核对记录里注明
VERIFIED = {}


def record(v, s, hyp, seed):
    e, ops = compare(s, hyp)
    return {'voice': v, 'text': s, 'asr': hyp, 'errors': e, 'diff': ops, 'seed': seed}


def synth(requests, rec, log):
    """requests: {(声音, 文字)}；返回 {(声音, 文字): (原始音频, sr, 核对记录)}。有出入就换种子重合成，挑最好的一版。"""
    by_voice = {}
    for v, s in sorted(requests):
        by_voice.setdefault(v, []).append(s)
    got = {}
    for v, texts in by_voice.items():
        for s, (a, sr) in zip(texts, MA.Worker(voice_cfg(v)).synth_all([spoken(t) for t in texts])):
            got[(v, s)] = (a, sr, record(v, s, rec(a, sr), None))
    for (v, s), seed in VERIFIED.items():
        if (v, s) in got:
            if seed is not None:
                (a, sr), = MA.Worker(voice_cfg(v, seed)).synth_all([spoken(s)])
                got[(v, s)] = (a, sr, record(v, s, rec(a, sr), seed))
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
                r = record(v, s, rec(a, sr), seed)
                log(f"  种子 {seed} {v}：{s} → {r['asr']}（{r['errors']}）")
                if r['errors'] < got[(v, s)][2]['errors']:
                    got[(v, s)] = (a, sr, r)
    return got



def silence(sec):
    return np.zeros(int(round(sec * SR)), np.float32)


def piece(raw, tempo):
    a, sr = raw[0], raw[1]
    return G.fade(G.level(G.trim(MA.to_sr(MA.tempo_pitch(a, sr, tempo, 0), sr))))




def verify(mp3, items, speech48):
    """工具包的核查（整体响度、峰值、电磁音）；短时响度波动在朗读部分上另量。"""
    import loudness
    lrep, errs = MA.verify(mp3, items, -16.0)
    errs = [e for e in errs if '句间' not in e and '短时' not in e]     # 句间偏差：一两个词的短片段电平起伏大，同 A2 不作要求
    sp_mp3 = G.encode_mp3(speech48, kbps=128)
    srep, serrs = loudness.verify(sp_mp3, [{'start': 0.0, 'end': len(speech48) / G.OUT_SR - 0.05}], -16.0)
    lrep['short_term_std_speech_lu'] = srep['short_term_std_lu']
    errs += [e.replace('朗读范围内', '去掉作答停顿后的朗读部分') for e in serrs if '短时' in e]
    return lrep, errs


def fallbacks(errs, lrep):
    """同 A2：短时响度波动加强慢速电平；单个频点的电磁音在母带处理之后陷波；整体响度不到目标就补增益再限幅。"""
    lev = [{}]
    if any('短时' in e for e in errs):
        lev = [{'leveler_win': 0.75, 'leveler_rng': 6.0}, {'leveler_win': 0.75, 'leveler_rng': 8.0}, {'leveler_win': 0.5, 'leveler_rng': 8.0}]
    extra = {}
    if any('整体响度' in e for e in errs):
        extra['relevel'] = True
    if any(re.search(r'电磁音：\d+ Hz', e) for e in errs):
        extra['post_notch'] = [round(float(lrep['buzz_hz']))]
    return [dict(x, **extra) for x in lev if x or extra]
