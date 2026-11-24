"""第一、二、三册单词表的结果合在一起：第四册哪些词、哪些词形前三册已经学过或见过。

    import prior
    prior.ENTRY[('casa', 'f.')]  → {'book': 1, 'lesson': 7, 'zh': '家；房子', 'senses': [(1, 7, '家；房子')], 'phon_only': False, ...}
    prior.FORM['tengo']          → [('tener', 'v.', '有')]       前三册见过的词形和它归到的词条
    prior.VFORM['tengo']         → {'tener'}                     前三册见过的动词形式（含不定式）
    prior.SKIP['ana']            → '#人名'                       前三册归并时跳过的词形（人名、错误形式）
    prior.where(e)               → '第一册第 7 课' / '第三册第 13 课'
    prior.VERBS_TABLE            → {动词: (册, 课)}               前三册出过变位表的动词（第一册 127 个、第二册 142 个、第三册 200 个，haber 第一、二册都有）

senses：这个词条在前三册学过的所有意思（第一次学的意思，加上后面单列的“新义”），按先后排。
数据目录默认是仓库里的 课件/第一册/单词表/data、课件/第二册/单词表/data、课件/第三册/单词表/data（从 tools/ 算起 ../../../第一册/…），
可以用环境变量 BOOK1_DATA、BOOK2_DATA、BOOK3_DATA 指定。"""
import json
import os
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[3]
DATA1 = Path(os.environ.get('BOOK1_DATA') or _ROOT / '第一册' / '单词表' / 'data')
DATA2 = Path(os.environ.get('BOOK2_DATA') or _ROOT / '第二册' / '单词表' / 'data')
DATA3 = Path(os.environ.get('BOOK3_DATA') or _ROOT / '第三册' / '单词表' / 'data')
V1 = json.loads((DATA1 / 'vocab.json').read_text('utf-8'))
V2 = json.loads((DATA2 / 'vocab.json').read_text('utf-8'))
V3 = json.loads((DATA3 / 'vocab.json').read_text('utf-8'))
BOOK_ZH = {1: '第一册', 2: '第二册', 3: '第三册'}

ENTRY, FORM, VFORM, SKIP = {}, {}, {}, {}


def where(e):
    return f'{BOOK_ZH[e["book"]]}第 {e["lesson"]} 课'


def _add_form(f, lemma, pos, zh):
    FORM.setdefault(f, [])
    if not any(x[0] == lemma and x[1] == pos for x in FORM[f]):
        FORM[f].append((lemma, pos, zh))


# 第一册：课文等里学过的词（lesson 是课次），只在语音练习里出现的（lesson 为 None，phon 是语音练习的课）
for L in V1['lessons']:
    for e in L['words'] + L['phon']:
        for pos in e['pos'].split('；'):
            k = (e['lemma'], pos)
            old = ENTRY.get(k)
            cur = {'book': 1, 'lesson': e['lesson'], 'zh': e['zh'], 'senses': [(1, e['lesson'], e['zh'])] if e['lesson'] else [],
                   'phon_only': e['lesson'] is None, 'phon': e['phon'], 'vtype': e['vtype']}
            if old is None or (old['phon_only'] and not cur['phon_only']):
                ENTRY[k] = cur
            for f in e['forms']:
                _add_form(f, e['lemma'], pos, e['zh'])
            if pos == 'v.':
                for f in e['forms']:
                    VFORM.setdefault(f, set()).add(e['lemma'])
    for v in L['vforms']:
        VFORM.setdefault(v['form'], set()).add(v['lemma'])
    for x in L.get('newforms', []):
        _add_form(x['form'], x['lemma'], x['pos'], ENTRY.get((x['lemma'], x['pos']), {}).get('zh', ''))

# 第二、三册：新词；第一册只在语音练习里出现过、这一册才学的（phon）；前面学过、这一课有新意思的（newsense）
for book, L in [(2, L) for L in V2['lessons']] + [(3, L) for L in V3['lessons']]:
    for e in L['words']:
        for pos in e['pos'].split('；'):
            k = (e['lemma'], pos)
            old = ENTRY.get(k)
            if e.get('newsense'):
                if old is None:
                    raise SystemExit(f'{BOOK_ZH[book]}的新义找不到原来的词条：{k}')
                old['senses'].append((book, e['lesson'], e['zh']))
            elif old is None or old['phon_only']:
                ENTRY[k] = {'book': book, 'lesson': e['lesson'], 'zh': e['zh'], 'senses': [(book, e['lesson'], e['zh'])], 'phon_only': False,
                            'phon': old['phon'] if old else None, 'vtype': e['vtype']}
            else:
                old['senses'].append((book, e['lesson'], e['zh']))     # 同一个词条后面另一课又列了一次（不同词性合并的行）
            for f in e['forms']:
                _add_form(f, e['lemma'], pos, e['zh'])
            if pos == 'v.':
                for f in e['forms']:
                    VFORM.setdefault(f, set()).add(e['lemma'])
    for v in L['vforms']:
        VFORM.setdefault(v['form'], set()).add(v['lemma'])
    for x in L.get('newforms', []):
        _add_form(x['form'], x['lemma'], x['pos'], ENTRY.get((x['lemma'], x['pos']), {}).get('zh', ''))

# 三册的归并结果：跳过的词形；归到前三册已有词条、但单词表里没单列的形式（复数 hospitales 这类）
for d in (DATA1, DATA2, DATA3):
    for f in sorted(d.glob('lex_L*.tsv')):
        for ln in f.read_text('utf-8').rstrip('\n').split('\n')[1:]:
            b = (ln.split('\t') + ['', '', '', ''])[:5]
            if b[1] in ('#跳过', '#人名'):
                SKIP[b[0]] = b[1]
            elif (b[1], b[2]) in ENTRY:
                _add_form(b[0], b[1], b[2], ENTRY[(b[1], b[2])]['zh'])
                if b[2] == 'v.':
                    VFORM.setdefault(b[0], set()).add(b[1])

# 前三册的所有词形（含只以大写出现的人名、跳过的错误形式）
ALL_FORMS = {e['form'] for d in (DATA1, DATA2, DATA3) for e in json.loads((d / 'forms.json').read_text('utf-8'))}
VERBS = {lemma for (lemma, pos), e in ENTRY.items() if pos == 'v.' and not e['phon_only']}
VERBS_TABLE = {}
for book, V in ((1, V1), (2, V2), (3, V3)):
    for v in V['conj']:
        if v not in VERBS_TABLE:
            e = ENTRY.get((v, 'v.'))
            VERBS_TABLE[v] = (book, e['lesson'] if e and e['book'] == book else None)
assert all(L for b, L in VERBS_TABLE.values()), [v for v, (b, L) in VERBS_TABLE.items() if not L]


def learned(lemma, pos):
    """前三册在课文、语法、练习里学过的词条（第一册只在语音练习里出现、后面也没学的不算）。"""
    e = ENTRY.get((lemma, pos))
    return bool(e) and not e['phon_only']


def senses_text(e):
    """前三册学过的意思：家；房子（第一册第 7 课）；……（第二册第 3 课新义）"""
    out = []
    for i, (b, l, z) in enumerate(e['senses']):
        out.append(f'{z}（{BOOK_ZH[b]}第 {l} 课{"新义" if i else ""}）')
    return '；'.join(out) if out else f'{e["zh"]}（第一册第 {e["phon"]} 课语音练习）'


if __name__ == '__main__':
    print(DATA1, DATA2, DATA3)
    print('词条', len(ENTRY), '（只在第一册语音练习的', sum(e['phon_only'] for e in ENTRY.values()), '）；词形', len(ALL_FORMS),
          '；动词', len(VERBS), '；有变位表的动词', len(VERBS_TABLE), '；动词形式', len(VFORM), '；跳过', len(SKIP))
    print('后面有新义的', sum(len(e['senses']) > 1 for e in ENTRY.values()))
