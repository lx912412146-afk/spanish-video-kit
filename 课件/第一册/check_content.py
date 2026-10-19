"""课件内容 JSON 自检：字段、数量、长度、西语标点。用法：python check_content.py L01.json [L02.json …]"""
import json
import re
import sys
from pathlib import Path


def zlen(s):
    """中文按字数、西语按字符数：全角字符算 1，半角也算 1（长度上限已按两种分别给出）。"""
    return len(s)


def check(path):
    e = []
    try:
        d = json.loads(Path(path).read_text('utf-8'))
    except Exception as x:
        return [f'JSON 读不出来：{x}']
    n = d.get('lesson')
    if not isinstance(n, int) or not 1 <= n <= 24:
        e.append('lesson 应为 1–24')
    for k in ('title_es', 'title_zh', 'goals', 'vocab', 'text', 'grammar', 'exercises', 'summary', 'homework', 'notes'):
        if k not in d:
            e.append(f'缺字段 {k}')
    if e:
        return e

    def rng(name, xs, lo, hi):
        if not lo <= len(xs) <= hi:
            e.append(f'{name} 应有 {lo}–{hi} 项，现在 {len(xs)}')

    def mx(name, s, m):
        if zlen(s) > m:
            e.append(f'{name} 太长（{zlen(s)} > {m}）：{s}')

    rng('goals', d['goals'], 3, 5)
    for s in d['goals']:
        mx('goals', s, 30)
    pr = d.get('pronunciation') or []
    if pr and n > 8:
        e.append('第 9 课以后不写 pronunciation')
    if n <= 8 and not pr:
        e.append('第 1–8 课要有 pronunciation')
    rng('pronunciation', pr, 0, 3)
    for g in pr:
        rng(f'pronunciation「{g.get("title")}」items', g.get('items', []), 2, 6)
        for it in g.get('items', []):
            mx('pronunciation tip', it.get('tip', ''), 40)
            rng(f'pronunciation「{it.get("sound")}」words', it.get('words', []), 2, 3)
    rng('vocab', d['vocab'], 10, 18)
    for es, zh in d['vocab']:
        mx('vocab 西语', es, 26)
        mx('vocab 中文', zh, 14)
    t = d['text']
    rng('text.lines', t.get('lines', []), 6, 14)
    for ln in t.get('lines', []):
        mx('text 西语', ln.get('es', ''), 70)
        if ln.get('who') not in ('A', 'B', ''):
            e.append(f'text who 只能是 A、B 或空：{ln.get("who")}')
        if not ln.get('zh'):
            e.append(f'text 缺中文：{ln.get("es")}')
    rng('grammar', d['grammar'], 2, 4)
    for g in d['grammar']:
        rng(f'grammar「{g.get("title")}」points', g.get('points', []), 2, 4)
        for p in g.get('points', []):
            mx('grammar point', p, 46)
        tb = g.get('table')
        if tb:
            if len(tb['rows']) > 7 or len(tb['head']) > 4:
                e.append(f'grammar「{g.get("title")}」表格太大')
            for r in tb['rows']:
                if len(r) != len(tb['head']):
                    e.append(f'grammar「{g.get("title")}」表格列数不一致：{r}')
                for c in r:
                    mx('表格格子', c, 22)
        rng(f'grammar「{g.get("title")}」examples', g.get('examples', []), 2, 4)
        for es, zh in g.get('examples', []):
            mx('grammar 例句', es, 60)
    rng('phrases', d.get('phrases') or [], 0, 8)
    rng('exercises', d['exercises'], 6, 8)
    for x in d['exercises']:
        mx('exercise q', x.get('q', ''), 80)
        mx('exercise a', x.get('a', ''), 70)
    rng('summary', d['summary'], 3, 5)
    for s in d['summary']:
        mx('summary', s, 34)
    rng('homework', d['homework'], 2, 4)
    for s in d['homework']:
        mx('homework', s, 40)
    # 西语问句、感叹句要有倒写符号
    def es_strings():
        yield from (w[0] for g in pr for it in g.get('items', []) for w in it.get('words', []))
        yield from (v[0] for v in d['vocab'])
        yield from (ln['es'] for ln in t.get('lines', []))
        for g in d['grammar']:
            yield from (x[0] for x in g.get('examples', []))
        yield from (x[0] for x in d.get('phrases') or [])
    for s in es_strings():
        for m in re.finditer(r'([^.!?]*)\?', s):
            if '¿' not in m.group(1) and not m.group(1).strip().startswith('…'):
                e.append(f'问句缺 ¿：{s}')
                break
        for m in re.finditer(r'([^.!?]*)!', s):
            if '¡' not in m.group(1):
                e.append(f'感叹句缺 ¡：{s}')
                break
    if any(ord(c) > 0x1F000 for c in json.dumps(d, ensure_ascii=False)):
        e.append('有表情符号')
    return e


if __name__ == '__main__':
    bad = 0
    for p in sys.argv[1:]:
        errs = check(p)
        print(('✓ ' if not errs else '✗ ') + p)
        for x in errs:
            print('   ', x)
        bad += bool(errs)
    sys.exit(1 if bad else 0)
