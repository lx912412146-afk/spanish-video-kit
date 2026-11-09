"""第二批分级阅读：估算时长并做补充检查。python est.py <文章编号>…（读 西班牙语/文章/<编号>.json）
时长估算 = 片头 1.5 + 每词秒数 × 词数 + 句间 0.8 ×（句数 − 1）+ 结尾 2.0。每词秒数按第一批实测（含逗号停顿）：
A1 0.375、A2 0.45（0.8 倍速）；B1 0.34、B2 0.39、C1 0.365（原速，2026-11-10 按第二批 c1_11、c1_13 实测重新校准；B2 原来按 B1、C1 取中间值 0.355，b2_11 实测 146 词朗读 57.0 秒，即每词 0.39 秒，改成 0.39）。目标 57–63 秒，B1—C1 最好在 58–62 秒。
补充检查：原文不能有数字、引号、括号、破折号、省略号；生词只在词头第一次出现的句子标（句中写法在前面的句子里出现过就提醒）；
每句 3–5 个生词；释义 ≤ 14 字（这几项 check_articles.py 也查）。"""
import json, re, sys
from pathlib import Path
RATE = {'A1': 0.385, 'A2': 0.40, 'B1': 0.34, 'B2': 0.39, 'C1': 0.365}
TARGET = {'A1': '约 12 句、125 词', 'A2': '约 10 句、108 词', 'B1': '约 9 句、145 词', 'B2': '约 8 句、143 词', 'C1': '约 8 句、140 词'}
W = re.compile(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+")
bad_total = 0
for pid in sys.argv[1:]:
    p = json.loads((Path(__file__).parent / '西班牙语' / '文章' / f'{pid}.json').read_text('utf-8'))
    sents = [s for para in p['paras'] for s in para]
    words = sum(len(W.findall(s['es'])) for s in sents)
    n = len(sents)
    est = 1.5 + RATE[p['level']] * words + 0.8 * (n - 1) + 2.0
    probs = []
    if not 57 <= est <= 63:
        probs.append(f'估算 {est:.1f} 秒，不在 57–63 秒（{p["level"]} 目标{TARGET[p["level"]]}）')
    for k, s in enumerate(sents, 1):
        if re.search(r'[0-9"“”«»()\[\]—–…]|\.\.\.', s['es']):
            probs.append(f'第 {k} 句有数字、引号、括号、破折号或省略号：{s["es"]}')
        for w in s['w']:
            pat = re.compile(r'(?<![A-Za-zÁÉÍÓÚÜÑáéíóúüñ])' + re.escape(w['surface'].lower()) + r'(?![A-Za-zÁÉÍÓÚÜÑáéíóúüñ])')
            for j in range(k - 1):
                if pat.search(sents[j]['es'].lower()):
                    inside = [v for v in sents[j]['w'] if pat.search(v['surface'].lower()) and v['h'].lower() != w['h'].lower()]
                    if inside:
                        print(f'  提醒：第 {k} 句的生词「{w["surface"]}」在第 {j + 1} 句的词组「{inside[0]["surface"]}」里出现过（词义不同可以保留）')
                    else:
                        probs.append(f'第 {k} 句的生词「{w["surface"]}」在第 {j + 1} 句已经出现，应该标在第一次出现的地方')
                    break
    print(f'{pid}：{n} 句，{words} 词，估算 {est:.1f} 秒' + ('' if not probs else ''.join('\n  ✗ ' + x for x in probs)))
    bad_total += bool(probs)
sys.exit(1 if bad_total else 0)
