"""把 conj.py 和仓库里审校过的变位表逐格比对：python check_tables.py <仓库目录>
找两种表：第一、二、三册课件 content/Lxx.json 的语法表（head 里有不定式），各教程 .md 里的 Markdown 表（表头有不定式、行首是人称）。
每一列先找最吻合的时态（现在时、简单过去时、过去未完成时、将来未完成时、简单条件式、虚拟式现在时、虚拟式过去未完成时 -ra / -se、命令式），吻合 4 行以上的才比，
列出对不上的格子。haber 按助动词比（he, has, ha…）。"""
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
        r = conj.conjugate(lemma, aux=(lemma == 'haber'))
    except Exception as e:
        return None
    out = {k: r[k] for k in ('pres', 'pret', 'impf', 'fut', 'cond', 'subj', 'sra', 'sse')}
    im = r['imp']
    out['imp'] = ['—', im['tú'], im['usted'], im['nosotros'], im['vosotros'], im['ustedes']]
    ng = r['neg']
    out['neg'] = ['—', ng['tú'], ng['usted'], ng['nosotros'], ng['vosotros'], ng['ustedes']]
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
for f in [g for b in ('第一册', '第二册', '第三册') for g in sorted((REPO / '课件' / b / 'content').glob('L*.json'))]:
    j = json.loads(f.read_text('utf-8'))
    for g in j.get('grammar', []):
        t = g.get('table')
        if t:
            results += compare(f'{f.parent.parent.name} {f.name} {g["title"]}', t['head'], t['rows'])
# 第三册复合时态的表（第 9 课 hubiera 式 / hubiese 式 / 复合条件式，第 13、15、18 课 habré terminado、haya leído）：表头不是不定式，
# 每格第一个词是助动词 haber 的形式，按 haber 比
HP = paradigms('haber')
for f in sorted((REPO / '课件' / '第三册' / 'content').glob('L*.json')):
    j = json.loads(f.read_text('utf-8'))
    for g in j.get('grammar', []):
        t = g.get('table')
        if not t or t['head'][0] != '人称':
            continue
        for col, h in enumerate(t['head']):
            if col == 0 or INF.match(h.lower()) and not h.lower().startswith('haber'):
                continue
            cells = [(person(r[0]), clean(r[col]).split()[0], r[0]) for r in t['rows'] if len(r) > col and clean(r[col])]
            cells = [c for c in cells if c[0] is not None]
            if len(cells) < 4 or h.lower().startswith('haber'):
                continue                                    # haber（将来时）这类表头上面已经按不定式比过
            best = max(HP, key=lambda k: sum(HP[k][pi] == v for pi, v, _ in cells))
            if sum(HP[best][pi] == v for pi, v, _ in cells) < 4:
                continue
            results.append((f'{f.parent.parent.name} {f.name} {g["title"]}（{h}）', 'haber', best, len(cells),
                            [(lab, v, HP[best][pi]) for pi, v, lab in cells if HP[best][pi] != v]))
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
# 每行一个动词的表（第二册第 3 课 hacer (hago) | no hagas | no haga…，第 7 课 poder, saber | podr-, sabr- | podré, sabré，第 13 课分词表）：
# 每格的形式要是它左边那格的动词的某个形式（个数相同就一一对应）
ROW_INF = re.compile(r'^(?:[a-záéíóúñ]+(?:ar|er|ir|ír)|ir)(?:se)?$')


def all_forms(lemma):
    r = conj.conjugate(lemma, aux=(lemma == 'haber'))
    b = conj.base_conj(lemma[:-2] if r['reflexive'] else lemma)
    out = {x for k in ('pres', 'pret', 'impf', 'fut', 'cond', 'subj', 'sra', 'sse') for x in r[k] + b[k]}
    out |= set(r['imp'].values()) | set(r['neg'].values()) | set(b['imp'].values()) | {r['ger'], r['part'], lemma}
    out |= {f'no {x}' for x in b['subj']}
    return out


row_checked, row_bad = 0, []
for f in [g for b in ('第二册', '第三册') for g in sorted((REPO / '课件' / b / 'content').glob('L*.json'))]:
    j = json.loads(f.read_text('utf-8'))
    for g in j.get('grammar', []):
        t = g.get('table')
        if not t:
            continue
        for r in t['rows']:
            cur = None
            for c in r:
                toks = [clean(x).lower() for x in re.split(r',\s*|\s*/\s*', re.sub(r'\([^)]*\)', '', c)) if x.strip()]
                if toks and all(ROW_INF.match(x) for x in toks):
                    cur = toks
                    continue
                if not cur or any(x.endswith('-') for x in toks) or not toks:
                    continue
                pairs = list(zip(cur, toks)) if len(cur) == len(toks) else [(None, x) for x in toks]
                for v, x in pairs:
                    if not re.fullmatch(r'(no )?[a-záéíóúñü]+', x):
                        continue
                    row_checked += 1
                    cands = [v] if v else cur
                    if not any(x in all_forms(w) for w in cands):
                        row_bad.append(f'{f.parent.parent.name} {f.name} {g["title"]}：{"/".join(cands)} 的「{x}」程序里没有')
print(f'按行比对：{row_checked} 个形式，对不上 {len(row_bad)} 个')
for b in row_bad:
    print('  ' + b)

cols = len(results)
bad = [r for r in results if r[4]]
print(f'比对了 {cols} 列（{sum(r[3] for r in results)} 格）；有出入的列 {len(bad)}')
for src, lemma, t, n, diffs in bad:
    print(f'  {src}  {lemma}（{t}）：' + '；'.join(f'{lab} 表里 {v}，程序 {w}' for lab, v, w in diffs))
lem = sorted({r[1] for r in results})
print('比对过的动词：', len(lem))
# 前言里引用的核对数字
stats = {'verbs': len(lem), 'cells': sum(r[3] for r in results), 'cols': cols, 'bad_cols': len(bad), 'rows': row_checked, 'bad_rows': len(row_bad)}
(Path(__file__).resolve().parent.parent / 'data' / 'check_stats.json').write_text(json.dumps(stats, ensure_ascii=False) + '\n', 'utf-8')
