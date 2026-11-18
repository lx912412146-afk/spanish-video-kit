# -*- coding: utf-8 -*-
"""DELE 模拟卷排版：content/<级别>/*.json → out/<级别>/pdf/ 三本 A4 PDF（考生题册、答题卡、教师用书）。

    python tools/build_pdf.py <级别> [--html-only]

HTML 由本脚本生成，再用 Playwright 的 Chromium 打印（Chromium 要在命令沙盒外运行）。
插图读 art/png/<id>.png（没有就印一个占位框并在最后列出）；录音时长读 out/<级别>/audio/核对/report.json（没有就按估计值）。
题型按 数据格式.md 的 tipo 排，不按级别写死；评分方法按 考试规格.md。
"""
import html
import json
import math
import re
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LV = sys.argv[1].upper()
C = ROOT / 'content' / LV
OUT = ROOT / 'out' / LV / 'pdf'
ARTDIR = ROOT / 'art' / 'png'
CL, CA, EIE, EIO = (json.loads((C / f'{p}.json').read_text('utf-8')) for p in ('cl', 'ca', 'eie', 'eio'))
ARTS = {}
for _p in sorted(C.glob('art_*.json')):
    for _a in json.loads(_p.read_text('utf-8')):
        ARTS[_a['id']] = _a
REP_P = ROOT / 'out' / LV / 'audio' / '核对' / 'report.json'
REP = json.loads(REP_P.read_text('utf-8')) if REP_P.exists() else {}
LET = 'ABCDEFGHIJKLMNOP'
LOW = LV in ('A1', 'A2')
C1 = LV == 'C1'
MISSING = []
DOCS = {'cl': CL, 'ca': CA, 'eie': EIE, 'eio': EIO}
PN = {'cl': 1, 'ca': 2, 'eie': 3, 'eio': 4}
ZH = {'cl': '阅读', 'ca': '听力', 'eie': '写作', 'eio': '口语'}
DEFAULT_ES = {'cl': 'Comprensión de lectura', 'ca': 'Comprensión auditiva', 'eie': 'Expresión e interacción escritas', 'eio': 'Expresión e interacción orales'}
if C1:
    DEFAULT_ES = {'cl': 'Comprensión de lectura y uso de la lengua', 'ca': 'Comprensión auditiva y uso de la lengua',
                  'eie': 'Expresión, mediación e interacción escritas', 'eio': 'Expresión, mediación e interacción orales'}
PES = {k: (DOCS[k].get('prueba') or DEFAULT_ES[k]) for k in DOCS}
TITLE = f'DELE {LV} 模拟卷（非官方）'
DISCLAIMER = ('本卷为原创的非官方模拟练习，按 DELE（对外西班牙语水平证书）公开的考试结构编写，与塞万提斯学院（Instituto Cervantes）没有任何关系，'
              '也未经其审定；所有文章、录音、插图和题目均为原创。')
DISCLAIMER_ES = ('Examen de práctica no oficial, elaborado según la estructura pública de los exámenes DELE. No está vinculado al Instituto Cervantes '
                 'ni ha sido revisado por esta institución. Todos los textos, audios, ilustraciones y tareas son originales.')

e = lambda s: html.escape(str(s), quote=False)


def ol(i):
    """选项字母：A1、A2 印 A) B) C)，B1 起印 a) b) c)。"""
    return (LET[i] if LOW else LET[i].lower()) + ')'


def okey(k):
    return ol(LET.index(k))


CSS = """
@page { size: A4; margin: 17mm 17mm 19mm 17mm; }
* { box-sizing: border-box; }
body { font-family: "Times New Roman", "Songti SC", "STSong", serif; font-size: 10.5pt; line-height: 1.5; color: #111; margin: 0; }
.sans, h1, h2, h3, h4, .tag, th, .cab, .rot, .ejt { font-family: "Helvetica Neue", "PingFang SC", "Heiti SC", sans-serif; }
h1 { font-size: 20pt; margin: 0 0 6pt; line-height: 1.25; }
h2 { font-size: 15pt; margin: 0 0 8pt; padding-bottom: 4pt; border-bottom: 1.4pt solid #222; }
h3 { font-size: 12.5pt; margin: 12pt 0 5pt; break-after: avoid; }
h4 { font-size: 10.5pt; margin: 9pt 0 4pt; break-after: avoid; }
p { margin: 3pt 0; text-align: justify; }
section.pg { break-before: page; }
.inst { background: #f1f1ef; border-left: 2.5pt solid #444; padding: 4pt 8pt; margin: 4pt 0 8pt; font-style: italic; break-inside: avoid; break-after: avoid; }
.inst p { margin: 1.5pt 0; }
.box { border: 0.7pt solid #777; border-radius: 3pt; padding: 6pt 10pt; margin: 6pt 0; break-inside: avoid; }
.box.long, .card.long { break-inside: auto; }
.box .cab { font-weight: 600; font-size: 9.5pt; letter-spacing: .3pt; margin-bottom: 3pt; }
.box p { margin: 2.5pt 0; }
.box p.tt, .art p.tt { font-weight: bold; text-align: left; margin-bottom: 3pt; }
.art p.tt { text-align: center; font-size: 11.5pt; }
.box p.st, .art p.st { font-weight: bold; text-align: left; margin: 6pt 0 1pt; break-after: avoid; }
.box p.hd { font-family: "Helvetica Neue", sans-serif; font-size: 9pt; margin: 0; text-align: left; }
p.fi { text-align: right; font-style: italic; }
p.au { text-align: right; font-size: 9.5pt; font-style: italic; }
.q { margin: 6pt 0 8pt; break-inside: avoid; padding-left: 22pt; text-indent: -22pt; }
.q .n { font-weight: bold; font-family: "Helvetica Neue", sans-serif; display: inline-block; min-width: 19pt; text-indent: 0; }
.q > div, .q > table { text-indent: 0; }
.ej { background: #f4f4f2; border-radius: 3pt; padding-top: 2pt; padding-bottom: 3pt; padding-right: 4pt; }
.ejt { display: inline-block; font-size: 8pt; border: 0.6pt solid #555; border-radius: 6pt; padding: 0 5pt; margin-right: 4pt; vertical-align: 1pt; text-indent: 0; }
p.ejr, .ejr { font-family: "Helvetica Neue", sans-serif; font-size: 9pt; margin: 2pt 0 0; text-indent: 0; }
.opts { list-style: none; padding-left: 0; margin: 2pt 0 0; }
.opts li { margin: 1pt 0; padding-left: 15pt; text-indent: -15pt; }
.opts b, .ol { font-family: "Helvetica Neue", sans-serif; font-weight: bold; margin-right: 4pt; }
.opts li.ok { font-weight: bold; }
.gap { font-family: "Helvetica Neue", sans-serif; font-weight: bold; white-space: nowrap; }
.gap i { display: inline-block; width: 4.2em; border-bottom: 0.7pt solid #111; margin-left: 2pt; }
.pgap { font-family: "Helvetica Neue", sans-serif; font-weight: bold; border: 0.7pt dashed #666; padding: 7pt 8pt; margin: 6pt 0; text-align: left; }
.blank { display: inline-block; min-width: 7em; border-bottom: 0.7pt solid #111; text-align: center; font-family: "Helvetica Neue", sans-serif; font-weight: bold; text-indent: 0; }
table { border-collapse: collapse; width: 100%; margin: 5pt 0; break-inside: avoid; }
th, td { border: 0.6pt solid #888; padding: 2.5pt 5pt; vertical-align: top; font-size: 9.8pt; text-align: left; }
th { background: #ecebe8; font-weight: 600; font-size: 9.3pt; }
td.c, th.c { text-align: center; }
table.long { break-inside: auto; }
table.long tr { break-inside: avoid; }
.grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 6pt 10pt; align-items: start; }
.grid2 .box { margin: 0; }
.grid3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 6pt 8pt; align-items: start; }
.two { display: grid; grid-template-columns: 1fr 1fr; gap: 10pt; align-items: start; }
.tag { display: inline-block; font-size: 8.5pt; border: 0.6pt solid #555; border-radius: 8pt; padding: 0 6pt; margin-left: 6pt; vertical-align: 1pt; font-weight: normal; }
.track { font-family: "Helvetica Neue", "PingFang SC", sans-serif; font-size: 9pt; color: #333; margin: 0 0 3pt; }
.rot { font-size: 8.8pt; font-weight: 600; color: #333; margin-right: 3pt; }
.imgrow { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 6pt; margin: 4pt 0 0; }
.ic { border: 0.6pt solid #999; border-radius: 3pt; padding: 3pt; position: relative; }
.ic.ok { border: 2pt solid #111; }
.ic .il { position: absolute; left: 3pt; top: 2pt; font-family: "Helvetica Neue", sans-serif; font-weight: bold; font-size: 11pt; background: #fff; padding: 0 3pt; border-radius: 2pt; }
img.opt { display: block; width: 100%; height: 33mm; object-fit: contain; }
.imggrid img.opt { height: 40mm; }
img.scene { display: block; max-width: 100%; max-height: 105mm; margin: 4pt auto; border: 0.6pt solid #999; border-radius: 2pt; }
img.ico { float: left; width: 15mm; height: 15mm; object-fit: contain; margin: 0 6pt 2pt 0; }
img.prop { display: block; width: 100%; height: 42mm; object-fit: contain; margin-bottom: 3pt; }
.ph { border: 0.8pt dashed #999; color: #666; font-size: 8pt; font-family: "Helvetica Neue", sans-serif; padding: 3pt; display: flex; align-items: center; justify-content: center; text-align: center; }
div.opt.ph { height: 33mm; }
div.scene.ph { height: 80mm; margin: 4pt 0; }
div.ico.ph { float: left; width: 15mm; height: 15mm; margin: 0 6pt 2pt 0; font-size: 6pt; }
div.prop.ph { height: 42mm; }
.card { border: 0.9pt solid #444; border-radius: 4pt; padding: 7pt 11pt; margin: 8pt 0; break-inside: avoid; }
.card .cab { font-weight: 700; font-size: 10pt; margin-bottom: 4pt; border-bottom: 0.6pt solid #aaa; padding-bottom: 2pt; }
.card ul, ul.pautas { margin: 3pt 0; padding-left: 16pt; }
.card li, ul.pautas li { margin: 1.5pt 0; }
p.pal { font-family: "Helvetica Neue", sans-serif; font-size: 9.5pt; font-weight: 600; margin-top: 5pt; }
.notes { border: 0.7pt solid #777; padding: 2pt 8pt; margin-top: 6pt; }
.notes div { height: 8mm; border-bottom: 0.5pt solid #bbb; }
.cover { height: 250mm; display: flex; flex-direction: column; }
.cover .top { border-top: 4pt solid #222; padding-top: 14pt; }
.cover .sub { font-size: 12pt; color: #333; margin: 2pt 0 16pt; font-family: "Helvetica Neue", "PingFang SC", sans-serif; }
.cover .disc { margin-top: auto; font-size: 8.8pt; color: #444; border-top: 0.6pt solid #999; padding-top: 6pt; }
.small { font-size: 9pt; color: #333; }
.zh { font-family: "Songti SC", "STSong", serif; }
table.par { break-inside: auto; margin: 2pt 0 6pt; }
table.par td { border: none; border-top: 0.4pt dotted #bbb; padding: 2.5pt 6pt 2.5pt 0; font-size: 9.8pt; text-align: left; }
table.par tr { break-inside: avoid; }
table.par tbody.keep { break-inside: avoid; }
table.par tr.lab td { border-top: 0.6pt solid #888; padding-top: 4pt; }
.who { font-family: "Helvetica Neue", sans-serif; font-weight: 600; font-size: 8.8pt; color: #333; }
.key { font-family: "Helvetica Neue", sans-serif; font-weight: bold; }
.expl { margin: 2pt 0 7pt 20pt; font-size: 9.8pt; text-indent: 0; }
.q .expl { margin-left: 0; }
.exam { border: 1pt solid #333; background: #f7f7f5; border-radius: 3pt; padding: 6pt 10pt; margin: 6pt 0; }
.exam p { margin: 2pt 0; }
svg.chart { display: block; margin: 4pt auto; }
/* 答题卡 */
.blocks { display: flex; flex-wrap: wrap; gap: 8pt 12pt; align-items: flex-start; }
.blocks table { width: auto; margin: 0; }
.sheet td, .sheet th { text-align: center; font-family: "Helvetica Neue", sans-serif; font-size: 9.5pt; padding: 2.2pt 4pt; }
.sheet td.l { text-align: left; font-weight: bold; width: 22pt; }
.bub { font-family: "Helvetica Neue", sans-serif; display: inline-block; width: 13.5pt; height: 13.5pt; border: 0.8pt solid #222; border-radius: 50%; font-size: 7.5pt; line-height: 12pt; text-align: center; margin: 0 1.3pt; }
.wbox { display: inline-block; width: 22pt; height: 15pt; border: 0.8pt solid #222; vertical-align: middle; text-align: center; font-family: "Helvetica Neue", sans-serif; font-weight: bold; line-height: 14pt; text-indent: 0; }
.lines { border: 0.8pt solid #444; padding: 2pt 8pt; }
.lines div { height: 8.6mm; border-bottom: 0.5pt solid #aaa; }
.field { display: inline-block; border-bottom: 0.7pt solid #111; min-width: 60mm; height: 12pt; vertical-align: bottom; }
.chk { display: inline-block; width: 10pt; height: 10pt; border: 0.8pt solid #222; vertical-align: -1pt; margin: 0 3pt 0 10pt; }
table.form td { height: 10mm; vertical-align: middle; }
table.form td.fl { width: 38%; font-size: 9.6pt; background: #f6f6f4; }
"""


def doc(title, body):
    return f'<!doctype html><html lang="es"><head><meta charset="utf-8"><title>{e(title)}</title><style>{CSS}</style></head><body>{body}</body></html>'


def nb(s):
    """说明语里的“(1-5)”“(A, B o C)”“45 segundos”“250 y 300”不在中间折行。"""
    return re.sub(r'\([^()<>]{1,14}\)|\d+ (?:segundos|minutos|palabras)|\d+ y \d+',
                  lambda m: f'<span style="white-space:nowrap">{m.group(0)}</span>', s)


def lst(x):
    if x is None:
        return []
    return x if isinstance(x, list) else [x]


def inst(s):
    s = [x for x in lst(s) if x]
    return '<div class="inst">' + ''.join(f'<p>{nb(e(x))}</p>' for x in s) + '</div>' if s else ''


def gaps(s):
    return re.sub(r'\[(\d+)\]', r'<span class="gap">(\1)<i></i></span>', e(s))


def mmss(sec):
    sec = int(round(sec))
    return f'{sec // 60}:{sec % 60:02d}'


def dur(tid):
    return mmss(REP[tid]['duration']) if tid in REP else '—'


def art_img(ref, cls='opt'):
    aid = str(ref)[4:] if str(ref).startswith('art:') else str(ref)
    p = ARTDIR / f'{aid}.png'
    if p.exists():
        return f'<img class="{cls}" src="{p.as_uri()}">'
    MISSING.append(aid)
    a = ARTS.get(aid, {})
    return f'<div class="{cls} ph">[{e(aid)}] {e(a.get("es", ""))}</div>'


ART_PAREN = re.compile(r'画|写字|避免|提示|白底|线条|区分')                   # 括号里的画手注意事项
ART_SENT = re.compile(r'不画|只画|白底|避免|构图|三张|同一个|留一行|单个物品|线条清楚')  # 整句都是给画手的话


def art_zh(ref):
    """插图的中文说明，去掉写给画手的话（括号里的“不写字”“避免提示答案”、“单个物品，白底”之类），只留画面内容。"""
    aid = str(ref)[4:] if str(ref).startswith('art:') else str(ref)
    s = ARTS.get(aid, {}).get('zh', '')
    s = re.sub(r'（[^（）]*）', lambda m: '' if ART_PAREN.search(m.group()) else m.group(), s)
    s = re.sub(r'^[^：。]{0,14}插画：', '', s)
    s = re.sub(r'[，；][^，。；]*不写字', '', s)
    keep = [x for x in re.split(r'(?<=。)', s) if x.strip() and not ART_SENT.search(x)]
    return ''.join(keep).strip() or s


def imgrow(refs, key=None):
    cells = ''.join(f'<div class="ic{" ok" if key == LET[i] else ""}"><span class="il">{LET[i]}</span>{art_img(r)}</div>' for i, r in enumerate(refs))
    return f'<div class="imgrow">{cells}</div>'


def opts_html(o, key=None):
    if o and all(str(x).startswith('art:') for x in o):
        return imgrow(o, key)
    return '<ul class="opts">' + ''.join(f'<li{" class=ok" if key == LET[i] else ""}><b>{ol(i)}</b>{e(x)}</li>' for i, x in enumerate(o)) + '</ul>'


def ej_line(key, letter_only=False):
    shown = key if letter_only else okey(key)
    return f'<p class="ejr">Opción correcta: <b>{e(shown)}</b></p>'


def q_html(q, pre=''):
    ex = q.get('n') == 0
    o = q.get('opciones') or []
    tag = '<span class="ejt">Ejemplo</span>' if ex else ''
    return (f'<div class="q{" ej" if ex else ""}"><span class="n">{q["n"]}.</span> {tag}{pre}{e(q.get("enunciado", ""))}'
            f'{opts_html(o, q.get("clave") if ex else None)}{ej_line(q["clave"]) if ex else ""}</div>')


def textbox(tx, label='', cls='box', gap=False, icon=True):
    f = gaps if gap else e
    h = [f'<div class="{cls}">']
    if label:
        h.append(f'<div class="cab">{e(label)}</div>')
    if icon and str(tx.get('icono', '')).startswith('art:'):
        h.append(art_img(tx['icono'], 'ico'))
    if tx.get('titulo'):
        h.append(f'<p class="tt">{f(tx["titulo"])}</p>')
    for c in lst(tx.get('cabecera')):
        h.append(f'<p class="hd">{e(c)}</p>')
    cu = lst(tx.get('cuerpo'))
    for i, p in enumerate(cu):
        m = re.fullmatch(r'\s*\[(\d+)\]\s*', p)
        h.append(f'<div class="pgap">({m.group(1)})</div>' if (gap and m) else f'<p{subtit(cu, i)}>{f(p)}</p>')
    if tx.get('firma'):
        h.append('<p class="fi">' + '<br>'.join(e(x) for x in str(tx['firma']).split('\n')) + '</p>')
    if tx.get('autor'):
        h.append(f'<p class="au">{e(tx["autor"])}</p>')
    h.append('<div style="clear:both"></div></div>')
    return ''.join(h)


def words_of(x):
    return len(re.findall(r"[0-9A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+", ' '.join(lst(x))))


def subtit(cu, i):
    """正文中间不带句末标点的短段（≤8 词）是小标题，加粗印。"""
    p = cu[i]
    if 0 < i < len(cu) - 1 and isinstance(p, str) and 0 < words_of(p) <= 8 and not re.search(r'[.!?…:;,»"”)\]]\s*$', p):
        return ' class="st"'
    return ''


# ================================================================ 图表（写作的 grafico、口语的 encuesta）
PAL = ['#2b2b2b', '#8a8a8a', '#c4c4c4', '#5a5a5a']


def fmtv(v, unidad=''):
    s = (f'{v:g}' if isinstance(v, (int, float)) else str(v)).replace('.', ',')
    if not unidad:
        return s
    return s + unidad if unidad in ('%', '‰') else f'{s} {unidad}'


def chart(g):
    if not g:
        return ''
    cats = [str(c) for c in g.get('categorias', [])]
    series = g.get('series') or ([{'nombre': '', 'valores': g.get('valores', [])}] if g.get('valores') else [])
    uni = g.get('unidad', '')
    tipo = g.get('tipo', 'barras')
    head = f'<p class="tt" style="text-align:center;font-weight:bold;margin:4pt 0 2pt">{e(g.get("titulo", ""))}</p>' if g.get('titulo') else ''
    foot = f'<p class="small" style="text-align:right">{e(g["fuente"])}</p>' if g.get('fuente') else ''
    if tipo == 'tabla' or not series:
        th = '<tr><th></th>' + ''.join(f'<th class="c">{e(s.get("nombre", ""))}</th>' for s in series) + '</tr>'
        rows = ''.join(f'<tr><td>{e(c)}</td>' + ''.join(f'<td class="c">{e(fmtv(s["valores"][i], uni))}</td>' for s in series) + '</tr>' for i, c in enumerate(cats))
        return f'<div style="break-inside:avoid">{head}<table style="width:80%;margin:4pt auto">{th}{rows}</table>{foot}</div>'
    vals = [v for s in series for v in s.get('valores', []) if isinstance(v, (int, float))]
    vmax = max(vals) if vals else 1
    vmax = vmax * 1.12 or 1
    legend = ''
    if len(series) > 1 or (series and series[0].get('nombre')):
        legend = '<p class="small" style="text-align:center;margin:0">' + '　'.join(
            f'<span style="display:inline-block;width:9pt;height:9pt;background:{PAL[i % 4]};vertical-align:-1pt;margin-right:3pt"></span>{e(s.get("nombre", ""))}'
            for i, s in enumerate(series) if s.get('nombre')) + '</p>'
    if tipo == 'lineas':
        W, H, L, R_, T, B = 460, 230, 46, 16, 14, 34
        n = max(len(cats), 2)
        x = lambda i: L + (W - L - R_) * i / (n - 1)
        y = lambda v: T + (H - T - B) * (1 - v / vmax)
        svg = [f'<svg class="chart" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Helvetica Neue, sans-serif" font-size="10">']
        raw = vmax / 4
        mag = 10 ** math.floor(math.log10(raw)) if raw > 0 else 1
        step = next(m * mag for m in (1, 2, 2.5, 5, 10) if m * mag >= raw)
        vmax = step * 4
        for k in range(5):
            v = step * k
            svg.append(f'<line x1="{L}" x2="{W - R_}" y1="{y(v):.1f}" y2="{y(v):.1f}" stroke="#ddd" stroke-width="0.7"/>'
                       f'<text x="{L - 4}" y="{y(v) + 3:.1f}" text-anchor="end" fill="#555">{e(fmtv(round(v, 1), uni if uni == "%" else ""))}</text>')
        for i, c in enumerate(cats):
            svg.append(f'<text x="{x(i):.1f}" y="{H - B + 14}" text-anchor="middle" fill="#222">{e(c)}</text>')
        for si, s in enumerate(series):
            pts = [(x(i), y(v)) for i, v in enumerate(s.get('valores', [])) if isinstance(v, (int, float))]
            svg.append(f'<polyline fill="none" stroke="{PAL[si % 4]}" stroke-width="2" points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in pts)}"/>')
            for (a, b), v in zip(pts, s.get('valores', [])):
                svg.append(f'<circle cx="{a:.1f}" cy="{b:.1f}" r="3" fill="{PAL[si % 4]}"/><text x="{a:.1f}" y="{b - 6:.1f}" text-anchor="middle" fill="#111">{e(fmtv(v, uni))}</text>')
        svg.append('</svg>')
        return f'<div style="break-inside:avoid">{head}{"".join(svg)}{legend}{foot}</div>'
    # barras（横向，分组）
    ns = len(series)
    bh = 11 if ns > 1 else 14
    W, L = 470, 170
    # 长标签按词折成几行（每行不超过 34 个字符），不截断；行高随行数加高
    labs = [textwrap.wrap(c, 34) or [''] for c in cats]
    ghs = [max(bh * ns + 8, 11 * len(lb) + 6) for lb in labs]
    H = sum(ghs) + 10
    svg = [f'<svg class="chart" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Helvetica Neue, sans-serif" font-size="9.5">']
    for i, c in enumerate(cats):
        y0, gh = 5 + sum(ghs[:i]), ghs[i]
        lb = labs[i]
        ty = y0 + gh / 2 + 3 - 5.5 * (len(lb) - 1)
        svg.append(f'<text x="{L - 6}" y="{ty:.1f}" text-anchor="end" fill="#222">'
                   + ''.join(f'<tspan x="{L - 6}" dy="{0 if k == 0 else 11}">{e(t)}</tspan>' for k, t in enumerate(lb)) + '</text>')
        y0 += (gh - (bh * ns + 8)) / 2
        for si, s in enumerate(series):
            v = s.get('valores', [0] * len(cats))[i]
            w = (W - L - 50) * (v / vmax if isinstance(v, (int, float)) else 0)
            yy = y0 + 4 + si * bh
            svg.append(f'<rect x="{L}" y="{yy}" width="{w:.1f}" height="{bh - 2}" fill="{PAL[si % 4]}"/>'
                       f'<text x="{L + w + 4:.1f}" y="{yy + bh - 4}" fill="#111">{e(fmtv(v, uni))}</text>')
    svg.append(f'<line x1="{L}" x2="{L}" y1="2" y2="{H - 3}" stroke="#555" stroke-width="0.8"/></svg>')
    return f'<div style="break-inside:avoid">{head}{"".join(svg)}{legend}{foot}</div>'


# ================================================================ 每个 tarea 的题号和字母（答题卡、答案速查共用）
def items(part, t):
    """[(题号, 可选字母)]，不含例题。"""
    tipo = t['tipo']
    if part == 'cl':
        if tipo == 'seleccion':
            return [(q['n'], 'ABC') for q in t['preguntas'] if q['n']]
        if tipo == 'relacionar':
            return [(x['n'], LET[:len(t['textos'])]) for x in t['enunciados'] if x['n']]
        if tipo == 'fragmentos':
            return [(h['n'], LET[:len(t['fragmentos'])]) for h in t['huecos']]
        if tipo == 'huecos':
            return [(q['n'], 'ABC') for q in t['preguntas']]
    else:
        if tipo == 'imagenes':
            return [(int(a['id']), 'ABC') for a in t['audios'] if a['id'] != '0']
        if tipo == 'relacionar_imagenes':
            return [(int(a['id']), LET[:len(t['imagenes'])]) for a in t['audios'] if a['id'] != '0']
        if tipo == 'frases':
            return [(i['n'], LET[:len(t['finales'])]) for i in t['inicios'] if i['n']]
        if tipo == 'completar':
            return [(f['n'], LET[:len(t['opciones'])]) for f in t['frases'] if f['n']]
        if tipo == 'seleccion':
            return [(q['n'], 'ABC') for q in t['preguntas'] if q['n']]
        if tipo == 'quien':
            return [(x['n'], 'ABC') for x in t['enunciados']]
        if tipo == 'relacionar':
            return [(int(a['id']), LET[:len(t['frases'])]) for a in t['audios'] if a['id'] != '0']
        if tipo == 'seleccion_multiple':
            return [(n, LET[:len(t['frases'])]) for n in range(1, 7)]
    raise ValueError(f'{part} T{t["n"]} 题型 {tipo} 不认识')


def keys(part, t):
    """{题号: 答案字母}，不含例题。"""
    tipo = t['tipo']
    if tipo in ('seleccion', 'huecos'):
        return {q['n']: q['clave'] for q in t['preguntas'] if q['n']}
    if tipo == 'relacionar' and part == 'cl':
        return {x['n']: x['clave'] for x in t['enunciados'] if x['n']}
    if tipo == 'fragmentos':
        return {h['n']: h['clave'] for h in t['huecos']}
    if tipo in ('imagenes', 'relacionar_imagenes', 'relacionar'):
        return {int(a['id']): a['clave'] for a in t['audios'] if a['id'] != '0'}
    if tipo == 'frases':
        return {i['n']: i['clave'] for i in t['inicios'] if i['n']}
    if tipo == 'completar':
        return {f['n']: f['clave'] for f in t['frases'] if f['n']}
    if tipo == 'quien':
        return {x['n']: x['clave'] for x in t['enunciados']}
    if tipo == 'seleccion_multiple':
        ok = sorted(f['id'] for f in t['frases'] if f.get('correcta') is True)
        return {i + 1: k for i, k in enumerate(ok)}
    raise ValueError(tipo)


NITEMS = {p: sum(len(items(p, t)) for t in DOCS[p]['tareas']) for p in ('cl', 'ca')}


# ================================================================ 考生题册
def ca_track(n):
    return f'DELE_{LV}_CA_T{n}'


CA_MIN = round(REP[f'DELE_{LV}_CA_completa']['duration'] / 60) if f'DELE_{LV}_CA_completa' in REP else CA.get('duracion_min')


def sec_head(part, extra=''):
    d = DOCS[part]
    mins = d.get('duracion_min')
    tag = f'<span class="tag">{mins} minutos</span>' if mins else ''
    return f'<section class="pg"><h2>Prueba {PN[part]} · {e(PES[part])} {tag}{extra}</h2>' + inst(d.get('intro_es'))


def cover():
    rows = []
    for p in ('cl', 'ca', 'eie', 'eio'):
        d = DOCS[p]
        nt = len(d['tareas'])
        cnt = f'{nt} tareas · {NITEMS[p]} preguntas' if p in NITEMS else f'{nt} tareas'
        tm = f'{d.get("duracion_min")} min'
        if p == 'eio':
            tm += f' + {d.get("preparacion_min")} min de preparación'
        rows.append(f'<tr><td>Prueba {PN[p]}</td><td>{e(PES[p])}</td><td>{cnt}</td><td>{tm}</td></tr>')
    notes = ''.join(f'<li>{x}</li>' for x in (
        '四项考试：阅读、听力、写作在同一场连续进行（教师可在听力和写作之间安排休息），口语另行安排，一名考官和一名考生面对面进行。',
        '每项满分 25 分，共 100 分。第 1 组（阅读＋写作）和第 2 组（听力＋口语）各自至少 30 分为“APTO”（通过）。',
        '阅读、听力的答案涂在答题卡（Hoja de respuestas）上，只涂一个圆圈；写作写在答题卡的作文页上。写在题册上的不计分。',
        '听力每段录音放两遍；读题时间、两遍之间的停顿和作答时间都已录在音轨里，中途不要暂停。',
        '口语的考生材料在本册最后（Prueba 4）；准备时间里可以记笔记，考试时可以看笔记，但不能照着念。'))
    return (f'<div class="cover"><div class="top"><h1 class="sans">Examen de práctica no oficial<br>Formato DELE {LV}</h1>'
            f'<div class="sub">{TITLE}　考生题册 · Cuadernillo del candidato</div>'
            f'<table><tr><th style="width:12%">Prueba</th><th>Contenido</th><th style="width:24%">Tareas</th><th style="width:22%">Tiempo</th></tr>{"".join(rows)}</table>'
            f'<h3 class="sans">考生须知</h3><ol class="small">{notes}</ol>'
            f'<p class="small" style="margin-top:14pt">Nombre y apellidos <span class="field"></span>　　Fecha <span class="field" style="min-width:35mm"></span></p></div>'
            f'<div class="disc">{e(DISCLAIMER_ES)}<br>{e(DISCLAIMER)}</div></div>')


# ---------------------------------------------------------------- 阅读
def cl_seleccion(t):
    tx, qs = t['textos'], t['preguntas']
    if len(tx) == 1:
        long = words_of(tx[0].get('cuerpo')) > 330
        return textbox(tx[0], cls='box long' if long else 'box') + ''.join(q_html(q) for q in qs)
    by = {}
    for q in qs:
        by.setdefault(q.get('texto'), []).append(q)
    return ''.join(f'<div style="break-inside:avoid">{textbox(x, "Texto " + str(x["id"]))}{"".join(q_html(q) for q in by.get(x["id"], []))}</div>' for x in tx)


def cl_relacionar(t):
    tx, en = t['textos'], t['enunciados']
    L = LET[:len(tx)]
    if len(tx) <= 4:
        boxes = ''.join(textbox(x, x['id']) for x in tx)
        th = '<tr><th style="width:6%"></th><th>Preguntas</th>' + ''.join(f'<th class="c" style="width:7%">{x}</th>' for x in L) + '</tr>'
        rows = ''.join(f'<tr><td class="key">{x["n"]}.</td><td>{e(x["texto"])}</td>' + '<td></td>' * len(L) + '</tr>' for x in en)
        return boxes + f'<table style="margin-top:8pt">{th}{rows}</table>'
    has_p = any(x.get('persona') for x in en)
    th = '<tr><th style="width:6%"></th>' + ('<th style="width:14%">Persona</th>' if has_p else '') + '<th>Enunciado</th><th class="c" style="width:9%">Texto</th></tr>'
    rows = ''.join(f'<tr{" style=background:#f4f4f2" if x["n"] == 0 else ""}><td class="key">{x["n"]}.</td>' + (f'<td>{e(x.get("persona", ""))}</td>' if has_p else '')
                   + f'<td>{e(x["texto"])}' + (' <span class="ejt">Ejemplo</span>' if x['n'] == 0 else '') + '</td>'
                   + f'<td class="c key">{x["clave"] if x["n"] == 0 else ""}</td></tr>' for x in en)
    long = max(words_of(x.get('cuerpo')) for x in tx) > 70
    grid = ''.join(textbox(x, x['id'], cls='box') for x in tx)
    return f'<table>{th}{rows}</table>' + (f'<div>{grid}</div>' if long else f'<div class="grid2">{grid}</div>')


def article(x):
    """不加框的长文（片段题、完形填空）：标题居中，文中 [n] 印成空。"""
    h = ['<div class="art">']
    if x.get('titulo'):
        h.append(f'<p class="tt">{e(x["titulo"])}</p>')
    for c in lst(x.get('cabecera')):
        h.append(f'<p class="small" style="margin:0">{e(c)}</p>')
    cu = lst(x.get('cuerpo'))
    for i, p in enumerate(cu):
        m = re.fullmatch(r'\s*\[(\d+)\]\s*', p)
        h.append(f'<div class="pgap">({m.group(1)})</div>' if m else f'<p{subtit(cu, i)}>{gaps(p)}</p>')
    if x.get('firma'):
        h.append('<p class="fi">' + '<br>'.join(e(s) for s in str(x['firma']).split('\n')) + '</p>')
    if x.get('autor'):
        h.append(f'<p class="au">{e(x["autor"])}</p>')
    return ''.join(h) + '</div>'


def cl_fragmentos(t):
    fr = ''.join(f'<p><b class="sans">{f["id"]}.</b> {e(f["texto"])}</p>' for f in t['fragmentos'])
    long = sum(words_of(f['texto']) for f in t['fragmentos']) > 250
    return article(t['texto']) + f'<div class="box{" long" if long else ""}"><div class="cab">Fragmentos</div>{fr}</div>'


def cl_huecos(t):
    rows = ''.join(f'<tr><td class="key" style="width:6%">{q["n"]}.</td>' + ''.join(f'<td style="width:31.3%"><span class="ol">{ol(i)}</span>{e(o)}</td>' for i, o in enumerate(q['opciones'])) + '</tr>'
                   for q in t['preguntas'])
    return article(t['texto']) + f'<table class="long" style="margin-top:8pt">{rows}</table>'


R_CL = {'seleccion': cl_seleccion, 'relacionar': cl_relacionar, 'fragmentos': cl_fragmentos, 'huecos': cl_huecos}


def booklet_cl():
    h = [sec_head('cl')]
    for k, t in enumerate(CL['tareas']):
        h.append(('<section class="pg">' if k else '<section>') + f'<h3>Tarea {t["n"]}</h3>' + inst(t['instruccion_es']) + R_CL[t['tipo']](t) + '</section>')
    return ''.join(h) + '</section>'


# ---------------------------------------------------------------- 听力
def rot(a):
    return f'<span class="rot">{e(a["rotulo"])}</span>' if a.get('rotulo') else ''


def ca_imagenes(t):
    out = []
    for a in t['audios']:
        ex = a['id'] == '0'
        tag = '<span class="ejt">Ejemplo</span>' if ex else ''
        out.append(f'<div class="q{" ej" if ex else ""}"><span class="n">{a["id"]}.</span> {tag}{rot(a)}{e(a.get("pregunta_oral", ""))}'
                   f'{imgrow(a["opciones"], a["clave"] if ex else None)}{ej_line(a["clave"]) if ex else ""}</div>')
    return ''.join(out)


def ca_relacionar_imagenes(t):
    rows = ''.join(f'<tr{" style=background:#f4f4f2" if a["id"] == "0" else ""}><td>{e(a.get("rotulo") or "Mensaje " + a["id"])}'
                   + (' <span class="ejt">Ejemplo</span>' if a['id'] == '0' else '') + f'</td><td class="c key">{a["id"]}</td><td class="c key">{a["clave"] if a["id"] == "0" else ""}</td></tr>'
                   for a in t['audios'])
    grid = ''.join(f'<div class="ic"><span class="il">{im["id"]}</span>{art_img(im["art"])}</div>' for im in t['imagenes'])
    return (f'<table style="width:62%;margin:4pt auto 8pt"><tr><th>Mensaje</th><th class="c">Pregunta</th><th class="c">Imagen</th></tr>{rows}</table>'
            f'<div class="imgrow imggrid">{grid}</div>')


def ca_frases(t):
    left = ''.join(f'<p style="text-align:left"><b class="sans">{i["n"]}.</b> {e(i["texto"])} <span class="wbox">{i["clave"] if i["n"] == 0 else ""}</span>'
                   + (' <span class="ejt">Ejemplo</span>' if i['n'] == 0 else '') + '</p>' for i in t['inicios'])
    right = ''.join(f'<p style="text-align:left"><b class="sans">{f["id"]}.</b> {e(f["texto"])}</p>' for f in t['finales'])
    return f'<div class="two"><div class="box"><div class="cab">Frases</div>{left}</div><div class="box"><div class="cab">Opciones</div>{right}</div></div>'


def ca_completar(t):
    op = t['opciones']
    cells = [f'<td><b class="sans">{o["id"]}.</b> {e(o["texto"])}</td>' for o in op]
    while len(cells) % 3:
        cells.append('<td></td>')
    bank = '<table style="margin-bottom:8pt">' + ''.join('<tr>' + ''.join(cells[i:i + 3]) + '</tr>' for i in range(0, len(cells), 3)) + '</table>'
    lines = []
    for f in t['frases']:
        ex = f['n'] == 0
        txt = re.sub(r'_{3,}', f'<span class="blank">{f["clave"] if ex else ""}</span>', e(f['texto']))
        lines.append(f'<div class="q{" ej" if ex else ""}"><span class="n">{f["n"]}.</span> ' + ('<span class="ejt">Ejemplo</span>' if ex else '') + f'{txt}</div>')
    return bank + ''.join(lines)


def ca_seleccion(t):
    au = {a['id']: a for a in t['audios']}
    per = {}
    for q in t['preguntas']:
        per.setdefault(q.get('audio'), []).append(q)
    multi = len(t['audios']) > 1
    out, last = [], None
    for q in t['preguntas']:
        a = au.get(q.get('audio'), {})
        if multi and len(per[q.get('audio')]) > 1:
            if q.get('audio') != last:
                out.append(f'<h4>{e(a.get("rotulo") or "Audio " + str(q.get("audio")))}</h4>')
            out.append(q_html(q))
        else:
            out.append(q_html(q, rot(a) if multi else ''))
        last = q.get('audio')
    return ''.join(out)


def ca_quien(t):
    ps = t['personas']
    th = (f'<tr><th style="width:6%"></th><th>Enunciados</th><th class="c" style="width:12%">A<br>{e(ps["A"])}</th>'
          f'<th class="c" style="width:12%">B<br>{e(ps["B"])}</th><th class="c" style="width:14%">C<br>Ninguno de los dos</th></tr>')
    rows = ''.join(f'<tr><td class="key">{x["n"]}.</td><td>{e(x["texto"])}</td><td></td><td></td><td></td></tr>' for x in t['enunciados'])
    return f'<table>{th}{rows}</table>'


def ca_relacionar(t):
    fr = ''.join(f'<p style="text-align:left"><b class="sans">{f["id"]}.</b> {e(f["texto"])}</p>' for f in t['frases'])
    rows = ''.join(f'<tr{" style=background:#f4f4f2" if a["id"] == "0" else ""}><td>{e(a.get("rotulo") or "Mensaje " + a["id"])}'
                   + (' <span class="ejt">Ejemplo</span>' if a['id'] == '0' else '') + f'</td><td class="c key">{a["id"]}</td><td class="c key">{a["clave"] if a["id"] == "0" else ""}</td></tr>'
                   for a in t['audios'])
    return (f'<div class="box"><div class="cab">Enunciados</div>{fr}</div>'
            f'<table style="width:62%;margin:8pt auto"><tr><th>Audio</th><th class="c">Pregunta</th><th class="c">Enunciado</th></tr>{rows}</table>')


def ca_seleccion_multiple(t):
    fr = ''.join(f'<p style="text-align:left"><b class="sans">{f["id"]}.</b> {e(f["texto"])}</p>' for f in t['frases'])
    return f'<div class="box"><div class="cab">Enunciados</div>{fr}</div>'


R_CA = {'imagenes': ca_imagenes, 'relacionar_imagenes': ca_relacionar_imagenes, 'frases': ca_frases, 'completar': ca_completar,
        'seleccion': ca_seleccion, 'quien': ca_quien, 'relacionar': ca_relacionar, 'seleccion_multiple': ca_seleccion_multiple}


def booklet_ca():
    h = [sec_head('ca')]
    for k, t in enumerate(CA['tareas']):
        h.append(('<section class="pg">' if k else '<section>') + f'<h3>Tarea {t["n"]}</h3><p class="track">♪ Pista: {ca_track(t["n"])}.mp3</p>'
                 + inst(t['instruccion_es']) + R_CA[t['tipo']](t) + '</section>')
    return ''.join(h) + '</section>'


# ---------------------------------------------------------------- 写作
def split_inst(ins):
    """说明语在刺激材料前后各印一部分：从最后一个以冒号结尾的句子起放到材料后面（“Escriba un correo en el que:”）。"""
    ins = [x for x in lst(ins) if x]
    cut = len(ins)
    for i in range(len(ins) - 1, -1, -1):
        if ins[i].rstrip().endswith(':'):
            cut = i
            break
    return ins[:cut], ins[cut:]


def estimulo(st, t):
    if not st:
        return ''
    tp = st.get('tipo')
    h = []
    if tp == 'texto':
        h.append(textbox(st, cls='box long' if words_of(st.get('cuerpo')) > 300 else 'box'))
    elif tp == 'audio':
        a = st.get('audio', {})
        h.append(f'<p class="track">♪ Pista: DELE_{LV}_EIE_T{t["n"]}.mp3</p>')
        if a.get('presentacion'):
            h.append(f'<p><i>{e(a["presentacion"])}</i></p>')
        h.append('<div class="notes"><p class="small" style="margin:2pt 0">Notas</p>' + '<div></div>' * 9 + '</div>')
    elif tp == 'grafico':
        h.append(chart(st.get('grafico') or st))
        for p in lst(st.get('cuerpo')) + lst(st.get('texto')):
            h.append(f'<p>{e(p)}</p>')
    elif tp == 'imagen':
        if st.get('titulo'):
            h.append(f'<p class="tt" style="font-weight:bold">{e(st["titulo"])}</p>')
        h.append(art_img(st.get('art', ''), 'scene'))
        for p in lst(st.get('cuerpo')) + lst(st.get('texto')) + lst(st.get('datos')):
            h.append(f'<p>{e(p)}</p>')
    else:
        h.append(textbox(st))
    return ''.join(h)


def eie_unit(u, t):
    pre, post = split_inst(u.get('instruccion_es'))
    h = [inst(pre), estimulo(u.get('estimulo') or {}, t), inst(post)]
    if u.get('pautas'):
        h.append('<ul class="pautas">' + ''.join(f'<li>{e(p)}</li>' for p in u['pautas']) + '</ul>')
    if t.get('formulario'):
        h.append('<p class="small"><i>Complete el formulario en la Hoja de respuestas.</i></p>')
    w = u.get('palabras') or t.get('palabras')
    if w and not t.get('formulario'):
        h.append(f'<p class="pal">Número de palabras: entre {w[0]} y {w[1]}.</p>')
    return ''.join(h)


def booklet_eie():
    h = [sec_head('eie')]
    for k, t in enumerate(EIE['tareas']):
        h.append(('<section class="pg">' if k else '<section>') + f'<h3>Tarea {t["n"]}</h3>')
        if t.get('opciones'):
            h.append(inst(t.get('instruccion_es')))
            for j, o in enumerate(t['opciones']):
                brk = j and (LV in ("B2", "C1") or 'art:' in json.dumps(o, ensure_ascii=False))   # 带图的选项另起一页，免得图和写作要求分在两页
                h.append(f'<div{" style=break-before:page" if brk else ""}><h4>{e(o.get("titulo") or "Opción " + str(o["id"]))}</h4>{eie_unit(o, t)}</div>')
        else:
            h.append(eie_unit(t, t))
        h.append('</section>')
    return ''.join(h) + '</section>'


# ---------------------------------------------------------------- 口语（考生材料）
def propuestas(ps):
    if not ps:
        return ''
    if all(isinstance(p, str) for p in ps):
        return '<ul>' + ''.join(f'<li>{e(p)}</li>' for p in ps) + '</ul>'
    cells = []
    for p in ps:
        img = art_img(p['art'], 'prop') if str(p.get('art', '')).startswith('art:') else ''
        cells.append(f'<div class="box" style="margin:0"><div class="cab">{e(p.get("id", ""))}{" · " + e(p["titulo"]) if p.get("titulo") else ""}</div>{img}'
                     f'<p style="text-align:left">{e(p.get("descripcion", p.get("texto", "")))}</p></div>')
    return '<div class="grid2">' + ''.join(cells) + '</div>'


def encuesta(en):
    if not en:
        return ''
    h = []
    qs = en.get('preguntas', [])
    if qs:
        h.append('<div class="box"><div class="cab">Encuesta</div>')
        for i, q in enumerate(qs):
            if isinstance(q, str):
                h.append(f'<p style="text-align:left"><b class="sans">{i + 1}.</b> {e(q)}</p>')
            else:
                h.append(f'<p style="text-align:left"><b class="sans">{i + 1}.</b> {e(q.get("texto") or q.get("pregunta", ""))}</p>')
                if q.get('opciones'):
                    h.append('<p style="text-align:left;padding-left:16pt">' + '　'.join(f'<span class="chk" style="margin-left:0"></span>{e(o)}' for o in q['opciones']) + '</p>')
        h.append('</div>')
    if en.get('resultados'):
        h.append('<div class="box"><div class="cab">Resultados de la encuesta</div>' + chart(en['resultados']) + '</div>')
    return ''.join(h)


def card(o, t, multi):
    if not any(o.get(k) for k in ('titulo', 'art', 'texto', 'puntos', 'propuestas', 'encuesta')):
        return ''
    if not multi and not any(o.get(k) for k in ('art', 'texto', 'puntos', 'propuestas', 'encuesta')):
        return ''      # 只有标题的单个选项（如 B1 口语 T2“就 T1 话题交谈”），考生没有材料，不印空框
    lab =(f'Opción {o.get("id")}' if multi else '') + (' · ' if multi and o.get('titulo') else '') + str(o.get('titulo', ''))
    long = words_of(o.get('texto')) > 200
    h = [f'<div class="card{" long" if long else ""}">' + (f'<div class="cab">{e(lab)}</div>' if lab else '')]
    if str(o.get('art', '')).startswith('art:'):
        h.append(art_img(o['art'], 'scene'))
    tx, pu = lst(o.get('texto')), lst(o.get('puntos'))
    if tx and pu and len(tx) == len(pu) and not long:
        # 话题卡：每个方面配一组提示问题（A1 口语 T2 这类）
        h.append('<table>' + ''.join(f'<tr><td style="width:38%"><b>{e(p)}</b></td><td><i>{e(q)}</i></td></tr>' for p, q in zip(pu, tx)) + '</table>')
    else:
        for p in tx:
            h.append(f'<p>{e(p)}</p>')
        if pu:
            h.append('<ul>' + ''.join(f'<li>{e(p)}</li>' for p in pu) + '</ul>')
    h.append(propuestas(o.get('propuestas')))
    h.append(encuesta(o.get('encuesta')))
    return ''.join(h) + '</div>'


def booklet_eio():
    tag = f'<span class="tag">Preparación: {EIO.get("preparacion_min")} minutos</span>'
    h = [sec_head('eio', tag) + '<p class="small"><i>Material del candidato. En el examen real, el entrevistador le entrega estas láminas; en este modelo las fotografías son ilustraciones.</i></p>']
    for k, t in enumerate(EIO['tareas']):
        mins = t.get('minutos')
        mt = f'<span class="tag">{mins[0]}-{mins[1]} minutos</span>' if isinstance(mins, list) and len(mins) == 2 else (f'<span class="tag">{mins} minutos</span>' if mins else '')
        pt = '<span class="tag">Con preparación</span>' if t.get('preparacion') else '<span class="tag">Sin preparación</span>'
        ops = t.get('opciones', [])
        cards = [card(o, t, len(ops) > 1) for o in ops]
        # 没有插图、卡片很短（或没有卡片）的 tarea 不另起一页，接在上一个 tarea 后面
        light = not any(str(o.get('art', '')).startswith('art:') for o in ops) and len(re.findall(r'\w+', re.sub(r'<[^>]+>', ' ', ''.join(cards)))) < 60
        h.append(('<section class="pg">' if k and not light else '<section style="margin-top:14pt">' if k else '<section>')
                 + f'<h3>Tarea {t["n"]} · {e(t.get("titulo_es", ""))}{mt}{pt}</h3>' + inst(t.get('instruccion_es')))
        for j, o in enumerate(ops):
            brk = j and (words_of(o.get('texto')) > 200 or str(o.get('art', '')).startswith('art:') and len(ops) > 1 and LV != 'A1')
            h.append(('<div style="break-before:page"></div>' if brk else '') + cards[j])
        h.append('</section>')
        if light and k:
            print(f'  口语 Tarea {t["n"]} 卡片很短，接在上一个 tarea 后面，不另起一页')
    return ''.join(h) + '</section>'


# ================================================================ 答题卡
def bub(letters):
    return ''.join(f'<span class="bub">{x}</span>' for x in letters)


def sheet_block(cap, rows):
    return (f'<table class="sheet"><tr><th colspan="2">{e(cap)}</th></tr>'
            + ''.join(f'<tr><td class="l">{n}</td><td style="text-align:left">{bub(L)}</td></tr>' for n, L in rows) + '</table>')


def sheet_part(part):
    d = DOCS[part]
    blocks = ''.join(sheet_block(f'Tarea {t["n"]}', items(part, t)) for t in d['tareas'])
    n = NITEMS[part]
    score = (f'<table style="margin-top:10pt;width:100%"><tr><th>Para el examinador · 教师填写</th><th class="c">Aciertos (0-{n})</th>'
             f'<th class="c">Puntuación (aciertos × 25 ÷ {n})</th></tr><tr><td>{e(PES[part])}</td><td style="height:9mm"></td><td></td></tr></table>')
    return f'<h3>Prueba {PN[part]} · {e(PES[part])}</h3><div class="blocks">{blocks}</div>{score}'


def lines(k):
    return '<div class="lines">' + '<div></div>' * k + '</div>'


def sheet_head(sub):
    return (f'<h2 class="sans">DELE {LV} · Hoja de respuestas <span class="tag">Examen de práctica no oficial</span></h2>'
            f'<p>Nombre y apellidos <span class="field"></span>　Fecha <span class="field" style="min-width:30mm"></span></p>'
            f'<p class="small">{sub}</p>')


def form_html(fo):
    rows = []
    for f in fo:
        if f.get('tipo') == 'largo':
            w = f.get('palabras') or [10, 15]
            k = max(2, math.ceil(w[1] / 8))
            rows.append(f'<tr><td class="fl">{e(f["campo"])}</td><td style="padding:0 6pt">'
                        + ''.join('<div style="height:8.6mm;border-bottom:0.5pt solid #aaa"></div>' for _ in range(k)) + '</td></tr>')
        else:
            rows.append(f'<tr><td class="fl">{e(f["campo"])}</td><td></td></tr>')
    return '<table class="form">' + ''.join(rows) + '</table>'


def sheet():
    h = ['<section>' + sheet_head('Marque una sola opción en cada pregunta: rellene el círculo (●). Use lápiz o bolígrafo negro. 每题只涂一个圆圈。')
         + sheet_part('cl') + '</section>']
    h.append('<section class="pg">' + sheet_head('Marque una sola opción en cada pregunta: rellene el círculo (●). 每题只涂一个圆圈。') + sheet_part('ca') + '</section>')
    for t in EIE['tareas']:
        cap = f'Prueba 3 · {e(PES["eie"])} · Tarea {t["n"]}'
        if t.get('formulario'):
            h.append(f'<section class="pg"><h2 class="sans" style="font-size:13pt">{cap}</h2><p class="small">Complete el formulario.</p>{form_html(t["formulario"])}</section>')
            continue
        w = t.get('palabras') or (t['opciones'][0].get('palabras') if t.get('opciones') else None) or [100, 150]
        nl = max(7, math.ceil(w[1] / 9) + 3)
        ch = ''
        if t.get('opciones'):
            ch = '<p>Opción elegida:' + ''.join(f'<span class="chk"></span>{e(o.get("titulo") or "Opción " + str(o["id"]))}　' for o in t['opciones']) + '</p>'
        first = min(nl, 24)
        h.append(f'<section class="pg"><h2 class="sans" style="font-size:13pt">{cap}</h2>{ch}<p class="small">Número de palabras: entre {w[0]} y {w[1]}.</p>{lines(first)}'
                 + ('' if nl > first else '<p style="text-align:right">Número de palabras: <span class="field" style="min-width:25mm"></span></p>') + '</section>')
        if nl > first:
            h.append(f'<section class="pg"><h2 class="sans" style="font-size:13pt">{cap} (continuación)</h2>{lines(nl - first)}'
                     '<p style="text-align:right">Número de palabras: <span class="field" style="min-width:25mm"></span></p></section>')
    return ''.join(h)


# ================================================================ 教师用书
def par_rows(segs, label=None):
    rows = f'<tr class="lab"><td colspan="2" class="who">{label}</td></tr>' if label else ''
    for s in segs:
        who = f'<span class="who">{e(s["who"])}：</span>' if s.get('who') else ''
        rows += f'<tr><td>{who}{e(s["es"])}</td><td class="zh">{e(s.get("zh", ""))}</td></tr>'
    return f'<tbody class="{"keep" if len(segs) <= 3 else ""}">{rows}</tbody>'


def par_table(body):
    return f'<table class="par"><colgroup><col style="width:52%"><col style="width:48%"></colgroup>{body}</table>'


def par_text(x, label=None):
    """文本原文和译文逐段对照。"""
    es = []
    if x.get('titulo'):
        es.append(x['titulo'])
    es += lst(x.get('cabecera')) + lst(x.get('cuerpo')) + ([x['firma']] if x.get('firma') else [])
    zh = lst(x.get('zh'))
    body = lst(x.get('cuerpo'))
    rows = f'<tr class="lab"><td colspan="2" class="who">{e(label)}</td></tr>' if label else ''
    # 标题和第一段放在同一行，免得标题单独落在页底；标题译文用 titulo_zh
    pre_es = f'<b>{gaps(x["titulo"])}</b><br>' if x.get('titulo') else ''
    pre_zh = f'<b>{e(x["titulo_zh"])}</b><br>' if x.get('titulo') and x.get('titulo_zh') else ''
    cab = lst(x.get('cabecera'))
    for c in cab:
        rows += f'<tr><td class="small">{pre_es}{e(c)}</td><td class="zh">{pre_zh}</td></tr>'
        pre_es = pre_zh = ''
    if (pre_es or pre_zh) and not body:
        rows += f'<tr><td>{pre_es}</td><td class="zh">{pre_zh}</td></tr>'
    for i, p in enumerate(body):
        st = ' class="st"' if subtit(body, i) else ''
        rows += f'<tr><td{st}>{pre_es}{gaps(p)}</td><td class="zh">{pre_zh}{e(zh[i]) if i < len(zh) else ""}</td></tr>'
        pre_es = pre_zh = ''
    for i in range(len(body), len(zh)):
        rows += f'<tr><td></td><td class="zh">{e(zh[i])}</td></tr>'
    if x.get('firma'):
        rows += f'<tr><td><i>{e(x["firma"])}</i></td><td></td></tr>'
    return f'<tbody class="{"keep" if len(body) <= 2 else ""}">{rows}</tbody>'


def expl(s):
    return f'<div class="expl">{e(s)}</div>' if s else ''


def kq(n, txt, key, extra=''):
    return f'<div class="q"><span class="n">{n}.</span> {txt} <span class="key">答案 {key}</span>{extra}'


def t_head(t, part):
    tr = f'<span class="tag">{ca_track(t["n"])}.mp3 · {dur(ca_track(t["n"]))}</span>' if part == 'ca' else ''
    return (f'<h3>Tarea {t["n"]}{tr}</h3><p class="small"><b>话题：</b>{e(t.get("tema_zh", ""))}　<b>说明语译文：</b>{e(t.get("instruccion_zh", ""))}</p>')


def opt_line(o, key):
    return '　'.join(f'<span{" class=key" if LET[i] == key else ""}>{ol(i)} {e(x)}</span>' for i, x in enumerate(o))


def teach_cl():
    h = ['<section class="pg"><h2>三、阅读：译文与解析</h2>']
    for t in CL['tareas']:
        h.append(t_head(t, 'cl'))
        tp = t['tipo']
        if tp == 'seleccion':
            h.append(par_table(''.join(par_text(x, ('Texto ' + str(x['id'])) if len(t['textos']) > 1 else None) for x in t['textos'])))
            h.append('<h4>答案与解析</h4>')
            for q in t['preguntas']:
                o = q['opciones']
                if all(str(x).startswith('art:') for x in o):
                    ol_ = '；'.join(f'{ol(i)} {e(art_zh(x))}' for i, x in enumerate(o))
                    h.append(kq(q['n'], e(q.get('enunciado', '')), okey(q['clave'])) + f'<div class="small">图片：{ol_}</div>{expl(q.get("explicacion"))}</div>')
                else:
                    h.append(kq(q['n'], e(q.get('enunciado', '')), okey(q['clave'])) + f'<div class="small">{opt_line(o, q["clave"])}</div>{expl(q.get("explicacion"))}</div>')
        elif tp == 'relacionar':
            h.append(par_table(''.join(par_text(x, f'Texto {x["id"]}') for x in t['textos'])))   # 小图标只是装饰，教师用书不印说明
            h.append('<h4>答案与解析</h4>')
            used = []
            for x in t['enunciados']:
                used.append(x['clave'])
                who = f'{e(x["persona"])}：' if x.get('persona') else ''
                h.append(kq(x['n'], f'{who}{e(x["texto"])}<span class="small">（{e(x.get("zh", ""))}）</span>', x['clave'] + ('（例题）' if x['n'] == 0 else '')) + f'{expl(x.get("explicacion"))}</div>')
            un = [L for L in LET[:len(t['textos'])] if L not in used]
            if un:
                h.append(f'<p class="small">没有用到的文本：{"、".join(un)}。</p>')
        elif tp == 'fragmentos':
            x = t['texto']
            kmap = {h_['n']: h_['clave'] for h_ in t['huecos']}
            filled = dict(x)
            filled['cuerpo'] = [re.sub(r'\[(\d+)\]', lambda m: f'[{m.group(1)}]→{kmap.get(int(m.group(1)), "?")}', p) for p in lst(x.get('cuerpo'))]
            h.append(par_table(par_text(filled, x.get('titulo') and None)))
            h.append('<h4>片段</h4>' + par_table(''.join(f'<tr><td><b class="sans">{f["id"]}.</b> {e(f["texto"])}</td><td class="zh">{e(f.get("zh", ""))}</td></tr>' for f in t['fragmentos'])))
            h.append('<h4>答案与解析</h4>')
            fr = {f['id']: f['texto'] for f in t['fragmentos']}
            for g in t['huecos']:
                h.append(kq(g['n'], '', g['clave']) + f' <span class="small">{e(fr.get(g["clave"], "")[:90])}{"…" if len(fr.get(g["clave"], "")) > 90 else ""}</span>{expl(g.get("explicacion"))}</div>')
            for dd in t.get('distractores', []):
                h.append(f'<div class="q"><span class="n">{dd["id"]}</span> <span class="key">不用的片段</span>{expl(dd.get("explicacion"))}</div>')
        elif tp == 'huecos':
            h.append(par_table(par_text(t['texto'])))
            h.append('<h4>答案与解析</h4>')
            for q in t['preguntas']:
                h.append(kq(q['n'], '', okey(q['clave'])) + f' <span class="small">（{e(q.get("foco", ""))}）{opt_line(q["opciones"], q["clave"])}</span>{expl(q.get("explicacion"))}</div>')
    return ''.join(h) + '</section>'


def audio_label(a):
    lab = e(a.get('rotulo') or '')
    if a.get('presentacion'):
        lab += ('　' if lab else '') + f'<span style="font-weight:normal">（{e(a["presentacion"])}）</span>'
    return lab or None


def transcript(t):
    body = ''
    for a in t['audios']:
        segs = list(a.get('segs', []))
        if a.get('pregunta_oral'):
            segs = segs + [{'who': 'Pregunta', 'es': a['pregunta_oral'], 'zh': ''}]
        body += par_rows(segs, audio_label(a))
    return par_table(body)


def teach_ca():
    h = ['<section class="pg"><h2>四、听力：原文、译文与解析</h2>'
         '<p class="small">左栏为录音原文，右栏为中文译文。播音员读的说明语、编号（“Conversación número uno.”等）和读题提示不列出；说明语原文见考生题册。</p>']
    for t in CA['tareas']:
        h.append(t_head(t, 'ca'))
        tp = t['tipo']
        if tp == 'frases':
            a = t['audios'][0]
            h.append(par_table(par_rows(a['segs'], audio_label(a))))
        else:
            h.append(transcript(t))
        h.append('<h4>答案与解析</h4>')
        if tp == 'imagenes':
            for a in t['audios']:
                pics = '；'.join(f'<span{" class=key" if LET[i] == a["clave"] else ""}>{LET[i]} {e(art_zh(x))}</span>' for i, x in enumerate(a['opciones']))
                h.append(kq(a['id'], e(a.get('pregunta_oral', '')), a['clave'] + ('（例题）' if a['id'] == '0' else '')) + f'<div class="small">图片：{pics}</div>{expl(a.get("explicacion"))}</div>')
        elif tp == 'relacionar_imagenes':
            h.append('<p class="small">图片：' + '；'.join(f'{im["id"]} {e(art_zh(im["art"]))}' for im in t['imagenes']) + '</p>')
            for a in t['audios']:
                h.append(kq(a['id'], e(a.get('rotulo', '')), a['clave'] + ('（例题）' if a['id'] == '0' else '')) + f'{expl(a.get("explicacion"))}</div>')
            un = [im['id'] for im in t['imagenes'] if im['id'] not in {a['clave'] for a in t['audios']}]
            h.append(f'<p class="small">没有用到的图片：{"、".join(un)}。</p>')
        elif tp == 'frases':
            fin = {f['id']: f for f in t['finales']}
            for i in t['inicios']:
                f = fin.get(i['clave'], {})
                h.append(kq(i['n'], e(i['texto']), i['clave'] + ('（例题）' if i['n'] == 0 else '')) + f' {e(f.get("texto", ""))}<span class="small">（{e(f.get("zh", ""))}）</span>{expl(i.get("explicacion"))}</div>')
            un = [f for f in t['finales'] if f['id'] not in {i['clave'] for i in t['inicios']}]
            h.append('<p class="small">没有用到的结尾：' + '；'.join(f'{f["id"]} {e(f["texto"])}（{e(f.get("zh", ""))}）' for f in un) + '</p>')
        elif tp == 'completar':
            op = {o['id']: o['texto'] for o in t['opciones']}
            for f in t['frases']:
                h.append(kq(f['n'], e(f['texto']), f'{f["clave"]}（{e(op.get(f["clave"], ""))}）' + ('（例题）' if f['n'] == 0 else '')) + f'{expl(f.get("explicacion"))}</div>')
            un = [k for k in op if k not in {f['clave'] for f in t['frases']}]
            h.append('<p class="small">没有用到的选项：' + '、'.join(f'{k}（{e(op[k])}）' for k in un) + '</p>')
        elif tp == 'seleccion':
            for q in t['preguntas']:
                h.append(kq(q['n'], e(q.get('enunciado', '')), okey(q['clave']) + ('（例题）' if q['n'] == 0 else '')) + f'<div class="small">{opt_line(q["opciones"], q["clave"])}</div>{expl(q.get("explicacion"))}</div>')
        elif tp == 'quien':
            ps = t['personas']
            name = {'A': f'A（{ps["A"]}）', 'B': f'B（{ps["B"]}）', 'C': 'C（Ninguno de los dos，两人都没说）'}
            for x in t['enunciados']:
                h.append(kq(x['n'], f'{e(x["texto"])}<span class="small">（{e(x.get("zh", ""))}）</span>', e(name.get(x['clave'], x['clave']))) + f'{expl(x.get("explicacion"))}</div>')
        elif tp == 'relacionar':
            fr = {f['id']: f for f in t['frases']}
            for a in t['audios']:
                f = fr.get(a['clave'], {})
                h.append(kq(a['id'], e(a.get('rotulo', '')), a['clave'] + ('（例题）' if a['id'] == '0' else '')) + f' {e(f.get("texto", ""))}<span class="small">（{e(f.get("zh", ""))}）</span>{expl(a.get("explicacion"))}</div>')
            un = [f for f in t['frases'] if f['id'] not in {a['clave'] for a in t['audios']}]
            h.append('<p class="small">没有用到的陈述：' + '；'.join(f'{f["id"]} {e(f["texto"])}（{e(f.get("zh", ""))}）' for f in un) + '</p>')
        elif tp == 'seleccion_multiple':
            ok = sorted(f['id'] for f in t['frases'] if f.get('correcta') is True)
            h.append(f'<p>正确的六项（按字母顺序依次填在第 1—6 题）：<span class="key">{"、".join(ok)}</span></p>')
            for f in t['frases']:
                mark = '<span class="key">✓ 符合</span>' if f.get('correcta') is True else '<span class="small">✗ 不符合</span>'
                h.append(f'<div class="q"><span class="n">{f["id"]}.</span> {e(f["texto"])}<span class="small">（{e(f.get("zh", ""))}）</span> {mark}{expl(f.get("explicacion"))}</div>')
    return ''.join(h) + '</section>'


# ---------------------------------------------------------------- 评分（按 考试规格.md；官方量表的权重之外是本卷的做法）
BANDS = [('3', '完全达到本级要求：任务全部完成，表达恰当、清楚，词汇和语法准确、有一定变化，错误很少且不影响理解。'),
         ('2', '达到本级要求（及格水平）：任务基本完成，意思清楚；有一些错误，但基本不影响理解。'),
         ('1', '低于本级要求：只完成部分任务，表达有限，错误较多，有时影响理解。'),
         ('0', '没有作答、离题、无法理解，或全部是背诵的材料。')]

SC_EIE = {
    'A1': ([('整体评分（0—3）', None)], '每个 tarea 用整体量表给一个分（0—3，2 分＝达到 A1）。写作得分 =（T1 + T2）÷ 2 × 25 ÷ 3。'
                                    'Tarea 2 少于 20 词不评分（0 分），20—29 词最高 1 分。'),
    'A2': ([('语言运用（66%）', .66), ('完成任务（34%）', .34)], '每个 tarea：0.66 × 语言运用 + 0.34 × 完成任务。写作得分 =（T1 + T2）÷ 2 × 25 ÷ 3。'),
    'B1': ([('文体适切', None), ('连贯', None), ('准确', None), ('广度', None), ('整体', None)],
           '每个 tarea：分析量表四项（Adecuación、Coherencia、Corrección、Alcance）取平均，占 60%；整体量表占 40%。写作得分 =（T1 + T2）÷ 2 × 25 ÷ 3。'),
    'B2': ([('文体适切', None), ('连贯', None), ('准确', None), ('广度', None), ('整体', None)],
           '每个 tarea：分析量表四项（Adecuación、Coherencia、Corrección、Alcance）取平均，占 60%；整体量表占 40%。写作得分 =（T1 + T2）÷ 2 × 25 ÷ 3。'),
    'C1': ([('连贯与衔接 22%', .22), ('准确 22%', .22), ('广度 22%', .22), ('中介/适切与完成 34%', .34)],
           '只用分析量表。每个 tarea：0.22 ×（连贯与衔接 + 准确 + 广度）+ 0.34 × 完成度（Tarea 1 为 Mediación y cumplimiento，Tarea 2 为 Adecuación y cumplimiento）。写作得分 =（T1 + T2）÷ 2 × 25 ÷ 3。'),
}
SC_EIO = {
    'A1': (['T1', 'T2', 'T3'], [('语言运用 66%', .66), ('完成任务 34%', .34)], (.20, .35, .45),
           '评分员（calificador）给每个 tarea 打两个分：0.66 × 语言运用 + 0.34 × 完成任务；三个 tarea 按 20%、35%、45% 加权，得评分员分 R。'
           '考官（entrevistador）听完整场后用整体量表给一个分 H（0—3）。口语得分 =（0.6 × R + 0.4 × H）× 25 ÷ 3。'),
    'A2': (['T1', 'T2', 'T3'], [('语言运用 66%', .66), ('完成任务 34%', .34)], (.25, .25, .50),
           '评分员给每个 tarea 打两个分：0.66 × 语言运用 + 0.34 × 完成任务；三个 tarea 按 25%、25%、50% 加权，得评分员分 R。'
           '考官用整体量表给一个分 H（0—3）。口语得分 =（0.6 × R + 0.4 × H）× 25 ÷ 3。'),
    'B1': (['T1＋T2', 'T3＋T4'], [('连贯', None), ('流利', None), ('准确', None), ('广度', None)], (.5, .5),
           '评分员用分析量表（Coherencia、Fluidez、Corrección、Alcance，各 0—3）打两次：T1＋T2 一次，T3＋T4 一次；每次四项取平均，两次再平均，得 R。'
           '考官用整体量表给一个分 H（0—3）。口语得分 =（0.6 × R + 0.4 × H）× 25 ÷ 3。'),
    'B2': (['T1', 'T2', 'T3'], [('连贯', None), ('流利', None), ('准确', None), ('广度', None)], (.35, .35, .30),
           '评分员用分析量表（Coherencia、Fluidez、Corrección、Alcance，各 0—3）给每个 tarea 打分，四项取平均；三个 tarea 按 35%、35%、30% 加权，得 R。'
           '考官用整体量表给一个分 H（0—3）。口语得分 =（0.6 × R + 0.4 × H）× 25 ÷ 3。'),
    'C1': (['T1', 'T2', 'T3'], [('流利 22%', .22), ('准确 22%', .22), ('广度 22%', .22), ('完成度 34%', .34)], (1 / 3, 1 / 3, 1 / 3),
           '评分员用分析量表给每个 tarea 打分：0.22 ×（Fluidez + Corrección + Alcance）+ 0.34 × 完成度（T1 Mediación、T2 Entrevista、T3 Interacción y cumplimiento）；'
           '三个 tarea 等权，得 R。考官用整体量表给一个分 H（0—3）。口语得分 =（0.6 × R + 0.4 × H）× 25 ÷ 3。'),
}


def crit_table(d):
    cr = d.get('criterios', [])
    if not cr:
        return ''
    return '<table><tr><th style="width:30%">评分项</th><th>看什么</th></tr>' + ''.join(f'<tr><td class="sans">{e(c.get("es", ""))}</td><td>{e(c.get("zh", ""))}</td></tr>' for c in cr) + '</table>'


def bands_block(d):
    """编写者已在评分项里写了分档（“3 puntos”这类），就不再印通用分档。"""
    if any(re.match(r'\s*\d', c.get('es', '')) or 'punto' in c.get('es', '').lower() for c in d.get('criterios', [])):
        return ''
    return '<h3>分档</h3>' + bands_table()


def bands_table():
    return ('<table><tr><th style="width:7%" class="c">分</th><th>每个评分项的分档（本卷为课堂评分自拟的简化描述）</th></tr>'
            + ''.join(f'<tr><td class="c key">{a}</td><td>{b}</td></tr>' for a, b in BANDS) + '</table>')


def model_html(m, label='范文'):
    if not m:
        return ''
    txt = lst(m.get('texto'))
    long = words_of(txt) > 150
    nw = m.get('palabras') or words_of(txt)
    h = [f'<h4>{label}（{nw} 词）</h4><div class="box{" long" if long else ""}">' + ''.join(f'<p>{e(p)}</p>' for p in txt) + '</div>']
    if m.get('zh'):
        h.append('<p class="small"><b>译文：</b>' + ''.join(e(z) for z in lst(m['zh'])) + '</p>')
    if m.get('comentario_zh'):
        h.append(f'<p><b>点评：</b>{e(m["comentario_zh"])}</p>')
    return ''.join(h)


def stim_teacher(st, t):
    if not st:
        return ''
    tp = st.get('tipo')
    if tp == 'texto':
        return '<h4>材料原文与译文</h4>' + par_table(par_text(st))
    if tp == 'audio':
        a = st.get('audio', {})
        tid = f'DELE_{LV}_EIE_T{t["n"]}'
        return (f'<h4>录音原文与译文 <span class="tag">{tid}.mp3 · {dur(tid)}</span></h4>'
                + par_table(par_rows(a.get('segs', []), e(a['presentacion']) if a.get('presentacion') else None)))
    if tp == 'grafico':
        g = st.get('grafico') or st
        return f'<p class="small"><b>图表：</b>{e(g.get("titulo", ""))}（{e(g.get("fuente", ""))}）{e(st.get("zh", "") if isinstance(st.get("zh"), str) else "".join(lst(st.get("zh"))))}</p>'
    if tp == 'imagen':
        return f'<p class="small"><b>图片：</b>{e(art_zh(st.get("art", "")))}　{e("".join(lst(st.get("zh"))))}</p>'
    return ''


def teach_eie():
    fs = SC_EIE[LV]
    h = ['<section class="pg"><h2>五、写作：评分、材料与范文</h2>', '<h3>评分项</h3>', crit_table(EIE), bands_block(EIE),
         f'<h3>计分方法</h3><p>{fs[1]}</p><p class="small">各评分项和权重按官方考试说明；分档描述和组合方式是本卷为课堂评分设计的，结果只作练习参考。</p>']
    for t in EIE['tareas']:
        h.append(f'<h3>Tarea {t["n"]}</h3><p class="small"><b>说明语译文：</b>{e(t.get("instruccion_zh", ""))}</p>')
        if t.get('formulario'):
            h.append(stim_teacher(t.get('estimulo') or {}, t))
            h.append('<h4>表格与参考答案</h4><table><tr><th style="width:40%">栏目</th><th>参考答案</th></tr>'
                     + ''.join(f'<tr><td>{e(f["campo"])}</td><td>{e(f.get("modelo", ""))}</td></tr>' for f in t['formulario']) + '</table>')
            m = t.get('modelo') or {}
            if lst(m.get('texto')):
                h.append(model_html(m))
            else:
                if m.get('zh'):
                    h.append('<p class="small"><b>参考答案译文：</b>' + ''.join(e(z) for z in lst(m['zh'])) + '</p>')
                if m.get('comentario_zh'):
                    h.append(f'<p><b>点评：</b>{e(m["comentario_zh"])}</p>')
            continue
        units = t.get('opciones') or [t]
        for u in units:
            if t.get('opciones'):
                h.append(f'<h4 style="font-size:11pt">{e(u.get("titulo") or "Opción " + str(u.get("id")))}</h4>')
                if u.get('instruccion_zh'):
                    h.append(f'<p class="small"><b>说明语译文：</b>{e(u["instruccion_zh"])}</p>')
            h.append(stim_teacher(u.get('estimulo') or {}, t))
            h.append(model_html(u.get('modelo')))
    return ''.join(h) + '</section>'


def teach_eio():
    fs = SC_EIO[LV]
    prep = [str(t['n']) for t in EIO['tareas'] if t.get('preparacion')]
    h = ['<section class="pg"><h2>六、口语：实施、考官材料与参考回答</h2>',
         f'<h3>实施</h3><p>考试时间 {EIO.get("duracion_min")} 分钟，考前准备 {EIO.get("preparacion_min")} 分钟（准备 Tarea {"、".join(prep)}）。'
         '考生在准备室拿到考生材料（考生题册 Prueba 4），可以记笔记；进考场后由考官主持，另有一名评分员只听不说（课堂上可由同一位教师兼任，建议录音后再评分）。'
         '每个 tarea 的时间见下；考官按“考官材料”里的话和问题进行，不要提示答案，时间到就进入下一项。</p>'
         '<table><tr><th style="width:10%">Tarea</th><th>任务</th><th style="width:14%">时长</th><th style="width:14%">准备</th></tr>'
         + ''.join(f'<tr><td>Tarea {t["n"]}</td><td>{e(t.get("titulo_es", ""))}</td><td>{"—".join(str(x) for x in lst(t.get("minutos")))} 分钟</td><td>{"有" if t.get("preparacion") else "无"}</td></tr>' for t in EIO['tareas'])
         + '</table>', '<h3>评分项</h3>', crit_table(EIO), bands_block(EIO), f'<h3>计分方法</h3><p>{fs[3]}</p>']
    for t in EIO['tareas']:
        mins = '—'.join(str(x) for x in lst(t.get('minutos')))
        h.append(f'<section class="pg"><h3>Tarea {t["n"]} · {e(t.get("titulo_es", ""))} <span class="tag">{mins} 分钟</span></h3>'
                 f'<p class="small"><b>说明语译文：</b>{e(t.get("instruccion_zh", ""))}</p>')
        ex = t.get('examinador') or {}
        h.append('<div class="exam"><p class="sans" style="font-weight:700">Hoja del entrevistador · 考官材料</p>'
                 + ''.join(f'<p>{e(g)}</p>' for g in lst(ex.get('guion')))
                 + (('<p class="sans small" style="margin-top:4pt"><b>Preguntas</b></p><ul>' + ''.join(f'<li>{e(q)}</li>' for q in lst(ex.get('preguntas'))) + '</ul>') if ex.get('preguntas') else '')
                 + (f'<p class="small"><b>考官提示：</b>{e(ex["notas_zh"])}</p>' if ex.get('notas_zh') else '') + '</div>')
        for o in t.get('opciones', []):
            lab = (f'Opción {o.get("id")}' if len(t.get('opciones', [])) > 1 else '') + (' · ' if len(t.get('opciones', [])) > 1 and o.get('titulo') else '') + str(o.get('titulo', ''))
            h.append(f'<h4>{e(lab)}</h4>')
            if str(o.get('art', '')).startswith('art:'):
                h.append(f'<p class="small"><b>照片内容：</b>{e(art_zh(o["art"]))}</p>')
            if o.get('texto_zh'):
                h.append(f'<p class="small"><b>{"文章译文" if words_of(o.get("texto")) > 200 else "考生材料译文"}：</b>' + ''.join(e(z) for z in lst(o['texto_zh'])) + '</p>')
            for p in o.get('propuestas') or []:
                if isinstance(p, dict) and str(p.get('art', '')).startswith('art:'):
                    h.append(f'<p class="small"><b>方案 {e(p.get("id", ""))}：</b>{e(art_zh(p["art"]))}</p>')
            if o.get('modelo'):
                h.append('<p class="sans small" style="margin-top:4pt"><b>参考回答</b></p><div class="box long">' + ''.join(f'<p>{e(p)}</p>' for p in lst(o['modelo'])) + '</div>')
            if o.get('modelo_zh'):
                h.append('<p class="small"><b>参考回答译文：</b>' + ''.join(e(z) for z in lst(o['modelo_zh'])) + '</p>')
        h.append('</section>')
    return ''.join(h) + '</section>'


# ---------------------------------------------------------------- 使用说明、答案速查、换算、评分表
def tracks():
    ts = [(ca_track(t['n']), f'听力 Tarea {t["n"]}') for t in CA['tareas']]
    ts.append((f'DELE_{LV}_CA_completa', f'听力全部 {len(CA["tareas"])} 个 tarea 连播（每段之间 3 秒）'))
    for t in EIE['tareas']:
        st = t.get('estimulo') or {}
        if st.get('tipo') == 'audio':
            ts.append((f'DELE_{LV}_EIE_T{t["n"]}', f'写作 Tarea {t["n"]} 的录音（放两遍）'))
    return ts


def teach_intro():
    rows = []
    for p in ('cl', 'ca', 'eie', 'eio'):
        d = DOCS[p]
        cnt = f'{len(d["tareas"])} 个 tarea · {NITEMS[p]} 题' if p in NITEMS else f'{len(d["tareas"])} 个 tarea'
        tm = f'{d.get("duracion_min")} 分钟' + (f' ＋ 准备 {d.get("preparacion_min")} 分钟' if p == 'eio' else '')
        mat = {'cl': '考生题册 Prueba 1，答题卡第 1 页', 'ca': f'考生题册 Prueba 2，答题卡第 2 页，音轨 DELE_{LV}_CA_T1… 或连播版',
               'eie': '考生题册 Prueba 3，答题卡的作文页' + ('，写作录音' if any((t.get('estimulo') or {}).get('tipo') == 'audio' for t in d['tareas']) else ''),
               'eio': '考生题册 Prueba 4（考生材料），本书第六部分（考官材料）'}[p]
        rows.append(f'<tr><td>Prueba {PN[p]}</td><td>{ZH[p]}（{e(PES[p])}）</td><td>{cnt}</td><td>{tm}</td><td>{mat}</td></tr>')
    trs = ''.join(f'<tr><td class="sans">{tid}.mp3</td><td>{lab}</td><td class="c">{dur(tid)}</td></tr>' for tid, lab in tracks())
    return ('<section class="pg"><h2>一、使用说明</h2><h3>1. 考试安排</h3>'
            '<table><tr><th style="width:9%">部分</th><th style="width:25%">内容</th><th style="width:16%">题量</th><th style="width:16%">时间</th><th>材料</th></tr>'
            + ''.join(rows) + '</table>'
            '<p>阅读、听力、写作在同一场按顺序进行（可在听力和写作之间休息），口语另行安排。每部分满分 25 分，总分 100 分；'
            '第 1 组（阅读＋写作）、第 2 组（听力＋口语）各自达到 30 分（满分 50）为 APTO（通过），两组都通过才算通过考试。</p>'
            '<h3>2. 听力的播放</h3><p>每个 tarea 一条音轨，播音员读说明语、编号和例题答案，读题时间、两遍之间的停顿和作答时间都已录进去，播放时不要暂停；'
            f'也可以直接播放连播版（DELE_{LV}_CA_completa.mp3）。考生题册里每个 tarea 都标了对应的音轨。录音中的人物都说西班牙标准语。</p>'
            '<h3>3. 录音清单</h3><table><tr><th style="width:34%">文件</th><th>内容</th><th style="width:12%" class="c">时长</th></tr>' + trs + '</table>'
            '<p class="small">录音为语音合成：每一句都经语音识别逐词核对，成品响度 −16 LUFS，MP3 128 kbps。</p>'
            '<h3>4. 本书内容</h3><p>二、答案速查　三、阅读译文与解析　四、听力原文、译文与解析　五、写作评分、材料与范文　六、口语实施、考官材料与参考回答　七、成绩换算　八、评分表（可复印）</p></section>')


def keygrid(part):
    allk = {}
    for t in DOCS[part]['tareas']:
        allk.update(keys(part, t))
    ns = sorted(allk)
    rows = ''
    for i in range(0, len(ns), 15):
        seg = ns[i:i + 15]
        rows += '<tr>' + ''.join(f'<th class="c">{n}</th>' for n in seg) + '</tr><tr>' + ''.join(f'<td class="c key">{allk[n]}</td>' for n in seg) + '</tr>'
    return f'<table>{rows}</table>'


def unused_notes(part):
    out = []
    for t in DOCS[part]['tareas']:
        tp = t['tipo']
        if part == 'cl' and tp == 'relacionar' and len(t['textos']) > 4:
            used = {x['clave'] for x in t['enunciados']}
            ex = [x['clave'] for x in t['enunciados'] if x['n'] == 0]
            un = '、'.join(L for L in LET[:len(t['textos'])] if L not in used)
            out.append(f'T{t["n"]} ' + (f'例题用 {ex[0]}，' if ex else '') + (f'没有用到 {un}' if un else '每篇都用到'))
        elif tp == 'fragmentos':
            out.append(f'T{t["n"]} 多余的片段 {"、".join(d_["id"] for d_ in t.get("distractores", []))}')
        elif part == 'ca' and tp in ('relacionar_imagenes', 'relacionar'):
            pool = [x['id'] for x in (t.get('imagenes') or t.get('frases'))]
            used = {a['clave'] for a in t['audios']}
            ex = [a['clave'] for a in t['audios'] if a['id'] == '0']
            out.append(f'T{t["n"]} 例题用 {ex[0] if ex else "—"}，没有用到 {"、".join(x for x in pool if x not in used)}')
        elif tp == 'frases':
            used = {i['clave'] for i in t['inicios']}
            out.append(f'T{t["n"]} 例题用 {t["inicios"][0]["clave"]}，没有用到 {"、".join(f["id"] for f in t["finales"] if f["id"] not in used)}')
        elif tp == 'completar':
            used = {f['clave'] for f in t['frases']}
            out.append(f'T{t["n"]} 例题用 {t["frases"][0]["clave"]}，没有用到 {"、".join(o["id"] for o in t["opciones"] if o["id"] not in used)}')
        elif tp == 'seleccion_multiple':
            out.append(f'T{t["n"]}（1—6）：六个正确项按字母顺序填，顺序不对的按每个位置是否等于标准答案计分')
    return ('<p class="small">' + '；'.join(out) + '。</p>') if out else ''


def teach_keys():
    low = '' if LOW else '（B1 起题册印小写 a) b) c)，答题卡和本表用大写）'
    return (f'<section class="pg"><h2>二、答案速查</h2><h3>阅读（{e(PES["cl"])}）· {NITEMS["cl"]} 题</h3>{keygrid("cl")}{unused_notes("cl")}'
            f'<h3>听力（{e(PES["ca"])}）· {NITEMS["ca"]} 题</h3>{keygrid("ca")}{unused_notes("ca")}'
            f'<p class="small">每题 1 分，答错不扣分{low}。得分 = 答对题数 × 25 ÷ 题数，换算表见第七部分。</p></section>')


def conv_table(n):
    ns = list(range(n + 1))
    rows = ''
    for i in range(0, len(ns), 14):
        seg = ns[i:i + 14]
        rows += ('<tr><th>答对</th>' + ''.join(f'<td class="c">{a}</td>' for a in seg) + '</tr><tr><th>得分</th>'
                 + ''.join(f'<td class="c key">{a * 25 / n:.2f}</td>' for a in seg) + '</tr>')   # 教师用书是中文，用小数点
    return f'<table>{rows}</table>'


def teach_conv():
    return ('<section class="pg"><h2>七、成绩换算</h2>'
            f'<h3>阅读：答对题数 → 得分（× 25 ÷ {NITEMS["cl"]}）</h3>{conv_table(NITEMS["cl"])}'
            f'<h3>听力：答对题数 → 得分（× 25 ÷ {NITEMS["ca"]}）</h3>{conv_table(NITEMS["ca"])}'
            '<h3>写作、口语</h3><p>每个评分项 0—3 分，按第五、六部分的方法加权平均后 × 25 ÷ 3（平均 3 分＝25 分，2 分＝16.67 分，1.8 分＝15 分，1 分＝8.33 分）。</p>'
            '<h3>是否通过</h3><table><tr><th>组</th><th>部分</th><th>满分</th><th>通过线</th></tr>'
            '<tr><td>第 1 组</td><td>阅读 ＋ 写作</td><td class="c">50</td><td class="c">30</td></tr>'
            '<tr><td>第 2 组</td><td>听力 ＋ 口语</td><td class="c">50</td><td class="c">30</td></tr></table>'
            '<p>两组都达到 30 分为 APTO（通过），总分 = 四部分相加（满分 100）。例：阅读 16、写作 15 → 第 1 组 31，通过；听力 20、口语 9 → 第 2 组 29，不通过。</p>'
            '<p class="small">说明：换算方法和通过线依据官方公开的考试说明；本卷是模拟卷，难度没有经过真实考生的等值校准，结果只作练习参考。</p></section>')


def teach_forms():
    cols, f1 = SC_EIE[LV]
    eie = ('<table><tr><th>Tarea</th>' + ''.join(f'<th class="c">{e(c)}</th>' for c, _ in cols) + '<th class="c">本 tarea 得分（0—3）</th></tr>'
           + ''.join(f'<tr><td>Tarea {t["n"]}</td>' + '<td style="height:9mm"></td>' * (len(cols) + 1) + '</tr>' for t in EIE['tareas'])
           + f'<tr><td colspan="{len(cols) + 1}" style="text-align:right">写作得分 =（T1 + T2）÷ 2 × 25 ÷ 3（满分 25）</td><td></td></tr></table>')
    parts, crit, w, f2 = SC_EIO[LV]
    eio = ('<table><tr><th>评分员</th>' + ''.join(f'<th class="c">{e(c)}</th>' for c, _ in crit) + '<th class="c">小计（0—3）</th><th class="c">权重</th></tr>'
           + ''.join(f'<tr><td>{p}</td>' + '<td style="height:9mm"></td>' * (len(crit) + 1) + f'<td class="c">{round(x * 100)}%</td></tr>' for p, x in zip(parts, w))
           + f'<tr><td colspan="{len(crit) + 1}" style="text-align:right">评分员分 R（加权）</td><td></td><td></td></tr>'
           f'<tr><td colspan="{len(crit) + 1}" style="text-align:right">考官整体分 H（0—3）</td><td></td><td></td></tr>'
           f'<tr><td colspan="{len(crit) + 1}" style="text-align:right">口语得分 =（0.6 × R + 0.4 × H）× 25 ÷ 3（满分 25）</td><td></td><td></td></tr></table>')
    total = ('<table><tr><th>部分</th><th class="c">得分（满分 25）</th><th>组</th><th class="c">组得分（满分 50，30 通过）</th></tr>'
             '<tr><td>阅读</td><td></td><td rowspan="2">第 1 组</td><td rowspan="2"></td></tr><tr><td>写作</td><td style="height:9mm"></td></tr>'
             '<tr><td>听力</td><td style="height:9mm"></td><td rowspan="2">第 2 组</td><td rowspan="2"></td></tr><tr><td>口语</td><td style="height:9mm"></td></tr>'
             '<tr><td>总分（满分 100）</td><td></td><td>结果</td><td>APTO ☐　NO APTO ☐</td></tr></table>')
    return ('<section class="pg"><h2>八、评分表（可复印）</h2><p>考生姓名 <span class="field"></span>　日期 <span class="field" style="min-width:30mm"></span></p>'
            f'<h3>写作</h3>{eie}<p class="small">{f1}</p><h3>口语</h3>{eio}<p class="small">{f2}</p><h3>总成绩</h3>{total}</section>')


def teacher():
    head = (f'<div class="cover"><div class="top"><h1 class="sans">Examen de práctica no oficial<br>Formato DELE {LV}</h1><div class="sub">{TITLE}　教师用书</div>'
            '<p>内容：使用说明 · 答案速查 · 阅读译文与解析 · 听力原文、译文与解析 · 写作评分与范文 · 口语实施、考官材料与参考回答 · 成绩换算 · 评分表</p></div>'
            f'<div class="disc">{e(DISCLAIMER)}<br>{e(DISCLAIMER_ES)}</div></div>')
    return head + teach_intro() + teach_keys() + teach_cl() + teach_ca() + teach_eie() + teach_eio() + teach_conv() + teach_forms()


# ================================================================
def main():
    OUT.mkdir(parents=True, exist_ok=True)
    base = f'DELE_{LV}模拟卷'
    books = {
        '考生题册': (doc(f'{TITLE} · 考生题册', cover() + booklet_cl() + booklet_ca() + booklet_eie() + booklet_eio()), f'DELE {LV} · Examen de práctica no oficial · Cuadernillo del candidato'),
        '答题卡': (doc(f'{TITLE} · 答题卡', sheet()), f'DELE {LV} · Examen de práctica no oficial · Hoja de respuestas'),
        '教师用书': (doc(f'{TITLE} · 教师用书', '<style>p { text-align: left; }</style>' + teacher()), f'{TITLE} · 教师用书'),
    }
    for name, (text, _) in books.items():
        (OUT / f'{base}_{name}.html').write_text(text, 'utf-8')
    miss = sorted(set(MISSING))
    if miss:
        print(f'注意：{len(miss)} 张插图还没有 PNG（印成占位框）：{" ".join(miss[:12])}{" …" if len(miss) > 12 else ""}')
    if not REP:
        print('注意：还没有录音核对记录，时长先空着')
    if '--html-only' in sys.argv:
        print('HTML OK')
        return
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        pg = br.new_page()
        for name, (_, foot) in books.items():
            pg.goto((OUT / f'{base}_{name}.html').as_uri())
            pg.wait_for_load_state('networkidle')
            ft = (f'<div style="font-size:7.5pt;width:100%;text-align:center;color:#444;font-family:\'Helvetica Neue\',\'PingFang SC\',sans-serif;">'
                  f'{e(foot)}　·　<span class="pageNumber"></span> / <span class="totalPages"></span></div>')
            pg.pdf(path=str(OUT / f'{base}_{name}.pdf'), format='A4', print_background=True, display_header_footer=True,
                   header_template='<div></div>', footer_template=ft, margin={'top': '17mm', 'bottom': '19mm', 'left': '17mm', 'right': '17mm'})
            print(name, 'PDF')
        br.close()


if __name__ == '__main__':
    main()
