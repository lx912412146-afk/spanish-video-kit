"""检查各个合成声音能不能读出齿间音 [θ]：每个声音合成几组最小对立词（caza / casa …），
用 Parakeet 识别，并量词首摩擦音 3.5–11 kHz 的能量（[θ] 比 [s] 弱得多）。

    python theta_test.py <工具包目录> <教材目录> <识别模型目录>
"""
import sys
from pathlib import Path

import numpy as np
import soxr

KIT, BOOK, ASR = (Path(p).resolve() for p in sys.argv[1:4])
sys.path.insert(0, str(KIT / '西班牙语' / 'tools'))
import c4  # noqa: E402

MA = c4.load('es_make_audio', '西班牙语/tools/make_audio.py')
MA.CACHE = BOOK / 'audio_build' / 'theta'
MALE = dict(MA.VOICES['qwen3_M1F5_25'])
REFS = {'女1': KIT / '试卷' / '第一册高考模拟卷' / '听力' / 'ref_female_F1.wav',
        '男2': BOOK / 'voices' / 'ref_M5.wav', '女2': BOOK / 'voices' / 'ref_F2.wav', '女3': BOOK / 'voices' / 'ref_F5.wav'}
PAIRS = [('caza', 'casa'), ('cien', 'sien'), ('cocer', 'coser'), ('ciento', 'siento'), ('zeta', 'seta'), ('cerrar', 'serrar')]
WORDS = [w for p in PAIRS for w in p] + ['Zaragoza es una ciudad.', 'Cenamos a las diez.']


def rec_init():
    import sherpa_onnx
    d = ASR if (ASR / 'tokens.txt').exists() else next(p for p in ASR.iterdir() if p.is_dir() and 'parakeet' in p.name)
    return sherpa_onnx.OfflineRecognizer.from_transducer(
        encoder=str(d / 'encoder.int8.onnx'), decoder=str(d / 'decoder.int8.onnx'), joiner=str(d / 'joiner.int8.onnx'),
        tokens=str(d / 'tokens.txt'), model_type='nemo_transducer', num_threads=4)


def asr(rec, a, sr):
    st = rec.create_stream()
    pad = np.zeros(int(0.3 * sr), np.float32)
    st.accept_waveform(16000, soxr.resample(np.concatenate([pad, a, pad]), sr, 16000).astype(np.float32))
    rec.decode_stream(st)
    return st.result.text.strip()


def hf_onset(a, sr):
    """词首 200 ms 内 3.5–11 kHz 能量的最大值，减去全词 100–1500 Hz 能量的最大值（dB）。"""
    n, h = int(0.02 * sr), int(0.005 * sr)
    f = np.fft.rfftfreq(n, 1 / sr)
    nz = np.flatnonzero(np.abs(a) > np.abs(a).max() * 0.02)
    a = a[nz[0]:nz[-1]] if len(nz) else a
    def band(x, lo, hi):
        X = np.abs(np.fft.rfft(x * np.hanning(len(x)))) ** 2
        return 10 * np.log10(X[(f >= lo) & (f < hi)].sum() + 1e-12)
    frames = [a[i:i + n] for i in range(0, len(a) - n, h)]
    on = [band(x, 3500, 11000) for x in frames[:int(0.2 * sr / h)]]
    vow = [band(x, 100, 1500) for x in frames]
    return max(on) - max(vow)


rec = rec_init()
for v in ('男1', '男2', '女1', '女2', '女3'):
    cfg = dict(MALE) if v == '男1' else dict(MALE, ref_audio=str(REFS[v]))
    outs = MA.Worker(cfg).synth_all(WORDS)
    print(f'== {v}', flush=True)
    res = {w: (asr(rec, a, sr), hf_onset(a, sr)) for w, (a, sr) in zip(WORDS, outs)}
    for x, y in PAIRS:
        print(f'  {x:7s} → {res[x][0]:10s} {res[x][1]:+6.1f} dB   |  {y:7s} → {res[y][0]:10s} {res[y][1]:+6.1f} dB', flush=True)
    for w in WORDS[-2:]:
        print(f'  {w} → {res[w][0]}', flush=True)
