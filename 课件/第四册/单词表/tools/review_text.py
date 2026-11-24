"""把 data/vocab.json 写成审读用的纯文本：python review_text.py <输出目录>
words_L01-09.txt、words_L10-18.txt（每课的生词、生词表里前面学过的词、短语、动词形式、新词形），conj.txt（新动词变位表、前三册动词索引）。"""
import json
import sys
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / 'data'
OUT = Path(sys.argv[1])
OUT.mkdir(parents=True, exist_ok=True)
d = json.loads((DATA / 'vocab.json').read_text('utf-8'))


def lesson_text(L):
    out = [f'===== 第 {L["lesson"]} 课 {L["title_zh"]}（{L["title_es"]}）', '-- 生词（西语 | 词性 | 中文 | 备注；★=课件生词表里的词）']
    for e in L['words']:
        out.append(f'{"★" if e["core"] else " "} {e["lemma"]} | {e["pos"]} | {e["zh"]} | ' + '；'.join(filter(None, ['，'.join(e['vtype']), e['note']])))
    if L['seen']:
        out.append('-- 生词表里前面学过的词（西语 | 本课课件释义 | 第一次出现）')
        out += [f'  {s["item"]} | {s["zh"]} | {s["where"]}' for s in L['seen']]
    if L['vphrases']:
        out.append('-- 生词表里的短语')
        out += [f'  {p["es"]} | {p["zh"]}' for p in L['vphrases']]
    if L['vforms']:
        out.append('-- 本课第一次出现的动词形式（形式 ← 原形：说明）')
        out += [f'  {v["form"]} ← {v["lemma"]}：' + '；'.join(filter(None, [v['analysis'], v['usage']])) for v in L['vforms']]
    if L['newforms']:
        out.append('-- 已学词的新形式')
        out += [f'  {v["form"]} ← {v["lemma"]}（{v["where"]}）：{v["note"]}' for v in L['newforms']]
    out.append('-- 新动词（有变位表）：' + '，'.join(L['verbs']))
    return out


for a, b in ((1, 9), (10, 18)):
    lines = []
    for L in d['lessons']:
        if a <= L['lesson'] <= b:
            lines += lesson_text(L) + ['']
    (OUT / f'words_L{a:02d}-{b:02d}.txt').write_text('\n'.join(lines) + '\n', 'utf-8')

lines = []
TOP = ('现在时', '简单过去时', '过去未完成时', '将来时', '条件式')   # 下表：虚拟式现在时、-ra、-se、肯定命令式、否定命令式
for L in d['lessons']:
    for v in L['verbs']:
        c = d['conj'][v]
        lines.append(f'== {v}{"（助动词）" if c["aux"] else ""}（第 {L["lesson"]} 课）副动词 {c["ger"]["f"]}，过去分词 {c["part"]["f"]}' + ('；' + '；'.join(c['notes']) if c['notes'] else ''))
        for i in range(6):
            lines.append('  ' + ' | '.join(x['f'] + ('*' if x['irr'] else '') for x in c['top'][i] + c['bottom'][i]))
lines.append('')
lines.append('== 前三册出过变位表的动词（册·课）')
for r in d['prior_verbs']:
    lines.append(f'  {r["verb"]}（{r["zh"]}，{r["book"]}·{r["lesson"]}）' + ('，'.join(r['vtype']) and '：' + '，'.join(r['vtype'])))
(OUT / 'conj.txt').write_text('\n'.join(lines) + '\n', 'utf-8')
print('写好', OUT)
