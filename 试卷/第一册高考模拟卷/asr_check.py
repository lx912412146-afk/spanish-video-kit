"""听力音频自检：把每一句合成录音用语音识别（Parakeet-TDT 0.6B v3，sherpa-onnx int8）转回文字，和录音稿逐词比对。

    python asr_check.py 工具包目录 试卷.md 音频目录 识别模型目录

比对前统一成小写、去掉重音和标点，数字换成西语单词。只差空格（mejor en / mejoren）、人名地名（Xi'an、Wang）和同音（单独的 Sí 识别成 c）
的出入记「≈」、不算错词，其余人工判断。读得不对的句子可以用 asr_retry.py 换种子重新合成。
输出：每句的错词数，对不上的片段；最后汇总。写到 音频目录/听力_识别核对.json。
"""
import difflib
import importlib.util
import json
import re
import sys
import unicodedata
from pathlib import Path

import numpy as np
import soundfile as sf
import soxr
from num2words import num2words

KIT, PAPER, AUDIO, ASR = (Path(p).resolve() for p in sys.argv[1:5])
spec = importlib.util.spec_from_file_location('ml', Path(__file__).with_name('make_listening.py'))
sys.argv = [sys.argv[0], str(KIT), str(PAPER), str(AUDIO)]
ml = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ml)
NAMES = {'xian', 'wang', 'beijing', 'shanghai'}       # 识别模型认不准的中国人名、地名
APOCOPE = {'veintiun': 'veintiuno', 'un': 'uno', 'una': 'uno'}
HOMOPHONES = {('si', 'c'), ('ah', 'a'), ('tambien', 'tan bien')}   # 读音相同：单独的 Sí 识别成字母 c，Ah 识别成 a，también 识别成 tan bien


def norm(t):
    t = re.sub(r'\d+', lambda m: ' ' + num2words(int(m.group()), lang='es') + ' ', t.lower())
    t = ''.join(c for c in unicodedata.normalize('NFD', t) if unicodedata.category(c) != 'Mn')
    words = re.sub(r"[^a-zñ ]", ' ', t.replace("'", '')).split()
    return [APOCOPE.get(w, w) for w in words]               # 21 识别成数字再转回来是 veintiuno，和 veintiún 视为相同


def recognizer():
    import sherpa_onnx
    d = next(p for p in ASR.iterdir() if p.is_dir() and 'parakeet' in p.name)
    return sherpa_onnx.OfflineRecognizer.from_transducer(
        encoder=str(d / 'encoder.int8.onnx'), decoder=str(d / 'decoder.int8.onnx'), joiner=str(d / 'joiner.int8.onnx'),
        tokens=str(d / 'tokens.txt'), model_type='nemo_transducer', num_threads=4)


def transcribe(rec, f):
    a, sr = sf.read(str(f), dtype='float32')
    st = rec.create_stream()
    st.accept_waveform(16000, soxr.resample(a, sr, 16000).astype(np.float32))
    rec.decode_stream(st)
    return st.result.text.strip()


def compare(s, hyp):
    """返回 (错词数, 出入列表[(稿, 识别, 算不算错)])。"""
    r, h = norm(s), norm(hyp)
    ops, err = [], 0
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(a=r, b=h, autojunk=False).get_opcodes():
        if op == 'equal':
            continue
        x, y = ' '.join(r[i1:i2]), ' '.join(h[j1:j2])
        counts = x.replace(' ', '') != y.replace(' ', '') and not (set(r[i1:i2]) & NAMES) and (x, y) not in HOMOPHONES
        ops.append((x, y, counts))
        err += max(len(x.split()), len(y.split())) if counts else 0
    return err, ops


def sentences(texts):
    """[(段号, 说话人, 句子)]，和 make_listening.py 合成时的切分一致。"""
    return [(k, spk, p) for k, lines in texts.items() for spk, line in lines for p in ml.pieces(line)]


def main():
    rec, eng = recognizer(), ml.engines()
    texts = ml.parse(PAPER.read_text('utf-8'))
    seeds = ml.seed_overrides()
    report, total_err, total_words = [], 0, 0
    for k, spk, s in sentences(texts):
        f = ml.cached_file(eng, spk, s)
        if not f.exists():
            raise SystemExit(f'Texto {k}：这句还没有合成：{s}')
        hyp = transcribe(rec, f)
        err, ops = compare(s, hyp)
        total_err += err
        total_words += len(norm(s))
        report.append({'texto': k, 'speaker': spk, 'text': s, 'seed': seeds.get(s), 'asr': hyp, 'errors': err,
                       'diff': [[x, y] for x, y, _ in ops], 'ignored': [[x, y] for x, y, c in ops if not c]})
        mark = '✗' if err else ('≈' if ops else '✓')
        print(f'{mark} T{k} {spk} {err}/{len(norm(s))}  ' + '；'.join(f'「{x}」→「{y}」' for x, y, _ in ops), flush=True)
    (AUDIO / '听力_识别核对.json').write_text(json.dumps(report, ensure_ascii=False, indent=1), 'utf-8')
    bad = [x for x in report if x['errors']]
    near = [x for x in report if x['ignored'] and not x['errors']]
    print(f'共 {len(report)} 句、{total_words} 词；有错词的句子 {len(bad)} 句，错词 {total_err} 个'
          f'（词错误率 {total_err / total_words:.1%}）；只差空格、人名或同音的 {len(near)} 句')


if __name__ == '__main__':
    main()
