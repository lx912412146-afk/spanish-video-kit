"""《西班牙语 A1 教程》录音：按 audio/uNN.md 录音稿合成每段录音，并按学生用书生词总表生成生词跟读录音。

    python make_tracks.py <工具包目录> <教材目录> <输出目录> <识别模型目录> 单元… [--draft]

- 声音五个（都是 Qwen3-TTS 1.7B 克隆，参考录音见 voices/）：男1 = 工具包推荐男声 qwen3_M1F5_25；
  女1 = 模拟卷听力用的 Supertonic 3 F1 克隆（试卷/第一册高考模拟卷/听力/ref_female_F1.wav）；
  男2 = Supertonic 3 M5 克隆（约 95 Hz，比男1 低）；女2 = F2 克隆（约 225 Hz，比女1 高）；女3 = F5 克隆（约 170 Hz）。
  2026-10-21 用 audition.py 试听：三句测试句识别全对（F2 有一词小出入），音高彼此相差 15–40 Hz。
- 语速：对话、课文、听力 0.92 倍；跟读、发音、生词 0.85 倍（A1 稍慢于正常语速）。电磁音核查不过时在附近换语速。
- 停顿：同一人连续两句 0.35 秒，换人 0.6 秒；跟读每行后留“这行时长 ×1.3＋0.5 秒”（至少 1.6 秒）；
  发音词表每个词之间 0.8 秒，每行后同跟读；片头 1 秒，片尾 1.5 秒。
- 核对：每段（一句）用 Parakeet 识别，和原文逐词比（去重音、标点，数字转西语单词）；三个词以上的句子有出入就换种子
  （2000…6000）重合成，挑最准的一版；仍有出入的不输出（--draft 除外）。一两个词的短片段识别不可靠，只记录、不卡。
- 成品：G.master 到 −16 LUFS，MP3 128k；用工具包的 verify 核查响度和电磁音。
输出：<输出目录>/A1_<录音号>.mp3、A1_<单元>-V.mp3（生词跟读），<输出目录>/核对/u<单元>.json。
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
SEEDS = (2000, 3000, 4000, 5000, 6000)
SENT_GAP, TURN_GAP, WORD_GAP, LEAD, TAIL = 0.35, 0.6, 0.8, 1.0, 1.5
SPOKEN_TEMPO = (0.92, 0.91, 0.93, 0.90, 0.94)
DRILL_TEMPO = (0.85, 0.84, 0.86, 0.83, 0.87)

MALE = dict(MA.VOICES['qwen3_M1F5_25'])
MA.chain(MALE)
REFS = {'女1': KIT / '试卷' / '第一册高考模拟卷' / '听力' / 'ref_female_F1.wav',
        '男2': BOOK / 'voices' / 'ref_M5.wav', '女2': BOOK / 'voices' / 'ref_F2.wav', '女3': BOOK / 'voices' / 'ref_F5.wav'}


def voice_cfg(v, seed=None):
    cfg = dict(MALE) if v == '男1' else dict(MALE, ref_audio=str(REFS[v]), label=f'Qwen3-TTS 克隆（A1 教程 {v}）')
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


def norm(t):
    global NUMW
    if NUMW is None:
        from num2words import num2words
        NUMW = num2words
    t = re.sub(r'\d+', lambda m: ' ' + NUMW(int(m.group()), lang='es') + ' ', t.lower())
    t = ''.join(c for c in unicodedata.normalize('NFD', t) if unicodedata.category(c) != 'Mn')
    return [APOCOPE.get(w, w) for w in re.sub(r"[^a-zñ ]", ' ', t.replace("'", '')).split()]


# 识别模型认不准、但不算读错的词：字母名称（拼读名字时用）和句中的专有名词（人名、地名，尤其是拼音人名）
LETTERS = {'a', 'be', 'ce', 'de', 'e', 'efe', 'ge', 'hache', 'i', 'jota', 'ka', 'ele', 'eme', 'ene', 'ene', 'o', 'pe', 'cu',
           'erre', 'ese', 'te', 'u', 'uve', 'doble', 'equis', 'ye', 'zeta', 'tilde', 'griega', 'latina',
           'punto', 'arroba', 'guion', 'barra', 'edu', 'com', 'cn'}   # 念邮箱、网址时的说法，识别结果常写成符号


def lenient_tokens(s):
    words = re.findall(r"[\wÁÉÍÓÚÑáéíóúñü']+", s)
    names = set()
    for k, w in enumerate(words):
        if w[:1].isupper() and k > 0 and not re.search(r'[.!?¿¡]\s*$', s[:s.find(w)]):
            names.update(norm(w))
    return names | LETTERS


def compare(s, hyp):
    r, h = norm(s), norm(hyp)
    soft = lenient_tokens(s)
    err, ops = 0, []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(a=r, b=h, autojunk=False).get_opcodes():
        if op == 'equal':
            continue
        x, y = ' '.join(r[i1:i2]), ' '.join(h[j1:j2])
        if x.replace(' ', '') == y.replace(' ', ''):
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
def synth(requests, rec, log):
    """requests: {(声音, 文字)}；返回 {(声音, 文字): (原始音频, sr, 核对记录)}。三个词以上有出入就换种子重合成。"""
    by_voice = {}
    for v, s in requests:
        by_voice.setdefault(v, []).append(s)
    got = {}
    for v, texts in by_voice.items():
        for s, (a, sr) in zip(texts, MA.Worker(voice_cfg(v)).synth_all(texts)):
            hyp = rec(a, sr)
            e, ops = compare(s, hyp)
            got[(v, s)] = (a, sr, {'voice': v, 'text': s, 'asr': hyp, 'errors': e, 'diff': ops, 'seed': None})
    for seed in SEEDS:
        bad = {}
        for (v, s), (_, _, r) in got.items():
            if r['errors'] and len(norm(s)) >= 3:
                bad.setdefault(v, []).append(s)
        if not bad:
            break
        for v, texts in bad.items():
            for s, (a, sr) in zip(texts, MA.Worker(voice_cfg(v, seed)).synth_all(texts)):
                hyp = rec(a, sr)
                e, ops = compare(s, hyp)
                log(f'  种子 {seed} {v}：{s} → {hyp}（{e}）')
                if e < got[(v, s)][2]['errors']:
                    got[(v, s)] = (a, sr, {'voice': v, 'text': s, 'asr': hyp, 'errors': e, 'diff': ops, 'seed': seed})
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
        if u[0] not in 'T':
            tid = u if u[0] == 'R' else str(int(u))
            tracks.append({'id': f'{tid}-V', 'title': '生词跟读', 'type': '生词',
                           'lines': [('女1', w) for w in vocab_words(u)]})
        req = {x for tr in tracks for x in units_of(tr)}
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
            pieces = [got[x][2] for x in units_of(tr)]
            strict = [p for p in pieces if p['errors'] and len(norm(p['text'])) >= 3]
            loose = [p for p in pieces if p['errors'] and len(norm(p['text'])) < 3]
            ok = not errs and not strict
            if ok or A.draft:
                (OUT / f'A1_{tr["id"]}.mp3').write_bytes(mp3)
            dur = len(a48) / G.OUT_SR
            report['tracks'].append({'id': tr['id'], 'type': tr['type'], 'tempo': tempo, 'duration': round(dur, 1),
                                     'loudness': lrep, 'check_errors': errs, 'asr_strict_errors': len(strict),
                                     'asr_short_mismatch': len(loose), 'pieces': pieces})
            print(f"{'✓' if ok else '✗'} {tr['id']} {tr['type']} {dur:.1f} 秒 语速 {tempo}；"
                  f"{lrep['integrated_lufs']} LUFS，电磁音 {lrep['buzz_hz']:.0f} Hz {lrep['buzz_db']:+.1f} dB"
                  + (f"；核查：{'；'.join(errs)}" if errs else '')
                  + (f"；识别有出入 {len(strict)} 句：" + '；'.join(f"{p['text']}→{p['asr']}" for p in strict) if strict else '')
                  + (f"；短片段出入 {len(loose)} 个（只记录）" if loose else ''), flush=True)
            if not ok:
                fails.append(tr['id'])
        (OUT / '核对' / f'u{u}.json').write_text(json.dumps(report, ensure_ascii=False, indent=1), 'utf-8')
    print('全部通过' if not fails else f'未通过：{"、".join(fails)}')
    sys.exit(1 if fails and not A.draft else 0)


if __name__ == '__main__':
    main()
