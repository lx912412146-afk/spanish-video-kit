"""挑女4（Irene）的声音：用候选参考录音克隆，读几句台词和 caza / casa 这类词，量音高、做识别，和女2、女3 比。
python voice4_test.py <工具包目录> <教材目录> <识别模型目录> 候选1.wav [候选2.wav …]
"""
import sys
from pathlib import Path

import numpy as np
import soxr

KIT, BOOK, ASR = (Path(p).resolve() for p in sys.argv[1:4])
CANDS = [Path(p).resolve() for p in sys.argv[4:]]
sys.path.insert(0, str(KIT / '西班牙语' / 'tools'))
import c4  # noqa: E402

MA = c4.load('es_make_audio', '西班牙语/tools/make_audio.py')
MA.CACHE = BOOK / 'audio_build' / 'voice4'
MALE = dict(MA.VOICES['qwen3_M1F5_25'])
MA.chain(MALE)
SENTS = ['Gracias, profesora. Encantada.',
         'Nunca he estado tan lejos de casa, pero Chen Yu y Li Hao me ayudan mucho.',
         '¡Ay, chicos, no os lo vais a creer! Me equivoqué de aula.',
         'Desde que llegué, solo pienso en la comida de aquí. ¡Me encantan los jianbing!',
         'Andrés, siento mucho la nota de la nevera. Estaba enfadada.',
         'Si vienes a Granada, te llevaré a la Alhambra.']
THETA = ['caza', 'casa', 'cien', 'sien', 'cocer', 'coser', 'zeta', 'seta']


def f0(a, sr):
    fs, n = [], int(0.04 * sr)
    for i in range(0, len(a) - n, n // 2):
        x = a[i:i + n] - a[i:i + n].mean()
        if np.sqrt((x ** 2).mean()) < 0.02:
            continue
        c = np.correlate(x, x, 'full')[n - 1:]
        lo, hi = int(sr / 400), int(sr / 70)
        k = lo + np.argmax(c[lo:hi])
        if c[k] > 0.3 * c[0]:
            fs.append(sr / k)
    return round(float(np.median(fs))) if fs else 0


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


rec = rec_init()
voices = [('女2', BOOK / 'voices' / 'ref_F2.wav'), ('女3', BOOK / 'voices' / 'ref_F5.wav')] + [(c.stem, c) for c in CANDS]
for name, ref in voices:
    cfg = dict(MALE, ref_audio=str(ref))
    texts = SENTS + (THETA if name not in ('女2', '女3') else [])
    outs = MA.Worker(cfg).synth_all(texts)
    pitches = []
    print(f'== {name}', flush=True)
    for t, (a, sr) in zip(texts, outs):
        a = a.mean(1) if a.ndim > 1 else a
        if t in SENTS:
            pitches.append(f0(a, sr))
        print(f'  {t[:40]:40s} → {asr(rec, a, sr)}', flush=True)
    print(f'  音高中位数（各句）：{pitches}，总中位 {int(np.median(pitches))} Hz', flush=True)
