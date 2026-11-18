"""DELE 模拟卷内容自查：按 考试规格.md 逐项核对 content/<级别>/*.json。

    python3 tools/check_content.py A1            # 查 A1 全部四个文件和插图清单 art_*.json
    python3 tools/check_content.py A1 cl ca      # 只查阅读、听力

✗ 是必须改的错误，△ 是提醒（自己判断，确实没问题可以不改）。全部没有 ✗ 才算通过（最后一行 PASS）。
"""
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VOCES = {'男1', '男2', '女1', '女2', '女3', '女4'}
LET = 'ABCDEFGHIJKLMNOP'


def R(a, b):
    return list(range(a, b + 1))


# ------------------------------------------------------------------ 规格：每个 tarea 的题型、题号、文本数、词数
# words：每篇文本/每段录音的词数范围；total：整篇的词数范围
SPEC = {
    'A1': {
        'cl': [dict(tipo='seleccion', items=[0] + R(1, 5), ntext=1, words=(150, 175), opts=3, img_items=[5]),
               dict(tipo='relacionar', items=[0] + R(6, 11), letters=10, words=(20, 30), icono=True, otipo='textos'),
               dict(tipo='relacionar', items=[0] + R(12, 17), letters=10, words=(20, 30), stmt_words=(10, 25), otipo='textos', persona=True),
               dict(tipo='seleccion', items=R(18, 25), ntext=1, words=(175, 210), opts=3)],
        'ca': [dict(tipo='imagenes', audio_ids=[str(i) for i in range(0, 6)], words=(30, 40)),
               dict(tipo='relacionar_imagenes', audio_ids=['0'] + [str(i) for i in R(6, 10)], images=9, words=(15, 30)),
               dict(tipo='frases', items=[0] + R(11, 18), sentences=9, sent_words=(15, 25), finales=12),
               dict(tipo='completar', items=[0] + R(19, 25), opciones=9, words=(160, 185))],
        'eie': [dict(form=True, words=(15, 25)), dict(words=(30, 40))],
        'eio': [dict(nopt=1), dict(nopt=2), dict(nopt=1)],
    },
    'A2': {
        'cl': [dict(tipo='seleccion', items=R(1, 5), ntext=1, words=(250, 300), opts=3),
               dict(tipo='seleccion', items=[0] + R(6, 13), ntext=9, words=(50, 80), opts=3),
               dict(tipo='relacionar', items=R(14, 19), letters=3, words=(100, 120), otipo='textos'),
               dict(tipo='seleccion', items=R(20, 25), ntext=1, words=(375, 425), opts=3)],
        'ca': [dict(tipo='imagenes', audio_ids=[str(i) for i in range(0, 7)], words=(50, 80)),
               dict(tipo='seleccion', items=[0] + R(7, 12), audio_ids=['0'] + [str(i) for i in R(7, 12)], words=(40, 60), opts=3),
               dict(tipo='quien', items=R(13, 18), words=(225, 275)),
               dict(tipo='relacionar', otipo='frases', letters=11, audio_ids=['0'] + [str(i) for i in R(19, 25)], words=(30, 50))],
        'eie': [dict(words=(60, 70), stim_words=(35, 45)), dict(nopt=2, words=(70, 80))],
        'eio': [dict(nopt=2), dict(nopt=2, art=True), dict(nopt=2)],
    },
    'B1': {
        'cl': [dict(tipo='relacionar', items=[0] + R(1, 6), letters=10, words=(40, 60), stmt_words=(20, 30), otipo='textos', persona=True),
               dict(tipo='seleccion', items=R(7, 12), ntext=1, words=(400, 450), opts=3),
               dict(tipo='relacionar', items=R(13, 18), letters=3, words=(100, 120), otipo='textos'),
               dict(tipo='fragmentos', items=R(19, 24), nfrag=8, words=(400, 450)),
               dict(tipo='huecos', items=R(25, 30), words=(150, 200))],
        'ca': [dict(tipo='seleccion', items=R(1, 6), audio_ids=[str(i) for i in R(1, 6)], words=(40, 60), opts=3),
               dict(tipo='seleccion', items=R(7, 12), audio_ids=['1'], words=(400, 450), opts=3),
               dict(tipo='seleccion', items=R(13, 18), audio_ids=['1'], words=(350, 400), opts=3),
               dict(tipo='relacionar', otipo='frases', letters=10, audio_ids=['0'] + [str(i) for i in R(19, 24)], words=(50, 70)),
               dict(tipo='quien', items=R(25, 30), words=(250, 300))],
        'eie': [dict(words=(100, 120), stim_words=(75, 85)), dict(nopt=2, words=(130, 150), stim_words=(40, 50))],
        'eio': [dict(nopt=2), dict(nopt=1), dict(nopt=2, art=True), dict(nopt=2)],
    },
    'B2': {
        'cl': [dict(tipo='seleccion', items=R(1, 6), ntext=1, words=(400, 450), opts=3),
               dict(tipo='relacionar', items=R(7, 16), letters=4, words=(130, 150), otipo='textos'),
               dict(tipo='fragmentos', items=R(17, 22), nfrag=8, words=(400, 450), frag_words=(15, 20)),
               dict(tipo='huecos', items=R(23, 36), words=(400, 450))],
        'ca': [dict(tipo='seleccion', items=R(1, 6), audio_ids=[str(i) for i in R(1, 6)], words=(40, 60), opts=3),
               dict(tipo='quien', items=R(7, 12), words=(250, 300)),
               dict(tipo='seleccion', items=R(13, 18), audio_ids=['1'], words=(400, 450), opts=3),
               dict(tipo='relacionar', otipo='frases', letters=10, audio_ids=['0'] + [str(i) for i in R(19, 24)], words=(50, 70)),
               dict(tipo='seleccion', items=R(25, 30), audio_ids=['1'], words=(400, 450), opts=3)],
        'eie': [dict(words=(150, 180), audio_words=(200, 250)), dict(nopt=2, words=(150, 180))],
        'eio': [dict(nopt=2), dict(nopt=2, art=True), dict(nopt=2)],
    },
    'C1': {
        'cl': [dict(tipo='seleccion', items=R(1, 6), ntext=1, words=(650, 750), opts=3),
               dict(tipo='fragmentos', items=R(7, 12), nfrag=7, words=(550, 650)),
               dict(tipo='seleccion', items=R(13, 18), ntext=1, words=(550, 650), opts=3),
               dict(tipo='relacionar', items=R(19, 26), letters=6, words=(100, 150), otipo='textos', repeat_ok=True),
               dict(tipo='huecos', items=R(27, 40), words=(375, 425))],
        'ca': [dict(tipo='seleccion_multiple', frases=12, correct=6, words=(700, 750)),
               dict(tipo='seleccion', items=R(7, 14), audio_ids=['1', '2', '3', '4'], words=(220, 300), opts=3, per_audio=2),
               dict(tipo='seleccion', items=R(15, 20), audio_ids=['1'], words=(750, 900), opts=3),
               dict(tipo='seleccion', items=R(21, 30), audio_ids=[str(i) for i in R(1, 10)], words=(38, 45), opts=3)],
        'eie': [dict(words=(220, 250), audio_words=(650, 750)), dict(nopt=2, words=(180, 220))],
        'eio': [dict(nopt=2, text_words=(750, 850)), dict(nopt=1), dict(nopt=2, propuestas=4)],
    },
}
DUR = {'A1': (45, 25, 25, 10), 'A2': (60, 40, 45, 12), 'B1': (70, 40, 60, 15), 'B2': (70, 40, 80, 20), 'C1': (90, 50, 80, 20)}
PREP = {'A1': 10, 'A2': 12, 'B1': 15, 'B2': 20, 'C1': 20}

ERR, WARN = [], []


def err(where, msg):
    ERR.append(f'✗ {where}：{msg}')


def warn(where, msg):
    WARN.append(f'△ {where}：{msg}')


WORD = re.compile(r"[0-9A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+(?:[:.,'][0-9]+)*")


def nwords(x):
    if isinstance(x, list):
        return sum(nwords(s) for s in x)
    return len(WORD.findall(re.sub(r'\[\d+\]', ' ', x or '')))


def in_range(n, rg, slack=0.03):
    lo, hi = rg
    return lo * (1 - slack) <= n <= hi * (1 + slack)


def es_strings(obj, path=''):
    """所有西语字符串（键名不是 zh/explicacion/…_zh 的字符串）。"""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in ('zh', 'explicacion', 'comentario_zh', 'notas_zh', 'instruccion_zh', 'tema_zh', 'modelo_zh', 'texto_zh', 'uso', 'v', 'who', 'clave', 'tipo', 'id', 'art', 'icono', 'estilo', 'foco', 'opciones_tipo'):
                continue
            yield from es_strings(v, f'{path}.{k}')
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from es_strings(v, f'{path}[{i}]')
    elif isinstance(obj, str):
        if obj.startswith('art:'):
            return
        yield path, obj


def zh_missing(obj, path, keys=('zh',)):
    pass


ORTO = [(r'\bsólo\b', 'sólo 应写 solo'), (r'\b(éste|ésta|éstos|éstas|ése|ésa|ésos|ésas|aquél|aquélla|aquéllos|aquéllas)\b', '指示代词不带重音'),
        (r'\s[,.;:]', '标点前多了空格'), (r'[a-záéíóúñ][¿¡]', '¿¡ 前少了空格'), (r'\.\.', '两个句号'), (r'  ', '两个空格')]


def check_es(where, s):
    for pat, msg in ORTO:
        if re.search(pat, s):
            err(where, f'{msg}：{s[:70]}')
    for a, b in (('¿', '?'), ('¡', '!')):
        if s.count(a) != s.count(b):
            err(where, f'{a}{b} 不成对：{s[:70]}')
    if re.search(r'[一-鿿]', s):
        err(where, f'西语字段里有汉字：{s[:40]}')


AUDIO_BAD = [(r'\b(Sr|Sra|Srta|Dr|Dra|etc|Ud|Uds|Avda|pág|tel|núm)\.', '缩写'), (r'%', '% 号（写 por ciento）'), (r'€|\$', '货币符号（写 euros）'),
             (r'…|\.\.\.', '省略号'), (r'\b(km|kg|cm|mm|h)\b', '单位缩写'), (r'\b[A-ZÁÉÍÓÚÑ]{2,}\b', '全大写的词/缩略语'),
             (r'\b(ejem|mmm+|ehh*|jaja\w*|uf+)\b', '拟声词'), (r'[()\[\]]', '括号（舞台说明？）'), (r'www\.|@|https?:', '网址或邮箱'),
             (r'"', '直引号')]


def check_audio_text(where, s):
    for pat, msg in AUDIO_BAD:
        m = re.search(pat, s, flags=0 if 'A-Z' in pat else re.I)
        if m:
            err(where, f'录音原文有{msg}「{m.group()}」：{s[:60]}')
    for sent in re.split(r'(?<=[.!?])\s+', s.strip()):
        w = WORD.findall(sent)
        if len(w) == 1 and sent.strip('¡¿!?.').lower() in ('sí', 'no', 'vale', 'claro', 'bueno', 'gracias', 'vale'):
            err(where, f'单独一个词成句「{sent}」（和后面的话连在一起）')
        if len(w) > 30:
            warn(where, f'一句 {len(w)} 个词，太长：{sent[:50]}…')
        elif len(w) > 25:
            warn(where, f'一句 {len(w)} 个词，超过 25 词（合成容易出错，最好拆开）：{sent[:50]}…')
        # 少于 4 词的短句合成时由 make_audio.chunks() 并进前后句，这里不再提醒


def check_segs(where, segs, monologue_ok_male1=False):
    whos = {}
    for k, sg in enumerate(segs):
        w = f'{where}.segs[{k}]'
        if sg.get('v') not in VOCES:
            err(w, f"声音 {sg.get('v')!r} 不在 {sorted(VOCES)}")
        for f in ('who', 'es', 'zh'):
            if not sg.get(f):
                err(w, f'缺 {f}')
        check_es(w, sg.get('es', ''))
        check_audio_text(w, sg.get('es', ''))
        whos.setdefault(sg.get('who'), set()).add(sg.get('v'))
    for who, vs in whos.items():
        if len(vs) > 1:
            err(where, f'同一个人 {who} 用了几个声音 {vs}')
    byvoice = Counter(next(iter(vs)) for vs in whos.values())
    for v, n in byvoice.items():
        if n > 1:
            err(where, f'一段录音里 {n} 个人都用 {v}')
    if len(whos) == 1 and '男1' in next(iter(whos.values())) and not monologue_ok_male1:
        err(where, '独白不用男1（播音员的声音）')


def keys_check(where, keys, nopts):
    keys = [k for k in keys if k]
    if not keys:
        return
    c = Counter(keys)
    n = len(keys)
    if nopts <= 4 and n >= 5:
        hi = math.ceil(n / nopts) + 1
        for k, v in c.items():
            if v > hi:
                warn(where, f'答案 {k} 出现 {v} 次（共 {n} 题），分布不均：{"".join(keys)}')
        missing = [LET[i] for i in range(nopts) if LET[i] not in c]
        if missing and n >= 2 * nopts:
            warn(where, f'答案里一次也没有 {missing}：{"".join(keys)}')
    for i in range(len(keys) - 2):
        if keys[i] == keys[i + 1] == keys[i + 2]:
            warn(where, f'连续三题答案都是 {keys[i]}：{"".join(keys)}')
            break


LONG = []


def mc_check(where, q, nopts=3):
    o = q.get('opciones', [])
    if len(o) != nopts:
        err(where, f'选项 {len(o)} 个，应为 {nopts}')
        return
    if q.get('clave') not in LET[:nopts]:
        err(where, f"答案 {q.get('clave')!r} 不对")
        return
    if len(set(o)) < len(o):
        err(where, '有相同的选项')
    if not any(x.startswith('art:') for x in o):
        for i, x in enumerate(o):
            check_es(f'{where}.opciones[{i}]', x)
        L = [len(x) for x in o]
        k = LET.index(q['clave'])
        LONG.append(L[k] == max(L) and L.count(max(L)) == 1)
    if not q.get('explicacion') or len(q['explicacion']) < 25:
        err(where, '解析太短或没有')


def ids_seq(where, got, want, what):
    if got != want:
        err(where, f'{what}应为 {want}，实际 {got}')


def check_cl_ca(lv, part, d):
    spec = SPEC[lv][part]
    T = d.get('tareas', [])
    if len(T) != len(spec):
        err(part, f'tarea 数 {len(T)}，应为 {len(spec)}')
    for t, sp in zip(T, spec):
        W = f"{part}.T{t.get('n')}"
        if t.get('tipo') != sp['tipo']:
            err(W, f"tipo 应为 {sp['tipo']}，实际 {t.get('tipo')}")
            continue
        for f in ('instruccion_es', 'instruccion_zh', 'tema_zh'):
            if not t.get(f):
                err(W, f'缺 {f}')
        check_es(W + '.instruccion_es', t.get('instruccion_es', ''))
        if part == 'ca':
            check_audio_text(W + '.instruccion_es', t.get('instruccion_es', ''))
        tipo = sp['tipo']
        keys = []
        if part == 'cl' and tipo == 'seleccion':
            tx = t.get('textos', [])
            if len(tx) != sp['ntext']:
                err(W, f"文本 {len(tx)} 篇，应为 {sp['ntext']}")
            for x in tx:
                n = nwords(x.get('cuerpo', []))
                if not in_range(n, sp['words']):
                    err(f"{W}.texto {x.get('id')}", f"正文 {n} 词，应为 {sp['words'][0]}—{sp['words'][1]}")
                if len(x.get('zh', [])) != len(x.get('cuerpo', [])):
                    err(f"{W}.texto {x.get('id')}", '中文译文段数和原文不一致')
            qs = t.get('preguntas', [])
            ids_seq(W, [q.get('n') for q in qs], sp['items'], '题号')
            ids_t = {x.get('id') for x in tx}
            for q in qs:
                if q.get('texto') not in ids_t:
                    err(f"{W}.{q.get('n')}", f"texto {q.get('texto')!r} 找不到")
                mc_check(f"{W}.{q.get('n')}", q)
                if q.get('n') in sp.get('img_items', []) and not all(o.startswith('art:') for o in q.get('opciones', [])):
                    err(f"{W}.{q.get('n')}", '这题的选项应是图片 art:…')
                if q.get('n'):
                    keys.append(q.get('clave'))
            if sp['ntext'] > 1:
                ids_seq(W, [x.get('id') for x in tx], [str(i) for i in sp['items']], '文本 id ')
        elif tipo == 'relacionar' and sp.get('otipo') == 'textos':
            tx = t.get('textos', [])
            ids_seq(W, [x.get('id') for x in tx], list(LET[:sp['letters']]), '文本字母')
            for x in tx:
                n = nwords(x.get('cuerpo', []))
                if not in_range(n, sp['words'], 0.1):
                    err(f"{W}.texto {x.get('id')}", f"{n} 词，应为 {sp['words'][0]}—{sp['words'][1]}")
                if sp.get('icono') and not str(x.get('icono', '')).startswith('art:'):
                    err(f"{W}.texto {x.get('id')}", '缺图标 icono')
            en = t.get('enunciados', [])
            ids_seq(W, [e.get('n') for e in en], sp['items'], '题号')
            used = []
            for e in en:
                w = f"{W}.{e.get('n')}"
                if e.get('clave') not in LET[:sp['letters']]:
                    err(w, f"答案 {e.get('clave')!r} 不对")
                check_es(w, e.get('texto', ''))
                if sp.get('persona') and not e.get('persona'):
                    err(w, '缺 persona')
                if sp.get('stmt_words') and not in_range(nwords(e.get('texto', '')), sp['stmt_words'], 0.1):
                    err(w, f"陈述 {nwords(e.get('texto', ''))} 词，应为 {sp['stmt_words'][0]}—{sp['stmt_words'][1]}")
                if not e.get('explicacion'):
                    err(w, '缺解析')
                used.append(e.get('clave'))
            if sp['letters'] <= 4:                      # 几篇文本对多题（A2/B1 T3、B2 T2）：每篇文本对应的题数要均衡
                cu = Counter(used)
                lo, hi = len(used) // sp['letters'], -(-len(used) // sp['letters'])
                if set(cu) != set(LET[:sp['letters']]) or any(not (lo <= v <= hi) for v in cu.values()):
                    err(W, f'每篇文本应对应 {lo}—{hi} 题：{dict(sorted(cu.items()))}')
            elif not sp.get('repeat_ok') and len(set(used)) != len(used):
                err(W, f'答案字母重复：{used}')
            if sp.get('repeat_ok') and len(set(used)) < 5:
                warn(W, f'只用到 {len(set(used))} 篇文本：{used}')
            keys = [e.get('clave') for e in en if e.get('n')]
            if sp['letters'] <= 4:
                keys_check(W, keys, sp['letters'])
            keys = []
        elif tipo == 'fragmentos':
            x = t.get('texto', {})
            n = nwords(x.get('cuerpo', []))
            if not in_range(n, sp['words']):
                err(W, f"正文（不算片段）{n} 词，应为 {sp['words'][0]}—{sp['words'][1]}")
            gaps = [int(g) for g in re.findall(r'\[(\d+)\]', ' '.join(x.get('cuerpo', [])))]
            ids_seq(W, gaps, sp['items'], '文中空缺')
            fr = t.get('fragmentos', [])
            ids_seq(W, [f.get('id') for f in fr], list(LET[:sp['nfrag']]), '片段字母')
            for f in fr:
                if sp.get('frag_words') and not in_range(nwords(f.get('texto', '')), sp['frag_words'], 0.1):
                    err(f"{W}.片段{f.get('id')}", f"{nwords(f.get('texto', ''))} 词，应为 {sp['frag_words'][0]}—{sp['frag_words'][1]}")
                check_es(f"{W}.片段{f.get('id')}", f.get('texto', ''))
            hu = t.get('huecos', [])
            ids_seq(W, [h.get('n') for h in hu], sp['items'], '答案题号')
            ks = [h.get('clave') for h in hu]
            if len(set(ks)) != len(ks):
                err(W, f'片段重复使用：{ks}')
            unused = set(LET[:sp['nfrag']]) - set(ks)
            if {d_.get('id') for d_ in t.get('distractores', [])} != unused:
                err(W, f'distractores 应解释没用的片段 {sorted(unused)}')
        elif tipo == 'huecos':
            x = t.get('texto', {})
            n = nwords(x.get('cuerpo', []))
            if not in_range(n, sp['words']):
                err(W, f"正文 {n} 词，应为 {sp['words'][0]}—{sp['words'][1]}")
            gaps = [int(g) for g in re.findall(r'\[(\d+)\]', ' '.join(x.get('cuerpo', [])))]
            ids_seq(W, gaps, sp['items'], '文中空缺')
            qs = t.get('preguntas', [])
            ids_seq(W, [q.get('n') for q in qs], sp['items'], '题号')
            for q in qs:
                mc_check(f"{W}.{q.get('n')}", q)
                keys.append(q.get('clave'))
        # ---------------- 听力
        elif part == 'ca':
            au = t.get('audios', [])
            if 'audio_ids' in sp:
                ids_seq(W, [a.get('id') for a in au], sp['audio_ids'], '录音 id ')
            for a in au:
                w = f"{W}.audio {a.get('id')}"
                check_segs(w, a.get('segs', []))
                n = nwords([s.get('es', '') for s in a.get('segs', [])])
                rg = sp.get('words')
                if rg and tipo not in ('frases',) and not in_range(n, rg, 0.05):
                    err(w, f'录音 {n} 词，应为 {rg[0]}—{rg[1]}')
                for f in ('presentacion', 'pregunta_oral'):
                    if a.get(f):
                        check_es(w, a[f])
                        check_audio_text(w + '.' + f, a[f])
            if tipo == 'imagenes':
                for a in au:
                    w = f"{W}.audio {a.get('id')}"
                    if not a.get('pregunta_oral'):
                        err(w, '缺 pregunta_oral')
                    if len(a.get('opciones', [])) != 3 or not all(str(o).startswith('art:') for o in a.get('opciones', [])):
                        err(w, '要三张图 art:…')
                    if a.get('clave') not in 'ABC' or not a.get('clave'):
                        err(w, '答案不对')
                    if not a.get('explicacion'):
                        err(w, '缺解析')
                    if a.get('id') != '0':
                        keys.append(a.get('clave'))
                if lv == 'A2':
                    for a in au:
                        if not a.get('presentacion'):
                            err(f"{W}.audio {a.get('id')}", 'A2 T1 每段要有情景介绍 presentacion')
            elif tipo == 'relacionar_imagenes':
                im = t.get('imagenes', [])
                ids_seq(W, [i.get('id') for i in im], list(LET[:sp['images']]), '图片字母')
                ks = [a.get('clave') for a in au]
                if len(set(ks)) != len(ks) or not set(ks) <= set(LET[:sp['images']]):
                    err(W, f'答案重复或不对：{ks}')
            elif tipo == 'frases':
                if len(au) != 1:
                    err(W, '只要一段独白')
                segs = au[0].get('segs', []) if au else []
                if len(segs) != sp['sentences']:
                    err(W, f"独白要 {sp['sentences']} 句（片段），实际 {len(segs)}")
                for k, sg in enumerate(segs):
                    if not in_range(nwords(sg.get('es', '')), sp['sent_words'], 0.1):
                        err(f'{W}.句{k}', f"{nwords(sg.get('es', ''))} 词，应为 {sp['sent_words'][0]}—{sp['sent_words'][1]}")
                ini = t.get('inicios', [])
                ids_seq(W, [i.get('n') for i in ini], sp['items'], '题号')
                ids_seq(W, [i.get('seg') for i in ini], list(range(sp['sentences'])), 'seg 序号')
                fi = t.get('finales', [])
                ids_seq(W, [f.get('id') for f in fi], list(LET[:sp['finales']]), '结尾字母')
                ks = [i.get('clave') for i in ini]
                if len(set(ks)) != len(ks):
                    err(W, f'答案重复：{ks}')
                for i in ini:
                    if not i.get('explicacion'):
                        err(f"{W}.{i.get('n')}", '缺解析')
            elif tipo == 'completar':
                fr = t.get('frases', [])
                ids_seq(W, [f.get('n') for f in fr], sp['items'], '题号')
                op = t.get('opciones', [])
                ids_seq(W, [o.get('id') for o in op], list(LET[:sp['opciones']]), '选项字母')
                ks = [f.get('clave') for f in fr]
                if len(set(ks)) != len(ks):
                    err(W, f'答案重复：{ks}')
                for f in fr:
                    if '____' not in f.get('texto', ''):
                        err(f"{W}.{f.get('n')}", '句子里要有 ____')
                    if not f.get('explicacion'):
                        err(f"{W}.{f.get('n')}", '缺解析')
            elif tipo == 'seleccion':
                qs = t.get('preguntas', [])
                ids_seq(W, [q.get('n') for q in qs], sp['items'], '题号')
                aid = {a.get('id') for a in au}
                per = Counter(q.get('audio') for q in qs)
                for q in qs:
                    if q.get('audio') not in aid:
                        err(f"{W}.{q.get('n')}", f"audio {q.get('audio')!r} 找不到")
                    mc_check(f"{W}.{q.get('n')}", q)
                    if q.get('n'):
                        keys.append(q.get('clave'))
                if sp.get('per_audio') and any(v != sp['per_audio'] for v in per.values()):
                    err(W, f"每段录音 {sp['per_audio']} 题：{dict(per)}")
            elif tipo == 'quien':
                ps = t.get('personas', {})
                if set(ps) != {'A', 'B'}:
                    err(W, 'personas 要有 A、B')
                if len(au) != 1:
                    err(W, '只要一段对话')
                else:
                    vs = {sg.get('who'): sg.get('v') for sg in au[0].get('segs', [])}
                    if set(vs) != set(ps.values()):
                        err(W, f'对话里的人物 {sorted(vs)} 和 personas {ps} 对不上')
                    elif not (str(vs.get(ps.get('A'))).startswith('男') and str(vs.get(ps.get('B'))).startswith('女')):
                        err(W, 'A 要是男声、B 要是女声')
                en = t.get('enunciados', [])
                ids_seq(W, [e.get('n') for e in en], sp['items'], '题号')
                for e in en:
                    if e.get('clave') not in 'ABC' or not e.get('clave'):
                        err(f"{W}.{e.get('n')}", '答案不对')
                    if not e.get('explicacion'):
                        err(f"{W}.{e.get('n')}", '缺解析')
                    check_es(f"{W}.{e.get('n')}", e.get('texto', ''))
                keys = [e.get('clave') for e in en]
            elif tipo == 'relacionar':
                fr = t.get('frases', [])
                ids_seq(W, [f.get('id') for f in fr], list(LET[:sp['letters']]), '陈述字母')
                ks = [a.get('clave') for a in au]
                if len(set(ks)) != len(ks) or not set(ks) <= set(LET[:sp['letters']]):
                    err(W, f'答案重复或不对：{ks}')
                for a in au:
                    if not a.get('explicacion'):
                        err(f"{W}.audio {a.get('id')}", '缺解析')
                    if not a.get('rotulo'):
                        err(f"{W}.audio {a.get('id')}", '缺 rotulo')
            elif tipo == 'seleccion_multiple':
                fr = t.get('frases', [])
                ids_seq(W, [f.get('id') for f in fr], list(LET[:sp['frases']]), '陈述字母')
                c = [f for f in fr if f.get('correcta') is True]
                if len(c) != sp['correct']:
                    err(W, f"正确项要 {sp['correct']} 个，实际 {len(c)}")
                for f in fr:
                    if not f.get('explicacion'):
                        err(f"{W}.{f.get('id')}", '缺解析')
                if len(au) != 1:
                    err(W, '只要一段独白')
        if keys and tipo not in ('relacionar',):
            keys_check(W, keys, 3)
    if LONG:
        r = sum(LONG) / len(LONG)
        (err if r > 0.4 else (warn if r > 0.34 else (lambda *a: None)))(part, f'正确项是最长选项的比例 {r:.0%}（{sum(LONG)}/{len(LONG)}，上限 40%）')
        LONG.clear()


def check_eie(lv, d):
    spec = SPEC[lv]['eie']
    T = d.get('tareas', [])
    if len(T) != len(spec):
        err('eie', f'tarea 数 {len(T)}，应为 {len(spec)}')
    for t, sp in zip(T, spec):
        W = f"eie.T{t.get('n')}"
        units = t.get('opciones') or [t]
        if sp.get('nopt', 1) != len(t.get('opciones') or [1]):
            err(W, f"要 {sp.get('nopt', 1)} 个选项（opciones）")
        if list(t.get('palabras', [])) != list(sp['words']) and not t.get('opciones'):
            err(W, f"palabras 应为 {list(sp['words'])}")
        for u in units:
            w = W + (f" opción {u.get('id')}" if t.get('opciones') else '')
            for s in u.get('instruccion_es', []):
                check_es(w, s)
            if sp.get('form'):
                fo = t.get('formulario', [])
                if len(fo) < 5:
                    err(w, '表格栏目太少')
                nlong = sum(nwords(f.get('modelo', '')) for f in fo if f.get('tipo') == 'largo')
                if not in_range(nlong, sp['words'], 0.1):
                    warn(w, f'表格简答栏范文共 {nlong} 词（规格 15—25 词）')
                continue
            if not u.get('pautas'):
                err(w, '缺要点 pautas')
            m = u.get('modelo', {})
            n = nwords(m.get('texto', []))
            lo, hi = sp['words']
            if not (lo <= n <= hi):
                err(w, f'范文 {n} 词，应在 {lo}—{hi}')
            if not m.get('comentario_zh'):
                err(w, '缺范文点评')
            st = u.get('estimulo', {})
            if sp.get('stim_words') and st.get('tipo') == 'texto' and not in_range(nwords(st.get('cuerpo', [])), sp['stim_words'], 0.1):
                err(w, f"刺激文本 {nwords(st.get('cuerpo', []))} 词，应为 {sp['stim_words'][0]}—{sp['stim_words'][1]}")
            if sp.get('audio_words'):
                a = st.get('audio', {})
                if st.get('tipo') != 'audio':
                    err(w, 'Tarea 1 的刺激材料要是录音 audio')
                else:
                    check_segs(w + '.audio', a.get('segs', []))
                    n = nwords([s.get('es', '') for s in a.get('segs', [])])
                    if not in_range(n, sp['audio_words'], 0.05):
                        err(w, f"录音 {n} 词，应为 {sp['audio_words'][0]}—{sp['audio_words'][1]}")
    for c in d.get('criterios', []):
        if not c.get('es') or not c.get('zh'):
            err('eie.criterios', '评分项要有 es、zh')


def check_eio(lv, d):
    spec = SPEC[lv]['eio']
    T = d.get('tareas', [])
    if len(T) != len(spec):
        err('eio', f'tarea 数 {len(T)}，应为 {len(spec)}')
    if d.get('duracion_min') != DUR[lv][3] or d.get('preparacion_min') != PREP[lv]:
        err('eio', f'duracion_min 应为 {DUR[lv][3]}、preparacion_min 应为 {PREP[lv]}')
    for t, sp in zip(T, spec):
        W = f"eio.T{t.get('n')}"
        op = t.get('opciones', [])
        if len(op) != sp['nopt']:
            err(W, f"opciones 要 {sp['nopt']} 个，实际 {len(op)}")
        for o in op:
            w = f"{W}.opción {o.get('id')}"
            if sp.get('art') and not str(o.get('art', '')).startswith('art:'):
                err(w, '要有照片 art:…')
            if sp.get('text_words') and not in_range(nwords(o.get('texto', [])), sp['text_words'], 0.03):
                err(w, f"文章 {nwords(o.get('texto', []))} 词，应为 {sp['text_words'][0]}—{sp['text_words'][1]}")
            if sp.get('propuestas') and len(o.get('propuestas', [])) != sp['propuestas']:
                err(w, f"propuestas 要 {sp['propuestas']} 个")
            if not o.get('modelo'):
                err(w, '缺参考回答 modelo')
        ex = t.get('examinador', {})
        if not ex.get('guion'):
            err(W, '缺考官说的话 examinador.guion')
    for t in T:
        for p, s in es_strings(t):
            check_es(f"eio.T{t.get('n')}{p}", s)


def load_arts(lv):
    arts = []
    for p in sorted((ROOT / 'content' / lv).glob('art_*.json')):
        try:
            arts += json.loads(p.read_text('utf-8'))
        except json.JSONDecodeError as e:
            err(p.name, f'JSON 读不了：{e}')
    return arts


def check_art(lv, docs):
    arts = load_arts(lv)
    ids = [a.get('id') for a in arts]
    for k, v in Counter(ids).items():
        if v > 1:
            err('art', f'id 重复 {k}')
    refs = set(re.findall(r'art:([A-Za-z0-9_]+)', json.dumps(docs, ensure_ascii=False)))
    for r in sorted(refs - set(ids)):
        err('art', f'引用了 art:{r}，插图清单 art_*.json 里没有')
    for a in arts:
        if a.get('id') not in refs:
            warn('art', f"{a.get('id')} 没有被引用")
        if not a.get('zh') or a.get('estilo') not in ('icono', 'escena'):
            err('art', f"{a.get('id')} 缺 zh 或 estilo")


def main():
    lv = sys.argv[1].upper()
    parts = sys.argv[2:] or ['cl', 'ca', 'eie', 'eio']
    docs = {}
    for part in ['cl', 'ca', 'eie', 'eio']:
        p = ROOT / 'content' / lv / f'{part}.json'
        if not p.exists():
            if part in parts:
                err(part, f'没有 {p.name}')
            continue
        try:
            docs[part] = json.loads(p.read_text('utf-8'))
        except json.JSONDecodeError as e:
            err(part, f'JSON 读不了：{e}')
    for part in parts:
        d = docs.get(part)
        if d is None:
            continue
        if d.get('nivel') != lv:
            err(part, 'nivel 不对')
        if part in ('cl', 'ca', 'eie') and d.get('duracion_min') != DUR[lv][('cl', 'ca', 'eie').index(part)]:
            err(part, f"duracion_min 应为 {DUR[lv][('cl', 'ca', 'eie').index(part)]}")
        if part in ('cl', 'ca'):
            check_cl_ca(lv, part, d)
        elif part == 'eie':
            check_eie(lv, d)
        else:
            check_eio(lv, d)
        for p_, s in es_strings({k: v for k, v in d.items() if k not in ('tareas',)}):
            check_es(part + p_, s)
    if set(parts) >= {'cl', 'ca', 'eie', 'eio'} or 'art' in parts:
        check_art(lv, docs)
    elif any(re.search('art:', json.dumps(docs.get(p, {}))) for p in parts):
        sub = {p: docs[p] for p in parts if p in docs}
        ids = {a.get('id') for a in load_arts(lv)}
        for r in sorted(set(re.findall(r'art:([A-Za-z0-9_]+)', json.dumps(sub, ensure_ascii=False))) - ids):
            err('art', f'引用了 art:{r}，插图清单 art_*.json 里没有')
    print('\n'.join(ERR + WARN))
    print(f'{lv} {" ".join(parts)}：{len(ERR)} 个错误，{len(WARN)} 个提醒')
    print('PASS' if not ERR else 'FAIL')
    sys.exit(1 if ERR else 0)


if __name__ == '__main__':
    main()
