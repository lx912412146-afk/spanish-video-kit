import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from a2_data import DATA, COMMON  # noqa: E402

ART = Path(__file__).resolve().parents[2] / '西班牙语' / '文章'   # 工具包根目录（本文件在 记录/文章补写/ 下）
POS = {'m.': '阳性名词', 'f.': '阴性名词', 'adj.': '形容词', 'adv.': '副词', 'tr.': '及物动词', 'intr.': '不及物动词',
       'prnl.': '自复动词', 'prep.': '介词', 'conj.': '连词', 'num.': '数词', 'interj.': '感叹词', 'pron.': '代词',
       'loc.': '短语，固定搭配'}
OLD = 'zh、w 待补。'

for pid, d in DATA.items():
    f = ART / f'{pid}.json'
    p = json.loads(f.read_text('utf-8'))
    sents = [s for para in p['paras'] for s in para]
    assert len(sents) == len(d['s']), (pid, len(sents), len(d['s']))
    used = set()
    for s, (zh, ws) in zip(sents, d['s']):
        es = s['es']
        items = []
        for surface, h, pos, gl in ws:
            assert es.count(surface) == 1, (pid, surface, es)
            items.append((es.index(surface), {'h': h, 'pos': pos, 'zh': gl, 'surface': surface, 'source': 'supplement'}))
            used.add(pos)
        items.sort(key=lambda x: x[0])
        s['zh'] = zh
        s['w'] = [w for _, w in items]
    p['title_zh'] = d['title_zh']
    note = p['_说明']
    assert note.endswith(OLD), (pid, note)
    p['_说明'] = note[:-len(OLD)] + COMMON + d['note']
    p['pos_legend'] = {k: v for k, v in POS.items() if k in used}
    p['no_pause_commas'] = d['npc']
    f.write_text(json.dumps(p, ensure_ascii=False, indent=1) + '\n', 'utf-8')
    print(pid, 'written', len(sents), 'sents', sum(len(x[1]) for x in d['s']), 'words')
