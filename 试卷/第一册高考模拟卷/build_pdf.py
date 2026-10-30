"""把试卷 Markdown 排成 A4 的 PDF：学生版（注意事项 + 四部分试题）和教师版（全部内容）。

    python build_pdf.py 试卷.md 输出目录 [--html-only]

用 Python-Markdown 转 HTML，再用 Playwright 的 Chromium 打印（页脚“西班牙语试题 第 X 页（共 Y 页）”）。
Chromium 需要能打开系统端口，在受限的命令沙盒里会失败，要在普通终端里运行。
"""
import re
import sys
from pathlib import Path

import markdown

SRC, OUT = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
STUDENT = ('注意事项', '第一部分', '第二部分', '第三部分', '第四部分', '第五部分')   # 分阶段卷加了第四部分“基础知识”，写作是第五部分

CSS = """
@page { size: A4; margin: 18mm 18mm 20mm 18mm; }
body { font-family: "Times New Roman", "Songti SC", "STSong", serif; font-size: 10.5pt; line-height: 1.55; color: #111; }
h1 { font-size: 17pt; text-align: center; margin: 0 0 4pt; }
.date { text-align: center; color: #555; margin-bottom: 12pt; }
h2 { font-size: 12.5pt; margin: 16pt 0 6pt; font-family: "PingFang SC", "Heiti SC", sans-serif; }
h3 { font-size: 11pt; text-align: center; margin: 12pt 0 6pt; }
p { margin: 4pt 0; text-align: justify; }
ol { padding-left: 22pt; margin: 4pt 0; }
ol > li { margin: 6pt 0 2pt; break-inside: avoid; }
ol > li > ul { list-style: none; padding-left: 10pt; margin: 2pt 0; }
ol > li > ul > li { margin: 0; }
table { border-collapse: collapse; margin: 6pt 0; width: 100%; break-inside: avoid; }
th, td { border: 0.6pt solid #888; padding: 2pt 5pt; font-size: 9.5pt; vertical-align: top; }
th { background: #f0f0f0; }
blockquote { margin: 6pt 0 6pt 10pt; padding-left: 8pt; border-left: 2pt solid #bbb; }
a { color: #111; text-decoration: none; }
.blank { display: inline-block; width: 5em; border-bottom: 0.6pt solid #111; }
/* 标题、“第一节（共…）”这样的说明行和题目列表前的说明不单独留在页底 */
h2, h3, p:has(> strong:first-child), p:has(+ ol), p.lead { break-after: avoid; page-break-after: avoid; }
"""


def sections(md):
    """按 ## 切分：返回 (标题行之前的内容, [(二级标题, 整节文本), …])。"""
    parts = re.split(r'(?m)^(?=## )', md)
    return parts[0], [(p.splitlines()[0][3:].strip(), p) for p in parts[1:]]


def to_html(md, title):
    md = re.sub(r'(?m)^ {3}- ', '    - ', md)                  # 选项缩进统一为 4 格（Python-Markdown 的嵌套列表要求）
    head, rest = md.split('\n', 1) if md.startswith('# ') else ('', md)
    m = re.match(r'\s*(\d{4}-\d{2}-\d{2})\s*\n', rest)
    date = ''
    if m:
        date, rest = m.group(1), rest[m.end():]
    rest = re.sub(r'(?<!\\)_{4,}', 'BLANKLINE', rest)                       # 题干里的长横线（不然会被当成加粗、斜体）
    body = markdown.markdown(rest, extensions=['tables', 'sane_lists'])
    body = body.replace('BLANKLINE', '<span class="blank"></span>')
    body = re.sub(r'<p>(阅读下面|从每题所给|听下面|在空白处)', r'<p class="lead">\1', body)   # 题目说明和下面的短文、题目不分页
    body = re.sub(r'<p>([^<]{1,40}[:：])</p>', r'<p class="lead">\1</p>', body)   # 信的称呼（Querida Julia:）和正文不分页
    h1 = f'<h1>{head[2:].strip()}</h1>' if head else ''
    return (f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><title>{title}</title>'
            f'<style>{CSS}</style></head><body>{h1}<div class="date">{date}</div>{body}</body></html>')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    md = SRC.read_text('utf-8')
    pre, secs = sections(md)
    student = pre + ''.join(t for name, t in secs if name.startswith(STUDENT))
    title = re.match(r'# (.+)', md).group(1)
    files = {}
    for name, text in (('学生版', student), ('教师版', md)):
        html = OUT / f'试卷_{name}.html'
        html.write_text(to_html(text, f'{title}（{name}）'), 'utf-8')
        files[name] = html
    print('HTML:', ', '.join(str(p.name) for p in files.values()))
    if '--html-only' in sys.argv:
        return
    from playwright.sync_api import sync_playwright
    foot = ('<div style="font-size:8pt;width:100%;text-align:center;font-family:serif;">'
            '西班牙语试题第 <span class="pageNumber"></span> 页（共 <span class="totalPages"></span> 页）</div>')
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        pg = br.new_page()
        for name, html in files.items():
            pg.goto(html.as_uri())
            pdf = OUT / f'试卷_{name}.pdf'
            pg.pdf(path=str(pdf), format='A4', print_background=True, display_header_footer=True,
                   header_template='<div></div>', footer_template=foot,
                   margin={'top': '18mm', 'bottom': '20mm', 'left': '18mm', 'right': '18mm'})
            print('PDF:', pdf.name, pdf.stat().st_size, 'bytes')
        br.close()


if __name__ == '__main__':
    main()
