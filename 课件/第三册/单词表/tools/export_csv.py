"""把 data/vocab.json 导出成两张表格（UTF-8 带 BOM，Excel 直接打开）：python export_csv.py <输出目录>
单词表.csv：每个词条、生词表里前面学过的词、生词表里的短语、动词形式、已学词的新形式各一行；
动词变位表.csv：每个新动词 6 行（人称），后面附前两册动词的虚拟式过去未完成时（每个动词一行）。"""
import csv
import json
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / 'data'
OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)
d = json.loads((DATA / 'vocab.json').read_text('utf-8'))
PERS = ['yo', 'tú', 'él / ella / usted', 'nosotros', 'vosotros', 'ellos / ellas / ustedes']


def star(x):
    return x['f'] + ('*' if x['irr'] else '')


with open(OUT / '单词表.csv', 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(['课', '西语', '词性', '中文释义', '备注', '课件生词表', '类别'])
    for L in d['lessons']:
        for e in L['words']:
            w.writerow([L['lesson'], e['lemma'], e['pos'], e['zh'], '；'.join(filter(None, ['，'.join(e['vtype']), e['note']])),
                        '是' if e['core'] else '', '新义' if e.get('newsense') else '生词'])
        for s in L['seen']:
            w.writerow([L['lesson'], s['item'], '', s['zh'], f'第一次出现：{s["where"]}', '是', '生词表里前面学过的词'])
        for p in L['vphrases']:
            w.writerow([L['lesson'], p['es'], '', p['zh'], '', '是', '生词表里的短语'])
        for v in L['vforms']:
            w.writerow([L['lesson'], v['form'], 'v.', f'→ {v["lemma"]}', '；'.join(filter(None, [v['analysis'], v['usage']])), '', '动词形式'])
        for v in L['newforms']:
            w.writerow([L['lesson'], v['form'], v['pos'], f'→ {v["lemma"]}', f'{v["note"]}（原形：{v["where"]}）', '', '新词形'])

with open(OUT / '动词变位表.csv', 'w', encoding='utf-8-sig', newline='') as f:
    w = csv.writer(f)
    w.writerow(['动词', '课', '中文', '类型', '人称', '陈述式现在时', '简单过去时', '过去未完成时', '将来未完成时', '简单条件式',
                '虚拟式现在时', '虚拟式过去未完成时（-ra）', '虚拟式过去未完成时（-se）', '肯定命令式', '否定命令式', '副动词', '过去分词', '说明'])
    for L in d['lessons']:
        for v in L['verbs']:
            c = d['conj'][v]
            e = next(x for x in L['words'] if x['lemma'] == v and 'v.' in x['pos'].split('；'))
            name, zh = (f'{v}（助动词）', '和过去分词构成复合时态') if c['aux'] else (v, e['zh'])
            for i, p in enumerate(PERS):
                w.writerow([name, L['lesson'], zh, ('' if c['aux'] else '，'.join(e['vtype'])) or '规则', p,
                            *(star(x) for x in c['top'][i]), *(star(x) for x in c['bottom'][i]),
                            star(c['ger']) if i == 0 else '', star(c['part']) if i == 0 else '',
                            ('*＝和规则变位不一样；' + '；'.join(c['notes'])).rstrip('；') if i == 0 else ''])
    w.writerow([])
    w.writerow(['前两册动词的虚拟式过去未完成时', '册·课', '中文', '类型', '人称', '简单过去时 ellos', '-ra 形式', '-ra 形式 nosotros', '-se 形式', '说明'])
    for r in d['prior_verbs']:
        w.writerow([r['verb'], f'{r["book"]}·{r["lesson"]}', r['zh'], '，'.join(r['vtype']) or '规则', '第三人称单数' if r['third'] else 'yo',
                    star(r['pret6']), star(r['sra1']), star(r['sra4']), star(r['sse1']),
                    ('*＝和规则变位不一样；' + '；'.join(r['notes'] + {'sg': ['只用第三人称单数'], '3': ['只用第三人称，简单过去时是 ellos 的形式']}.get(r['third'], []))).rstrip('；')])
print('写好', OUT / '单词表.csv', OUT / '动词变位表.csv')
