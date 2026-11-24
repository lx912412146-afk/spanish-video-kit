"""“每日一读”离线试排：对一篇文章试几种改写，只排静态页，报告选定的字号字距、最大词间空白，以及重点词汇越界、页面溢出的条数。

    python trygap.py <文章.json> <插图.svg> <改法.json>      # 环境变量 LINES=1：逐行列出词间空白

改法.json：{"标签": {"句号(正文从 1 数)": "新西语句子", ...}, ...}；标签 "原文" 可以给 {}。
两端对齐的词间空白超过上限时，用它在合成前比较几种改法（只改一两个词让换行位置变一变）。
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ART, SVG, VAR = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
RENDER = Path(__file__).resolve().parent / 'render_page.py'
base = json.loads(ART.read_text('utf-8'))
for label, changes in json.loads(VAR.read_text('utf-8')).items():
    a = json.loads(json.dumps(base))
    sents = [s for p in a['paras'] for s in p]
    for k, es in changes.items():
        sents[int(k) - 1]['es'] = es
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        (td / 'a.json').write_text(json.dumps(a, ensure_ascii=False), 'utf-8')
        r = subprocess.run([sys.executable, str(RENDER), str(td / 'a.json'), str(SVG), str(td / 'page')],
                           capture_output=True, text=True)
        if r.returncode:
            print(f'{label}: 出错 {r.stderr.strip()[-200:]}')
            continue
        L = json.loads((td / 'page' / 'layout.json').read_text('utf-8'))
        worst = max((g for g in L['es_gaps'] if g[0] == 'mid'), key=lambda g: g[1])
        print(f"{label}: 字号 {L['es_font']}，最大空白 {L['es_max_gap']} px（{worst[2][:40]}…），"
              f"越界 {L.get('vocab_out')}，溢出 {L.get('overflow')}", flush=True)
        if os.environ.get('LINES'):
            for g in L['es_gaps']:
                print(f'    {g[1]:4} {g[2]}')
