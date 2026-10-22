"""生词表去重：python dedupe_vocab.py [--apply]

同一个词（西语写法和词性都相同）只留在第一次收它的单元；后面单元的生词表（课文生词表和生词总表）里的重复行删去。
后面单元的词义如果和前面不同（例如 tomar 第 7 单元是“吃、喝、点菜”），中文释义不同的不删，只列出来供人工判断。
课文生词表删空的，整张表连同前面紧挨着的说明行一起换成一句“这段课文没有新的生词。”
不加 --apply 只报告不改。
"""
import re
import sys
from pathlib import Path

B = Path(__file__).resolve().parent.parent
UNITS = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
HEAD = '|西语|词性|中文|'


def norm_word(w):
    return re.sub(r'\*\*', '', w).strip().lower()


def main(apply):
    first = {}                     # (词, 词性) → (单元, 中文)
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
                if key in first and first[key][0] != u:
                    pu, pzh = first[key]
                    # 释义相近（去掉“的”和括号说明后，至少有两个相同的汉字，或一方包含另一方）算同一个词义
                    core = lambda z: set(re.sub(r'（[^）]*）|[^\u4e00-\u9fff]|的', '', z))
                    a1, a2 = core(pzh), core(c[2])
                    same = len(a1 & a2) >= 2 or (a1 and a2 and (a1 <= a2 or a2 <= a1))
                    report.append(f'{u}: {c[0]}（{c[1]}）第 {int(pu)} 单元已收' + ('' if same else f'，释义不同：「{pzh}」→「{c[2]}」，保留'))
                    if same:
                        tables[-1][2] += 1
                        continue
                first.setdefault(key, (u, c[2]))
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
