"""把 content/*.json 排成三本 A4 PDF：考生试题册、答题卡、教师用书。

    python tools/build_pdf.py <输出目录> [--html-only]

HTML 由本脚本直接生成，再用 Playwright 的 Chromium 打印（Chromium 要在命令沙盒外运行）。
教师用书里的录音时长读 out/audio/核对/report.json（没有就留空）。插图读 eio.json 里 Tarea 2 每张图的 archivo。
"""
import base64
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(sys.argv[1]).resolve()
C = ROOT / 'content'
CL, CA, EIE, EIO = (json.loads((C / f'{p}.json').read_text('utf-8')) for p in ('cl', 'ca', 'eie', 'eio'))
REPORT = ROOT / 'out' / 'audio' / '核对' / 'report.json'
REP = json.loads(REPORT.read_text('utf-8')) if REPORT.exists() else {}
LET = 'ABCDEFGHIJKLMNO'
NAME = 'SIELE Global 模拟卷（第五套）'
DISCLAIMER = ('本卷为原创的非官方模拟练习，按 SIELE 公开的考试结构编写，与 SIELE、塞万提斯学院及合作大学无任何关系；'
              '所有文章、录音和题目均为原创。')
DISCLAIMER_ES = ('Examen de práctica no oficial, elaborado según la estructura pública del examen SIELE. '
                 'No está vinculado a SIELE, al Instituto Cervantes ni a las universidades asociadas. Todos los textos, audios y tareas son originales.')

e = lambda s: html.escape(str(s), quote=False)
CURSIVA = sorted({t for d in (CL, CA, EIE, EIO) for t in d.get('cursiva', [])}, key=len, reverse=True)

CSS = """
@page { size: A4; margin: 17mm 17mm 19mm 17mm; }
* { box-sizing: border-box; }
body { font-family: "Times New Roman", "Songti SC", "STSong", serif; font-size: 10.5pt; line-height: 1.5; color: #111; margin: 0; }
.sans, h1, h2, h3, h4, .tag, th { font-family: "Helvetica Neue", "PingFang SC", "Heiti SC", sans-serif; }
h1 { font-size: 20pt; margin: 0 0 6pt; line-height: 1.25; }
h2 { font-size: 15pt; margin: 0 0 8pt; padding-bottom: 4pt; border-bottom: 1.4pt solid #222; }
h3 { font-size: 12pt; margin: 14pt 0 5pt; break-after: avoid; }
h4 { font-size: 10.5pt; margin: 10pt 0 4pt; break-after: avoid; }
p { margin: 3pt 0; text-align: justify; }
.page { break-before: page; }
.inst { background: #f1f1ef; border-left: 2.5pt solid #444; padding: 5pt 8pt; margin: 4pt 0 8pt; font-style: italic; break-inside: avoid; break-after: avoid; }
.box { border: 0.7pt solid #777; border-radius: 3pt; padding: 7pt 10pt; margin: 6pt 0; break-inside: avoid; }
.box .cab { font-family: "Helvetica Neue", "PingFang SC", sans-serif; font-weight: 600; font-size: 9.5pt; letter-spacing: .3pt; margin-bottom: 3pt; }
.box p { margin: 2.5pt 0; }
.t2mail { font-size: 10pt; line-height: 1.42; }
.t2mail p { margin: 1.5pt 0; }
.q { margin: 6pt 0 8pt; break-inside: avoid; padding-left: 22pt; text-indent: -22pt; }
.q .n { font-weight: bold; font-family: "Helvetica Neue", sans-serif; display: inline-block; min-width: 19pt; text-indent: 0; }
.opts { list-style: none; padding-left: 20pt; margin: 2pt 0 0; }
.q .opts { padding-left: 0; }
.opts li { margin: 1pt 0; padding-left: 13pt; text-indent: -13pt; }
.opts b { font-family: "Helvetica Neue", sans-serif; margin-right: 4pt; }
.gap { font-family: "Helvetica Neue", sans-serif; font-weight: bold; white-space: nowrap; }
.gap i { display: inline-block; width: 4.2em; border-bottom: 0.7pt solid #111; margin-left: 2pt; }
.blank { display: inline-block; width: 7em; border-bottom: 0.7pt solid #111; }
table { border-collapse: collapse; width: 100%; margin: 5pt 0; break-inside: avoid; }
th, td { border: 0.6pt solid #888; padding: 2.5pt 5pt; vertical-align: top; font-size: 9.8pt; }
th { background: #ecebe8; font-weight: 600; font-size: 9.3pt; }
.grid td { border: none; padding: 2pt 6pt; }
.bank td { border: 0.6pt solid #999; text-align: left; width: 20%; font-size: 10.5pt; }
.bank b { font-family: "Helvetica Neue", sans-serif; margin-right: 5pt; }
.four { display: grid; grid-template-columns: 0.9fr 0.9fr 1.25fr 1fr; gap: 7pt; align-items: start; }
.two { display: grid; grid-template-columns: 1fr 1fr; gap: 10pt; }
.three { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8pt; }
.three .box { font-size: 9.8pt; margin: 0; }
.tag { display: inline-block; font-size: 8.5pt; border: 0.6pt solid #555; border-radius: 8pt; padding: 0 6pt; margin-left: 6pt; vertical-align: 1pt; font-weight: normal; }
.track { font-family: "Helvetica Neue", "PingFang SC", sans-serif; font-size: 9pt; color: #333; }
img.ilu { max-width: 100%; max-height: 112mm; margin: 0 auto; border: 0.6pt solid #999; border-radius: 2pt; display: block; }
.cover { height: 250mm; display: flex; flex-direction: column; }
.cover .top { border-top: 4pt solid #222; padding-top: 14pt; }
.cover .sub { font-size: 12pt; color: #333; margin: 2pt 0 16pt; font-family: "Helvetica Neue", "PingFang SC", sans-serif; }
.cover .disc { margin-top: auto; font-size: 8.8pt; color: #444; border-top: 0.6pt solid #999; padding-top: 6pt; }
.small { font-size: 9pt; color: #333; }
.zh { font-family: "Songti SC", "STSong", serif; }
table.par { break-inside: auto; margin: 2pt 0 6pt; }
table.par td { border: none; border-top: 0.4pt dotted #bbb; padding: 2.5pt 6pt 2.5pt 0; font-size: 9.8pt; }
table.par tr { break-inside: avoid; }
table.par tbody.keep { break-inside: avoid; }
table.par tr.lab td { border-top: 0.6pt solid #888; padding-top: 4pt; }
.who { font-family: "Helvetica Neue", sans-serif; font-weight: 600; font-size: 8.8pt; color: #333; }
.key { font-family: "Helvetica Neue", sans-serif; font-weight: bold; }
.expl { margin: 2pt 0 7pt 20pt; font-size: 9.8pt; text-indent: 0; }
.q .expl { margin-left: 0; }
/* 答题卡 */
.sheet td, .sheet th { text-align: center; font-family: "Helvetica Neue", sans-serif; font-size: 9.5pt; padding: 2.4pt 3pt; }
.sheet td.l { text-align: left; font-weight: bold; width: 26pt; }
.bub { font-family: "Helvetica Neue", sans-serif; display: inline-block; width: 13.5pt; height: 13.5pt; border: 0.8pt solid #222; border-radius: 50%; font-size: 7.5pt; line-height: 12pt; text-align: center; margin: 0 1.4pt; }
.wbox { display: inline-block; width: 26pt; height: 17pt; border: 0.8pt solid #222; vertical-align: middle; }
.lines { border: 0.8pt solid #444; padding: 2pt 8pt; }
.lines div { height: 8.6mm; border-bottom: 0.5pt solid #aaa; }
.field { display: inline-block; border-bottom: 0.7pt solid #111; min-width: 60mm; height: 12pt; vertical-align: bottom; }
.chk { display: inline-block; width: 10pt; height: 10pt; border: 0.8pt solid #222; vertical-align: -1pt; margin: 0 3pt 0 10pt; }
"""


def doc(title, body):
    for t in CURSIVA:                       # 书名等用斜体：内容文件顶层的 "cursiva" 列出原文
        body = body.replace(e(t), f'<i>{e(t)}</i>')
    return f'<!doctype html><html lang="es"><head><meta charset="utf-8"><title>{e(title)}</title><style>{CSS}</style></head><body>{body}</body></html>'


def paras(lines, cls=''):
    return ''.join(f'<p{cls}>{e(x)}</p>' for x in lines)


def opts(o):
    return '<ul class="opts">' + ''.join(f'<li><b>{LET[i]})</b>{e(x)}</li>' for i, x in enumerate(o)) + '</ul>'


def q_block(n, enunciado, o=None):
    return f'<div class="q"><span class="n">{n}.</span> {e(enunciado)}{opts(o) if o else ""}</div>'


def gaps(s):
    return re.sub(r'\[(\d+)\]', r'<span class="gap">(\1)<i></i></span>', e(s))


def blanks(s):
    return re.sub(r'_{4,}', '<span class="blank"></span>', e(s))


def img_uri(path):
    p = ROOT / path
    if not p.exists():
        return ''
    return 'data:image/png;base64,' + base64.b64encode(p.read_bytes()).decode()


def mmss(sec):
    sec = int(round(sec))
    return f'{sec // 60}:{sec % 60:02d}'


TRACKS = [('SIELE5_CA_T1', '听力 Tarea 1'), ('SIELE5_CA_T2', '听力 Tarea 2'), ('SIELE5_CA_T3', '听力 Tarea 3'), ('SIELE5_CA_T4', '听力 Tarea 4'),
          ('SIELE5_CA_T5', '听力 Tarea 5'), ('SIELE5_CA_T6', '听力 Tarea 6'), ('SIELE5_CA_completa', '听力全部 6 个 tarea 连播（每段之间 3 秒）'),
          ('SIELE5_EIO_T1', '口语 Tarea 1'), ('SIELE5_EIO_T2', '口语 Tarea 2（计时）'), ('SIELE5_EIO_T3', '口语 Tarea 3（计时）'),
          ('SIELE5_EIO_T4_tema1', '口语 Tarea 4，话题 1'), ('SIELE5_EIO_T4_tema2', '口语 Tarea 4，话题 2'), ('SIELE5_EIO_T5', '口语 Tarea 5（计时）')]
dur = lambda tid: mmss(REP[tid]['duration']) if tid in REP else '—'
# 听力：连播版的长度（读题、停顿、作答都在音轨里）；口语：T1+T2+T3+T5，加两个 T4 话题的平均，再加选话题的约 30 秒
CA_MIN = round(REP['SIELE5_CA_completa']['duration'] / 60) if 'SIELE5_CA_completa' in REP else 45
_EIO = ('SIELE5_EIO_T1', 'SIELE5_EIO_T2', 'SIELE5_EIO_T3', 'SIELE5_EIO_T5', 'SIELE5_EIO_T4_tema1', 'SIELE5_EIO_T4_tema2')
EIO_MIN = (round((sum(REP[t]['duration'] for t in _EIO[:4]) + (REP[_EIO[4]]['duration'] + REP[_EIO[5]]['duration']) / 2 + 30) / 60)
           if all(t in REP for t in _EIO) else 25)
if not all(t in REP for t in _EIO + ('SIELE5_CA_completa',)):
    print('注意：还没有录音核对记录，时长先按估计值排版')


def nb(s):
    """题目说明里的“(1-5)”“(A, B o C)”“45 segundos”“250 y 300”不在中间折行。"""
    return re.sub(r'\([^()<>]{1,14}\)|\d+ (?:segundos|minutos|palabras)|\d+ y \d+',
                  lambda m: f'<span style="white-space:nowrap">{m.group(0)}</span>', s)


# ================================================================ 考生试题册
def cover():
    rows = ''.join(f'<tr><td>{a}</td><td>{b}</td><td>{c}</td><td>{d}</td></tr>' for a, b, c, d in (
        ('Prueba 1', 'Comprensión de lectura', '5 tareas · 38 preguntas', '60 min'),
        ('Prueba 2', 'Comprensión auditiva', '6 tareas · 38 preguntas', f'≈ {CA_MIN} min'),
        ('', 'Descanso', '', '15 min'),
        ('Prueba 3', 'Expresión e interacción escritas', '2 tareas', '50 min'),
        ('Prueba 4', 'Expresión e interacción orales', '5 tareas', f'≈ {EIO_MIN} min')))
    notes = ''.join(f'<li>{x}</li>' for x in (
        '四项考试按顺序进行：阅读 → 听力 →（休息 15 分钟）→ 写作 → 口语。每项各 250 分，共 1000 分，各项分别给出等级。',
        '阅读、听力的答案填在答题卡上（选择题把圆圈涂黑，方框里写字母）；写作写在答题卡的作文页上；口语用手机或电脑录音。',
        '听力每段录音放两遍，读题、作答时间都已录在音轨里，中途不要暂停。真实考试中题号和提示显示在屏幕上，本卷由录音里的男声简短报出。',
        '口语按音轨里的提示进行：一声提示音后开始说，两声提示音表示时间到。Tarea 1、Tarea 4 的问题只在录音里出现，试题册上没有。',
        '真实考试在电脑上进行：阅读和听力的 tarea 之间不能回头，写作的两个 tarea 可以自由切换。'))
    return (f'<div class="cover"><div class="top"><h1 class="sans">Examen de práctica no oficial<br>Modelo 5 · formato SIELE Global</h1>'
            f'<div class="sub">{NAME}　考生试题册</div>'
            f'<table><tr><th style="width:16%">Prueba</th><th>Contenido</th><th style="width:26%">Tareas</th><th style="width:12%">Tiempo</th></tr>{rows}</table>'
            f'<h3 class="sans">考生须知</h3><ol class="small">{notes}</ol>'
            f'<p class="small" style="margin-top:14pt">Nombre y apellidos <span class="field"></span>　　Fecha <span class="field" style="min-width:35mm"></span></p></div>'
            f'<div class="disc">{e(DISCLAIMER_ES)}<br>{e(DISCLAIMER)}</div></div>')


def booklet_cl():
    t1, t2, t3, t4, t5 = CL['tareas']
    h = [f'<div class="page"><h2>Prueba 1 · Comprensión de lectura <span class="tag">60 minutos</span></h2><p class="inst">{nb(e(CL["intro"]))}</p>']
    h.append(f'<h3>Tarea 1</h3><p class="inst">{nb(e(t1["instruccion"]))}</p>')
    for tx in t1['textos']:
        q = tx['preguntas'][0]
        h.append(f'<div style="break-inside:avoid"><div class="box"><div class="cab">Texto {tx["id"]} · {e(tx["cabecera"])}</div>{paras(tx["cuerpo"])}</div>'
                 f'{q_block(q["n"], q["enunciado"], q["opciones"])}</div>')
    tx = t2['textos'][0]
    h.append(f'<div class="page"></div><h3>Tarea 2</h3><p class="inst">{nb(e(t2["instruccion"]))}</p>')
    cab = '<br>'.join(e(x.strip()) for x in tx['cabecera'].split('·'))
    h.append(f'<div class="box t2mail" style="break-inside:auto"><div class="cab">{cab}</div>{paras(tx["cuerpo"])}</div>')
    qs = [q_block(q['n'], q['enunciado'], q['opciones']) for q in tx['preguntas']]
    h.append('<div class="two" style="gap:4pt 14pt"><div>' + ''.join(qs[:2]) + '</div><div>' + ''.join(qs[2:]) + '</div></div>')
    h.append(f'<div class="page"></div><h3>Tarea 3</h3><p class="inst">{nb(e(t3["instruccion"]))}</p><h4 style="text-align:center">{e(t3["titulo"])}</h4>')
    h += [f'<div class="box"><div class="cab">{e(tx["cabecera"])}</div>{paras(tx["cuerpo"])}</div>' for tx in t3['textos']]
    h.append('<table style="margin-top:8pt"><tr><th style="width:8%"></th><th>Preguntas</th><th style="width:7%">A</th><th style="width:7%">B</th><th style="width:7%">C</th></tr>'
             + ''.join(f'<tr><td class="key">{q["n"]}.</td><td>{e(q["enunciado"])}</td><td></td><td></td><td></td></tr>' for q in t3['preguntas'])
             + '</table><p class="small">(Marque sus respuestas en la Hoja de respuestas.)</p>')
    for k, tx in enumerate(t4['textos']):
        h.append('<div class="page"></div>' + (f'<h3>Tarea 4</h3><p class="inst">{nb(e(t4["instruccion"]))}</p>' if k == 0 else '<h3>Tarea 4 (continuación)</h3>'))
        h.append(f'<h4 style="text-align:center">Texto {k + 1}. {e(tx["titulo"])}</h4>' + ''.join(f'<p>{gaps(p)}</p>' for p in tx['cuerpo']))
        h.append('<div class="box"><div class="cab">Fragmentos</div>' + ''.join(f'<p><b class="sans">{f["letra"]}.</b> {e(f["texto"])}</p>' for f in tx['fragmentos']) + '</div>')
    h.append(f'<div class="page"></div><h3>Tarea 5</h3><p class="inst">{nb(e(t5["instruccion"]))}</p><h4 style="text-align:center">{e(t5["titulo"])}</h4>')
    h += [f'<p>{gaps(p)}</p>' for p in t5['cuerpo']]
    h.append(f'<p class="small" style="text-align:right"><i>{e(t5["fuente"])}</i></p>')
    cell = lambda q, w: (f'<td style="width:{w}%;font-size:9.4pt;padding:1.5pt 4pt 1.5pt 20.5pt;text-indent:-16.5pt"><b class="sans">{q["n"]}.</b> '
                      + ' '.join(f'<span style="white-space:nowrap;margin-right:7pt"><b class="sans">{LET[i]})</b> {e(o)}</span>' for i, o in enumerate(q['opciones'])) + '</td>')
    ps = t5['preguntas']
    h.append('<table class="grid" style="margin-top:6pt">' + ''.join(f'<tr>{cell(ps[i], 50)}{cell(ps[i + 6], 50)}</tr>' for i in range(6)) + '</table></div>')
    return ''.join(h)


def booklet_ca():
    T = CA['tareas']
    tr = lambda n: f'<p class="track">♪ Pista: SIELE5_CA_T{n}.mp3</p>'
    h = [f'<div class="page"><h2>Prueba 2 · Comprensión auditiva <span class="tag">≈ {CA_MIN} minutos</span></h2><p class="inst">{nb(e(CA["intro"]))}</p>']
    t = T[0]
    h.append(f'<h3>Tarea 1</h3>{tr(1)}<p class="inst">{nb(e(t["instruccion"]))}</p>')
    b = t['banco']
    h.append('<table class="bank">' + ''.join('<tr>' + ''.join(f'<td><b>{LET[i]}</b>{e(b[i])}</td>' for i in range(r, r + 5)) + '</tr>' for r in (0, 5, 10)) + '</table>')
    h += [f'<div class="q"><span class="n">{q["n"]}.</span> {blanks(q["enunciado"])}</div>' for q in t['preguntas']]
    t = T[1]
    h.append(f'<div class="page"></div><h3>Tarea 2</h3>{tr(2)}<p class="inst">{nb(e(t["instruccion"]))}</p>')
    for a, q in zip(t['audio'], t['preguntas']):
        lab = a['label'].replace('Noticia ', 'Noticia ')
        h.append(f'<div class="q"><span class="n">{q["n"]}.</span> <span class="sans small">[{e(lab)}]</span> {e(q["enunciado"])}{opts(q["opciones"])}</div>')
    t = T[2]
    h.append(f'<div class="page"></div><h3>Tarea 3</h3>{tr(3)}<p class="inst">{nb(e(t["instruccion"]))}</p>')
    h.append('<div class="box"><div class="cab">Enunciados</div>' + ''.join(f'<p><b class="sans">{LET[i]}.</b> {e(s)}</p>' for i, s in enumerate(t['enunciados'])) + '</div>')
    h.append('<table style="width:60%;margin:8pt auto"><tr><th>Pregunta</th><th>Audio</th><th>Enunciado</th></tr>'
             + ''.join(f'<tr><td class="key" style="text-align:center">{q["n"]}</td><td>Persona {q["persona"]}</td><td></td></tr>' for q in t['preguntas']) + '</table>')
    t = T[3]
    h.append(f'<div class="page"></div><h3>Tarea 4</h3>{tr(4)}<p class="inst">{nb(e(t["instruccion"]))}</p>')
    h += [q_block(q['n'], q['enunciado'], q['opciones']) for q in t['preguntas']]
    t = T[4]
    h.append(f'<div class="page"></div><h3>Tarea 5</h3>{tr(5)}<p class="inst">{nb(e(t["instruccion"]))}</p>')
    h += [f'<div class="q"><span class="n">{q["n"]}.</span> <span class="sans small">[Fragmento {q["fragmento"]}]</span> {e(q["enunciado"])}{opts(q["opciones"])}</div>' for q in t['preguntas']]
    t = T[5]
    h.append(f'<div class="page"></div><h3>Tarea 6</h3>{tr(6)}<p class="inst">{nb(e(t["instruccion"]))}</p>')
    h.append('<div class="box">' + ''.join(f'<p><b class="sans">{LET[i]}.</b> {e(s)}</p>' for i, s in enumerate(t['enunciados'])) + '</div>')
    h.append('<p class="small">Marque exactamente seis letras en la Hoja de respuestas (preguntas 33-38).</p></div>')
    return ''.join(h)


def booklet_eie():
    t1, t2 = EIE['tareas']
    st = t1['estimulo']
    h = [f'<div class="page"><h2>Prueba 3 · Expresión e interacción escritas <span class="tag">50 minutos</span></h2><p class="inst">{nb(e(EIE["intro"]))}</p>']
    h.append(f'<h3>Tarea 1</h3><p class="inst">{nb(e(t1["instruccion"]))}</p><ul>' + ''.join(f'<li>{e(p)}</li>' for p in t1['puntos']) + '</ul>')
    h.append(f'<div class="box"><div class="cab">De: {e(st["de"])}<br>Asunto: {e(st["asunto"])}</div>{paras(st["cuerpo"])}</div>')
    h.append(f'<p class="small">Número de palabras: entre {t1["palabras"][0]} y {t1["palabras"][1]}.</p>')
    h.append(f'<div class="page"></div><h3>Tarea 2</h3><p class="inst">{nb(e(t2["instruccion"]))}</p>')
    for o in t2['opciones']:
        s = o['estimulo']
        h.append(f'<div style="break-inside:avoid"><h4>{e(o["titulo"])}</h4><p>{nb(e(o["instruccion"]))}</p><ul>' + ''.join(f'<li>{e(p)}</li>' for p in o['puntos']) + '</ul>'
                 f'<div class="box"><div class="cab">{e(s["cabecera"])}</div><p><b>{e(s["titular"])}</b></p><p>{e(s["cuerpo"])}</p></div></div>')
    h.append(f'<p class="small">Número de palabras: entre {t2["palabras"][0]} y {t2["palabras"][1]}.</p></div>')
    return ''.join(h)


def booklet_eio():
    t1, t2, t3, t4, t5 = EIO['tareas']
    tr = lambda f: f'<p class="track">♪ Pista: {f}</p>'
    h = [f'<div class="page"><h2>Prueba 4 · Expresión e interacción orales <span class="tag">≈ {EIO_MIN} minutos</span></h2><p class="inst">{nb(e(EIO["intro"]))}</p>']
    h.append(f'<h3>Tarea 1</h3>{tr("SIELE5_EIO_T1.mp3")}<p class="inst">{nb(e(t1["instruccion"]))}</p>'
             '<p class="small">(Las preguntas solo se escuchan en el audio.)</p>')
    h.append(f'<h3>Tarea 2</h3>{tr("SIELE5_EIO_T2.mp3")}<p class="inst">{nb(e(t2["instruccion"]))}</p><ul>' + ''.join(f'<li>{e(a)}</li>' for a in t2['aspectos']) + '</ul>')
    h.append('<p class="small">En el examen real se muestran fotografías; en este modelo, ilustraciones.</p>')
    for im in t2['imagenes']:
        src = img_uri(im['archivo'])
        pic = f'<img class="ilu" src="{src}">' if src else f'<div class="box" style="height:110mm">[{e(im["archivo"])}]</div>'
        h.append(f'<div style="break-inside:avoid;margin-top:8pt"><h4>{e(im["titulo"])}</h4>{pic}</div>')
    h.append(f'<div class="page"></div><h3>Tarea 3</h3>{tr("SIELE5_EIO_T3.mp3")}<p class="inst">{nb(e(t3["instruccion"]))}</p>')
    for p in t3['partes']:
        h.append(f'<h4>{e(p["parte"])}</h4><div class="two">' + ''.join(
            f'<div class="box"><div class="cab">Opción {o["n"]}</div><p>{e(o["situacion"])}</p><ul>' + ''.join(f'<li>{e(x)}</li>' for x in o['puntos']) + '</ul></div>'
            for o in p['opciones']) + '</div>')
    h.append(f'<div class="page"></div><h3>Tarea 4</h3><p class="track">♪ Pista: SIELE5_EIO_T4_tema1.mp3 o SIELE5_EIO_T4_tema2.mp3 (según el tema elegido)</p><p class="inst">{nb(e(t4["instruccion"]))}</p>')
    for tm in t4['temas']:
        h.append(f'<div class="box"><div class="cab">Tema {tm["n"]} · {e(tm["titulo"])}</div><p>{e(tm["texto"])}</p></div>')
    h.append('<p class="small">(Las preguntas solo se escuchan en el audio.)</p>')
    h.append(f'<div class="page"></div><h3>Tarea 5</h3>{tr("SIELE5_EIO_T5.mp3")}<p class="inst">{nb(e(t5["instruccion"]))}</p><ul>' + ''.join(f'<li>{e(p)}</li>' for p in t5['puntos']) + '</ul>')
    for tm in t5['temas']:
        h.append(f'<div class="box"><div class="cab">Tema {tm["n"]} · {e(tm["titulo"])}</div>' + ''.join(f'<p><b class="sans">{a["letra"]}.</b> {e(a["es"])}</p>' for a in tm['afirmaciones']) + '</div>')
    h.append('</div>')
    return ''.join(h)


# ================================================================ 答题卡
def sheet():
    bub = lambda letters: ''.join(f'<span class="bub">{x}</span>' for x in letters)
    def block(rows, cap):
        return f'<table class="sheet"><tr><th colspan="2">{cap}</th></tr>' + ''.join(f'<tr><td class="l">{n}</td><td style="text-align:left">{cells}</td></tr>' for n, cells in rows) + '</table>'
    cl = [(n, bub('ABC')) for n in range(1, 19)] + [(n, bub('ABCDE')) for n in range(19, 23)] + [(n, bub('FGHIJ')) for n in range(23, 27)] + [(n, bub('ABC')) for n in range(27, 39)]
    ca = [(n, '<span class="wbox"></span> <span class="small">(A–O)</span>') for n in range(1, 6)] + [(n, bub('ABC')) for n in range(6, 11)] + \
         [(n, '<span class="wbox"></span> <span class="small">(A–K)</span>') for n in range(11, 19)] + [(n, bub('ABC')) for n in range(19, 33)]
    h = ['<h2 class="sans">Hoja de respuestas · 答题卡 <span class="tag">Modelo 5</span></h2>'
         '<p>Nombre y apellidos <span class="field"></span>　Fecha <span class="field" style="min-width:30mm"></span></p>'
         '<p class="small">Rellene el círculo de la opción elegida (●). En las preguntas con recuadro, escriba la letra. 选择题把选中的圆圈涂黑；方框里写字母。</p>'
         '<h3>Prueba 1 · Comprensión de lectura</h3><div class="four">' + block(cl[:10], 'Tareas 1-2') + block(cl[10:18], 'Tarea 3') + block(cl[18:26], 'Tarea 4') + block(cl[26:], 'Tarea 5') + '</div>'
         '<h3>Prueba 2 · Comprensión auditiva</h3><div class="four">' + block(ca[:10], 'Tareas 1-2') + block(ca[10:18], 'Tarea 3') + block(ca[18:26], 'Tarea 4') + '<div>' + block(ca[26:], 'Tarea 5')
         + '<p class="sans" style="font-size:8.5pt;margin:6pt 0 2pt;text-align:left"><b>Tarea 6 (33-38)</b>: marque seis letras / 选六个</p>'
         '<p style="line-height:2.1;margin:0">' + bub('ABCDEF') + '<br>' + bub('GHIJKL') + '</p></div></div>'
         '<table style="margin-top:8pt"><tr><th>Para el profesor · 教师填写</th><th>Aciertos (0-38)</th><th>Puntos (× 250 ÷ 38)</th><th>Nivel</th></tr>'
         '<tr><td>Comprensión de lectura</td><td></td><td></td><td></td></tr><tr><td>Comprensión auditiva</td><td></td><td></td><td></td></tr></table>']
    lines = lambda k: '<div class="lines">' + '<div></div>' * k + '</div>'
    h.append('<div class="page"><h2 class="sans">Expresión e interacción escritas · Tarea 1</h2>'
             '<p class="small">Entre 100 y 150 palabras.</p>' + lines(25) + '<p style="text-align:right">Número de palabras: <span class="field" style="min-width:25mm"></span></p></div>')
    h.append('<div class="page"><h2 class="sans">Expresión e interacción escritas · Tarea 2</h2>'
             '<p>Opción elegida:<span class="chk"></span>Opción 1 · Artículo de opinión<span class="chk"></span>Opción 2 · Carta a la redacción</p>'
             '<p class="small">Entre 250 y 300 palabras.</p>' + lines(25) + '</div>')
    h.append('<div class="page"><h2 class="sans">Expresión e interacción escritas · Tarea 2 (continuación)</h2>' + lines(26)
             + '<p style="text-align:right">Número de palabras: <span class="field" style="min-width:25mm"></span></p></div>')
    return ''.join(h)


# ================================================================ 教师用书
LEVEL_CUTS = {'阅读': (33, 66, 118, 178, 217), '听力': (33, 66, 112, 164, 211), '写作': (34, 69, 104, 167, 215), '口语': (40, 76, 125, 176, 215)}
LEVELS = ('A1', 'A2', 'B1', 'B2', 'C1')


def level(score, cuts):
    lv = '低于 A1'
    for c, name in zip(cuts, LEVELS):
        if score >= c:
            lv = name
    return lv


def par_rows(segs, label=None):
    """一段录音的原文、译文对照：短的（新闻、独白、片段）整段不跨页，长的（对话、访谈、讲座）每一行不跨页。"""
    rows = f'<tr class="lab"><td colspan="2" class="who">{e(label)}</td></tr>' if label else ''
    for s in segs:
        who = f'<span class="who">{e(s["who"])}：</span>' if s.get('who') else ''
        rows += f'<tr><td>{who}{e(s["es"])}</td><td class="zh">{e(s["zh"])}</td></tr>'
    return f'<tbody class="{"keep" if label and len(segs) <= 2 else ""}">{rows}</tbody>'


def teacher():
    h = [f'<div class="cover"><div class="top"><h1 class="sans">Examen de práctica no oficial<br>Modelo 5 · formato SIELE Global</h1><div class="sub">{NAME}　教师用书</div>'
         '<p>内容：使用说明 · 录音清单 · 答案速查 · 阅读解析 · 听力原文、译文与解析 · 写作评分与范文 · 口语实施、评分与范例 · 成绩换算 · 评分表</p></div>'
         f'<div class="disc">{e(DISCLAIMER)}<br>{e(DISCLAIMER_ES)}</div></div>']
    # ---- 1 使用说明
    trs = ''.join(f'<tr><td class="sans">{tid}.mp3</td><td>{lab}</td><td style="text-align:right">{dur(tid)}</td></tr>' for tid, lab in TRACKS)
    h.append('<div class="page"><h2>一、使用说明</h2>'
             '<h3>1. 考试流程</h3><table><tr><th style="width:6%">序</th><th>考试</th><th>时间</th><th>材料</th></tr>'
             '<tr><td>1</td><td>阅读（CL）</td><td>60 分钟</td><td>试题册 Prueba 1，答题卡第 1 页</td></tr>'
             f'<tr><td>2</td><td>听力（CA）</td><td>约 {CA_MIN} 分钟（音轨长度）</td><td>试题册 Prueba 2，答题卡第 1 页，SIELE5_CA_completa.mp3 或 T1–T6 分段音轨</td></tr>'
             '<tr><td>—</td><td>休息</td><td>15 分钟</td><td></td></tr>'
             '<tr><td>3</td><td>写作（EIE）</td><td>50 分钟</td><td>试题册 Prueba 3，答题卡第 2–4 页</td></tr>'
             f'<tr><td>4</td><td>口语（EIO）</td><td>约 {EIO_MIN} 分钟（每人，含准备时间）</td><td>试题册 Prueba 4，口语音轨，录音设备</td></tr></table>'
             '<h3>2. 听力</h3><p>每个 tarea 一条音轨，读题时间、两遍之间的停顿和作答时间都已录进去；也可以直接播放 SIELE5_CA_completa.mp3（六段连播）。'
             '各段的时间设定如下：读题 30/30/30/45/45/50 秒，T1、T4、T5、T6 两遍之间 10 秒，T2、T3 每段连放两遍（中间 5 秒）后留 10 秒作答，T5 片段之间 5 秒，每个 tarea 结束留 30 秒检查。'
             '真实考试由电脑显示题号和“Audio 1”等提示，本卷由男声旁白报出“Tarea uno.”“Noticia uno.”“Persona uno.”“Fragmento uno.”等，不读题目。</p>'
             '<h3>3. 口语</h3><p>真实考试没有考官，由电脑播放问题并录音。本卷按同样方式：考生边听音轨边作答，用手机或电脑把自己的回答录下来交给教师评分。'
             '音轨里一声提示音表示开始说，两声提示音表示时间到。Tarea 4 先给考生约 30 秒在试题册上选话题（音轨里没有这段时间），再播放对应话题的音轨（tema1 或 tema2）；Tarea 5 沿用同一话题。'
             '如果在教室集体进行，可以让考生分批在安静的地方录音；也可以由教师按音轨念出问题、计时。</p>'
             '<h3>4. 录音清单</h3><table><tr><th>文件</th><th>内容</th><th style="width:14%">时长</th></tr>' + trs + '</table>'
             '<p class="small">录音为语音合成，每一句都经语音识别逐词核对；成品响度 −16 LUFS，MP3 128 kbps。</p></div>')
    # ---- 2 答案速查
    cl = CL['tareas']
    clk = {q['n']: q['clave'] for tx in cl[0]['textos'] + cl[1]['textos'] for q in tx['preguntas']}
    clk.update({q['n']: q['clave'] for q in cl[2]['preguntas']})
    for tx in cl[3]['textos']:
        clk.update({int(g): L for g, L in tx['claves'].items()})
    clk.update({q['n']: q['clave'] for q in cl[4]['preguntas']})
    T = CA['tareas']
    cak = {q['n']: q['clave'] for t in T[:5] for q in t['preguntas']}
    keyrow = lambda d, a, b: '<tr>' + ''.join(f'<th>{n}</th>' for n in range(a, b)) + '</tr><tr>' + ''.join(f'<td class="key" style="text-align:center">{d[n]}</td>' for n in range(a, b)) + '</tr>'
    t1 = T[0]
    ca15 = '；'.join(f'{q["n"]} {q["clave"]}（{t1["banco"][LET.index(q["clave"])]}）' for q in t1['preguntas'])
    h.append('<div class="page"><h2>二、答案速查</h2><h3>阅读（Comprensión de lectura）</h3>'
             f'<table>{keyrow(clk, 1, 14)}{keyrow(clk, 14, 27)}{keyrow(clk, 27, 39)}</table>'
             f'<p class="small">T4 多余的片段：文本 1 是 {cl[3]["textos"][0]["sobra"]}，文本 2 是 {cl[3]["textos"][1]["sobra"]}。</p>'
             f'<h3>听力（Comprensión auditiva）</h3><table>{keyrow(cak, 1, 14)}{keyrow(cak, 14, 27)}{keyrow(cak, 27, 33)}</table>'
             f'<p>T1：{e(ca15)}。T3 多余的句子：{"、".join(T[2]["sobran"])}。</p>'
             f'<p>T6（33–38）选这六个：<span class="key">{"、".join(T[5]["claves"])}</span>（顺序不限，每选对一个得 1 分；多选的，每多一个扣 1 分，本 tarea 最低 0 分）。</p>'
             '<h3>计分</h3><p>阅读、听力各 38 分（每题 1 分），换算：得分 = 答对题数 × 250 ÷ 38，四舍五入。换算表和等级分界见第七部分。</p></div>')
    # ---- 3 阅读解析
    h.append('<div class="page"><h2>三、阅读解析</h2>')
    lv = {1: 'A1', 2: 'A2', 3: 'B1', 4: 'B2', 5: 'C1'}
    for t in cl:
        h.append(f'<h3>Tarea {t["n"]} <span class="tag">{lv[t["n"]]}</span></h3>')
        if t['n'] in (1, 2):
            for tx in t['textos']:
                for q in tx['preguntas']:
                    h.append(f'<div class="q"><span class="n">{q["n"]}.</span> {e(q["enunciado"])} <span class="key">答案 {q["clave"]}</span>'
                             f'<span class="small">（{e(q["foco"])}）</span>：{e(q["opciones"][LET.index(q["clave"])])}<div class="expl">{e(q["explicacion"])}</div></div>')
        elif t['n'] == 3:
            for q in t['preguntas']:
                h.append(f'<div class="q"><span class="n">{q["n"]}.</span> {e(q["enunciado"])} <span class="key">答案 {q["clave"]}</span><div class="expl">{e(q["explicacion"])}</div></div>')
        elif t['n'] == 4:
            for k, tx in enumerate(t['textos']):
                frag = {f['letra']: f['texto'] for f in tx['fragmentos']}
                h.append(f'<h4>文本 {k + 1}：{e(tx["titulo"])}（{e(tx["genero"])}）</h4>')
                for g, L in tx['claves'].items():
                    h.append(f'<div class="q"><span class="n">{g}.</span> <span class="key">{L}</span> {e(frag[L])}<div class="expl">{e(tx["explicaciones"][g])}</div></div>')
                h.append(f'<div class="q"><span class="n">多余</span> <span class="key">{tx["sobra"]}</span> {e(frag[tx["sobra"]])}<div class="expl">{e(tx["explicaciones"]["sobra"])}</div></div>')
        else:
            for q in t['preguntas']:
                h.append(f'<div class="q"><span class="n">{q["n"]}.</span> <span class="key">{q["clave"]} {e(q["opciones"][LET.index(q["clave"])])}</span>'
                         f'<span class="small">（{e(q["foco"])}；选项：{e(" / ".join(q["opciones"]))}）</span><div class="expl">{e(q["explicacion"])}</div></div>')
    h.append('</div>')
    # ---- 4 听力原文、译文、解析
    h.append('<div class="page"><h2>四、听力原文、译文与解析</h2><p class="small">左栏为录音原文，右栏为中文译文。录音中的旁白（“Tarea uno.”“Noticia uno.”等）不列出。</p>')
    lv = {1: 'A1', 2: 'A2', 3: 'B1', 4: 'B2', 5: 'C1', 6: 'C1'}
    for t in T:
        h.append(f'<h3>Tarea {t["n"]} <span class="tag">{lv[t["n"]]}</span> <span class="tag">SIELE5_CA_T{t["n"]}.mp3 · {dur("SIELE5_CA_T" + str(t["n"]))}</span></h3>')
        rows = ''.join(par_rows(a['segs'], a['label']) for a in t['audio'])
        h.append(f'<table class="par"><colgroup><col style="width:52%"><col style="width:48%"></colgroup>{rows}</table>')
        h.append('<h4>答案与解析</h4>')
        if t['n'] == 1:
            for q in t['preguntas']:
                h.append(f'<div class="q"><span class="n">{q["n"]}.</span> {blanks(q["enunciado"])} <span class="key">{q["clave"]}（{e(t["banco"][LET.index(q["clave"])])}）</span><div class="expl">{e(q["explicacion"])}</div></div>')
        elif t['n'] == 3:
            for q in t['preguntas']:
                L = q['clave']
                h.append(f'<div class="q"><span class="n">{q["n"]}.</span> Persona {q["persona"]} → <span class="key">{L}</span> {e(t["enunciados"][LET.index(L)])}'
                         f'<span class="small">（{e(t["enunciados_zh"][LET.index(L)])}）</span><div class="expl">{e(q["explicacion"])}</div></div>')
            h.append('<p class="small">多余的句子：' + '；'.join(f'{L}\u00a0{e(t["enunciados"][LET.index(L)].rstrip("."))}（{e(t["enunciados_zh"][LET.index(L)].rstrip("。"))}）' for L in t['sobran']) + '。</p>')
        elif t['n'] == 6:
            for i, s in enumerate(t['enunciados']):
                L = LET[i]
                h.append(f'<div class="q"><span class="n">{L}</span> {e(s)}<span class="small">（{e(t["enunciados_zh"][i])}）</span><div class="expl">{e(t["explicaciones"][L])}</div></div>')
        else:
            for q in t['preguntas']:
                h.append(f'<div class="q"><span class="n">{q["n"]}.</span> {e(q["enunciado"])} <span class="key">{q["clave"]}</span> {e(q["opciones"][LET.index(q["clave"])])}<div class="expl">{e(q["explicacion"])}</div></div>')
    h.append('</div>')
    # ---- 5 写作
    t1, t2 = EIE['tareas']
    crit = ''.join(f'<tr><td class="sans">{e(c["es"])}</td><td>{e(c["zh"])}</td></tr>' for c in EIE['criterios'])
    bands = [('5', '完全达到本 tarea 最高等级的要求（T1 为 B1，T2 为 C1）：表达准确、丰富、自然，几乎没有影响理解的错误。'),
             ('4', '基本达到最高等级：偶有错误或个别要点展开不足，但不影响整体效果。'),
             ('3', '达到中间等级（T1 为 A2，T2 为 B2）：意思清楚，结构和词汇比较简单或有若干错误。'),
             ('2', '接近中间等级：能完成部分要求，错误较多，有时影响理解。'),
             ('1', '只能用简单的词句表达部分内容（T1 约为 A1；T2 低于本 tarea 的等级范围，约为 B1 及以下）。'),
             ('0', '没有作答、完全离题，或无法评分。')]
    h.append('<div class="page"><h2>五、写作：评分与范文</h2>'
             f'<h3>评分维度</h3><table><tr><th style="width:26%">维度</th><th>看什么</th></tr>{crit}</table>'
             '<h3>分档参考（本卷自拟）</h3><p class="small">官方评分员用的是 SIELE 指南里的分级描述；下面是本卷为课堂评分自拟的简化参考，每个维度各给 0–5 分。</p>'
             '<table><tr><th style="width:8%">分</th><th>描述</th></tr>' + ''.join(f'<tr><td class="key" style="text-align:center">{a}</td><td>{b}</td></tr>' for a, b in bands) + '</table>'
             '<p>字数明显不足（少于下限的 80%）或明显超出，“完成任务”一项最多给 3 分；漏掉一个要点，“完成任务”扣 1 分。</p>'
             '<h3>换算</h3><p>每个 tarea：(0.22 ×（衔接 + 准确 + 广度）+ 0.34 × 完成任务) ÷ 5 × 125；两个 tarea 相加即写作得分（满分 250）。'
             '三个语言维度各占 22%、完成任务占 34%、两篇权重相同，是公开资料中的说法（未经官方文件证实），本卷照此换算。</p>')
    h.append(f'<h3>Tarea 1 范文</h3><div class="box">{paras(t1["modelo"]["texto"])}</div><p class="small">{e(t1["modelo"]["nota"])}</p><p><b>点评：</b>{e(t1["modelo"]["comentario"])}</p>'
             f'<p class="small">来信译文：{e(t1["estimulo"]["zh"])}</p>')
    for o in t2['opciones']:
        h.append(f'<h3>Tarea 2 · {e(o["titulo"])} 范文</h3><p class="small">新闻译文：{e(o["estimulo"]["zh"])}</p>'
                 f'<div class="box" style="break-inside:auto">{paras(o["modelo"]["texto"])}</div><p><b>点评：</b>{e(o["modelo"]["comentario"])}</p>')
    h.append('</div>')
    # ---- 6 口语
    o1, o2, o3, o4, o5 = EIO['tareas']
    crit = ''.join(f'<tr><td class="sans">{e(c["es"])}</td><td>{e(c["zh"])}</td></tr>' for c in EIO['criterios'])
    h.append('<div class="page"><h2>六、口语：实施、评分与范例</h2>'
             f'<h3>评分维度</h3><table><tr><th style="width:26%">维度</th><th>看什么</th></tr>{crit}</table>'
             '<p>每个 tarea 两个维度各 0–5 分，分档思路同写作：5 分完全达到本 tarea 的等级（T1 A2、T2 A2、T3 B1、T4 B2、T5 C1），3 分低一级，1 分只能零星表达，0 分没有作答或离题。'
             '本卷换算：每个 tarea（语言运用 + 完成任务）÷ 10 × 50，五个 tarea 相加即口语得分（满分 250）。官方各 tarea 的权重没有公开，这里按等权处理。</p>'
             '<h3>Tarea 1 问题（录音内容）</h3><table><tr><th style="width:6%"></th><th>问题</th><th>译文</th><th style="width:10%">作答</th></tr>'
             + ''.join(f'<tr><td class="key">{q["n"]}</td><td>{e(q["es"])}</td><td>{e(q["zh"])}</td><td>{q["segundos"]} 秒</td></tr>' for q in o1['preguntas']) + '</table>'
             '<h4>范例回答</h4>' + ''.join(f'<p><b class="sans">{q["n"]}.</b> {e(q["modelo"])}</p>' for q in o1['preguntas']))
    h.append('<h3>Tarea 2 插图内容（供评分对照）</h3>' + ''.join(f'<p><b>{e(im["titulo"])}</b>：{e(im["zh"])}</p>' for im in o2['imagenes'])
             + f'<h4>范例描述（图 {o2["modelo"]["imagen"]}）</h4><div class="box">{paras([o2["modelo"]["texto"]])}</div><p><b>点评：</b>{e(o2["modelo"]["comentario"])}</p>')
    h.append('<h3>Tarea 3 情境译文</h3>' + ''.join(f'<p><b>{e(p["parte"])} · Opción {o["n"]}</b>：{e(o["zh"])}</p>' for p in o3['partes'] for o in p['opciones'])
             + '<h4>范例留言</h4>' + ''.join(f'<div style="break-inside:avoid"><p><b>{e(m["parte"])} · Opción {m["opcion"]}</b></p><div class="box">{paras([m["texto"]])}</div></div>' for m in o3['modelos'])
             + f'<p><b>点评：</b>{e(o3["modelos_comentario"])}</p>')
    h.append('<h3>Tarea 4 短文译文与问题</h3>')
    for tm in o4['temas']:
        h.append(f'<div style="break-inside:avoid"><h4>话题 {tm["n"]}：{e(tm["titulo"])}</h4><p class="small">短文译文：{e(tm["zh"])}</p><table><tr><th style="width:12%">功能</th><th>问题（录音）</th><th>译文</th></tr>'
                 + ''.join(f'<tr><td>{e(q["tipo"])}</td><td>{e(q["es"])}</td><td>{e(q["zh"])}</td></tr>' for q in tm['preguntas']) + '</table></div>')
        if any('modelo' in q for q in tm['preguntas']):
            h.append('<h4>范例回答（话题 1）</h4>' + ''.join(f'<p><b class="sans">{k + 1}.</b> {e(q["modelo"])}</p>' for k, q in enumerate(tm['preguntas'])))
    h.append(f'<p><b>点评：</b>{e(o4["modelo_comentario"])}</p>')
    m = o5['modelo']
    h.append('<h3>Tarea 5 论断译文</h3>' + ''.join(f'<p>话题 {tm["n"]} · {a["letra"]}：{e(a["zh"])}</p>' for tm in o5['temas'] for a in tm['afirmaciones'])
             + f'<div style="break-inside:avoid"><h4>范例独白（话题 {m["tema"]}，论断 {m["afirmacion"]}）</h4><div class="box">{paras(m["texto"])}</div><p><b>点评：</b>{e(m["comentario"])}</p></div></div>')
    # ---- 7 成绩换算
    conv = lambda a: round(a * 250 / 38)
    rows = [list(range(i, min(i + 13, 39))) for i in (0, 13, 26)]
    tbl = ''.join('<tr><th>答对</th>' + ''.join(f'<td style="text-align:center">{a}</td>' for a in r) + '</tr><tr><th>得分</th>'
                  + ''.join(f'<td style="text-align:center" class="key">{conv(a)}</td>' for a in r) + '</tr>' for r in rows)
    cut = ''.join(f'<tr><td>{k}</td>' + ''.join(f'<td style="text-align:center">{c}</td>' for c in v) + '</tr>' for k, v in LEVEL_CUTS.items())
    lvl = lambda k: '；'.join(f'{name} {next(a for a in range(39) if conv(a) >= c)} 题' for c, name in zip(LEVEL_CUTS[k], LEVELS))
    h.append('<div class="page"><h2>七、成绩换算与等级</h2><h3>阅读、听力：答对题数 → 得分（× 250 ÷ 38）</h3>'
             f'<table>{tbl}</table><h3>各部分等级分界（250 分制，达到即为该等级）</h3>'
             '<table><tr><th>部分</th>' + ''.join(f'<th>{x}</th>' for x in LEVELS) + f'</tr>{cut}</table>'
             '<p>低于 A1 分界为“低于 A1”。总分为四部分相加（满分 1000）；SIELE 证书按各部分分别标注等级。</p>'
             f'<p class="small">达到各等级最少要答对（阅读）：{lvl("阅读")}。</p><p class="small">达到各等级最少要答对（听力）：{lvl("听力")}。</p>'
             '<p class="small">说明：分数换算公式和分界来自官方公开资料；本卷是模拟卷，题目难度没有经过真实考生的等值校准，结果只作练习参考。</p>')
    # ---- 8 评分表
    eie_t = '<table><tr><th>Tarea</th><th>衔接</th><th>准确</th><th>广度</th><th>完成任务</th><th>本 tarea 得分</th></tr>' + \
            ''.join(f'<tr><td>Tarea {n}</td><td></td><td></td><td></td><td></td><td></td></tr>' for n in (1, 2)) + '<tr><td colspan="5" style="text-align:right">写作得分（满分 250）</td><td></td></tr></table>'
    eio_t = '<table><tr><th>Tarea</th><th>语言运用</th><th>完成任务</th><th>本 tarea 得分</th><th>备注</th></tr>' + \
            ''.join(f'<tr><td>Tarea {n}</td><td></td><td></td><td></td><td></td></tr>' for n in range(1, 6)) + '<tr><td colspan="3" style="text-align:right">口语得分（满分 250）</td><td></td><td></td></tr></table>'
    total = '<table><tr><th>部分</th><th>得分</th><th>等级</th></tr>' + ''.join(f'<tr><td>{k}</td><td></td><td></td></tr>' for k in ('阅读', '听力', '写作', '口语')) + '<tr><td>总分（满分 1000）</td><td></td><td></td></tr></table>'
    h.append('<div class="page"><h2>八、评分表（可复印）</h2><p>考生姓名 <span class="field"></span>　日期 <span class="field" style="min-width:30mm"></span></p>'
             f'<h3>写作</h3>{eie_t}<p class="small">每个 tarea：(0.22 ×（衔接 + 准确 + 广度）+ 0.34 × 完成任务) ÷ 5 × 125</p>'
             f'<h3>口语</h3>{eio_t}<p class="small">每个 tarea：（语言运用 + 完成任务）÷ 10 × 50</p><h3>总成绩</h3>{total}</div></div>')
    return ''.join(h)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    books = {
        '考生试题册': (doc('SIELE 模拟卷 5 · 考生试题册', cover() + booklet_cl() + booklet_ca() + booklet_eie() + booklet_eio()), 'SIELE 模拟卷（第五套，非官方）· Examen de práctica no oficial · Cuadernillo del candidato'),
        '答题卡': (doc('SIELE 模拟卷 5 · 答题卡', sheet()), 'SIELE 模拟卷（第五套，非官方）· Examen de práctica no oficial · Hoja de respuestas'),
        '教师用书': (doc('SIELE 模拟卷 5 · 教师用书', '<style>p { text-align: left; } .q { margin: 5pt 0 6pt; } .expl { margin-bottom: 5pt; }</style>' + teacher()), 'SIELE 模拟卷（第五套，非官方）· 教师用书'),
    }
    for name, (text, _) in books.items():
        (OUT / f'SIELE模拟卷5_{name}.html').write_text(text, 'utf-8')
    if '--html-only' in sys.argv:
        return
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        pg = br.new_page()
        for name, (_, foot) in books.items():
            pg.goto((OUT / f'SIELE模拟卷5_{name}.html').as_uri())
            pg.wait_for_load_state('networkidle')
            ft = (f'<div style="font-size:7.5pt;width:100%;text-align:center;color:#444;font-family:\'Helvetica Neue\',\'PingFang SC\',sans-serif;">'
                  f'{e(foot)}　·　<span class="pageNumber"></span> / <span class="totalPages"></span></div>')
            pg.pdf(path=str(OUT / f'SIELE模拟卷5_{name}.pdf'), format='A4', print_background=True, display_header_footer=True,
                   header_template='<div></div>', footer_template=ft, margin={'top': '17mm', 'bottom': '19mm', 'left': '17mm', 'right': '17mm'})
            print(name, 'PDF')
        br.close()


if __name__ == '__main__':
    main()
