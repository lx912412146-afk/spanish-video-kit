import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from a1_data import A  # noqa: E402

DIR = Path(sys.argv[1])
POS = {'m.': '阳性名词', 'f.': '阴性名词', 'adj.': '形容词', 'adv.': '副词', 'tr.': '及物动词', 'intr.': '不及物动词',
       'prnl.': '自复动词', 'prep.': '介词', 'conj.': '连词', 'num.': '数词', 'interj.': '感叹词', 'pron.': '代词',
       'loc.': '短语，固定搭配'}
DESC = ('zh：逐句中文翻译；w：生词栏（全部为补充词条，source=supplement），h 词头（词典原形）、pos 词性（按句中用法标）、'
        'zh 释义（取句中义）、surface 句中原样写法（在句中恰好出现一次）；同一个词头只在第一次出现的句子里列；'
        'no_pause_commas 登记列举和并列形容词之间不停顿的逗号。')

for pid, d in A.items():
    f = DIR / f'{pid}.json'
    p = json.loads(f.read_text('utf-8'))
    sents = [s for para in p['paras'] for s in para]
    assert len(sents) == len(d['sents']), (pid, len(sents), len(d['sents']))
    used = set()
    for s, (zh, ws) in zip(sents, d['sents']):
        s['zh'] = zh
        items = [{'h': h, 'pos': pos, 'zh': g, 'surface': sf, 'source': 'supplement'} for h, pos, g, sf in ws]
        items.sort(key=lambda w: s['es'].find(w['surface']))
        s['w'] = items
        used |= {w['pos'] for w in items}
    p['title_zh'] = d['title_zh']
    old = p['_说明']
    assert old.endswith('zh、w 待补。') or 'zh：逐句中文翻译' in old, old
    base = old.split('zh、w 待补。')[0] if old.endswith('zh、w 待补。') else old.split('zh：逐句中文翻译')[0]
    p['_说明'] = base + DESC + '特别判断：' + d['note']
    p['pos_legend'] = {k: v for k, v in POS.items() if k in used}
    p['no_pause_commas'] = d['nopause']
    f.write_text(json.dumps(p, ensure_ascii=False, indent=1) + '\n', 'utf-8')
    print(pid, 'written')
