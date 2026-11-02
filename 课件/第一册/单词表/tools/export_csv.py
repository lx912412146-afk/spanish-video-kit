"""把 data/vocab.json 导出成两张表格（UTF-8 带 BOM，Excel 直接打开）：python export_csv.py <输出目录>
单词表.csv：每个词条一行；动词变位表.csv：每个动词 6 行（人称）。"""
import csv
import json
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / 'data'
OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)
d = json.loads((DATA / 'vocab.json').read_text('utf-8'))
PERS = ['yo', 'tú', 'él / ella / usted', 'nosotros', 'vosotros', 'ellos / ellas / ustedes']

with open(OUT / '单词表.csv', 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(['课', '西语', '词性', '中文释义', '备注', '课件生词表', '类别'])
    for L in d['lessons']:
        for e in L['words']:
            w.writerow([L['lesson'], e['lemma'], e['pos'], e['zh'], '；'.join(filter(None, ['，'.join(e['vtype']), e['note']])), '是' if e['core'] else '', '生词'])
        for e in L['phon']:
            w.writerow([L['lesson'], e['lemma'], e['pos'], e['zh'], '', '', '语音练习词'])
        for v in L['vforms']:
            w.writerow([L['lesson'], v['form'], 'v.', f'→ {v["lemma"]}', '；'.join(filter(None, [v['analysis'], v['usage']])), '', '动词形式'])
        for v in L['newforms']:
            w.writerow([L['lesson'], v['form'], v['pos'], f'→ {v["lemma"]}', v['note'], '', '新词形'])

with open(OUT / '动词变位表.csv', 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(['动词', '课', '中文', '类型', '人称', '陈述式现在时', '简单过去时', '过去未完成时', '命令式', '副动词', '过去分词', '说明'])
    for L in d['lessons']:
        for v in L['verbs']:
            e = next(x for x in L['words'] if x['lemma'] == v and x['pos'] == 'v.')
            c = d['conj'][v]
            for i, (p, r) in enumerate(zip(PERS, c['rows'])):
                cells = [x['f'] + ('*' if x['irr'] else '') for x in r]
                w.writerow([v, L['lesson'], e['zh'], '，'.join(e['vtype']) or '规则', p, *cells,
                            c['ger']['f'] if i == 0 else '', c['part']['f'] if i == 0 else '',
                            ('*＝和规则变位不一样；' + '；'.join(c['notes'])).rstrip('；') if i == 0 else ''])
print('写好', OUT / '单词表.csv', OUT / '动词变位表.csv')
