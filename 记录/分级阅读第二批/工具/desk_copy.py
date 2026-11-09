"""把分级阅读第二批 50 个视频复制到桌面：python desk_copy.py <KIT> <发布说明.md>
- ~/Desktop/西语视频/<级别>/西班牙语分级阅读 A1-12 Mi escuela 我的学校.mp4 …（各级文件夹里原有的视频不动）
- ~/Desktop/试卷集合/西班牙语分级阅读第二批/：50 个视频（换掉之前的 A1-11 试看版）和说明
复制后逐个比对 sha256。"""
import hashlib
import shutil
import sys
from pathlib import Path
kit, notes = Path(sys.argv[1]), Path(sys.argv[2])
sys.path.insert(0, str(kit / '西班牙语' / 'tools'))
import make_video as M  # noqa: E402
H = Path.home() / 'Desktop'
V, B = H / '西语视频', H / '试卷集合' / '西班牙语分级阅读第二批'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
n = 0
for lv in ('a1', 'a2', 'b1', 'b2', 'c1'):
    for k in range(11, 21):
        p = M.load(f'{lv}_{k}')
        name = M.video_name(p)
        src = kit / '西班牙语' / '最终视频' / name
        h = sha(src)
        for d in (V / lv.upper(), B):
            d.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, d / name)
            if sha(d / name) != h:
                sys.exit(f'复制后不一致：{d / name}')
            n += 1
shutil.copyfile(notes, B / '西班牙语分级阅读第二批 说明.md')
extra = [f.name for f in B.iterdir() if f.suffix == '.mp4' and not f.name.startswith('西班牙语分级阅读 ')]
print(f'OK：复制 {n} 个视频（西语视频 50 个、试卷集合 50 个）；试卷集合文件夹现在 {len(list(B.glob("*.mp4")))} 个视频', extra)
