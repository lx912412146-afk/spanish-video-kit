"""只合成、填缓存（不做后期处理、不出视频）：把文章的 Qwen3 原始合成先全部存进 audio/_合成缓存/。

    python 西班牙语/tools/fill_cache.py 音色 编号…        # 例：python 西班牙语/tools/fill_cache.py qwen3_M1F5_25_slow a1_01 a1_02

批量生成之前先跑它：最慢的合成和语速、音高、电平这些后期参数无关，参数还没定也可以先合成。之后 batch_mac.sh 直接用缓存，几秒一篇。
每篇单独调用一次合成，做完一篇就存一篇；中断后重跑，已经缓存的段会跳过。
"""
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import c4  # noqa: E402

MA = c4.load('es_make_audio', '西班牙语/tools/make_audio.py')
MV = c4.load('es_make_video', '西班牙语/tools/make_video.py')


def texts_of(p):
    """这篇文章送去合成的全部片段，切分和 make_audio.build 完全一致（含两处登记的不停顿逗号）。"""
    MA.PAUSES.clear()
    MA.PAUSES.update({k: v for k, v in MA.PAUSES_ALL.get(p['id'], {}).items() if not k.startswith('_')})
    MA.PAUSES.update({k: v for k, v in p.get('no_pause_commas', {}).items() if not k.startswith('_')})
    return [t for k, s in enumerate((s for para in p['paras'] for s in para), 1) for t in MA.segments(s['es'], k)]


def main():
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    voice, ids = sys.argv[1], sys.argv[2:]
    eng = MA.engine_for(MA.VOICES[voice])
    for pid in ids:
        t0 = time.time()
        texts = texts_of(MV.load(pid))
        eng.synth_all(texts)
        print(f'{pid}：{len(texts)} 段已在缓存里（{time.time() - t0:.0f} 秒）', flush=True)


if __name__ == '__main__':
    main()
