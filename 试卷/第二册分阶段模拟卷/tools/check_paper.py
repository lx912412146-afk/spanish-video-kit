"""《现代西班牙语》第二册分阶段高考模拟卷：格式和前后一致自检（沿用 Método 1–2 高考模拟卷的 check_paper.py）。

    python check_paper.py 试卷.md

查：二级标题顺序；题号和选项；完形填空空格和选项表；语法填空空格和提示词（恰好 5 空给提示词，位置不限）；
答案表和逐题依据表的字母一致；完形答案和选项表对得上；答案分布；听力原文（Texto 1–9、男女交替）；
写作词数要求和范文实际词数；西语标点（¿? ¡! 成对）。只查格式和前后一致，题目本身要人审。
有问题就列出来，退出码 1。
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
    ans, nums = {}, None
    for line in text.splitlines():
        cells = [c.strip().strip('*') for c in line.strip().strip('|').split('|')]
        if cells and cells[0] and all(re.fullmatch(r'\d{1,2}', c) for c in cells if c):
            nums = [int(c) for c in cells]
        elif nums and all(re.fullmatch(r'[A-D]', c) for c in cells) and len(cells) == len(nums):
            ans.update({n: c for n, c in zip(nums, cells) if lo <= n <= hi})
            nums = None
    return ans


def detail_rows(text):
    """三栏表「题号 | 答案 | 依据或考点」：{题号: (答案栏, 第三栏)}。"""
    rows = {}
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cells) == 3 and re.fullmatch(r'\d{1,2}', cells[0]):
            rows[int(cells[0])] = (cells[1], cells[2])
    return rows


def words(t):
    return len(re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+(?:[-'][A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+)*", t))


def punct(text, where, e):
    """¿…? ¡…! 成对；问号、感叹号前没有空格。"""
    for line in text.splitlines():
        s = re.sub(r'\(.*?\)|（.*?）', '', line)
        if not re.search(r'[A-Za-zÁÉÍÓÚáéíóúñÑ]', s):
            continue
        if s.count('¿') != s.count('?') or s.count('¡') != s.count('!'):
            e(f'{where}：¿? 或 ¡! 不成对：{line.strip()[:80]}')
        if re.search(r'[a-záéíóúñ] [?!]', s):
            e(f'{where}：问号、感叹号前有空格：{line.strip()[:80]}')


def check(path):
    md = Path(path).read_text('utf-8')
    errs, notes = [], []
    e = errs.append
    if not re.match(r'# .+\n\n\d{4}-\d{2}-\d{2}\n', md):
        e('开头要是「# 标题」、空行、日期')
    heads = re.findall(r'(?m)^## (.+)$', md)
    got = [next((s for s in SECTIONS if h.startswith(s)), None) for h in heads]
    if got != SECTIONS:
        e(f'二级标题顺序不对：{heads}')

    lis, rea, use = sec(md, '第一部分　听力'), sec(md, '第二部分　阅读'), sec(md, '第三部分　语言运用')
    key, script, wr = sec(md, '参考答案与评分标准（教师用）'), sec(md, '听力原文'), sec(md, '第四部分　写作')
    ql, qr = questions(lis), questions(rea)
    if sorted(ql) != list(range(1, 21)):
        e(f'听力题号应为 1–20：{sorted(ql)}')
    for n, (stem, opts) in ql.items():
        if [o[0] for o in opts] != list('ABC'):
            e(f'听力第 {n} 题选项应为 A、B、C')
        if len({o[1] for o in opts}) != len(opts):
            e(f'听力第 {n} 题有重复选项')
    for k, (a, b) in LISTEN_GROUPS.items():
        if f'听第 {k} 段录音，回答第 {a} 至 {b} 题。' not in lis:
            e(f'缺「听第 {k} 段录音，回答第 {a} 至 {b} 题。」')
    if sorted(qr) != list(range(21, 41)):
        e(f'阅读题号应为 21–40：{sorted(qr)}')
    for n, (stem, opts) in qr.items():
        if [o[0] for o in opts] != list('ABCD'):
            e(f'阅读第 {n} 题选项应为 A–D')
        if len({o[1] for o in opts}) != len(opts):
            e(f'阅读第 {n} 题有重复选项')
    if re.findall(r'(?m)^### ([A-D])$', rea) != list('ABCD'):
        e('阅读应有 A–D 四篇')
    for p, body in zip('ABCD', re.split(r'(?m)^### [A-D]$', rea)[1:]):
        qs = sorted(questions(body))
        if len(qs) != 5:
            e(f'阅读 {p} 篇有 {len(qs)} 题')
        text = '\n'.join(l for l in body.splitlines() if not re.match(r'^(\d{1,2}\.| {3,4}- )', l))
        notes.append(f'阅读 {p} 篇短文 {words(text)} 词')

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
    ctext = '\n'.join(l for l in cloze.splitlines() if not l.startswith('|') and not l.startswith('**') and not l.startswith('阅读'))
    notes.append(f'完形填空短文 {words(re.sub(r"[0-9_]", "", ctext))} 词（不算空格）')
    gram = use.split('**第二节**')[1] if '**第二节**' in use else ''
    gb = re.findall(r'\\_\\_(\d{2})\\_\\_( \(([^)]+)\))?', gram)
    if [int(b[0]) for b in gb] != list(range(61, 71)):
        e(f'语法填空空格应为 61–70：{[b[0] for b in gb]}')
    if len([b for b in gb if b[1]]) != 5:
        e(f'语法填空应恰好 5 空给提示词：{[int(b[0]) for b in gb if b[1]]}')
    gtext = '\n'.join(l for l in gram.splitlines() if not l.startswith('阅读') and not l.startswith('（'))
    gwords = words(re.sub(r'[0-9_]|\([a-z]+\)', '', gtext))
    notes.append(f'语法填空短文 {gwords} 词（不算空格和提示词）')

    al, ar = letter_table(key, 1, 20), letter_table(key, 21, 40)
    ac = letter_table(key, 41, 60)
    if sorted(al) != list(range(1, 21)):
        e(f'听力答案表不全：{sorted(al)}')
    if sorted(ar) != list(range(21, 41)):
        e(f'阅读答案表不全：{sorted(ar)}')
    if sorted(ac) != list(range(41, 61)):
        e(f'完形答案表不全：{sorted(ac)}')
    rows = detail_rows(key)
    for n in range(1, 61):
        if n not in rows:
            e(f'第 {n} 题没有依据或考点')
            continue
        a = rows[n][0].split()[0]
        want = al.get(n) or ar.get(n) or ac.get(n)
        if a != want:
            e(f'第 {n} 题：依据表写 {a}，答案表是 {want}')
        if 41 <= n <= 60:
            m = re.match(r'([A-D]) (.+)$', rows[n][0])
            if not m or opts.get(n, ['?'] * 4)['ABCD'.index(m.group(1))] != m.group(2):
                e(f'完形第 {n} 题答案「{rows[n][0]}」和选项表对不上')
    for n in range(61, 71):
        if n not in rows:
            e(f'语法填空第 {n} 题没有答案')
        elif len(re.sub(r'（.*?）', '', rows[n][0]).split()) != 1:
            e(f'语法填空第 {n} 题答案应为 1 个词：{rows[n][0]}')
    for n in list(al) + list(ar):
        q = (ql if n <= 20 else qr).get(n)
        if q and len(q[1]) and (al.get(n) or ar.get(n)) not in [o[0] for o in q[1]]:
            e(f'第 {n} 题答案不在选项里')

    for name, ans, letters in (('听力', al, 'ABC'), ('阅读', ar, 'ABCD'), ('完形', ac, 'ABCD')):
        c = Counter(ans.values())
        notes.append(f'{name}答案分布：{dict(sorted(c.items()))}')
        lo = len(ans) / len(letters)
        if ans and (min(c.get(x, 0) for x in letters) < lo * 0.6 or max(c.values()) > lo * 1.5):
            e(f'{name}答案分布太偏：{dict(sorted(c.items()))}')
        run = max((len(m.group()) for m in re.finditer(r'(.)\1*', ''.join(ans[k] for k in sorted(ans)))), default=0)
        if run > 3:
            e(f'{name}答案连续 {run} 题相同')

    texts = re.split(r'(?m)^\*\*Texto (\d+)\*\*$', script)
    nums = [int(x) for x in texts[1::2]]
    if nums != list(range(1, 10)):
        e(f'听力原文应有 Texto 1–9：{nums}')
    for k, body in zip(nums, texts[2::2]):
        lines = re.findall(r'(?m)^(?:- )?([男女])：(.+)$', body)
        if not lines:
            e(f'Texto {k} 没有台词行')
        spk = [x[0] for x in lines]
        if any(a == b for a, b in zip(spk, spk[1:])):
            e(f'Texto {k} 有同一人连续两行')
        for _, s in lines:
            if re.search(r'\d|[()"“”]|Sr\.|Sra\.|[一-鿿]', s):
                e(f'Texto {k} 台词里有数字、括号、引号、缩写或中文：{s[:60]}')
        notes.append(f'Texto {k}：{len(lines)} 行，{sum(words(s) for _, s in lines)} 词')

    lim = [tuple(map(int, x)) for x in re.findall(r'词数 (\d+)～(\d+) 个', wr)]
    if len(lim) != 2:
        e(f'写作两节都要写「词数 X～Y 个」：{lim}')
    for i, label in enumerate(('第一节', '第二节')):
        m = re.search(rf'\*\*{label}范文\*\*（([^）]*)）\n\n((?:>.*\n?)+)', key)
        if not m:
            e(f'缺{label}范文')
            continue
        lines = [l[1:].strip() for l in m.group(2).splitlines()]
        body = [l for l in lines if l and not l.startswith('**')]
        n = words(' '.join(body))
        if i == 0:
            inner = words(' '.join(body[1:-2]))
            want = f'{n} 词，含称呼、结尾语和署名；正文 {inner} 词'
        else:
            want = f'正文 {n} 词'
        if m.group(1) != want:
            e(f'{label}范文标注「{m.group(1)}」，应为「{want}」')
        if lim and not (lim[i][0] <= n <= lim[i][1]):
            e(f'{label}范文 {n} 词，不在 {lim[i][0]}～{lim[i][1]}')

    for name, text in (('听力题', lis), ('阅读', rea), ('语言运用', use), ('听力原文', script)):
        punct(text, name, e)
    for m in re.finditer(r'[^\s(（]\(|\)[A-Za-zÁÉÍÓÚáéíóú]', rea + use):
        e(f'括号前后少空格：…{(rea + use)[max(0, m.start() - 15):m.end() + 5]}…')
    return errs, notes


if __name__ == '__main__':
    bad = False
    for p in sys.argv[1:]:
        errs, notes = check(p)
        for n in notes:
            print('·', n)
        for x in errs:
            print('✗', x)
        bad |= bool(errs)
        print('✓ 格式自检通过' if not errs else f'✗ {len(errs)} 处问题')
    sys.exit(1 if bad else 0)
