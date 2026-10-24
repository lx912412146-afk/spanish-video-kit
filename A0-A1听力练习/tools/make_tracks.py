"""《西班牙语 A0—A1 听力练习》录音：按 sets/NN.md 合成每套每个部分的录音，逐句识别核对，再查响度和电磁音。

    python make_tracks.py <工具包目录> <输出目录> <识别模型目录> 套号… [--draft]

沿用《西班牙语 A2 教程》的 tools/make_tracks.py（合成缓存、换种子重合成、补救办法都一样），不同的是：
- 声音五个：播音员固定是男1（工具包推荐男声 qwen3_M1F5_25）；男2、女1、女2、女3 和 A1、A2 教程相同（参考录音见 voices/）。
- 一个部分一段录音：开头 1 秒；播音员读“Parte uno.”和西语指令（整段录音的部分再读看题时间，留出这么多秒）；
  配对题也先留看选项的时间；每题（例题、第 N 题）先报题号，停 0.8 秒，读一遍，停 2 秒，再读一遍，然后留作答时间（各部分的“停顿”）；
  整段录音的部分读一遍，停 3 秒，再读一遍，留作答时间；最后“Fin de la parte uno.”，片尾 1.5 秒。
  对话里同一人连续两句停 0.35 秒，换人停 0.6 秒。
- 语速：第 1—4 套 0.86 倍，第 5 套 0.88 倍，第 6—10 套 0.9 倍；听写（填写）部分再慢 0.02。电磁音核查不过时在附近换语速。
- 核对：每一句都用 Parakeet 识别，和原文逐词比（去重音、标点，数字转西语单词；识别结果的价格 12,90€ 按“doce euros noventa”比）。
  拼读的字母不放宽：字母名称（ge、jota、uve…）和识别结果里的单个字母（G、J、V…）都换成字母再比，
  连着的字母拼成一个词（H U G O 和 Hugo 一样）；只有字母 i 识别成同音的 Y（像连词 y）不算错。有出入就换种子（2000…10000）重合成，挑最准的一版；仍有出入的不输出（--draft 除外）。
  专有名词（句中大写的人名、地名）的拼法出入只记录、不算错（拼读的字母除外）；整个漏掉的照样算错。
- 成品：G.master 到 −16 LUFS，MP3 128k；用工具包的 verify 核查整体响度、峰值和电磁音。短时响度波动只在去掉作答停顿后的朗读部分上量
  （作答停顿 5—10 秒，按原测法会把停顿前后的起伏算进去）。
输出：<输出目录>/A0A1_<套号>-<部分号>.mp3，<输出目录>/核对/setNN.json。
"""
import argparse
import difflib
import json
import re
import sys
import unicodedata
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import sets as S  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('kit')
ap.add_argument('out')
ap.add_argument('asr')
ap.add_argument('sets', nargs='+')
ap.add_argument('--draft', action='store_true')
A = ap.parse_args()
KIT, OUT, ASR = (Path(p).resolve() for p in (A.kit, A.out, A.asr))
sys.path.insert(0, str(KIT / '西班牙语' / 'tools'))
import c4  # noqa: E402

MA = c4.load('es_make_audio', '西班牙语/tools/make_audio.py')
MA.CACHE = ROOT / 'audio_build' / '_合成缓存'
G = MA.G
SR = G.SR
SEEDS = (2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000)
SENT_GAP, TURN_GAP, LEAD, TAIL = 0.35, 0.6, 1.0, 1.5
LABEL_GAP, REPEAT_GAP, SHARED_REPEAT_GAP, INTRO_GAP = 0.8, 2.0, 3.0, 1.5
BASE_TEMPO = {1: 0.86, 2: 0.86, 3: 0.86, 4: 0.86, 5: 0.88}     # 其余 0.9

MALE = dict(MA.VOICES['qwen3_M1F5_25'])
MA.chain(MALE)
VOICE_DIR = ROOT / 'voices' if (ROOT / 'voices').exists() else KIT / 'A2教程' / 'voices'     # 仓库里用 A2教程/voices/ 的参考录音
REFS = {'女1': KIT / '试卷' / '第一册高考模拟卷' / '听力' / 'ref_female_F1.wav',
        '男2': VOICE_DIR / 'ref_M5.wav', '女2': VOICE_DIR / 'ref_F2.wav', '女3': VOICE_DIR / 'ref_F5.wav'}


def voice_cfg(v, seed=None):
    cfg = dict(MALE) if v == '男1' else dict(MALE, ref_audio=str(REFS[v]), label=f'Qwen3-TTS 克隆（西班牙语教程 {v}，与 A1、A2 相同的声音）')
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
        t = re.sub(r'(\d+),(\d{2})\s*€', r'\1 euros \2', t)
        t = re.sub(r'(\d+)\s*€', r'\1 euros', t)
        t = re.sub(r'(\d+)\s*%', r'\1 por ciento', t)
        t = t.replace('<unk>', ' ')
        t = re.sub(r'\b(\d{1,2}):30\b', r'\1 y media', t)              # 识别结果写成 8:30 的钟点
        t = re.sub(r'\b(\d{1,2}):15\b', r'\1 y cuarto', t)
        t = re.sub(r'\b(\d{1,2}):00\b', r'\1', t)
        t = re.sub(r'\b(\d{1,2}):(\d{2})\b', r'\1 y \2', t)
        t = split_caps(t).replace('-', ' ')
    t = re.sub(r'(?<![\d.])\d{1,3}(?:\.\d{3})+(?![\d.])', lambda m: m.group().replace('.', ''), t.lower())
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
        t = re.sub(r'n(?=[pb])', 'm', t)
        return re.sub(r'(.)\1', r'\1', t).replace('y', 'i')
    return key(x) == key(y)


def compare(s, hyp):
    """数字有两种读法（整数、逐位的号码），字母有两种比法（一个个比、连起来比），取出入最少的。"""
    return min((compare1(s, hyp, d, g) for d in (False, True) for g in (False, True)), key=lambda x: x[0])


def compare1(s, hyp, digitwise=False, glue=False):
    (r, gr), (h, gh) = norm(spoken(s), glue=True) if glue else (norm(spoken(s)), set()), \
        norm(hyp, digitwise, hyp=True, glue=True) if glue else (norm(hyp, digitwise, hyp=True), set())
    soft = lenient_tokens(s)
    err, ops = 0, []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(a=r, b=h, autojunk=False).get_opcodes():
        if op == 'equal':
            continue
        x, y = ' '.join(r[i1:i2]), ' '.join(h[j1:j2])
        # 拼读里的 i 和 y 同音（识别模型常把字母 i 写成 Y，就像连词 y）：只有这一处出入时不算
        if x.replace('L:i', 'L:y').replace('i', 'y') == y.replace('i', 'y') and ('L:i' in x or (glue and x in gr)):
            continue
        strict = any(w.startswith('L:') or w in gr for w in r[i1:i2]) or any(w.startswith('L:') or w in gh for w in h[j1:j2])
        if not strict and sounds_same(x, y):
            continue
        # 连上前面一个相同的词再比：seseo 里 va a hacer 和 va a ser 读音一样（a＋hacer → aser）
        prev = r[i1 - 1] if i1 else ''
        if not strict and op == 'replace' and prev.startswith('L:') and sounds_same(prev[2:] + x, prev[2:] + y):
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


# ---------------------------------------------------------------- 拼成一段
def silence(sec):
    return np.zeros(int(round(sec * SR)), np.float32)


def piece(raw, tempo):
    a, sr = raw[0], raw[1]
    return G.fade(G.level(G.trim(MA.to_sr(MA.tempo_pitch(a, sr, tempo, 0), sr))))


def part_units(p):
    """这一部分要合成的片段：[(声音, 句子)]，按出现顺序（重复的只算一次）。"""
    roles = p['roles']
    units = [(S.NARRATOR, es) for es, _ in S.intro_lines(p)] + [(S.NARRATOR, S.outro_line(p)[0])]
    units += [(S.NARRATOR, S.item_label(it)[0]) for it in p['items']] if not p['audio'] else []
    for ln in p['audio'] + [ln for it in p['items'] for ln in it['audio']]:
        units += [(roles[ln[0]], s) for s in sentences(ln[1])]
    return units


def assemble(p, got, tempo):
    """返回 (48 kHz 成品, 朗读片段时间表, 去掉作答停顿后的朗读部分)。"""
    out, items, t = [], [], 0.0
    speech = []          # 只留朗读、作答停顿缩成 0.6 秒，量短时响度用

    def add(seg, text=None):
        nonlocal t
        if text is not None:
            items.append({'k': len(items) + 1, 'start': round(t, 3), 'end': round(t + len(seg) / SR, 3), 'text': text})
            speech.append(seg)
        elif len(seg) > 1.2 * SR:
            speech.append(silence(0.6))
        else:
            speech.append(seg)
        out.append(seg)
        t += len(seg) / SR

    def say(v, s):
        add(piece(got[(v, s)], tempo), s)

    def lines(ls):
        prev = None
        for who, es, _ in ls:
            v = p['roles'][who]
            if prev is not None:
                add(silence(TURN_GAP if who != prev else SENT_GAP))
            for j, s in enumerate(sentences(es)):
                if j:
                    add(silence(SENT_GAP))
                say(v, s)
            prev = who

    add(silence(LEAD))
    for j, (es, _) in enumerate(S.intro_lines(p)):
        if j:
            add(silence(0.6))
        say(S.NARRATOR, es)
    if p['audio']:
        add(silence(p['read'] or INTRO_GAP))
        lines(p['audio'])
        add(silence(SHARED_REPEAT_GAP))
        lines(p['audio'])
        add(silence(p['pause']))
    else:
        add(silence(p['read'] or INTRO_GAP))
        for it in p['items']:
            say(S.NARRATOR, S.item_label(it)[0])
            add(silence(LABEL_GAP))
            lines(it['audio'])
            add(silence(REPEAT_GAP))
            lines(it['audio'])
            add(silence(p['pause']))
    say(S.NARRATOR, S.outro_line(p)[0])
    add(silence(TAIL))
    return G.master(np.concatenate(out), -16.0), items, np.concatenate(speech)


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


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / '核对').mkdir(exist_ok=True)
    rec = Recognizer()
    fails = []
    for n in A.sets:
        st = S.parse(ROOT / 'sets' / f'{int(n):02d}.md')
        units = [u for p in st['parts'] for u in part_units(p)]
        req = set(units)
        print(f"=== 第 {st['num']} 套：{len(st['parts'])} 段录音，{len(req)} 个合成片段", flush=True)
        got = synth(req, rec, lambda m: print(m, flush=True))
        report = {'set': st['num'], 'tracks': []}
        base = BASE_TEMPO.get(st['num'], 0.90)
        for p in st['parts']:
            b = round(base - (0.02 if p['type'] == '填写' else 0), 2)
            ladder = (b, round(b - 0.01, 2), round(b + 0.01, 2), round(b - 0.02, 2), round(b + 0.02, 2))
            for tempo in ladder:
                a48, items, sp48 = assemble(p, got, tempo)
                mp3 = G.encode_mp3(a48, kbps=128)
                lrep, errs = verify(mp3, items, sp48)
                if not errs:
                    break
            fix = None
            if errs:
                tempo = ladder[0]
                for fix in fallbacks(errs, lrep):
                    MA.chain(dict(MALE, **{k: v for k, v in fix.items() if k not in ('post_notch', 'relevel')}))
                    base48, items, sp48 = assemble(p, got, tempo)
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
            tid = f"{st['num']:02d}-{p['idx']}"
            pieces = [got[u][2] for u in dict.fromkeys(part_units(p))]
            bad = [x for x in pieces if x['errors']]
            ok = not errs and not bad
            if ok or A.draft:
                (OUT / f'A0A1_{tid}.mp3').write_bytes(mp3)
            dur = len(a48) / G.OUT_SR
            report['tracks'].append({'id': tid, 'type': p['type'], 'tempo': tempo, 'duration': round(dur, 1), 'loudness': lrep,
                                     'fallback': fix if fix and not errs else None, 'check_errors': errs, 'asr_errors': len(bad),
                                     'pieces': pieces})
            print(f"{'✓' if ok else '✗'} {tid} {p['type']} {dur:.1f} 秒 语速 {tempo}；"
                  f"{lrep['integrated_lufs']} LUFS，朗读部分短时波动 {lrep['short_term_std_speech_lu']} LU，"
                  f"电磁音 {lrep['buzz_hz']:.0f} Hz {lrep['buzz_db']:+.1f} dB"
                  + (f"；核查：{'；'.join(errs)}" if errs else '')
                  + (f"；识别有出入 {len(bad)} 句：" + '；'.join(f"{x['text']}→{x['asr']} {x['diff']}" for x in bad) if bad else ''), flush=True)
            if not ok:
                fails.append(tid)
        (OUT / '核对' / f"set{st['num']:02d}.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), 'utf-8')
    print('全部通过' if not fails else f'未通过：{"、".join(fails)}')
    sys.exit(1 if fails and not A.draft else 0)


if __name__ == '__main__':
    main()
