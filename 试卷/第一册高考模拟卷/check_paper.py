"""试卷格式自检：题号、选项个数、答案表、完形填空答案和选项是否对得上、语法填空的提示词、听力原文、范文词数。

    python check_paper.py 试卷.md [试卷2.md …]

只查格式和前后一致，不判断题目本身对不对（那要人看）。有问题就列出来，退出码 1。
"""
import re
import sys
from collections import Counter
from pathlib import Path

SECTIONS = ['考试说明（教师用）', '注意事项', '第一部分　听力', '第二部分　阅读', '第三部分　语言运用', '第四部分　写作',
            '参考答案与评分标准（教师用）', '听力原文', '知识点覆盖表（教师用）']
LISTEN_GROUPS = {6: (6, 8), 7: (9, 12), 8: (13, 16), 9: (17, 20)}


def sec(md, name):
    m = re.search(rf'(?m)^## {re.escape(name)}.*$', md)
    if not m:
        return ''
    nxt = re.search(r'(?m)^## ', md[m.end():])
    return md[m.end(): m.end() + nxt.start()] if nxt else md[m.end():]


def questions(text):
    """{题号: (题干, [(字母, 选项), …])}"""
    out, cur = {}, None
    for line in text.splitlines():
        m = re.match(r'^(\d{1,2})\. (.+)$', line)
        if m:
            cur = int(m.group(1))
            out[cur] = (m.group(2).strip(), [])
            continue
        m = re.match(r'^ {3,4}- ([A-D])\. (.+)$', line)
        if m and cur is not None:
            out[cur][1].append((m.group(1), m.group(2).strip()))
    return out


def letter_table(text, lo, hi):
    """答案表（题号行 + 字母行交替）里 lo–hi 题的答案。"""
    ans, nums = {}, None
    for line in text.splitlines():
        cells = [c.strip().strip('*') for c in line.strip().strip('|').split('|')]
        if all(re.fullmatch(r'\d{1,2}', c) for c in cells if c) and cells and cells[0]:
            nums = [int(c) for c in cells]
        elif nums and all(re.fullmatch(r'[A-D]', c) for c in cells) and len(cells) == len(nums):
            ans.update({n: c for n, c in zip(nums, cells) if lo <= n <= hi})
            nums = None
    return ans


def words(t):
    return len(re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+(?:[-'][A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+)*", t))


def check(path):
    md = Path(path).read_text('utf-8')
    errs, notes = [], []
    e = errs.append
    if not re.match(r'# .+\n\n\d{4}-\d{2}-\d{2}\n', md):
        e('开头要是「# 标题」、空行、日期')
    heads = re.findall(r'(?m)^## (.+)$', md)
    got = [next((s for s in SECTIONS if h.startswith(s)), None) for h in heads]
    if [g for g in got if g] != SECTIONS:
        e(f'二级标题顺序不对：{heads}')
    if None in got:
        e(f'多出的二级标题：{[h for h, g in zip(heads, got) if not g]}')

    lis, rea, use = sec(md, '第一部分　听力'), sec(md, '第二部分　阅读'), sec(md, '第三部分　语言运用')
    key, script = sec(md, '参考答案与评分标准（教师用）'), sec(md, '听力原文')
    ql, qr = questions(lis), questions(rea)
    if sorted(ql) != list(range(1, 21)):
        e(f'听力题号应为 1–20：{sorted(ql)}')
    for n, (stem, opts) in ql.items():
        if [o[0] for o in opts] != list('ABC'):
            e(f'听力第 {n} 题选项应为 A、B、C：{[o[0] for o in opts]}')
        if len({o[1] for o in opts}) != len(opts):
            e(f'听力第 {n} 题有重复选项')
    for k, (a, b) in LISTEN_GROUPS.items():
        if f'听第 {k} 段录音，回答第 {a} 至 {b} 题。' not in lis:
            e(f'缺「听第 {k} 段录音，回答第 {a} 至 {b} 题。」')
    if sorted(qr) != list(range(21, 41)):
        e(f'阅读题号应为 21–40：{sorted(qr)}')
    for n, (stem, opts) in qr.items():
        if [o[0] for o in opts] != list('ABCD'):
            e(f'阅读第 {n} 题选项应为 A–D：{[o[0] for o in opts]}')
        if len({o[1] for o in opts}) != len(opts):
            e(f'阅读第 {n} 题有重复选项')
    passages = re.findall(r'(?m)^### ([A-D])$', rea)
    if passages != list('ABCD'):
        e(f'阅读应有 A–D 四篇：{passages}')
    for p, body in zip('ABCD', re.split(r'(?m)^### [A-D]$', rea)[1:]):
        qs = sorted(questions(body))
        if len(qs) != 5:
            notes.append(f'阅读 {p} 篇有 {len(qs)} 题（{qs}）')

    # 完形填空
    cloze = use.split('**第二节**')[0]
    blanks = [int(x) for x in re.findall(r'\\_\\_(\d{2})\\_\\_', cloze)]
    if blanks != list(range(41, 61)):
        e(f'完形填空空格应为 41–60 各一次、按顺序：{blanks}')
    opts = {}
    for line in cloze.splitlines():
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cells) == 5 and re.fullmatch(r'\d{2}', cells[0]):
            opts[int(cells[0])] = cells[1:]
    if sorted(opts) != list(range(41, 61)):
        e(f'完形填空选项表应有 41–60：{sorted(opts)}')
    for n, o in opts.items():
        if len(set(o)) != 4 or not all(o):
            e(f'完形填空第 {n} 题选项重复或为空：{o}')
    # 语法填空
    gram = use.split('**第二节**')[1] if '**第二节**' in use else ''
    gb = re.findall(r'\\_\\_(\d{2})\\_\\_( \(([^)]+)\))?', gram)
    if [int(b[0]) for b in gb] != list(range(61, 71)):
        e(f'语法填空空格应为 61–70 各一次、按顺序：{[b[0] for b in gb]}')
    hinted = [int(b[0]) for b in gb if b[1]]
    if len(hinted) != 5:
        e(f'语法填空应有 5 空给提示词，现在 {len(hinted)} 空：{hinted}')

    # 答案
    al, ar = letter_table(key, 1, 20), letter_table(key, 21, 40)
    if sorted(al) != list(range(1, 21)):
        e(f'听力答案表不全：{sorted(al)}')
    if sorted(ar) != list(range(21, 41)):
        e(f'阅读答案表不全：{sorted(ar)}')
    for n, a in al.items():
        if a not in 'ABC':
            e(f'听力第 {n} 题答案 {a} 不在 A–C')
    ck, gk = {}, {}
    for line in key.splitlines():
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cells) == 3 and re.fullmatch(r'\d{2}', cells[0]):
            n = int(cells[0])
            if 41 <= n <= 60:
                m = re.match(r'([A-D]) (.+)$', cells[1])
                if not m:
                    e(f'完形填空第 {n} 题答案格式应为「字母 单词」：{cells[1]}')
                    continue
                ck[n] = m.groups()
                if n in opts and opts[n]['ABCD'.index(m.group(1))] != m.group(2):
                    e(f'完形填空第 {n} 题答案 {m.group(1)} {m.group(2)} 和选项表的 {opts[n]["ABCD".index(m.group(1))]} 对不上')
            elif 61 <= n <= 70:
                gk[n] = cells[1]
    if sorted(ck) != list(range(41, 61)):
        e(f'完形填空答案不全：{sorted(ck)}')
    if sorted(gk) != list(range(61, 71)):
        e(f'语法填空答案不全：{sorted(gk)}')
    for n, w in gk.items():
        if len(w.split()) != 1:
            e(f'语法填空第 {n} 题答案应为 1 个词：{w}')

    # 答案分布
    for name, ans, letters in (('听力', al, 'ABC'), ('阅读', ar, 'ABCD'), ('完形', {n: v[0] for n, v in ck.items()}, 'ABCD')):
        c = Counter(ans.values())
        lo = len(ans) / len(letters)
        if ans and (min(c.get(x, 0) for x in letters) < lo * 0.6 or max(c.values()) > lo * 1.5):
            e(f'{name}答案分布太偏：{dict(sorted(c.items()))}')
        runs = max((len(m.group()) for m in re.finditer(r'(.)\1*', ''.join(ans[k] for k in sorted(ans)))), default=0)
        if runs > 3:
            e(f'{name}答案连续 {runs} 题相同')

    # 听力原文
    texts = re.split(r'(?m)^\*\*Texto (\d+)\*\*$', script)
    nums = [int(x) for x in texts[1::2]]
    if nums != list(range(1, 10)):
        e(f'听力原文应有 Texto 1–9：{nums}')
    for k, body in zip(nums, texts[2::2]):
        lines = re.findall(r'(?m)^(?:- )?([男女])：(.+)$', body)
        if not lines:
            e(f'Texto {k} 没有「- 男：」「- 女：」台词行')
        if k <= 5 and len(lines) < 2:
            e(f'Texto {k} 应是对话')

    # 写作要求和范文词数
    wr = sec(md, '第四部分　写作')
    lim = [tuple(map(int, x)) for x in re.findall(r'词数 (\d+)～(\d+) 个', wr)]
    if len(lim) != 2:
        e(f'写作两节都要写「词数 X～Y 个」：{lim}')
    for i, label in enumerate(('第一节', '第二节')):
        m = re.search(rf'\*\*{label}范文\*\*（[^）]*）\n\n((?:>.*\n?)+)', key)
        if not m:
            e(f'缺{label}范文')
            continue
        lines = [l[1:].strip() for l in m.group(1).splitlines()]
        body = [l for l in lines if l and not l.startswith('**')]
        if i == 0:
            n = words(' '.join(body))
            stated = re.search(r'（(\d+) 词', key[m.start():m.start() + 80])
        else:
            n = words(' '.join(body))
            stated = re.search(r'正文 (\d+) 词', key[m.start():m.start() + 80])
        if lim and len(lim) == 2 and not (lim[i][0] <= n <= lim[i][1]):
            e(f'{label}范文 {n} 词，不在 {lim[i][0]}～{lim[i][1]}')
        if stated and int(stated.group(1)) != n:
            e(f'{label}范文标注 {stated.group(1)} 词，实际数出 {n} 词')
    return errs, notes


def main():
    bad = 0
    for p in sys.argv[1:]:
        errs, notes = check(p)
        print(f'{"✓" if not errs else "✗"} {p}')
        for x in errs:
            print('   ✗', x)
        for x in notes:
            print('   ·', x)
        bad += bool(errs)
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
