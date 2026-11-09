"""按 (文章, 原文片段, 新片段) 逐条替换文章 JSON 里的文字（原文片段在文件里必须恰好出现一次），改完检查 JSON 能读：python fix.py fixes.json"""
import json, sys
from pathlib import Path
fixes = json.loads(Path(sys.argv[1]).read_text('utf-8'))
for pid, old, new in fixes:
    p = Path(f'西班牙语/文章/{pid}.json'); t = p.read_text('utf-8')
    n = t.count(old)
    if n != 1:
        sys.exit(f'{pid}：「{old}」出现 {n} 次，没有改')
    t = t.replace(old, new); json.loads(t); p.write_text(t, 'utf-8')
    print(f'{pid} ✓ {old[:30]} → {new[:30]}')
