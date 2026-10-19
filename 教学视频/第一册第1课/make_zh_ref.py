"""做中文讲解音色的参考录音（build.py 用的 build/ref_zh.wav 就是这样做的）：

    python make_zh_ref.py 工具包目录 输出目录 女声参考录音 中文识别模型目录

用女声（克隆 Supertonic F1）说一段中文，挑语音识别完全正确的一版当参考录音，再用它克隆。最后试读三句并核对。
"""
import sys
from pathlib import Path
import numpy as np, soundfile as sf, soxr, sherpa_onnx
KIT, OUT, FREF, ASRD = Path(sys.argv[1]), Path(sys.argv[2]).resolve(), sys.argv[3], sys.argv[4]
sys.path.insert(0, str(KIT / '西班牙语' / 'tools'))
import c4
MA = c4.load('es_make_audio', '西班牙语/tools/make_audio.py')
MA.CACHE = OUT / '_合成缓存'
G = MA.G
rec = sherpa_onnx.OfflineRecognizer.from_sense_voice(model=f'{ASRD}/model.int8.onnx', tokens=f'{ASRD}/tokens.txt', language='zh', use_itn=False, num_threads=4)
def asr(a, sr):
    st = rec.create_stream(); st.accept_waveform(16000, soxr.resample(a, sr, 16000).astype(np.float32)); rec.decode_stream(st)
    return st.result.text
import re, difflib
def cer(ref, hyp):
    r = re.sub(r'[^一-鿿0-9a-z]', '', ref.lower()); h = re.sub(r'[^一-鿿0-9a-z]', '', hyp.lower())
    sm = difflib.SequenceMatcher(a=r, b=h, autojunk=False)
    return sum(max(i2 - i1, j2 - j1) for op, i1, i2, j1, j2 in sm.get_opcodes() if op != 'equal') / max(1, len(r))
base = dict(MA.VOICES['qwen3_M1F5_25'], ref_audio=FREF, language='chinese')
REF = '同学们好，欢迎来到西班牙语课堂。今天我们一起学习发音、语法和课文，请大家跟着我认真练习。'
best = None
for seed in (1234, 2000, 3000, 4000, 5000, 6000):
    (a, sr), = MA.Worker(dict(base, seed=seed)).synth_all([REF])
    h = asr(a, sr); c = cer(REF, h)
    print(seed, f'{len(a)/sr:.1f}s', f'CER {c:.3f}', h, flush=True)
    if best is None or c < best[0]:
        best = (c, seed, a, sr)
c, seed, a, sr = best
a = G.trim(MA.to_sr(a, sr))
sf.write(str(OUT / 'ref_zh.wav'), a / max(1e-6, np.abs(a).max()) * 0.7, G.SR, subtype='FLOAT')
(OUT / 'ref_zh.txt').write_text(REF, 'utf-8')
print('picked seed', seed, 'CER', c)
zh = dict(MA.VOICES['qwen3_M1F5_25'], ref_audio=str(OUT / 'ref_zh.wav'), ref_text=REF, language='chinese')
tests = ['同学们好！今天我们学习《现代西班牙语》第一册第一课。',
         '西班牙语一共有五个元音。它们的发音短促、清楚，口型从头到尾保持不变。',
         '请注意，这个辅音不送气，和汉语拼音里的 b 差不多。']
for i, (a, sr) in enumerate(MA.Worker(zh).synth_all(tests)):
    sf.write(str(OUT / f'zhref_{i}.wav'), a, sr)
    h = asr(a, sr); print('ZH', i, f'CER {cer(tests[i], h):.3f}', h)
