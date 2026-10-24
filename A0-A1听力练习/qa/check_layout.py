"""版面检查：python check_layout.py [student|teacher]（不写就两版都查）。列出可疑的地方：
空白页、页面下部空白过多（下一页不是新的一套）、题干和选项分页、选项被拆到两页、部分标题落在页尾、
“依据”和它的题目分页、西语单词被断开、数字被断开、页眉缺失、残留的标记符号。"""
import os
import re
import subprocess
import sys
from pathlib import Path

B = Path(__file__).resolve().parent.parent
PDFTOTEXT = os.environ.get('PDFTOTEXT', 'pdftotext')     # poppler 的 pdftotext
WORDS = set()
for f in (B / 'sets').glob('*.md'):
    for w in re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+", f.read_text('utf-8')):
        WORDS.add(w.lower())
TOP, BOT = 56.7, 841.9 - 56.7 - 20


def body_lines(pg):
    """一页的正文行（去掉页眉、页码），按从上到下的顺序：[(y, 文字)]。"""
    out = []
    for m in re.finditer(r'<line xMin="[\d.]+" yMin="([\d.]+)" xMax="[\d.]+" yMax="([\d.]+)">(.*?)</line>', pg, re.S):
        y0, y1 = float(m.group(1)), float(m.group(2))
        txt = ' '.join(re.findall(r'>([^<]*)</word>', m.group(3)))
        if y1 < TOP + 4 or y0 > BOT:          # 页眉、页码
            continue
        out.append((y0, y1, txt))
    out.sort()
    return out


def check(name):
    pdf = B / 'out' / f'西班牙语A0-A1听力练习_{name}.pdf'
    x = subprocess.run([PDFTOTEXT, '-bbox-layout', str(pdf), '-'], capture_output=True, text=True).stdout
    pages = x.split('<page ')[1:]
    P = [body_lines(pg) for pg in pages]
    heads = [' '.join(re.findall(r'>([^<]*)</word>', pg[:3000])) for pg in pages]
    issues = []
    stem = re.compile(r'^(\d{1,2}\.|例)\s')
    for i, lines in enumerate(P):
        n = i + 1
        if n > 1 and not lines:
            issues.append((n, '空白页', ''))
            continue
        if n > 1 and f'听力练习 · {name}' not in heads[i].replace('  ', ' ') and '听力练习' not in heads[i]:
            issues.append((n, '没有页眉', ''))
        txt = [t for _, _, t in lines]
        for t in txt:
            if re.search(r'\*\*|\{\d+\}|\{例\}|＝|^#|^> ', t):
                issues.append((n, '残留标记', t[:60]))
        if i + 1 < len(P) and P[i + 1]:
            last, first = txt[-1] if txt else '', P[i + 1][0][2]
            new_set = bool(re.search(r'第 ?\d+ ?套', ' '.join(t for _, _, t in P[i + 1][:3])))
            if stem.match(last) and re.match(r'^[A-C]\.', first):
                issues.append((n, '题干和选项分页', f'{last[:40]} / {first[:30]}'))
            if re.match(r'^[A-B]\.', last) and re.match(r'^[B-C]\.', first):
                issues.append((n, '选项分在两页', f'{last[:40]} / {first[:30]}'))
            if re.match(r'^第[一二三四]部分', last):
                issues.append((n, '部分标题在页尾', last[:40]))
            if T and re.match(r'^依据', first):
                issues.append((n + 1, '依据和题目分页', first[:40]))
            if lines:
                frac = (BOT - lines[-1][1]) / (BOT - TOP)
                if frac > 0.4 and not new_set and n > 3:
                    issues.append((n, f'页面下部空 {frac:.0%}', f'下一页开头：{first[:30]}'))
                if frac > 0.82 and new_set and n > 3:      # 一套的最后一页只有一两行
                    issues.append((n, f'一套的最后一页只排了 {1 - frac:.0%}', txt[0][:30]))
        for a, b in zip(txt, txt[1:]):
            ma, mb = re.search(r'([A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+)$', a), re.match(r'^([A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+)', b)
            if ma and mb:
                u, v = ma.group(1).lower(), mb.group(1).lower()
                if (u + v) in WORDS and (u not in WORDS or v not in WORDS) and len(u + v) > 3:
                    issues.append((n, '单词断开', f'{a[-25:]} / {b[:25]}'))
    # 数字串（电话号码、价格、日期、钟点）要在同一行里：把各套里带空格的数字串找出来，看排出来的每一行
    flat = '\n'.join(t for lines in P for _, _, t in lines)
    flat = flat.replace('\u2007', ' ').replace('\u00a0', ' ')
    nums = set()
    for f in (B / 'sets').glob('*.md'):
        nums.update(re.findall(r'\d+(?: \d+)+|\d+,\d+ €|\d+ 月 \d+ 日|\d+ (?:岁|个|本|号)', f.read_text('utf-8')))
    for s_ in sorted(nums):
        pat = re.escape(s_).replace('\\ ', r'\s+')
        whole = len(re.findall(pat, flat.replace('\n', ' ')))
        inline = len(re.findall(pat.replace(r'\s+', r'[ \t]+'), flat))
        if whole != inline:
            issues.append((0, '数字串跨行', s_))
    print(f'{name}：{len(pages)} 页，{len(issues)} 处可疑')
    for it in issues:
        print('  p%d %s %s' % it)
    return issues


if __name__ == '__main__':
    modes = sys.argv[1:] or ['student', 'teacher']
    for m in modes:
        T = m == 'teacher'
        check('学生版' if m == 'student' else '教师版')
