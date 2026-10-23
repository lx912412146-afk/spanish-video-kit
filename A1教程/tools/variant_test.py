"""试几种输入写法，看女2 能不能把单音节读成齿间音：python variant_test.py <工具包目录> <教材目录> 写法…"""
import sys
from pathlib import Path

KIT, BOOK = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
sys.path.insert(0, str(KIT / '西班牙语' / 'tools'))
sys.path.insert(0, str(BOOK / 'tools'))
import c4  # noqa: E402
import vowelid  # noqa: E402

MA = c4.load('es_make_audio', '西班牙语/tools/make_audio.py')
MA.CACHE = BOOK / 'audio_build' / '_合成缓存'
MALE = dict(MA.VOICES['qwen3_M1F5_25'])
texts = sys.argv[3:]
for seed in (None, 2000, 3000):
    cfg = dict(MALE, ref_audio=str(BOOK / 'voices' / 'ref_F2.wav'))
    if seed:
        cfg['seed'] = seed
    for t, (a, sr) in zip(texts, MA.Worker(cfg).synth_all(texts)):
        fd = vowelid.fricative_db(a, sr)
        f = vowelid.formants(a, sr)
        near = vowelid.classify(f)[0] if f else None
        print(f'{seed} {t!r}: 摩擦音 {fd:.1f} dB，元音 {vowelid.vowel_sec(a, sr)} 秒，像 {near} {tuple(round(x) for x in f) if f else ""}', flush=True)
