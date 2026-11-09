"""列出分级阅读第二批要提交进仓库的文件（每行一个，相对工具包根目录）：python gen_files.py <KIT> <输出 files.txt>
文章 JSON、音频 MP3 和字幕 SRT、timings.json、核查报告、改过的工具、README 和 记录/分级阅读第二批/ 下的全部文件；缺任何一个就报错。"""
import sys
from pathlib import Path
kit, out = Path(sys.argv[1]), Path(sys.argv[2])
sys.path.insert(0, str(kit / '西班牙语' / 'tools'))
import make_video as M  # noqa: E402
ES = kit / '西班牙语'
files, bad = ['README.md', '西班牙语/audio/timings.json', '西班牙语/tools/make_video.py', '西班牙语/tools/check_wraps.py',
              '西班牙语/tools/voices.json', '西班牙语/tools/asr_check_reading.py'], []
for lv in ('a1', 'a2', 'b1', 'b2', 'c1'):
    voice = 'qwen3_M1F5_25_slow' if lv in ('a1', 'a2') else 'qwen3_M1F5_25'
    for n in range(11, 21):
        pid = f'{lv}_{n}'
        files.append(f'西班牙语/文章/{pid}.json')
        for ext in ('mp3', 'srt'):
            m = sorted((ES / 'audio' / voice).glob(f'{pid}_*.{ext}'))
            if len(m) != 1:
                bad.append(f'{pid}：{voice} 里 .{ext} 有 {len(m)} 个')
            files += [str(x.relative_to(kit)) for x in m]
        files.append(f'西班牙语/最终视频/{Path(M.video_name(M.load(pid))).stem}_核查.json')
rec = kit / '记录' / '分级阅读第二批'
files += sorted(str(x.relative_to(kit)) for x in rec.rglob('*') if x.is_file())
for f in files:
    if not (kit / f).is_file():
        bad.append(f'没有这个文件：{f}')
if bad:
    sys.exit('\n'.join(bad))
out.write_text('\n'.join(files) + '\n', 'utf-8')
print(f'OK：{len(files)} 个文件（记录 {sum(1 for f in files if f.startswith("记录/"))} 个）')
