"""把《现代西班牙语》第四册（老版）18 课课件里的西语句子按课抽出来：python extract.py <课件 content 目录>
输出 data/sentences.json（每课的句子：西语、中文、出处）和 data/forms.json（每个词形第一次出现的课、出现次数、两个例句、前三册见过没有）；
前三册没见过的词形按课分三组写进 data/forms_L01-06.json 等（要归并的），前三册见过的写进 data/known_L01-06.json 等（附前三册归到的词条和学过的意思，
查同形词的新意思用），前三册的全部词条写进 data/prior_lemmas.tsv（给归并时对照）。课件里的“教学说明”（notes）、“教学目标”（goals）是写给老师的，不算（和第一、二册一样）。"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import prior  # noqa: E402

SRC = Path(sys.argv[1])
OUT = Path(__file__).resolve().parent.parent / 'data'
ES_WORD = re.compile(r"[A-Za-zÁÉÍÓÚÑÜáéíóúñü]+")
HAN = re.compile(r'[一-鿿]')


def es_spans(s):
    """混着中文的字符串（语法要点、练习题）：取出里面连着的西语片段。"""
    for part in re.split(r'[　-〿一-鿿＀-￯]+', s):
        part = part.strip(' ：:，,；;。.（）()“”')
        if ES_WORD.search(part):
            yield part


def units(j):
    """(西语, 中文, 出处)"""
    for w in j.get('vocab', []):
        yield w[0], w[1], '词汇'
    for blk in j.get('pronunciation', []):
        for it in blk.get('items', []):
            for w in it.get('words', []):
                yield w[0], w[1], '语音'
        for w in blk.get('words', []) if isinstance(blk.get('words'), list) else []:
            if isinstance(w, list):
                yield w[0], w[1], '语音'
    for ln in j['text']['lines']:
        yield ln['es'], ln['zh'], '课文'
    for g in j.get('grammar', []):
        for p in g.get('points', []):
            for sp in es_spans(p):
                yield sp, p, '语法要点'
        t = g.get('table')
        if t:
            for row in [t['head']] + t['rows']:
                for c in row:
                    for sp in es_spans(c):
                        yield sp, '', '语法表'
        for ex in g.get('examples', []):
            yield ex[0], ex[1], '语法例句'
    for ph in j.get('phrases', []):
        yield ph[0], ph[1], '常用表达'
    for ex in j.get('exercises', []):
        q = ex.get('q', '')
        if ex.get('type') == '选择':
            q = re.sub(r'\([^()]*/[^()]*\)', '', q)      # 选择题括号里的选项有故意写错的（Durmamos / Duermamos），只取答案
        for k, s in (('q', q), ('a', '' if ex.get('type') == '语音' else ex.get('a', ''))):   # 语音题的答案是拆开的音节
            for sp in es_spans(s):
                yield sp, ex.get('q', '') if k == 'a' else '', '练习'
    for k in ('summary', 'homework'):
        for s in j.get(k, []):
            for sp in es_spans(s):
                yield sp, s, '小结' if k == 'summary' else '作业'


lessons, forms = [], {}
for f in sorted(SRC.glob('L*.json')):
    j = json.loads(f.read_text('utf-8'))
    n = j['lesson']
    us = [{'es': es, 'zh': zh, 'src': src} for es, zh, src in units(j)]
    lessons.append({'lesson': n, 'title_es': j['title_es'], 'title_zh': j['title_zh'], 'units': us})
    for u in us:
        for w in ES_WORD.findall(u['es']):
            key = w.lower()
            e = forms.setdefault(key, {'form': key, 'lesson': n, 'count': 0, 'cap_only': True, 'ex': []})
            e['count'] += 1
            if w[0].islower():
                e['cap_only'] = False
            if e['lesson'] == n and len(e['ex']) < 2 and u not in e['ex']:
                e['ex'].append(u)
for e in forms.values():
    e['prev'] = e['form'] in prior.ALL_FORMS
OUT.mkdir(exist_ok=True)
(OUT / 'sentences.json').write_text(json.dumps(lessons, ensure_ascii=False, indent=1), 'utf-8')
allf = sorted(forms.values(), key=lambda e: (e['lesson'], e['form']))
(OUT / 'forms.json').write_text(json.dumps(allf, ensure_ascii=False, indent=1), 'utf-8')
GROUPS = [(1, 6), (7, 12), (13, 18)]
for a, b in GROUPS:
    tag = f'L{a:02d}-{b:02d}'
    new = [{k: e[k] for k in ('form', 'lesson', 'count', 'cap_only', 'ex')} for e in allf if a <= e['lesson'] <= b and not e['prev']]
    known = [dict({k: e[k] for k in ('form', 'lesson', 'count', 'ex')}, prev=prior.SKIP.get(e['form']) or
                  [f'{l}（{p}）{prior.senses_text(prior.ENTRY[(l, p)])}' for l, p, z in prior.FORM.get(e['form'], [])])
             for e in allf if a <= e['lesson'] <= b and e['prev']]
    (OUT / f'forms_{tag}.json').write_text(json.dumps(new, ensure_ascii=False, indent=1), 'utf-8')
    (OUT / f'known_{tag}.json').write_text(json.dumps(known, ensure_ascii=False, indent=1), 'utf-8')
    print(tag, '要归并的新词形', len(new), '；前三册见过的', len(known))
# 前三册的词条（原形、词性、第一次学的释义、第一次出现在哪册哪课、前三册学过的全部意思；“第一册语音N”＝只在第一册第 N 课语音练习里出现过），归并时照抄用
prows = sorted((f"{l}\t{p}\t{e['zh']}\t{('第一册语音' + str(e['phon'])) if e['phon_only'] else prior.where(e)}\t{prior.senses_text(e)}"
                for (l, p), e in prior.ENTRY.items()), key=str.lower)
(OUT / 'prior_lemmas.tsv').write_text('lemma\tpos\tzh\twhere\tsenses\n' + '\n'.join(prows) + '\n', 'utf-8')
by = {}
for e in forms.values():
    if not e['prev']:
        by[e['lesson']] = by.get(e['lesson'], 0) + 1
print('词形', len(forms), '；前三册没见过的', sum(by.values()), '；各课第一次出现（前三册没见过的）：', ' '.join(f'{k}:{v}' for k, v in sorted(by.items())))
print('只以大写出现（人名地名或句首）：', sum(e['cap_only'] and not e['prev'] for e in forms.values()))
