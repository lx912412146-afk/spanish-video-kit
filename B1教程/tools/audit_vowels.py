"""核查成品语音跟读里单音节的元音（和 make_tracks.py 合成时用的是同一个辨认方法，见 vowelid.py）：
按停顿切开 MP3，女声开音节逐个量前两个共振峰，列出元音不对的。

    python audit_vowels.py <教材目录>
"""
import sys
from pathlib import Path

import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parent))
import vowelid  # noqa: E402
from audit_drills import drills, segments  # noqa: E402

BOOK = Path(sys.argv[1])
voices = {}
for f in sorted((BOOK / 'audio').glob('u*.md')):
    cur = None
    for line in f.read_text('utf-8').split('\n'):
        if line.startswith('### '):
            cur = line.split()[1]
        elif line.startswith('- 角色：') and cur:
            voices[cur] = line.split('＝')[-1].strip()
n = bad = 0
for tid, items in drills(BOOK):
    if not voices.get(tid, '').startswith('女'):
        continue
    a, sr = sf.read(BOOK / 'audio_out' / f'B1_{tid}.mp3', dtype='float32')
    a = a.mean(1) if a.ndim > 1 else a
    segs = segments(a, sr)
    if len(segs) != len(items):
        print(f'✗ {tid}：切出 {len(segs)} 段，录音稿 {len(items)} 个')
        bad += 1
        continue
    for w, (b, e) in zip(items, segs):
        r = vowelid.check(w, a[b:e], sr)
        if r is None:
            continue
        n += 1
        if not r[0]:
            bad += 1
            print(f'✗ {tid} {w}：F1 {r[1][0]:.0f} Hz，F2 {r[1][1]:.0f} Hz，听着像 {r[2]}')
print(f'量了 {n} 个单音节，' + ('元音全部对' if not bad else f'{bad} 个有问题'))
