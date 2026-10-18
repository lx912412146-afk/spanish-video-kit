"""从《西班牙语A1-C1分级阅读文章集》提取的段落文本生成 50 篇文章骨架（es 原文按句号切句；zh、w 待补）。"""
import json
import re
import sys
from pathlib import Path

src, outdir = Path(sys.argv[1]), Path(sys.argv[2])
ALLOWED = re.compile(r"[^A-Za-zÁÉÍÓÚÜÑáéíóúüñ¿¡\s.,;:!?—\-]")
LEVEL_ZH = {'A1': '基础入门', 'A2': '初级进阶', 'B1': '中级', 'B2': '中高级', 'C1': '高级'}
level, arts, cur = None, [], None
for line in src.read_text('utf-8').splitlines():
    m = re.match(r'\[Heading1\] Nivel (\w\d)', line)
    if m:
        level, cur = m.group(1), None          # 等级下面那行中文简介不属于任何文章
        continue
    m = re.match(r'\[Heading2\] (\d\d)\. (.+)', line)
    if m:
        cur = {'level': level, 'no': int(m.group(1)), 'title_es': m.group(2).strip(), 'text': ''}
        arts.append(cur)
        continue
    if cur and not line.startswith('['):
        cur['text'] += line.strip() + ' '
for a in arts:
    sents = re.split(r'(?<=[.!?])\s+(?=[¿¡A-ZÁÉÍÓÚÑ])', a['text'].strip())
    pid = f"{a['level'].lower()}_{a['no']:02d}"
    bad = sorted({c for s in sents for c in ALLOWED.findall(s)})
    p = {'id': pid, 'level': a['level'], 'no': a['no'], 'title_es': a['title_es'], 'title_zh': '',
         'series': f"西班牙语分级阅读 · {a['level']} {LEVEL_ZH[a['level']]} · 第 {a['no']} 篇",
         'header': f"分级阅读 {a['level']}-{a['no']:02d}",
         '_说明': f"西班牙语分级阅读文章集（用户 2026-10-18 发来的 Word 文档《西班牙语A1-C1分级阅读文章集》）{a['level']} 第 {a['no']} 篇。es：原文（原样，按句号切句）；zh、w 待补。",
         'pos_legend': {}, 'no_pause_commas': {},
         'paras': [[{'es': s, 'zh': '', 'w': []} for s in sents]]}
    (outdir / f'{pid}.json').write_text(json.dumps(p, ensure_ascii=False, indent=1) + '\n', 'utf-8')
    print(pid, len(sents), 'sents', len(a['text'].split()), 'words, longest', max(len(s) for s in sents), 'chars', ''.join(bad) or '')
print('articles', len(arts))
