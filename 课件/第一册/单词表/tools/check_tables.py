"""把 conj.py 和仓库里审校过的变位表逐格比对：python check_tables.py <仓库目录>
找两种表：第一册课件 content/Lxx.json 的语法表（head 里有不定式），各教程 .md 里的 Markdown 表（表头有不定式、行首是人称）。
每一列先找最吻合的时态（现在时、简单过去时、过去未完成时、现在虚拟式、命令式），吻合 4 行以上的才比，列出对不上的格子。"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import conj  # noqa: E402

REPO = Path(sys.argv[1])
PERS_KEYS = [('yo',), ('tú',), ('él', 'ella', 'usted', 'ud'), ('nosotros', 'nosotras'), ('vosotros', 'vosotras'), ('ellos', 'ellas', 'ustedes', 'uds')]
IMP_KEYS = {'tú': 'tú', 'usted': 'usted', 'nosotros': 'nosotros', 'vosotros': 'vosotros', 'ustedes': 'ustedes'}
INF = re.compile(r'^\s*(?:\*\*)?([a-záéíóúñ]+(?:ar|er|ir|ír)(?:se)?)(?:\*\*)?\b')


def person(label):
    l = label.lower().strip('* ')
    if l.startswith('_'):
        return None
    hits = [(len(k), i) for i, ks in enumerate(PERS_KEYS) for k in ks if l.startswith(k)]
    return max(hits)[1] if hits else None


def clean(cell):
    c = re.sub(r'\*\*|<[^>]+>|`', '', cell).strip()
    c = re.split(r'[（(／/]', c)[0].strip()
    return c


def paradigms(lemma):
    try:
        r = conj.conjugate(lemma)
    except Exception as e:
        return None
    out = {k: r[k] for k in ('pres', 'pret', 'impf', 'subj')}
    im = r['imp']
    out['imp'] = ['—', im['tú'], im['usted'], im['nosotros'], im['vosotros'], im['ustedes']]
    if r['reflexive']:
        for k in ('subj',):
            out[k] = [f'{p} {x}' for p, x in zip(conj.REFL, out[k])]
    return out


def compare(src, head, rows):
    found = []
    for col, h in enumerate(head):
        if col == 0:
            continue
        m = INF.match(h.lower())
        if not m:
            continue
        lemma = m.group(1)
        P = paradigms(lemma)
        if P is None:
            continue
        cells = []
        for r in rows:
            if len(r) <= col:
                continue
            pi = person(r[0])
            if pi is None:
                continue
            v = clean(r[col])
            if v and v not in ('—', '-') and not v.startswith('_'):
                cells.append((pi, v, r[0]))
        if len(cells) < 4:
            continue
        best = max(P, key=lambda t: sum(P[t][pi] == v for pi, v, _ in cells))
        hits = sum(P[best][pi] == v for pi, v, _ in cells)
        if hits < 4:
            continue
        found.append((src, lemma, best, len(cells), [(lab, v, P[best][pi]) for pi, v, lab in cells if P[best][pi] != v]))
    return found


results = []
for f in sorted((REPO / '课件' / '第一册' / 'content').glob('L*.json')):
    j = json.loads(f.read_text('utf-8'))
    for g in j.get('grammar', []):
        t = g.get('table')
        if t:
            results += compare(f'{f.name} {g["title"]}', t['head'], t['rows'])
for f in sorted(REPO.rglob('*.md')):
    if 'node_modules' in f.parts:
        continue
    lines = f.read_text('utf-8', errors='ignore').splitlines()
    i = 0
    while i < len(lines):
        if lines[i].startswith('|') and i + 1 < len(lines) and re.match(r'^\|\s*:?-{3,}', lines[i + 1]):
            head = [c.strip() for c in lines[i].strip().strip('|').split('|')]
            rows, k = [], i + 2
            while k < len(lines) and lines[k].startswith('|'):
                rows.append([c.strip() for c in lines[k].strip().strip('|').split('|')])
                k += 1
            results += compare(f'{f.relative_to(REPO)}:{i + 1}', head, rows)
            i = k
        else:
            i += 1
cols = len(results)
bad = [r for r in results if r[4]]
print(f'比对了 {cols} 列（{sum(r[3] for r in results)} 格）；有出入的列 {len(bad)}')
for src, lemma, t, n, diffs in bad:
    print(f'  {src}  {lemma}（{t}）：' + '；'.join(f'{lab} 表里 {v}，程序 {w}' for lab, v, w in diffs))
lem = sorted({r[1] for r in results})
print('比对过的动词：', len(lem))
