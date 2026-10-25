"""整句识别有出入时，核对缓存里那一版录音到底读没读那个词：找出（声音、句子、种子）对应的缓存 wav，
整句识别（带词的时间），再把句子切成几段分别识别，打印每段的识别结果和时长。不重新合成。
python verify_piece.py <工具包目录> <教材目录> <识别模型目录> <声音> "<句子>" [种子或 -] [窗口，如 1.7-2.6,5.3-6.1]
"""
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
import soxr

KIT, BOOK, ASR = (Path(p).resolve() for p in sys.argv[1:4])
VOICE, TEXT = sys.argv[4], sys.argv[5]
SEED = int(sys.argv[6]) if len(sys.argv) > 6 and sys.argv[6] != '-' else None
WINDOWS = [tuple(float(x) for x in w.split('-')) for w in sys.argv[7].split(',')] if len(sys.argv) > 7 else [(0.0, 0.5), (0.3, 1.2), (0.5, 1.4), (0.6, 1.6)]
sys.path.insert(0, str(KIT / '西班牙语' / 'tools'))
import c4  # noqa: E402

MA = c4.load('es_make_audio', '西班牙语/tools/make_audio.py')
MA.CACHE = BOOK / 'audio_build' / '_合成缓存'
MALE = dict(MA.VOICES['qwen3_M1F5_25'])
MA.chain(MALE)
REFS = {'女1': KIT / '试卷' / '第一册高考模拟卷' / '听力' / 'ref_female_F1.wav',
        '男2': BOOK / 'voices' / 'ref_M5.wav', '女2': BOOK / 'voices' / 'ref_F2.wav', '女3': BOOK / 'voices' / 'ref_F5.wav',
        '女4': BOOK / 'voices' / 'ref_F3.wav'}
cfg = dict(MALE) if VOICE == '男1' else dict(MALE, ref_audio=str(REFS[VOICE]), label=f'Qwen3-TTS 克隆（西班牙语教程 {VOICE}）')
if SEED is not None:
    cfg['seed'] = SEED
f = MA.Worker(cfg)._cached(TEXT)
if not f.exists():
    sys.exit(f'缓存里没有这一版：{f.name}')
a, sr = sf.read(f, dtype='float32')
a = a.mean(1) if a.ndim > 1 else a
print(f'{f.name}  {len(a) / sr:.2f} 秒')

import sherpa_onnx  # noqa: E402
d = ASR if (ASR / 'tokens.txt').exists() else next(p for p in ASR.iterdir() if p.is_dir() and 'parakeet' in p.name)
rec = sherpa_onnx.OfflineRecognizer.from_transducer(
    encoder=str(d / 'encoder.int8.onnx'), decoder=str(d / 'decoder.int8.onnx'), joiner=str(d / 'joiner.int8.onnx'),
    tokens=str(d / 'tokens.txt'), model_type='nemo_transducer', num_threads=2)


def asr(x):
    st = rec.create_stream()
    pad = np.zeros(int(0.3 * sr), np.float32)
    st.accept_waveform(16000, soxr.resample(np.concatenate([pad, x, pad]), sr, 16000).astype(np.float32))
    rec.decode_stream(st)
    return st.result


r = asr(a)
print('整句：', r.text.strip())
toks = [(t, round(ts - 0.3, 2)) for t, ts in zip(r.tokens, r.timestamps)]
print('词的时间：', ' '.join(f'{t}@{ts}' for t, ts in toks))
# 按能量找停顿，切成几段分别识别
win = int(0.02 * sr)
e = np.array([np.sqrt((a[i:i + win] ** 2).mean()) for i in range(0, len(a) - win, win)])
quiet = e < max(e.max() * 0.04, 1e-4)
cuts, run = [], 0
for i, q in enumerate(quiet):
    run = run + 1 if q else 0
    if run == 4:
        cuts.append((i - 2) * win)
bounds = [0] + [c for c in cuts if 0.3 * sr < c < len(a) - 0.3 * sr] + [len(a)]
for s, t in zip(bounds, bounds[1:]):
    if t - s > 0.15 * sr:
        print(f'  {s / sr:5.2f}–{t / sr:5.2f} 秒：{asr(a[s:t]).text.strip()}')
# 指定的时间窗口单独识别（按整句识别给出的词的时间选）
for lo, hi in WINDOWS:
    s, t = int(lo * sr), min(len(a), int(hi * sr))
    print(f'  窗口 {lo:.1f}–{hi:.1f} 秒：{asr(a[s:t]).text.strip()}')
