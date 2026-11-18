"""成品录音逐句复核（DELE 模拟卷，摘自 SIELE 模拟卷的 check_final.py）：
    SIELE_KIT=… SIELE_ASR=… SIELE_ROOT=… python tools/check_final.py <级别> [音轨名…]

合成时逐句核对的是变速前的原始合成；这里按 核对/report.json 里记下的每一句在成品里的起止时间，
到成品 MP3（变速、母带处理、编码之后）里把每一句切出来再识别一遍，用同样的规则比对。
DELE_<级别>_CA_completa.mp3 不再逐句识别，而是核对它确实是各段听力按顺序、中间各隔 3 秒接起来的：
每一段在连播版里的位置和波形都要和单独的那一段对得上。"""
import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parent))
import asrcheck as X  # noqa: E402

LV = sys.argv[1].upper()
OUT = Path(__file__).resolve().parents[1] / 'out' / LV / 'audio'
want = sys.argv[2:]
rep = json.loads((OUT / '核对' / 'report.json').read_text('utf-8'))
FULL = f'DELE_{LV}_CA_completa'
tracks = [k for k in rep if k != FULL and (not want or k in want)]


def load(name):
    a, sr = sf.read(str(OUT / f'{name}.mp3'), dtype='float32')
    return (a if a.ndim == 1 else a.mean(1)), sr


rec = X.Recognizer()
total, bad_tracks, retried = 0, [], []
for tid in tracks:
    r = rep[tid]
    mp3, sr = load(tid)
    if abs(len(mp3) / sr - r['duration']) > 0.2:
        print(f"✗ {tid}：成品 {len(mp3) / sr:.1f} 秒，记录 {r['duration']} 秒，对不上")
        bad_tracks.append(tid)
        continue
    errs, ok_text, failed = [], set(), []
    for it in r['items']:
        total += 1
        tries = []
        # 识别模型对切点和电平很敏感：先按时间表切，有出入再换几种切法、把电平拉到一样再认；
        # 有一种完全对上就算这一句的读音没问题，每种都对不上的才算有出入
        for lo, hi, normgain in ((0.05, 0.12, False), (0.15, 0.25, False), (0.02, 0.05, False), (0.05, 0.12, True), (0.25, 0.4, True)):
            seg = mp3[max(0, int((it['start'] - lo) * sr)):int((it['end'] + hi) * sr)].copy()
            if normgain:
                seg *= 0.5 / (np.abs(seg).max() + 1e-9)
            hyp = rec(seg, sr)
            e, _ = X.compare(it['text'], hyp)
            tries.append((e, hyp))
            if not e:
                break
        if tries[-1][0]:
            failed.append((it['text'], ' / '.join(h for _, h in tries)))
            continue
        ok_text.add(it['text'])
        if len(tries) > 1:
            retried.append(f"{tid} {it['text']}（第 {len(tries)} 种切法对上；第一种认成“{tries[0][1]}”）")
    # 同一句在一段里出现两次（每段读两遍）用的是同一份录音：有一遍认对就说明读音没问题
    known = {p['text'] for p in r['pieces'] if p.get('verified')}
    for text, hyps in failed:
        if text in known:
            retried.append(f"{tid} {text}（合成时已切成片段单独核对过读音，记在 VERIFIED 里；这里认成“{hyps.split(' / ')[0]}”）")
        elif text in ok_text:
            retried.append(f"{tid} {text}（这一遍认成“{hyps.split(' / ')[0]}”，同一份录音的另一遍认对了）")
        else:
            errs.append(f'{text} → {hyps}')
    if errs:
        bad_tracks.append(tid)
    print(f"{'✓' if not errs else '✗'} {tid}：{len(r['items'])} 句" + ('' if not errs else '；有出入：'), flush=True)
    for e in errs:
        print('    ', e, flush=True)

if FULL in rep and not want:
    full, sr = load(FULL)
    pos, okc = 0, True
    for n, pid in enumerate(rep[FULL]['parts'], 1):
        part, sr2 = load(pid)
        assert sr2 == sr
        # 在预计位置前后 1 秒内找这一段的起点（编码的首尾填充会让位置差几十毫秒）
        head = part[:int(8 * sr)]
        lo = max(0, pos - sr)
        win = full[lo:lo + 2 * sr + len(head)]
        c = np.correlate(win, head, mode='valid')
        start = lo + int(np.argmax(c))
        seg = full[start:start + len(part)]
        m = min(len(seg), len(part))
        cc = float(np.dot(seg[:m], part[:m]) / (np.linalg.norm(seg[:m]) * np.linalg.norm(part[:m]) + 1e-9))
        drift = (start - pos) / sr
        good = cc > 0.98 and abs(drift) < 0.2
        okc &= good
        print(f"  {'✓' if good else '✗'} 连播版里的 Tarea {n}：起点 {start / sr:.2f} 秒（偏差 {drift:+.3f}），波形相关 {cc:.4f}")
        pos = start + len(part) + 3 * sr
    tail = (len(full) - pos + 3 * sr) / sr
    print(f"{'✓' if okc else '✗'} {FULL}：{len(rep[FULL]['parts'])} 段齐全、顺序对，结尾多出 {tail:.2f} 秒")
    if not okc:
        bad_tracks.append(FULL)

print('换切法后对上的句子：')
for x in retried:
    print('   ', x)
print(f'共 {total} 句；' + ('全部通过' if not bad_tracks else f'有问题：{"、".join(bad_tracks)}'))
sys.exit(1 if bad_tracks else 0)
