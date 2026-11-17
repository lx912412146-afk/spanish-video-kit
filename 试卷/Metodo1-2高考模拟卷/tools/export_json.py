"""试卷.md → out/paper.json（排版程序 build_exam.js 用）。

    python export_json.py 试卷.md 输出.json [听力_时间轴.json]

把每个二级标题下的内容切成“块”：标题、段落、小节说明、选择题、完形选项、列表、表格、范文引文。
学生版用「注意事项」到「第四部分」，教师版用其余各节；答题卡按题号直接生成，不读这里。
"""
import json
import re
import sys
from pathlib import Path

SRC, DST = Path(sys.argv[1]), Path(sys.argv[2])
TL = Path(sys.argv[3]) if len(sys.argv) > 3 else None


def blocks(text):
    out, lines, i = [], text.splitlines(), 0
    while i < len(lines):
        ln = lines[i]
        s = ln.strip()
        if not s:
            i += 1
            continue
        if s.startswith('### '):
            out.append({'t': 'h3', 'text': s[4:]})
            i += 1
        elif s.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                cells = [c.strip() for c in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r'-+', c) for c in cells):
                    rows.append(cells)
                i += 1
            if rows and rows[0][0] == '题号' and len(rows[0]) == 5:
                out.append({'t': 'cloze', 'rows': rows[1:]})
            else:
                out.append({'t': 'table', 'rows': rows})
        elif re.match(r'^\d{1,2}\. ', ln) and i + 1 < len(lines) and re.match(r'^ {3,4}- [A-D]\. ', lines[i + 1]):
            num, stem = re.match(r'^(\d{1,2})\. (.+)$', ln).groups()
            opts = []
            i += 1
            while i < len(lines) and re.match(r'^ {3,4}- [A-D]\. ', lines[i]):
                l, o = re.match(r'^ {3,4}- ([A-D])\. (.+)$', lines[i]).groups()
                opts.append([l, o])
                i += 1
            out.append({'t': 'q', 'num': int(num), 'stem': stem, 'options': opts})
        elif re.match(r'^\d+\. ', ln):
            items = []
            while i < len(lines) and re.match(r'^\d+\. ', lines[i]):
                items.append(re.sub(r'^\d+\. ', '', lines[i]).strip())
                i += 1
            out.append({'t': 'ol', 'items': items})
        elif s.startswith('- '):
            items = []
            while i < len(lines) and lines[i].strip().startswith('- '):
                items.append(lines[i].strip()[2:])
                i += 1
            out.append({'t': 'ul', 'items': items})
        elif s.startswith('>'):
            paras, cur = [], []
            while i < len(lines) and lines[i].strip().startswith('>'):
                x = lines[i].strip()[1:].strip()
                if x:
                    cur.append(x)
                elif cur:
                    paras.append(' '.join(cur))
                    cur = []
                i += 1
            if cur:
                paras.append(' '.join(cur))
            out.append({'t': 'quote', 'paras': paras})
        elif re.match(r'^\*\*第[一二]节\*\*', s) or re.match(r'^\*\*[^*]+\*\*（', s):
            out.append({'t': 'sub', 'text': s})
            i += 1
        else:
            out.append({'t': 'p', 'text': s})
            i += 1
    return out


def main():
    md = SRC.read_text('utf-8')
    title = re.match(r'# (.+)', md).group(1)
    date = re.search(r'\n\n(\d{4}-\d{2}-\d{2})\n', md).group(1)
    secs = []
    for part in re.split(r'(?m)^(?=## )', md)[1:]:
        head, body = part.split('\n', 1)
        secs.append({'title': head[3:].strip(), 'blocks': blocks(body)})
    data = {'title': title, 'date': date, 'sections': secs}
    if TL and TL.exists():
        tl = json.loads(TL.read_text('utf-8'))
        data['timeline'] = {'total_s': tl['total_s'], 'texts': tl['texts']}
    DST.parent.mkdir(parents=True, exist_ok=True)
    DST.write_text(json.dumps(data, ensure_ascii=False, indent=1), 'utf-8')
    print(f'{DST.name}：{len(secs)} 节，' + '、'.join(f"{s['title'][:6]} {len(s['blocks'])}" for s in secs))


if __name__ == '__main__':
    main()
