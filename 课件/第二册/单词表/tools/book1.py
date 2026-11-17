"""第一册单词表的结果（课件/第一册/单词表/data）：第二册哪些词、哪些词形第一册已经学过。

    import book1
    book1.ENTRY[('casa', 'f.')]  → {'lesson': 7, 'zh': '家；房子', 'phon_only': False}
    book1.FORM['tengo']          → [('tener', 'v.', '有')]       第一册见过的词形和它归到的词条
    book1.VFORM['tengo']         → {'tener'}                     第一册见过的动词形式（含不定式）
    book1.SKIP['ana']            → '#人名'                       第一册归并时跳过的词形（人名、错误形式）

数据目录默认是 ../../../第一册/单词表/data（从 tools/ 算起，即仓库里的 课件/第一册/单词表/data），可以用环境变量 BOOK1_DATA 指定。"""
import json
import os
from pathlib import Path

DATA = Path(os.environ.get('BOOK1_DATA') or Path(__file__).resolve().parents[3] / '第一册' / '单词表' / 'data')
_v = json.loads((DATA / 'vocab.json').read_text('utf-8'))
LESSONS = _v['lessons']
CONJ = _v['conj']

ENTRY, FORM, VFORM, SKIP = {}, {}, {}, {}
for L in LESSONS:
    for e in L['words'] + L['phon']:
        for pos in e['pos'].split('；'):              # 同课两个词性合成的一行（mío adj.；pron.）
            k = (e['lemma'], pos)
            old = ENTRY.get(k)
            cur = {'lesson': e['lesson'], 'zh': e['zh'], 'phon_only': e['lesson'] is None, 'phon': e['phon'], 'vtype': e['vtype']}
            if old is None or (old['phon_only'] and not cur['phon_only']):
                ENTRY[k] = cur
            for f in e['forms']:
                FORM.setdefault(f, [])
                if (e['lemma'], pos, e['zh']) not in FORM[f]:
                    FORM[f].append((e['lemma'], pos, e['zh']))
            if pos == 'v.':
                for f in e['forms']:
                    VFORM.setdefault(f, set()).add(e['lemma'])
    for v in L['vforms']:
        VFORM.setdefault(v['form'], set()).add(v['lemma'])
for f in sorted(DATA.glob('lex_L*.tsv')):
    for ln in f.read_text('utf-8').rstrip('\n').split('\n')[1:]:
        b = ln.split('\t')
        if b[1] in ('#跳过', '#人名'):
            SKIP[b[0]] = b[1]
# 第一册所有词形（含只以大写出现的人名、跳过的错误形式）
ALL_FORMS = {e['form'] for e in json.loads((DATA / 'forms.json').read_text('utf-8'))}
VERBS = {lemma for (lemma, pos) in ENTRY if pos == 'v.'}


def learned(lemma, pos):
    """第一册在课文、语法、练习里学过的词条（只在语音练习里出现的不算）。"""
    e = ENTRY.get((lemma, pos))
    return bool(e) and not e['phon_only']


if __name__ == '__main__':
    print(DATA)
    print('词条', len(ENTRY), '（只在语音练习的', sum(e['phon_only'] for e in ENTRY.values()), '）；词形', len(ALL_FORMS), '；动词', len(VERBS),
          '；动词形式', len(VFORM), '；跳过', len(SKIP))
