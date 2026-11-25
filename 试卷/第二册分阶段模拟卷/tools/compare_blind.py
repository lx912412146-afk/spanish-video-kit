"""把盲做答案和试卷的答案表逐题对：python compare_blind.py 试卷.md 盲做答案.json

盲做答案：{"1": "B", …, "61": "llegué", …, "疑问": {"题号": "原因"}}。语法填空按评分说明里列出的写法都算对
（第三栏里写“也给分”的词），大小写、首尾标点不计。
"""
import json
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from check_paper import detail_rows, letter_table, sec  # noqa: E402

md = Path(sys.argv[1]).read_text('utf-8')
ans = json.loads(Path(sys.argv[2]).read_text('utf-8'))
key = sec(md, '参考答案与评分标准（教师用）')
letters = {**letter_table(key, 1, 20), **letter_table(key, 21, 40), **letter_table(key, 41, 60)}
rows = detail_rows(key)


def norm(s):
    return unicodedata.normalize('NFC', s).strip().strip('.,;:!¡?¿«»"').lower()


bad = []
for n in range(1, 71):
    got = str(ans.get(str(n), '')).strip()
    if n <= 60:
        want = letters.get(n)
        if got.upper()[:1] != want:
            bad.append((n, got, want))
    else:
        main = re.sub(r'（.*?）', '', rows[n][0]).strip()
        ok = {norm(main)} | {norm(w) for w in re.findall(r'写成?\s*([A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+)[^，；。]*?也给分', rows[n][1])}
        if norm(got) not in ok:
            bad.append((n, got, main))
print(f'盲做和答案表一致：{70 - len(bad)}/70')
for n, got, want in bad:
    print(f'  第 {n} 题：盲做 {got or "（空）"}，答案表 {want}')
for n, why in (ans.get('疑问') or {}).items():
    print(f'  疑问 第 {n} 题：{why}')
