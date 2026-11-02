"""把《现代西班牙语》第一册（老版）24 课课件里的西语句子按课抽出来：python extract.py <课件 content 目录>
输出 data/sentences.json（每课的句子：西语、中文、出处）和 data/forms.json（每个词形第一次出现的课、出现次数、两个例句）。"""
import json
import re
import sys
from pathlib import Path

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
OUT.mkdir(exist_ok=True)
(OUT / 'sentences.json').write_text(json.dumps(lessons, ensure_ascii=False, indent=1), 'utf-8')
(OUT / 'forms.json').write_text(json.dumps(sorted(forms.values(), key=lambda e: (e['lesson'], e['form'])), ensure_ascii=False, indent=1), 'utf-8')
by = {}
for e in forms.values():
    by[e['lesson']] = by.get(e['lesson'], 0) + 1
print('词形', len(forms), '；各课第一次出现：', ' '.join(f'{k}:{v}' for k, v in sorted(by.items())))
print('只以大写出现（人名地名或句首）：', sum(e['cap_only'] for e in forms.values()))
