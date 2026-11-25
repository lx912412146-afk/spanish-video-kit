"""录音做好后，把试卷里“全长约 16 分钟”改成实际时长：python patch_duration.py 试卷.md 听力_时间轴.json"""
import json
import re
import sys
from pathlib import Path

p = Path(sys.argv[1])
total = json.loads(Path(sys.argv[2]).read_text('utf-8'))['total_s']
mins = int(total / 60 + 0.5)
md = p.read_text('utf-8')
new, n = re.subn(r'全长约 \d+ 分钟', f'全长约 {mins} 分钟', md)
if n != 2:
    raise SystemExit(f'“全长约 N 分钟”应出现 2 处，找到 {n} 处')
p.write_text(new, 'utf-8')
print(f'{p.parent.name}：{total / 60:.2f} 分钟 → 全长约 {mins} 分钟')
