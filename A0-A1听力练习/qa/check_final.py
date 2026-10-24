"""成品录音逐句复核：python check_final.py <工具包目录> <识别模型目录> [套号…]
合成时的逐句核对用的是变速前的原始合成；这里按核对记录里每句选中的版本（种子）和语速，从合成缓存重新排出时间表
（不重新合成），到成品 MP3（变速、母带处理、编码之后）里把每一句切出来再识别一遍，用同样的规则比对。"""
import json
import sys
from pathlib import Path

import numpy as np

KIT, ASRD = sys.argv[1], sys.argv[2]
want = [int(x) for x in sys.argv[3:]] or list(range(1, 11))
sys.argv = ['make_tracks.py', KIT, '/tmp/x', ASRD, '1']
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
import make_tracks as M  # noqa: E402
import sets as S  # noqa: E402
import soundfile as sf  # noqa: E402

rec = M.Recognizer()
total = bad = 0
retried = []
for st in S.load_all():
    if st['num'] not in want:
        continue
    rep = json.loads((ROOT / 'audio_out' / '核对' / f"set{st['num']:02d}.json").read_text('utf-8'))
    for p in st['parts']:
        tid = f"{st['num']:02d}-{p['idx']}"
        tr = next(t for t in rep['tracks'] if t['id'] == tid)
        assert tr['fallback'] is None, tid
        got = {}
        for pc in tr['pieces']:
            w = M.MA.Worker(M.voice_cfg(pc['voice'], pc['seed']))
            f = w._cached(M.spoken(pc['text']))
            assert f.exists(), f'{tid} 缓存里没有：{pc}'
            (a, sr), = w.synth_all([M.spoken(pc['text'])])
            got[(pc['voice'], pc['text'])] = (a, sr, pc)
        a48, items, _ = M.assemble(p, got, tr['tempo'])
        mp3, sr = sf.read(str(ROOT / 'audio_out' / f'A0A1_{tid}.mp3'), dtype='float32')
        mp3 = mp3 if mp3.ndim == 1 else mp3.mean(1)
        if abs(len(mp3) / sr - len(a48) / M.G.OUT_SR) > 0.2:
            print(f'✗ {tid}：成品 {len(mp3) / sr:.1f} 秒，排出来 {len(a48) / M.G.OUT_SR:.1f} 秒，对不上')
            bad += 1
            continue
        errs, ok_pieces, failed = [], set(), []
        for it in items:
            total += 1
            tries = []
            # 识别模型对切点和电平很敏感（同一句换个切法结果就变）：先按时间表切，有出入再换几种切法、把电平拉到一样再认，
            # 有一种完全对上就算这一句的读音没问题；每种都对不上的才算有出入（合成真的读错、漏词，换切法也认不对）
            for lo, hi, normgain in ((0.05, 0.12, False), (0.15, 0.25, False), (0.02, 0.05, False), (0.05, 0.12, True), (0.25, 0.4, True)):
                seg = mp3[max(0, int((it['start'] - lo) * sr)):int((it['end'] + hi) * sr)].copy()
                if normgain:
                    seg *= 0.5 / (np.abs(seg).max() + 1e-9)
                hyp = rec(seg, sr)
                e, ops = M.compare(it['text'], hyp)
                tries.append((e, hyp, ops))
                if not e:
                    break
            if tries[-1][0]:
                failed.append((it['text'], ' / '.join(h for _, h, _ in tries)))
                continue
            ok_pieces.add(it['text'])
            if len(tries) > 1:
                retried.append(f"{tid} {it['text']}（第 {len(tries)} 种切法对上；第一种认成“{tries[0][1]}”）")
        # 同一句在这一段里读了两遍（每题读两遍、整段读两遍），两遍是同一份录音：有一遍认对就说明这一句的读音没问题
        for text, hyps in failed:
            if text in ok_pieces:
                retried.append(f"{tid} {text}（这一遍认成“{hyps.split(' / ')[0]}”，同一份录音的另一遍认对了）")
            else:
                errs.append(f'{text} → {hyps}')
        bad += bool(errs)
        print(f"{'✓' if not errs else '✗'} {tid}：{len(items)} 句" + ('' if not errs else '；有出入：'), flush=True)
        for e in errs:
            print('    ', e, flush=True)
print('换切法后对上的句子：')
for x in retried:
    print('   ', x)
print(f'成品逐句复核：{total} 句，' + ('全部对上' if not bad else f'{bad} 段有出入'))
