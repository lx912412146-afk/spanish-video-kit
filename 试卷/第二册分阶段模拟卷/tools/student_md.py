"""盲做用的学生版：只留注意事项、四部分试题和听力原文（没有答案、依据、考试说明和覆盖表）。

    python student_md.py 试卷.md > 盲做.md
"""
import re
import sys
from pathlib import Path

md = Path(sys.argv[1]).read_text('utf-8')
parts = re.split(r'(?m)^(?=## )', md)
keep = [p for p in parts[1:] if re.match(r'## (注意事项|第[一二三四]部分|听力原文)', p)]
print(parts[0].split('\n')[0] + '\n\n' + ''.join(keep))
