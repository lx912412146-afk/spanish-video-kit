"""《西班牙语 B1 教程》录音：按 audio/uNN.md 录音稿合成每段录音，并按学生用书生词总表生成生词跟读录音。

    python make_tracks.py <工具包目录> <教材目录> <输出目录> <识别模型目录> 单元… [--draft]

- 声音五个（都是 Qwen3-TTS 1.7B 克隆，参考录音见 voices/）：男1 = 工具包推荐男声 qwen3_M1F5_25；
  女1 = 模拟卷听力用的 Supertonic 3 F1 克隆（试卷/第一册高考模拟卷/听力/ref_female_F1.wav）；
  男2 = Supertonic 3 M5 克隆（约 95 Hz，比男1 低）；女2 = F2 克隆（约 225 Hz，比女1 高）；女3 = F5 克隆（约 170 Hz）；
  女4 = F3 克隆（B1 新加，Irene，合成后约 173 Hz，读 seseo）。
  2026-10-21 用 audition.py 试听：三句测试句识别全对（F2 有一词小出入），音高彼此相差 15–40 Hz。
- 语速：对话、课文、听力 1.0 倍（正常语速）；跟读、发音、生词 0.92 倍（A1 是 0.92、0.85，A2 是 0.95、0.88）。电磁音核查不过时在附近换语速。
- 停顿：同一人连续两句 0.35 秒，换人 0.6 秒；跟读每行后留“这行时长 ×1.3＋0.5 秒”（至少 1.6 秒）；
  发音词表每个词之间 0.8 秒，每行后同跟读；片头 1 秒，片尾 1.5 秒。
- 核对：每段（一句）用 Parakeet 识别，和原文逐词比（去重音、标点，数字转西语单词）；三个词以上的句子有出入就换种子
  （2000…10000）重合成，挑最准的一版；仍有出入的不输出（--draft 除外）。一两个词的短片段识别不可靠，只记录、不卡；
  但单音节要量元音长度、辨认元音（vowelid.py），太短、识别不出来或元音不对也换种子重合成，仍不行的不输出；
  第 8 单元区分 [θ] 和 s 的跟读（8-5），词首 z、ce、ci 的摩擦音要够弱（齿间音），不然也换种子。
- 成品：G.master 到 −16 LUFS，MP3 128k（个别电磁音不过的，母带处理后在那几个频点陷波）；用工具包的 verify 核查响度和电磁音。
输出：<输出目录>/B1_<录音号>.mp3、B1_<单元>-V.mp3（生词跟读），<输出目录>/核对/u<单元>.json。
"""
import argparse
import difflib
import io
import json
import re
import sys
import unicodedata
from pathlib import Path

import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument('kit')
ap.add_argument('book')
ap.add_argument('out')
ap.add_argument('asr')
ap.add_argument('units', nargs='+')
ap.add_argument('--draft', action='store_true')
A = ap.parse_args()
KIT, BOOK, OUT, ASR = (Path(p).resolve() for p in (A.kit, A.book, A.out, A.asr))
sys.path.insert(0, str(KIT / '西班牙语' / 'tools'))
import c4  # noqa: E402

MA = c4.load('es_make_audio', '西班牙语/tools/make_audio.py')
MA.CACHE = BOOK / 'audio_build' / '_合成缓存'
G = MA.G
SR = G.SR
SEEDS = (2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000)
SENT_GAP, TURN_GAP, WORD_GAP, LEAD, TAIL = 0.35, 0.6, 0.8, 1.0, 1.5
SPOKEN_TEMPO = (1.0, 0.99, 1.01, 0.98, 1.02)
DRILL_TEMPO = (0.92, 0.91, 0.93, 0.90, 0.94)

MALE = dict(MA.VOICES['qwen3_M1F5_25'])
MA.chain(MALE)
REFS = {'女1': KIT / '试卷' / '第一册高考模拟卷' / '听力' / 'ref_female_F1.wav',
        '男2': BOOK / 'voices' / 'ref_M5.wav', '女2': BOOK / 'voices' / 'ref_F2.wav', '女3': BOOK / 'voices' / 'ref_F5.wav',
        '女4': BOOK / 'voices' / 'ref_F3.wav'}   # B1 新加：Irene，Supertonic 3 F3 克隆（tools/make_ref_voice.py 做的，约 173 Hz；voice4_test.py 比过 F4，F4 和女2 太像）


def voice_cfg(v, seed=None):
    cfg = dict(MALE) if v == '男1' else dict(MALE, ref_audio=str(REFS[v]), label=f'Qwen3-TTS 克隆（西班牙语教程 {v}）')
    if seed is not None:
        cfg['seed'] = seed
    return cfg


# ---------------------------------------------------------------- 录音稿
def parse_audio(path):
    tracks, cur = [], None
    for raw in path.read_text('utf-8').split('\n'):
        t = raw.strip()
        m = re.match(r'^### (\S+)　(.+)$', t)
        if m:
            cur = {'id': m.group(1), 'title': m.group(2), 'type': '', 'roles': {}, 'lines': []}
            tracks.append(cur)
        elif cur and t.startswith('- 类型：'):
            cur['type'] = t[5:].strip()
        elif cur and t.startswith('- 角色：'):
            for part in re.split(r'[；;]', t[5:]):
                if '＝' in part:
                    n, v = (x.strip() for x in part.split('＝', 1))
                    cur['roles'][n] = v
        elif cur and (m := re.match(r'^> ([^:：｜]+): (.+?)｜(.*)$', t)):
            cur['lines'].append((cur['roles'][m.group(1).strip()], m.group(2).strip()))
    return tracks


def sentences(s):
    return [p for p in re.split(r'(?<=[.!?…])\s+', s.strip()) if p]


def expand_vocab(w):
    """生词表的写法转成要读的话：alumno, -a → alumno, alumna；español, -a → español, española；inglés, -a → inglés, inglesa。"""
    w = re.sub(r'\*\*', '', w).strip()
    m = re.match(r'^(.+?), -(a|as|es)$', w)
    if not m:
        return w
    base, suf = m.group(1), m.group(2)
    if base.endswith('o'):
        fem = base[:-1] + suf
    elif re.search(r'[áéíóú][ns]$', base):                 # 末音节带重音的（inglés、alemán）加 -a 后重音规则变了，去掉重音符号
        fem = base[:-2] + unicodedata.normalize('NFC', unicodedata.normalize('NFD', base[-2]).replace('\u0301', '')) + base[-1] + suf
    else:
        fem = base + suf
    return f'{base}, {fem}'


def vocab_words(u):
    f = BOOK / 'student' / f'u{u}.md'
    words, inside = [], False
    for raw in f.read_text('utf-8').split('\n'):
        t = raw.strip()
        if t.replace(' ', '') == '|西语|词性|中文|':
            inside = True
            continue
        if inside and t.startswith('|'):
            if re.match(r'^\|[\s:|-]+\|$', t):
                continue
            w = expand_vocab(t.strip('|').split('|')[0])
            if w and w not in words:
                words.append(w)
        else:
            inside = False
    return words


# ---------------------------------------------------------------- 识别核对
NUMW = None
APOCOPE = {'veintiun': 'veintiuno', 'un': 'uno', 'una': 'uno'}


def norm(t, digitwise=False):
    """小写、去重音、数字换成西语读法。识别结果里的 800.000 是八十万（点是千位分隔）；
    digitwise：四位以上的数字和用连字符、空格连着的几组数字一个一个读（电话号码 6754-3321 = seis siete cinco cuatro…）。"""
    global NUMW
    if NUMW is None:
        from num2words import num2words
        NUMW = num2words
    t = re.sub(r'(?<![\d.])\d{1,3}(?:\.\d{3})+(?![\d.])', lambda m: m.group().replace('.', ''), t.lower())
    if digitwise:
        t = re.sub(r'\d+(?:[- ]\d+)+|\d{4,}', lambda m: ' '.join(NUMW(int(d), lang='es') for d in re.findall(r'\d', m.group())), t)
    t = re.sub(r'\d+', lambda m: ' ' + NUMW(int(m.group()), lang='es') + ' ', t)
    t = ''.join(c for c in unicodedata.normalize('NFD', t) if unicodedata.category(c) != 'Mn')
    return [APOCOPE.get(w, w) for w in re.sub(r"[^a-zñ ]", ' ', t.replace("'", '')).split()]


# 识别模型认不准、但不算读错的词：字母名称（拼读名字时用）和句中的专有名词（人名、地名，尤其是拼音人名）
LETTERS = {'a', 'be', 'ce', 'de', 'e', 'efe', 'ge', 'hache', 'i', 'jota', 'ka', 'ele', 'eme', 'ene', 'ene', 'o', 'pe', 'cu',
           'erre', 'ese', 'te', 'u', 'uve', 'doble', 'equis', 'ye', 'zeta', 'tilde', 'griega', 'latina',
           'punto', 'arroba', 'guion', 'barra', 'edu', 'com', 'cn'}   # 念邮箱、网址时的说法，识别结果常写成符号


FOREIGN = {'jiaozi', 'jianbing', 'baozi', 'xian'}   # 汉语词（饺子、煎饼、包子）和句首的 Xi'an：识别模型只会按西语猜拼法
# 整句识别有出入、但把这句切成片段单独识别核对过读音是对的（2026-10-24）：用核对过的那一版（种子，None 是不加种子的第一版），出入不计，核对记录里注明
VERIFIED = {}   # A2 的两句见 A2教程/tools/make_tracks.py；B1 的在这里加：(声音, 句子): 种子


def lenient_tokens(s):
    words = re.findall(r"[\wÁÉÍÓÚÑáéíóúñü']+", s)
    names = set()
    for k, w in enumerate(words):
        if w[:1].isupper() and k > 0 and not re.search(r'[.!?¿¡]\s*$', s[:s.find(w)]):
            names.update(norm(w))
    if 'arroba' in s:          # 念邮箱：逗号隔开的一个个部分（拼音名字 zhang、wei 等）和“es”后面紧跟的第一部分，识别结果常写成别的拼法
        parts = s.split(',')
        for k, part in enumerate(parts):
            ws = re.findall(r"[\wÁÉÍÓÚÑáéíóúñü']+", part)
            if len(ws) == 1 or (k == 0 and ws):
                names.update(norm(ws[-1]))
    if sum(norm(x) and norm(x)[0] in LETTERS and len(norm(x)) == 1 for x in s.split(',')) >= 3:   # 拼读（Sanz: ese, a, ene, zeta.）：识别结果写成单个字母
        names.update(norm(s))
    return names | LETTERS | FOREIGN


def sounds_same(x, y):
    """读音相同、只是写法或词界不同：连写分写（a mí sí → missy）、双写字母、词尾 y 和 i、不发音的 h、b 和 v，
    以及 seseo（z、ce、ci 读 s：ceno → seno）。女1、女3、男1 的声音读 seseo（见 theta_test.py），识别模型遇到同音词会写成 s。"""
    def key(t):
        t = re.sub(r'c(?=[ei])', 's', t.replace(' ', '')).replace('z', 's')
        t = re.sub(r'(?<!c)h', '', t).replace('v', 'b')            # h 不发音；b 和 v 同音（haba → aba / ava）
        t = re.sub(r'n(?=[pb])', 'm', t)                            # p、b 前的 n 读 m（con parada → comparada）
        return re.sub(r'(.)\1', r'\1', t).replace('y', 'i')
    return key(x) == key(y)


def compare(s, hyp):
    # 识别结果里的数字有两种读法（整数、逐位的号码），取对得上的那一种
    a, b = compare1(s, hyp), compare1(s, hyp, True)
    return b if b[0] < a[0] else a


def compare1(s, hyp, digitwise=False):
    r, h = norm(s), norm(hyp, digitwise)
    soft = lenient_tokens(s)
    err, ops = 0, []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(a=r, b=h, autojunk=False).get_opcodes():
        if op == 'equal':
            continue
        x, y = ' '.join(r[i1:i2]), ' '.join(h[j1:j2])
        if sounds_same(x, y):
            continue
        counts = not (r[i1:i2] and set(r[i1:i2]) <= soft)
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


# ---------------------------------------------------------------- 合成
SYLL_MIN_VOWEL = 0.14   # 秒（变速前）：单音节的元音短于这个、识别结果是空的、或者元音辨认不对（女声开音节，见 vowelid.py），都要重合成


def vowel_sec(a, sr):
    import vowelid
    return vowelid.vowel_sec(a, sr)


DRILL = set()   # 跟读类录音（发音、跟读、生词）里的片段；对话里的“Sí.”本来就短，不量
THETA_TRACKS = set()   # B1 没有区分 [θ] 和 s 的跟读（A1 是 8-5）。区分 [θ] 和 s 的语音跟读：词首 z、ce、ci 要读成齿间音（词首摩擦音弱，见 vowelid.fricative_db）
THETA_MAX_DB = -21.0     # 女2 的 [s] 最强到 −19 dB，[θ] 一般 −23 到 −34 dB
# 送进合成的写法（印出来的还是原文）：女2 单读 zu、ci 时常读成 [s]，写成 ¡Zú!、¡Ci! 才读出齿间音、元音也够长（variant_test.py 试过）
RESPELL = {('女2', 'zu'): '¡Zú!', ('女2', 'ci'): '¡Ci!'}
THETA = set()


def syllable(s):
    w = norm(s)
    return s in DRILL and len(w) == 1 and len(w[0]) <= 3


def weak(r):
    if r.get('theta_ok') is False:
        return True
    return r.get('vowel') is not None and (r['vowel'] < SYLL_MIN_VOWEL or not r['asr'].strip(' .') or r.get('vowel_ok') is False)


def record(v, s, a, sr, hyp, seed):
    import vowelid
    e, ops = compare(s, hyp)
    r = {'voice': v, 'text': s, 'asr': hyp, 'errors': e, 'diff': ops, 'seed': seed, 'vowel': None}
    fd = vowelid.fricative_db(a, sr) if s in THETA else None
    if fd is not None:
        r['fric_db'] = round(fd, 1)
        if vowelid.theta_initial(s):
            r['theta_ok'] = fd < THETA_MAX_DB
    if syllable(s):
        r['vowel'] = vowel_sec(a, sr)
        vid = vowelid.check(s, a, sr) if v.startswith('女') else None
        if vid:
            r.update(vowel_ok=vid[0], formants=[round(vid[1][0]), round(vid[1][1])], heard_vowel=vid[2])
    return r


def better(new, old):
    if old.get('vowel') is not None or old.get('theta_ok') is not None:   # 齿间音不对的最差，其次元音不对、识别不出来，再比元音长度
        rank = lambda r: (r.get('theta_ok') is not False, r.get('vowel_ok') is not False, bool(r['asr'].strip(' .')), r['vowel'] or 0)
        return weak(old) and rank(new) > rank(old)
    return new['errors'] < old['errors']


def synth(requests, rec, log):
    """requests: {(声音, 文字)}；返回 {(声音, 文字): (原始音频, sr, 核对记录)}。
    三个词以上有出入、单音节吞音（见 weak），就换种子重合成，挑最好的一版。"""
    by_voice = {}
    for v, s in requests:
        by_voice.setdefault(v, []).append(s)
    got = {}
    for v, texts in by_voice.items():
        for s, (a, sr) in zip(texts, MA.Worker(voice_cfg(v)).synth_all([RESPELL.get((v, t), t) for t in texts])):
            got[(v, s)] = (a, sr, record(v, s, a, sr, rec(a, sr), None))
    for (v, s), seed in VERIFIED.items():
        if (v, s) in got:
            if seed is not None:
                (a, sr), = MA.Worker(voice_cfg(v, seed)).synth_all([s])
                got[(v, s)] = (a, sr, record(v, s, a, sr, rec(a, sr), seed))
            got[(v, s)][2].update(errors=0, verified='整句识别有出入，切成片段单独识别核对过，读音正确')
    for seed in SEEDS:
        bad = {}
        for (v, s), (_, _, r) in got.items():
            if (r['errors'] and len(norm(s)) >= 3) or weak(r):
                bad.setdefault(v, []).append(s)
        if not bad:
            break
        for v, texts in bad.items():
            for s, (a, sr) in zip(texts, MA.Worker(voice_cfg(v, seed)).synth_all([RESPELL.get((v, t), t) for t in texts])):
                r = record(v, s, a, sr, rec(a, sr), seed)
                log(f"  种子 {seed} {v}：{s} → {r['asr']}（{r['errors']}" + (f"，元音 {r['vowel']} 秒" if r['vowel'] is not None else '')
                    + (f"，听着像 {r['heard_vowel']}" if r.get('vowel_ok') is False else '')
                    + (f"，词首摩擦音 {r['fric_db']} dB" if r.get('fric_db') is not None else '') + '）')
                if better(r, got[(v, s)][2]):
                    got[(v, s)] = (a, sr, r)
    return got


def silence(sec):
    return np.zeros(int(round(sec * SR)), np.float32)


def piece(raw, tempo):
    a, sr = raw[0], raw[1]
    return G.fade(G.level(G.trim(MA.to_sr(MA.tempo_pitch(a, sr, tempo, 0), sr))))


def assemble(track, got, tempo):
    """返回 (48 kHz 成品, items)。"""
    out, items, t = [silence(LEAD)], [], LEAD
    prev = None
    kind = track['type']
    for li, (v, line) in enumerate(track['lines']):
        if kind == '发音':
            units = [w.strip() for w in re.split(r',\s*', line) if w.strip()]
        else:
            units = sentences(line)
        st, parts = t, []
        if li and kind in ('对话', '课文', '听力'):
            g = TURN_GAP if v != prev else SENT_GAP
            out.append(silence(g))
            t += g
        for j, s in enumerate(units):
            if j:
                g = WORD_GAP if kind == '发音' else SENT_GAP
                out.append(silence(g))
                t += g
            seg = piece(got[(v, s)], tempo)
            parts.append([round(t, 3), round(t + len(seg) / SR, 3)])
            out.append(seg)
            t += len(seg) / SR
        items.append({'k': li + 1, 'start': round(st, 3), 'end': round(t, 3), 'parts': parts, 'text': line})
        if kind in ('跟读', '发音', '生词'):
            g = max(1.6, (t - st) * 1.3 + 0.5)
            out.append(silence(g))
            t += g
        prev = v
    out.append(silence(TAIL))
    return G.master(np.concatenate(out), -16.0), items


def fallbacks(errs, lrep):
    """换语速仍不过时依次试的处理（都是工具包里已有的做法）：短时响度波动按 qwen3_M1F5_25_slow 的 leveler_ladder 加强慢速电平；
    单个频点的电磁音按 Kokoro 的 debuzz 在这个频点做 60 Hz 带宽的陷波（放在母带处理之后，见下）；
    整体响度不到目标（短音节、长停顿的跟读，限幅后会偏低），差多少补多少增益，再用工具包的限幅（同 G.master 的做法）。"""
    lev = [{}]
    if any('短时' in e for e in errs):
        lev = [{'leveler_win': 0.75, 'leveler_rng': 6.0}, {'leveler_win': 0.75, 'leveler_rng': 8.0}, {'leveler_win': 0.5, 'leveler_rng': 8.0}]
    extra = {}
    if any('整体响度' in e for e in errs):
        extra['relevel'] = True
    if any(re.search(r'电磁音：\d+ Hz', e) for e in errs):
        # 12、13.5、15 kHz 这类细线是 500 Hz 的整数倍：工具包的压缩（2 ms 一块）和限幅（1 ms 一块）按块改增益带出来的，
        # 在压缩之前陷波没用，所以在母带处理之后陷波
        extra['post_notch'] = [round(float(lrep['buzz_hz']))]
    return [dict(x, **extra) for x in lev if x or extra]


def units_of(track):
    if track['type'] == '发音':
        return [(v, w.strip()) for v, line in track['lines'] for w in re.split(r',\s*', line) if w.strip()]
    return [(v, s) for v, line in track['lines'] for s in sentences(line)]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / '核对').mkdir(exist_ok=True)
    rec = Recognizer()
    fails = []
    for u in A.units:
        u = u if u[0] in 'RT' else f'{int(u):02d}'
        tracks = parse_audio(BOOK / 'audio' / f'u{u}.md')
        words = vocab_words(u) if u[0] not in 'T' else []      # 复习单元没有生词表，就没有生词跟读
        if words:
            tid = u if u[0] == 'R' else str(int(u))
            tracks.append({'id': f'{tid}-V', 'title': '生词跟读', 'type': '生词',
                           'lines': [('女1', w) for w in words]})
        req = {x for tr in tracks for x in units_of(tr)}
        DRILL.clear()
        DRILL.update(s for tr in tracks if tr['type'] in ('发音', '跟读', '生词') for _, s in units_of(tr))
        THETA.clear()
        THETA.update(s for tr in tracks if tr['id'] in THETA_TRACKS for _, s in units_of(tr))
        print(f'=== 单元 {u}：{len(tracks)} 段录音，{len(req)} 个合成片段', flush=True)
        got = synth(req, rec, lambda m: print(m, flush=True))
        report = {'unit': u, 'tracks': []}
        for tr in tracks:
            ladder = SPOKEN_TEMPO if tr['type'] in ('对话', '课文', '听力') else DRILL_TEMPO
            for tempo in ladder:
                a48, items = assemble(tr, got, tempo)
                mp3 = G.encode_mp3(a48, kbps=128)
                lrep, errs = MA.verify(mp3, items, -16.0)
                errs = [e for e in errs if '句间' not in e]       # 跟读、词表里一两个词的短片段电平起伏大，句间偏差不作要求
                if tr['type'] in ('跟读', '发音', '生词'):           # 跟读类大半是留给学生的停顿，3 秒窗的短时响度必然起伏，这一项不适用
                    errs = [e for e in errs if '短时' not in e]
                if not errs:
                    break
            fix = None
            if errs:      # 换语速仍不过：按工具包的做法补救，用第一种全部通过的
                tempo = ladder[0]
                for fix in fallbacks(errs, lrep):
                    MA.chain(dict(MALE, **{k: v for k, v in fix.items() if k not in ('post_notch', 'relevel')}))
                    base, items = assemble(tr, got, tempo)
                    for _ in range(8):         # 陷波后别的频点（多是 500 Hz 的整数倍）冒出来就把它也加上，最多八个频点；整体响度差多少补多少
                        a48 = MA.buzz.debuzz(base, G.OUT_SR, fix['post_notch']) if fix.get('post_notch') else base
                        if fix.get('gain_db'):
                            a48 = G.limit((a48 * 10 ** (fix['gain_db'] / 20)).astype(np.float32), G.OUT_SR, -1.5)
                        mp3 = G.encode_mp3(a48, kbps=128)
                        lrep, errs = MA.verify(mp3, items, -16.0)
                        errs = [e for e in errs if '句间' not in e]
                        if tr['type'] in ('跟读', '发音', '生词'):
                            errs = [e for e in errs if '短时' not in e]
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
            pieces = [got[x][2] for x in units_of(tr)]
            strict = [p for p in pieces if p['errors'] and len(norm(p['text'])) >= 3]
            loose = [p for p in pieces if p['errors'] and len(norm(p['text'])) < 3]
            clipped = [p for p in pieces if weak(p)]
            ok = not errs and not strict and not clipped
            if ok or A.draft:
                (OUT / f'B1_{tr["id"]}.mp3').write_bytes(mp3)
            dur = len(a48) / G.OUT_SR
            report['tracks'].append({'id': tr['id'], 'type': tr['type'], 'tempo': tempo, 'duration': round(dur, 1),
                                     'loudness': lrep, 'fallback': fix if fix and not errs else None, 'check_errors': errs, 'asr_strict_errors': len(strict),
                                     'asr_short_mismatch': len(loose), 'clipped_syllables': len(clipped), 'pieces': pieces})
            print(f"{'✓' if ok else '✗'} {tr['id']} {tr['type']} {dur:.1f} 秒 语速 {tempo}；"
                  f"{lrep['integrated_lufs']} LUFS，电磁音 {lrep['buzz_hz']:.0f} Hz {lrep['buzz_db']:+.1f} dB"
                  + (f"；核查：{'；'.join(errs)}" if errs else '')
                  + (f"；识别有出入 {len(strict)} 句：" + '；'.join(f"{p['text']}→{p['asr']}" for p in strict) if strict else '')
                  + (f"；单音节吞音或元音不对 {len(clipped)} 个：" + '、'.join(f"{p['text']}（元音 {p['vowel']} 秒" + (f"，听着像 {p['heard_vowel']}" if p.get('vowel_ok') is False else '')
                                                                        + (f"，词首摩擦音 {p['fric_db']} dB，不像齿间音" if p.get('theta_ok') is False else '') + f"，识别“{p['asr']}”）" for p in clipped) if clipped else '')
                  + (f"；短片段出入 {len(loose)} 个（只记录）" if loose else ''), flush=True)
            if not ok:
                fails.append(tr['id'])
        (OUT / '核对' / f'u{u}.json').write_text(json.dumps(report, ensure_ascii=False, indent=1), 'utf-8')
    print('全部通过' if not fails else f'未通过：{"、".join(fails)}')
    sys.exit(1 if fails and not A.draft else 0)


if __name__ == '__main__':
    main()
