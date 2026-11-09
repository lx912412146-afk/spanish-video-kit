"""分级阅读朗读音频逐句识别核对：

    python 西班牙语/tools/asr_check_reading.py <工具包目录> <识别模型目录> <音色> <文章编号>…

例：python 西班牙语/tools/asr_check_reading.py . sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8 qwen3_M1F5_25_slow a1_11

按 西班牙语/audio/timings.json 里每句的起止时间，从成品 MP3 切出每一句，用 Parakeet（sherpa-onnx）识别，
和朗读文本逐词比。比对规则借用 B1-B2听力练习/tools/make_tracks.py 的 compare（去重音和标点；数字、价钱、
词界读音相同等放宽规则一样）。识别模型对切点敏感，所以切点前后各试几种放宽，有一种完全对上就算这句读对了。
分级阅读第二批（2026-11-10 起）每篇都用它核对过。
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

KIT, ASRD, VOICE, IDS = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:]
if not IDS:
    sys.exit(__doc__)
# make_tracks.py 在导入时就解析命令行，这里换成它要的参数（不会合成，也不会写输出目录）
sys.argv = ['make_tracks.py', KIT, tempfile.gettempdir(), ASRD, '1']
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'B1-B2听力练习' / 'tools'))
import make_tracks as M  # noqa: E402

rec = M.Recognizer()
T = json.loads((Path(KIT) / '西班牙语' / 'audio' / 'timings.json').read_text('utf-8'))[VOICE]
SR = 48000
bad = 0
for pid in IDS:
    t = T[pid]
    mp3 = Path(KIT) / '西班牙语' / 'audio' / t['file']
    pcm = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(mp3), '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'],
                         capture_output=True, check=True).stdout
    a = np.frombuffer(pcm, np.float32)
    print(f'== {pid} {t["file"]} {len(a) / SR:.1f} 秒，{len(t["sentences"])} 句')
    for s in t['sentences']:
        best = None
        for pre, post in ((0.15, 0.25), (0.3, 0.4), (0.05, 0.15), (0.4, 0.6)):
            x = a[max(0, int((s['start'] - pre) * SR)):int((s['end'] + post) * SR)]
            hyp = rec(x, SR)
            e, ops = M.compare(s['read'], hyp)
            if best is None or e < best[0]:
                best = (e, ops, hyp)
            if e == 0:
                break
        ok = best[0] == 0
        bad += not ok
        print(f"{'✓' if ok else '✗'} {s['k']:2d} {s['read']}" + ('' if ok else f'\n     → {best[2]}  {best[1]}'))
        if ok and best[1]:
            print(f'     （不计：{best[1]}）')
print('全部对上' if not bad else f'{bad} 句有出入')
sys.exit(1 if bad else 0)
