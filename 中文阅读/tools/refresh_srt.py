"""按最终文章 JSON 重写 audio/<id>.srt（西语翻译可能在合成之后才审校定稿），并核对时间轴里的原文和 JSON 一致。

    python refresh_srt.py <文章目录> <音频目录>
"""
import json
import sys
from pathlib import Path


def ts(t):
    ms = int(round(t * 1000))
    return f'{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}'


arts, aud = Path(sys.argv[1]), Path(sys.argv[2])
changed, bad = [], []
for f in sorted(arts.glob('hsk1_*.json')):
    p = json.loads(f.read_text('utf-8'))
    T = json.loads((aud / f'{p["id"]}_timings.json').read_text('utf-8'))
    if [it['text'] for it in T['sentences']] != [s['zh'] for s in p['sents']]:
        bad.append(p['id'])
        continue
    srt = []
    for i, it in enumerate(T['sentences'], 1):
        srt += [str(i), f"{ts(it['start'])} --> {ts(it['end'])}", it['text'], p['sents'][i - 1]['es'], '']
    new = '\n'.join(srt)
    path = aud / f'{p["id"]}.srt'
    if path.read_text('utf-8') != new:
        changed.append(p['id'])
        path.write_text(new, 'utf-8')
print('原文不一致：', bad or '无')
print('重写字幕：', changed or '无')
sys.exit(1 if bad else 0)
