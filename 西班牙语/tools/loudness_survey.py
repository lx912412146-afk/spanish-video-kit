"""响度测法对比（只用缓存，不重新合成、不写任何文件）：每篇在几个音色下各算一次两种短时响度波动。

    python 西班牙语/tools/loudness_survey.py 编号…                                   # 默认比较 qwen3_M1F5_25 和 qwen3_M1F5_25_slow
    python 西班牙语/tools/loudness_survey.py --voices qwen3_M1F5_25_slow 编号…

“原测法”是 3 秒窗口从 0 秒滑到结尾（含片头 1.5 秒、结尾 2 秒静音）；“朗读范围”只统计第一句开始到最后一句结束，是现在判定用的（见 loudness.py）。
用的是音色的基本电平设置，不走 make_audio 的逐级加强电平。合成没有全部缓存的文章跳过（先跑 fill_cache.py）。
2026-10-18 的 50 篇结果在 记录/响度测法对比_50篇.txt。
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import c4  # noqa: E402
from fill_cache import texts_of  # noqa: E402

MA = c4.load('es_make_audio', '西班牙语/tools/make_audio.py')
MV = c4.load('es_make_video', '西班牙语/tools/make_video.py')
G = MA.G


def main():
    args = sys.argv[1:]
    voices = ['qwen3_M1F5_25', 'qwen3_M1F5_25_slow']
    if args[:1] == ['--voices']:
        voices, args = args[1].split(','), args[2:]
    if not args:
        raise SystemExit(__doc__)
    engs = {v: MA.engine_for(MA.VOICES[v]) for v in voices}
    fails = {(v, m): 0 for v in voices for m in ('原测法', '朗读范围')}
    n = 0
    for pid in args:
        p = MV.load(pid)
        texts = texts_of(p)
        if not all(engs[voices[0]]._cached(t).exists() for t in texts):
            print(f'{pid}：合成没有全部缓存，跳过')
            continue
        n += 1
        row = [pid]
        for v in voices:
            a48, items = MA.build(p, MA.VOICES[v], engs[v], log=lambda *_: None)
            rep, errs = MA.verify(G.encode_mp3(a48, kbps=128), items, -16.0)
            full, span = rep['short_term_std_full_lu'], rep['short_term_std_lu']
            fails[(v, '原测法')] += full > 1.0
            fails[(v, '朗读范围')] += span > 1.0
            other = [e for e in errs if '短时' not in e]
            row.append(f"{v}：原测法 {full:.2f}{'✗' if full > 1 else ' '} 朗读范围 {span:.2f}{'✗' if span > 1 else ' '}"
                       + (f"  其他问题 {other}" if other else ''))
        print('  '.join(row), flush=True)
    print(f'{n} 篇；超过 1.0 LU 的篇数：' + '，'.join(f'{v} {m} {c}' for (v, m), c in fails.items()))


if __name__ == '__main__':
    main()
