"""挑选对话用的第二男声、第二女声：用 Supertonic 3 合成各预置音色的参考录音，量平均音高（F0），
再用 Qwen3-TTS 克隆，合成几句测试句，用 Parakeet 识别核对。

    python audition.py <工具包目录> <输出目录> <识别模型目录>
"""
import json
import sys
from pathlib import Path

import librosa
import numpy as np
import soundfile as sf

KIT, OUT, ASR = (Path(p).resolve() for p in sys.argv[1:4])
sys.path.insert(0, str(KIT / '西班牙语' / 'tools'))
import c4  # noqa: E402

MA = c4.load('es_make_audio', '西班牙语/tools/make_audio.py')
MA.CACHE = OUT / '_合成缓存'
G, buzz = MA.G, MA.buzz
SR = G.SR
male = dict(MA.VOICES['qwen3_M1F5_25'])
TESTS = ['Hola, me llamo Lucía y soy de Sevilla.',
         '¿Cuánto cuesta este jersey azul?',
         'Por las mañanas voy a la universidad en metro.']


def f0(a, sr):
    f, v, _ = librosa.pyin(a.astype(np.float64), fmin=60, fmax=400, sr=sr)
    f = f[v & ~np.isnan(f)]
    return round(float(np.median(f)), 1) if len(f) else None


def supertonic_ref(name, sid):
    path = OUT / f'ref_{name}.wav'
    if not path.exists():
        cfg = {'engine': 'worker', 'python': 'self', 'script': 'sherpa.py', 'kind': 'supertonic',
               'model_dir': '西班牙语/models/supertonic3', 'sid': sid, 'lang': 'es', 'num_steps': 32, 'speed': 1.0}
        (a, sr), = MA.Worker(cfg).synth_all([male['ref_text']])
        a = buzz.deline(a, sr, buzz.load_comb('supertonic3_comb.json'))
        a = G.trim(MA.to_sr(a, sr))
        sf.write(str(path), a / max(1e-6, np.abs(a).max()) * 0.7, SR, subtype='FLOAT')
    return path


def recognizer():
    import sherpa_onnx
    d = ASR
    return sherpa_onnx.OfflineRecognizer.from_transducer(
        encoder=str(d / 'encoder.int8.onnx'), decoder=str(d / 'decoder.int8.onnx'), joiner=str(d / 'joiner.int8.onnx'),
        tokens=str(d / 'tokens.txt'), num_threads=4, model_type='nemo_transducer')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rec = recognizer()
    import soxr
    rows = []
    cands = [('F1', 0), ('F2', 1), ('F3', 2), ('F4', 3), ('F5', 4), ('M2', 6), ('M3', 7), ('M4', 8), ('M5', 9)]
    refs = {n: supertonic_ref(n, sid) for n, sid in cands}
    refs['M1F5_25'] = KIT / male['ref_audio']
    for n, p in refs.items():
        a, sr = sf.read(str(p), dtype='float32')
        cfg = dict(male, ref_audio=str(p))
        outs = MA.Worker(cfg).synth_all(TESTS)
        hyps, pitches = [], []
        for (b, bsr) in outs:
            pitches.append(f0(b, bsr))
            st = rec.create_stream()
            st.accept_waveform(16000, soxr.resample(b, bsr, 16000).astype(np.float32))
            rec.decode_stream(st)
            hyps.append(st.result.text.strip())
            sf.write(str(OUT / f'test_{n}_{len(hyps)}.wav'), b, bsr)
        rows.append({'voice': n, 'ref_f0': f0(a, sr), 'clone_f0': pitches, 'asr': hyps})
        print(n, rows[-1]['ref_f0'], pitches, hyps, flush=True)
    (OUT / 'audition.json').write_text(json.dumps(rows, ensure_ascii=False, indent=1), 'utf-8')


if __name__ == '__main__':
    main()
