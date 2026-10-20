# 检查白皮书章节文件的标记：python lint.py chapters/xx.md …
import re, sys

def lint(path):
    errs = []
    lines = open(path, encoding='utf-8').read().split('\n')
    h2 = [i for i, l in enumerate(lines) if l.startswith('## ')]
    first = next((i for i, l in enumerate(lines) if l.strip()), None)
    if first is None or not lines[first].startswith('## '):
        errs.append('第一行必须是 ## 章标题')
    if len(h2) != 1:
        errs.append(f'应该只有一个 ## 章标题，现在有 {len(h2)} 个')
    ncols = None
    zh = 0
    for i, l in enumerate(lines, 1):
        t = l.strip()
        if not t:
            ncols = None; continue
        zh += len(re.findall(r'[一-鿿]', t))
        if t.startswith('#'):
            if not re.match(r'^#{2,4} \S', t): errs.append(f'{i}: 标题只能用 ##、###、####，# 后要有空格')
            if re.match(r'^#{2,4} (第.+[章节]|\d+[.、])', t): errs.append(f'{i}: 标题里不要写编号')
            ncols = None; continue
        if t.startswith('|'):
            if re.match(r'^\|[\s:|-]+\|$', t): continue
            if not t.endswith('|'): errs.append(f'{i}: 表格行要以 | 结尾')
            n = len(t.strip('|').split('|'))
            if ncols is None: ncols = n
            elif n != ncols: errs.append(f'{i}: 表格这一行 {n} 列，表头 {ncols} 列')
            if n > 5: errs.append(f'{i}: 表格超过 5 列')
            continue
        ncols = None
        if t.startswith('> '):
            if '｜' not in t: errs.append(f'{i}: 例句行要用全角“｜”分隔西语和中文')
            continue
        if re.match(r'^\d+[.、)] ', t): errs.append(f'{i}: 不要用数字列表')
        if '`' in t or '<' in t and re.search(r'<[a-zA-Z/]', t): errs.append(f'{i}: 不要用代码或 HTML')
        if re.search(r'\[[^\]]+\]\(', t): errs.append(f'{i}: 不要用链接')
        if t.count('**') % 2: errs.append(f'{i}: ** 没有成对')
        if re.search(r'(?<![*\w])_[^_]+_(?![\w])', t) and '__' not in t: errs.append(f'{i}: 不要用下划线斜体')
        if re.match(r'^>\S', t): errs.append(f'{i}: 例句行 > 后要有空格')
    return errs, zh

ok = True
for p in sys.argv[1:]:
    errs, zh = lint(p)
    if errs:
        ok = False
        print(f'✗ {p}')
        for e in errs[:40]: print('   ', e)
    else:
        print(f'✓ {p}（约 {zh} 个汉字，含表格和例句）')
sys.exit(0 if ok else 1)
