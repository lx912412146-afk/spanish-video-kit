"""排版完整性：试卷.md 里的每一段文字（题干、选项、短文、表格单元格、列表项）都要在对应的 PDF 里找得到。

    python check_pdf_text.py paper.json 试卷.pdf 答案与评分说明.pdf <pdftotext 路径> [答题卡.pdf]

比较时去掉所有空白（含不换行空格、WJ）和 Markdown 记号，所以只查“字有没有丢、有没有变”，不查折行。
给了答题卡就再查：1–20 题各有 [A][B][C]，21–60 题各有 [A]–[D]，61–70 题各有一个填写处，写作两节。
"""
import json
import re
import subprocess
import sys

D = json.load(open(sys.argv[1], encoding='utf-8'))
PDF_S, PDF_T, PDFTOTEXT = sys.argv[2], sys.argv[3], sys.argv[4]


def pdftext(p):
    t = subprocess.run([PDFTOTEXT, '-raw', '-enc', 'UTF-8', p, '-'], capture_output=True, text=True, check=True).stdout
    # 页脚（段落跨页时夹在中间）先去掉
    t = re.sub(r'(西班牙语试题|西班牙语答题卡|答案与评分说明) 第 \d+ 页（共 \d+ 页）', '', t)
    return squash(t)


def squash(s):
    s = s.replace('\\_', '_').replace('**', '').replace('`', '')
    s = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\1（\2）', s)
    s = re.sub(r'_{2}(\d+)_{2}', r'\1', s)                  # 空格题号：PDF 里只剩数字（下划线是格式）
    s = re.sub(r'_{4,}', '', s)
    return re.sub(r'[\s ⁠​　\f]+', '', s)


def pieces(blocks):
    for b in blocks:
        t = b['t']
        if t in ('p', 'sub', 'h3'):
            yield b['text']
        elif t in ('ul', 'ol'):
            yield from b['items']
        elif t == 'quote':
            yield from b['paras']
        elif t == 'q':
            yield f"{b['num']}." + b['stem']
            for l, o in b['options']:
                yield f'{l}.{o}'
        elif t == 'cloze':
            for r in b['rows']:
                yield f'{r[0]}.'
                for l, o in zip('ABCD', r[1:]):
                    yield f'{l}.{o}'
        elif t == 'table':
            for r in b['rows']:
                yield from r


def main():
    st, te = pdftext(PDF_S), pdftext(PDF_T)
    miss, n = [], 0
    for sec in D['sections']:
        student = sec['title'] == '注意事项' or re.match(r'第[一二三四]部分', sec['title'])
        text = st if student else te
        if not squash(sec['title'].replace('（教师用）', '')) in text:
            miss.append(('标题', sec['title']))
        for s in pieces(sec['blocks']):
            n += 1
            # 页码栏、表格把长句拆到几行，pdftotext 按行输出；去掉空白后应当还是连着的
            if squash(s.replace('（教师用）', '')) not in text:
                miss.append((sec['title'][:8], s))
    if len(sys.argv) > 5:
        raw = subprocess.run([PDFTOTEXT, '-raw', '-enc', 'UTF-8', sys.argv[5], '-'], capture_output=True, text=True, check=True).stdout
        for q in range(1, 61):
            want = '[A] [B] [C]' + (' [D]' if q > 20 else '')
            if not re.search(rf'(?m)^{q} {re.escape(want)}$', raw):
                miss.append(('答题卡', f'第 {q} 题的选项'))
        for l, k in (('A', 60), ('B', 60), ('C', 60), ('D', 40)):
            if raw.count(f'[{l}]') != k:
                miss.append(('答题卡', f'[{l}] 有 {raw.count(f"[{l}]")} 个，应为 {k} 个'))
        for q in range(61, 71):
            if not re.search(rf'(?<!\d){q}\.(?!\d)', raw):
                miss.append(('答题卡', f'第 {q} 题'))
        for t in ('第一节（10 分）', '第二节（25 分）', '准考证号', '姓'):
            if t not in raw:
                miss.append(('答题卡', t))
    for where, s in miss:
        print(f'✗ {where}：{s[:90]}')
    print(f'PDF 文字核对：{n} 段，' + ('全部找到' if not miss else f'{len(miss)} 段没找到'))
    sys.exit(1 if miss else 0)


if __name__ == '__main__':
    main()
