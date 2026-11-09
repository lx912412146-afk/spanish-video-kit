"""对比工具包里的文章（旧）和 gr2art 里的文章（新）：python diff.py <工具包 文章 目录> <编号>…"""
import json, sys
from pathlib import Path
old_dir = Path(sys.argv[1])
for pid in sys.argv[2:]:
    a = json.loads((old_dir / f'{pid}.json').read_text('utf-8')); b = json.loads(Path(f'西班牙语/文章/{pid}.json').read_text('utf-8'))
    sa = [s for p in a['paras'] for s in p]; sb = [s for p in b['paras'] for s in p]
    oes = [s['es'] for s in sa]
    if len(sa) != len(sb): print(pid, f'句数 {len(sa)} → {len(sb)}')
    for k, y in enumerate(sb, 1):
        if y['es'] not in oes:
            print(f'{pid} {k} 新/改 ES: {y["es"]}\n{" " * len(pid)}   ZH: {y["zh"]}\n{" " * len(pid)}   W: ' + ' | '.join(f'{w["h"]} {w["pos"]} {w["zh"]} [{w["surface"]}]' for w in y['w']))
            continue
        x = sa[oes.index(y['es'])]
        if x['zh'] != y['zh']: print(f'{pid} {k} ZH: {x["zh"]} → {y["zh"]}')
        gx = [(w['h'], w['pos'], w['zh'], w['surface']) for w in x['w']]; gy = [(w['h'], w['pos'], w['zh'], w['surface']) for w in y['w']]
        if gx != gy: print(f'{pid} {k} W: -{[g for g in gx if g not in gy]} +{[g for g in gy if g not in gx]}')
    if a.get('no_pause_commas') != b.get('no_pause_commas'): print(pid, 'no_pause_commas:', json.dumps(b.get('no_pause_commas'), ensure_ascii=False))
    if a.get('pos_legend') != b.get('pos_legend'): print(pid, 'pos_legend:', list(b['pos_legend']))
