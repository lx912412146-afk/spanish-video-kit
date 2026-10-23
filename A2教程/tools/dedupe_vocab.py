"""生词表去重：python dedupe_vocab.py [--apply]

同一个词（西语写法和词性都相同）只留在第一次收它的单元（A1 教程已收的算在 A1）；后面单元的生词表（课文生词表和生词总表）里的重复行删去。
后面单元的词义如果和前面不同（例如 tomar 第 7 单元是“吃、喝、点菜”），中文释义不同的不删，只列出来供人工判断；释义里注明了“新义项”的一律保留。
课文生词表删空的，整张表连同前面紧挨着的说明行一起换成一句“这段课文没有新的生词。”
不加 --apply 只报告不改。
"""
import re
import sys
from pathlib import Path

B = Path(__file__).resolve().parent.parent
UNITS = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10']
A1 = B.parent / 'A1教程'                  # A1 教程在 A2 旁边（仓库里就是这样放的）
A1_UNITS = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
HEAD = '|西语|词性|中文|'


def norm_word(w):
    return re.sub(r'\*\*', '', w).strip().lower()


def a1_rows():
    """A1 教程各单元生词表里的词：{(词, 词性): [('A1', 中文), …]}"""
    rows = {}
    for u in A1_UNITS:
        inside = False
        for raw in (A1 / 'student' / f'u{u}.md').read_text('utf-8').split('\n'):
            t = raw.strip()
            if t.replace(' ', '') == HEAD:
                inside = True
                continue
            if inside and t.startswith('|'):
                if not re.match(r'^\|[\s:|-]+\|$', t):
                    c = [x.strip() for x in t.strip('|').split('|')]
                    rows.setdefault((norm_word(c[0]), c[1]), []).append(('A1', c[2]))
            else:
                inside = False
    return rows


def main(apply):
    first = a1_rows()              # (词, 词性) → [(单元, 中文), …]（一个词可以有几个义项）；A1 已收的记作 'A1'
    report = []
    for u in UNITS:
        f = B / 'student' / f'u{u}.md'
        lines = f.read_text('utf-8').split('\n')
        out, inside, seen_here = [], False, set()
        tables = []                # [(表头行号, [保留的行], 删去的行数)]
        for i, raw in enumerate(lines):
            t = raw.strip()
            if t.replace(' ', '') == HEAD:
                inside = True
                tables.append([len(out), 0, 0])
                out.append(raw)
                continue
            if inside and t.startswith('|'):
                if re.match(r'^\|[\s:|-]+\|$', t):
                    out.append(raw)
                    continue
                c = [x.strip() for x in t.strip('|').split('|')]
                key = (norm_word(c[0]), c[1])
                prev = [(pu, pzh) for pu, pzh in first.get(key, []) if pu != u]
                if prev:
                    # 释义相近（去掉“的”和括号说明后，至少有两个相同的汉字，或一方包含另一方）算同一个词义；和前面任何一个义项相近都算重复
                    core = lambda z: set(re.sub(r'（[^）]*）|[^\u4e00-\u9fff]|的', '', z))
                    def same(z1, z2):
                        a1, a2 = core(z1), core(z2)
                        return len(a1 & a2) >= 2 or bool(a1 and a2 and (a1 <= a2 or a2 <= a1))
                    # 编辑已经在释义里注明“新义项”的，按人的判断保留，不再删
                    match = None if '新义项' in c[2] else next(((pu, pzh) for pu, pzh in prev if same(pzh, c[2])), None)
                    pu, pzh = match or prev[-1]
                    where = 'A1 教程' if pu == 'A1' else f'第 {int(pu)} 单元'
                    report.append(f'{u}: {c[0]}（{c[1]}）{where}已收' + ('' if match else f'，释义不同：「{pzh}」→「{c[2]}」，保留'))
                    if match:
                        tables[-1][2] += 1
                        continue
                if (u, c[2]) not in first.get(key, []):
                    first.setdefault(key, []).append((u, c[2]))
                tables[-1][1] += 1
                out.append(raw)
                continue
            inside = False
            out.append(raw)
        # 删空的表：表头、分隔行都去掉，换成一句话
        for start, kept, dropped in reversed(tables):
            if kept == 0 and dropped:
                del out[start:start + 2]
                out.insert(start, '这段课文没有新的生词。')
                report.append(f'{u}: 有一张生词表删空了，换成了一句话（第 {start + 1} 行附近）')
        if apply:
            f.write_text('\n'.join(out), 'utf-8')
    print('\n'.join(report))
    print(f'共 {sum(1 for r in report if "已收" in r and "保留" not in r)} 行重复' + ('，已删去' if apply else '（没有改文件，加 --apply 才改）'))


if __name__ == '__main__':
    main('--apply' in sys.argv)
