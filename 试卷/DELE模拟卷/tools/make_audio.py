"""DELE 模拟卷录音：每一级听力每个 tarea 一条、整场连播一条；B2、C1 另有写作 Tarea 1 的录音。

    SIELE_KIT=… SIELE_ASR=… SIELE_ROOT=<本目录> python tools/make_audio.py <级别> [--draft] [--only DELE_A1_CA_T2 …] [--plan]

- 文字来自 content/<级别>/ca.json（和 eie.json 的录音）；播音员（男1）照读说明语、报编号、读例题答案和读题时间，流程照 考试规格.md
  （依据各级 Modelo 的录音稿：每段放两遍，两遍之间、放完之后的停顿秒数一样）。
- 每一片都用 Parakeet 识别核对，有出入换种子重合成（asrcheck.py，同 SIELE 模拟卷、B1—B2 听力练习）；
  成品 −16 LUFS、MP3 128k，查响度、峰值、电磁音；--plan 只打印每条音轨的流程和预计时长，不合成。
输出 out/<级别>/audio/：DELE_<级别>_CA_T1….mp3、DELE_<级别>_CA_completa.mp3、DELE_<级别>_EIE_T1.mp3；核对/report.json。
"""
import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
ap = argparse.ArgumentParser()
ap.add_argument('nivel')
ap.add_argument('--draft', action='store_true')
ap.add_argument('--plan', action='store_true')
ap.add_argument('--only', nargs='*')
A = ap.parse_args()
LV = A.nivel.upper()

if not A.plan:
    import asrcheck as X  # noqa: E402
    G, SR = X.G, X.SR
else:
    X = G = None
    SR = 24000

ROOT = HERE.parent
C = ROOT / 'content' / LV
OUT = ROOT / 'out' / LV / 'audio'
NAR = '男1'
SENT_GAP, TURN_GAP, LEAD, TAIL, LABEL_GAP, LINE_GAP = 0.35, 0.6, 1.0, 1.5, 0.8, 0.6
NUM = ['cero', 'uno', 'dos', 'tres', 'cuatro', 'cinco', 'seis', 'siete', 'ocho', 'nueve', 'diez', 'once', 'doce', 'trece', 'catorce',
       'quince', 'dieciséis', 'diecisiete', 'dieciocho', 'diecinueve', 'veinte', 'veintiuno', 'veintidós', 'veintitrés', 'veinticuatro',
       'veinticinco', 'veintiséis', 'veintisiete', 'veintiocho', 'veintinueve', 'treinta']
SECS = {10: 'diez segundos', 20: 'veinte segundos', 25: 'veinticinco segundos', 30: 'treinta segundos', 45: 'cuarenta y cinco segundos', 60: 'un minuto'}
TEMPO = {'A1': 0.9, 'A2': 0.95}.get(LV, 1.0)           # 只放慢录音材料；播音员按原速
# 读题时间（秒），照各级 Modelo
READ = {'A1': {4: 30}, 'A2': {3: 30, 4: 45}, 'B1': {1: 30, 2: 30, 3: 30, 4: 20, 5: 25}, 'B2': {1: 30, 2: 20, 3: 30, 4: 30, 5: 30},
        'C1': {1: 60, 3: 60}}


def chunks(es):
    """句子切分；少于 4 个词的短句并进后一句（最后一句就并进前一句）。"""
    ss = [p for p in re.split(r'(?<=[.!?…])\s+', es.strip()) if p]
    out, carry = [], ''
    for s in ss:
        s = (carry + ' ' + s).strip() if carry else s
        if len(re.findall(r'\w+', s)) < 4:
            carry = s
            continue
        out.append(s)
        carry = ''
    if carry:
        if out:
            out[-1] = out[-1] + ' ' + carry
        else:
            out.append(carry)
    return out


def say(t):
    return ('say', NAR, t)


def sil(s):
    return ('sil', s)


def lines(a, presentacion=True, pregunta=False):
    """一段录音：情景介绍（播音员）＋对话＋问题（播音员）。"""
    ev = []
    if presentacion and a.get('presentacion'):
        ev += [say(a['presentacion']), sil(LINE_GAP)]
    ev.append(('lines', [(s['v'], s['es']) for s in a['segs']]))
    if pregunta and a.get('pregunta_oral'):
        ev += [sil(1.0), say(a['pregunta_oral'])]
    return ev


def rot(a):
    """“Conversación 1” → “Conversación número uno.”（只读“Mensaje seis.”这样两个词，合成时常读错，加上 número）"""
    r = a.get('rotulo', '').strip()
    return re.sub(r'\b(\d+)\b', lambda m: 'número ' + NUM[int(m.group(1))], r).rstrip('.') + '.' if r else ''


def letra(k):
    return f'La opción correcta es la letra {k}.'


def ex_key(t, a):
    if t['tipo'] == 'seleccion':
        q = next(q for q in t['preguntas'] if q['n'] == 0)
        return q['clave']
    return a['clave']


def tarea_events(t, last, ntareas):
    n, tipo = t['n'], t['tipo']
    au = t.get('audios', [])
    ex = next((a for a in au if a.get('id') == '0'), None)
    items = [a for a in au if a.get('id') != '0']
    ev = [say(f'Tarea {NUM[n]}.'), sil(LINE_GAP), say(t['instruccion_es']), sil(2)]
    rd = READ[LV].get(n)
    if LV == 'A1':
        if tipo in ('imagenes', 'relacionar_imagenes', 'frases'):
            if tipo == 'frases':
                a0 = au[0]
                segs = a0['segs']
                order = sorted(t['inicios'], key=lambda i: i['n'])
                exs = order[0]
                one = lambda k: [('lines', [(segs[k]['v'], segs[k]['es'])])]
                ev += [say('Ahora va a escuchar un ejemplo.'), sil(2)] + one(exs['seg']) + [sil(5), say(letra(exs['clave'])), sil(2),
                                                                                           say(f'Empieza la tarea {NUM[n]}.'), sil(5)]
                for i in order[1:]:
                    ev += one(i['seg']) + [sil(10)] + one(i['seg']) + [sil(2), say('Ahora seleccione la opción correcta.'), sil(5)]
            else:
                pq = tipo == 'imagenes'
                ev += [say('Ahora va a escuchar un ejemplo.'), sil(2)] + lines(ex, pregunta=pq) + [sil(2 if pq else 5), say(letra(ex['clave'])), sil(2),
                                                                                                  say(f'Empieza la tarea {NUM[n]}.'), sil(5)]
                for a in items:
                    ev += ([say(rot(a)), sil(LABEL_GAP)] if rot(a) else []) + lines(a, pregunta=pq) + [sil(10)] + lines(a, pregunta=pq) + \
                          [sil(2), say('Ahora seleccione la imagen correcta.' if pq else 'Ahora seleccione la opción correcta.'), sil(5)]
            ev.append(sil(40))
        else:                                                    # completar
            ev += [say('Ahora tiene treinta segundos para leer las frases.'), sil(30), say(f'Empieza la tarea {NUM[n]}.'), sil(2)]
            ev += lines(au[0]) + [sil(10)] + lines(au[0]) + [sil(45)]
    elif LV == 'A2':
        if tipo == 'imagenes':
            ev += [say('A continuación va a escuchar un ejemplo.'), sil(LINE_GAP), say(rot(ex)), sil(2)] + lines(ex, pregunta=True) + \
                  [sil(2), say(letra(ex['clave'])), sil(LINE_GAP), say('Ahora va a escuchar las conversaciones.'), sil(5)]
            for a in items:
                ev += [say(rot(a)), sil(LABEL_GAP)] + lines(a) + [sil(5)] + lines(a) + [sil(3), say(a['pregunta_oral']), sil(10)]
            ev.append(sil(30))
        elif tipo == 'seleccion':
            ev += [say('A continuación va a escuchar un ejemplo.'), sil(LINE_GAP), say(rot(ex)), sil(LABEL_GAP)] + lines(ex) + \
                  [sil(2), say(letra(ex_key(t, ex))), sil(5)]
            for a in items:
                ev += [say(rot(a)), sil(LINE_GAP), say(f"Ahora tiene diez segundos para leer la pregunta {NUM[int(a['id'])]}."), sil(10)] + \
                      lines(a) + [sil(15)] + lines(a) + [sil(3), say('Ahora seleccione la opción correcta.'), sil(5)]
            ev.append(sil(30))
        elif tipo == 'quien':
            ev += [say('Ahora tiene treinta segundos para leer los enunciados.'), sil(30)] + lines(au[0]) + [sil(5)] + lines(au[0]) + \
                  [sil(3), say('Ahora seleccione las opciones correctas.'), sil(30)]
        else:                                                    # relacionar
            ev += [say('A continuación va a escuchar un ejemplo.'), sil(LINE_GAP), say(rot(ex)), sil(LABEL_GAP)] + lines(ex) + \
                  [sil(5), say(letra(ex['clave'])), sil(LINE_GAP), say('Ahora tiene cuarenta y cinco segundos para leer los enunciados.'), sil(45)]
            for a in items:
                ev += [say(rot(a)), sil(LABEL_GAP)] + lines(a) + [sil(15)] + lines(a) + [sil(3), say('Ahora seleccione la opción correcta.'), sil(10)]
            ev += [say('Complete ahora la Hoja de respuestas.'), sil(45)]
    elif LV in ('B1', 'B2'):
        if tipo == 'relacionar':
            ev += [say('Ahora escuche el ejemplo.'), sil(LINE_GAP), say(rot(ex)), sil(LABEL_GAP)] + lines(ex) + \
                  [sil(2), say(letra(ex['clave'])), sil(LINE_GAP), say(f'Ahora tiene {SECS[rd]} para leer los enunciados.'), sil(rd)]
            for a in items:
                ev += [say(rot(a)), sil(LABEL_GAP)] + lines(a) + [sil(5)] + lines(a) + [sil(10)]
        else:
            what = 'los enunciados' if tipo == 'quien' else 'las preguntas'
            ev += [say(f'Tiene {SECS[rd]} para leer {what}.'), sil(rd)]
            if len(items) > 1:
                for a in items:
                    ev += [say(rot(a)), sil(LABEL_GAP)] + lines(a) + [sil(5)] + lines(a) + [sil(10)]
            else:
                ev += lines(items[0]) + [sil(10)] + lines(items[0]) + [sil(10)]
        ev += [say('Complete ahora la Hoja de respuestas.'), sil(30)]
    else:                                                        # C1
        if tipo in ('seleccion_multiple',) or (tipo == 'seleccion' and len(items) == 1):
            what = 'las opciones' if tipo == 'seleccion_multiple' else 'las preguntas'
            ev += [say(f'Ahora dispone de un minuto para leer {what}.'), sil(60)] + lines(items[0]) + [sil(10)] + \
                  lines(items[0], presentacion=False) + [sil(30)]
        elif len(items) == 4:
            ev.append(sil(3))
            for a in items:
                ev += [say(rot(a)), sil(LABEL_GAP)] + lines(a) + [sil(20)] + lines(a) + [sil(10)]
        else:
            ev.append(sil(3))
            for a in items:
                ev += [say(rot(a)), sil(LABEL_GAP)] + lines(a) + [sil(3)] + lines(a) + [sil(15)]
    ev.append(say('Fin de la prueba de comprensión auditiva.' if last else f'Fin de la tarea {NUM[n]}.'))
    return ev


def ca_tracks():
    ca = json.loads((C / 'ca.json').read_text('utf-8'))
    T = ca['tareas']
    tr = []
    for k, t in enumerate(T):
        ev = ([say('Prueba de Comprensión auditiva.'), sil(LINE_GAP), say(ca['intro_es']), sil(2)] if k == 0 else []) + \
             tarea_events(t, k == len(T) - 1, len(T))
        tr.append({'id': f"DELE_{LV}_CA_T{t['n']}", 'tempo': TEMPO, 'nar_tempo': 1.0, 'events': ev})
    return tr


def eie_tracks():
    p = C / 'eie.json'
    if LV not in ('B2', 'C1') or not p.exists():
        return []
    t1 = json.loads(p.read_text('utf-8'))['tareas'][0]
    a = t1['estimulo']['audio']
    prueba = 'Prueba de Expresión e interacción escritas.' if LV == 'B2' else 'Prueba de Expresión, mediación e interacción escritas.'
    ev = [say(prueba), sil(LINE_GAP), say('Tarea uno.'), sil(LINE_GAP),
          say('Usted va a escuchar una audición dos veces. Durante la audición puede tomar notas.'), sil(10)]
    ev += lines(a) + [sil(15 if LV == 'C1' else 10)] + lines(a, presentacion=False) + [sil(3), say('Fin de la audición. Ahora puede empezar a escribir.')]
    return [{'id': f'DELE_{LV}_EIE_T1', 'tempo': 1.0, 'nar_tempo': 1.0, 'events': ev}]


def units(track):
    u = []
    for e in track['events']:
        if e[0] == 'say':
            u.append((e[1], e[2]))
        elif e[0] == 'lines':
            u += [(v, s) for v, es in e[1] for s in chunks(es)]
    return list(dict.fromkeys(u))


def plan(track):
    """预计时长：每个词 0.38 秒（放慢的除以语速），加停顿。"""
    t = LEAD + TAIL
    for e in track['events']:
        if e[0] == 'sil':
            t += e[1]
        elif e[0] == 'say':
            t += 0.36 * len(re.findall(r'\w+', e[2]))
        elif e[0] == 'lines':
            prev = None
            for v, es in e[1]:
                if prev is not None:
                    t += TURN_GAP if v != prev else SENT_GAP
                cs = chunks(es)
                t += sum(0.38 / track['tempo'] * len(re.findall(r'\w+', c)) for c in cs) + SENT_GAP * (len(cs) - 1)
                prev = v
    return t


# ---------------------------------------------------------------- 拼接、母带、核查（同 SIELE 模拟卷 make_audio.py）
def tone(freq, dur, amp=0.12):
    tt = np.arange(int(dur * SR)) / SR
    a = (amp * np.sin(2 * np.pi * freq * tt)).astype(np.float32)
    f = int(0.02 * SR)
    a[:f] *= np.linspace(0, 1, f, dtype=np.float32)
    a[-f:] *= np.linspace(1, 0, f, dtype=np.float32)
    return a


def assemble(track, got, tempo):
    out, items, speech, t = [], [], [], 0.0

    def add(seg, text=None):
        nonlocal t
        if text is not None:
            items.append({'k': len(items) + 1, 'start': round(t, 3), 'end': round(t + len(seg) / SR, 3), 'text': text})
            speech.append(('say', t, t + len(seg) / SR))
        elif len(seg) > 1.2 * SR:
            speech.append(('gap', t, t + len(seg) / SR))
        else:
            speech.append(('pause', t, t + len(seg) / SR))
        out.append(seg)
        t += len(seg) / SR

    add(X.silence(LEAD))
    for e in track['events']:
        if e[0] == 'say':
            add(X.piece(got[(e[1], e[2])], track.get('nar_tempo', tempo)), e[2])
        elif e[0] == 'sil':
            add(X.silence(e[1]))
        else:
            prev = None
            for v, es in e[1]:
                if prev is not None:
                    add(X.silence(TURN_GAP if v != prev else SENT_GAP))
                for j, s in enumerate(chunks(es)):
                    if j:
                        add(X.silence(SENT_GAP))
                    add(X.piece(got[(v, s)], tempo), s)
                prev = v
    add(X.silence(TAIL))
    return G.master(np.concatenate(out), -16.0), items, speech


def speech_of(a48, spans):
    """从成品（48 kHz，母带处理之后）里切出朗读部分量短时响度；一整段作答停顿只算一个 0.6 秒（同 SIELE 模拟卷）。"""
    R = G.OUT_SR
    say_ = [i for i, x in enumerate(spans) if x[0] == 'say']
    spans = spans[say_[0]:say_[-1] + 1]
    parts, run = [], []
    for k, a, b in spans:
        if k != 'say':
            run.append((k, a, b))
            continue
        if any(x[0] == 'gap' for x in run):
            parts.append(np.zeros(int(round(0.6 * R)), np.float32))
        else:
            parts += [a48[int(round(x * R)):int(round(y * R))] for _, x, y in run]
        run = []
        parts.append(a48[int(round(a * R)):int(round(b * R))])
    return np.concatenate(parts)


def build(track, got):
    b = track['tempo']
    ladder = (b, round(b - 0.01, 2), round(b + 0.01, 2), round(b - 0.02, 2), round(b + 0.02, 2))
    for tempo in ladder:
        a48, items, sp = assemble(track, got, tempo)
        mp3 = G.encode_mp3(a48, kbps=128)
        lrep, errs = X.verify(mp3, items, speech_of(a48, sp))
        if not errs:
            return a48, mp3, items, lrep, errs, tempo, None
    tempo, fix = ladder[0], None
    for fix in X.fallbacks(errs, lrep):
        X.MA.chain(dict(X.MALE, **{k: v for k, v in fix.items() if k not in ('post_notch', 'relevel')}))
        base48, items, sp = assemble(track, got, tempo)
        for _ in range(8):
            a48 = X.MA.buzz.debuzz(base48, G.OUT_SR, fix['post_notch']) if fix.get('post_notch') else base48
            if fix.get('gain_db'):
                a48 = G.limit((a48 * 10 ** (fix['gain_db'] / 20)).astype(np.float32), G.OUT_SR, -1.5)
            mp3 = G.encode_mp3(a48, kbps=128)
            lrep, errs = X.verify(mp3, items, speech_of(a48, sp))
            print(f"  补救 {fix}：{'；'.join(errs) if errs else '通过'}", flush=True)
            m = re.search(r'电磁音：(\d+) Hz', '；'.join(errs))
            if m and len(fix.get('post_notch', [])) < 8:
                fix = dict(fix, post_notch=fix.get('post_notch', []) + [int(m.group(1))])
            elif any('整体响度' in e for e in errs) and fix.get('relevel'):
                fix = dict(fix, gain_db=round(fix.get('gain_db', 0.0) - 16.0 - lrep['integrated_lufs'], 2))
            else:
                break
        if not errs:
            break
    X.MA.chain(X.MALE)
    return a48, mp3, items, lrep, errs, tempo, fix


def main():
    ca = ca_tracks()
    tracks = ca + eie_tracks()
    if A.plan:
        tot = 0
        for t in tracks:
            d = plan(t)
            if '_CA_' in t['id']:
                tot += d + 3
            print(f"{t['id']}: 预计 {d / 60:.1f} 分钟，{len(units(t))} 个片段")
        print(f'听力合计约 {tot / 60:.1f} 分钟')
        return
    if A.only:
        tracks = [t for t in tracks if t['id'] in A.only]
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / '核对').mkdir(exist_ok=True)
    rep_path = OUT / '核对' / 'report.json'
    report = json.loads(rep_path.read_text('utf-8')) if rep_path.exists() else {}
    rec = X.Recognizer()
    req = {u for t in tracks for u in units(t)}
    print(f'{LV}：{len(tracks)} 段录音，{len(req)} 个合成片段', flush=True)
    got = X.synth(req, rec, lambda m: print(m, flush=True))
    fails, full = [], {}
    for t in tracks:
        a48, mp3, items, lrep, errs, tempo, fix = build(t, got)
        pieces = [got[u][2] for u in units(t)]
        bad = [x for x in pieces if x['errors']]
        ok = not errs and not bad
        if ok or A.draft:
            (OUT / f"{t['id']}.mp3").write_bytes(mp3)
        dur = len(a48) / G.OUT_SR
        report[t['id']] = {'tempo': tempo, 'duration': round(dur, 1), 'loudness': lrep, 'fallback': fix if fix and not errs else None,
                           'check_errors': errs, 'asr_errors': len(bad), 'items': items, 'pieces': pieces}
        print(f"{'✓' if ok else '✗'} {t['id']} {dur:.1f} 秒（{int(dur // 60)} 分 {dur % 60:.0f} 秒） 语速 {tempo}；"
              f"{lrep['integrated_lufs']} LUFS，朗读部分短时波动 {lrep['short_term_std_speech_lu']} LU，"
              f"电磁音 {lrep['buzz_hz']:.0f} Hz {lrep['buzz_db']:+.1f} dB"
              + (f"；核查：{'；'.join(errs)}" if errs else '')
              + (f"；识别有出入 {len(bad)} 片：" + '；'.join(f"{x['text']}→{x['asr']} {x['diff']}" for x in bad) if bad else ''), flush=True)
        if not ok:
            fails.append(t['id'])
        if '_CA_' in t['id']:
            full[t['id']] = (a48, items)
    rep_path.write_text(json.dumps(report, ensure_ascii=False, indent=1), 'utf-8')
    # 整场连播：所有 tarea 都在、都通过（本次没重做的从已有 MP3 读回）才拼
    ids = [t['id'] for t in ca]
    if not any(f in ids for f in fails) and all(i in full or (OUT / f'{i}.mp3').exists() for i in ids):
        import soundfile as sf
        gap = np.zeros(int(3 * G.OUT_SR), np.float32)
        parts, its, t0 = [], [], 0.0
        for i in ids:
            if i in full:
                a48, items = full[i]
            else:
                a, sr = sf.read(str(OUT / f'{i}.mp3'), dtype='float32')
                a48, items = (a if a.ndim == 1 else a.mean(1)), report[i]['items']
            if parts:
                parts.append(gap)
                t0 += 3.0
            its += [dict(it, start=round(it['start'] + t0, 3), end=round(it['end'] + t0, 3)) for it in items]
            parts.append(a48)
            t0 += len(a48) / G.OUT_SR
        a = np.concatenate(parts)
        mp3 = G.encode_mp3(a, kbps=128)
        lrep, errs = X.MA.verify(mp3, its, -16.0)
        errs = [e for e in errs if '句间' not in e and '短时' not in e]
        (OUT / f'DELE_{LV}_CA_completa.mp3').write_bytes(mp3)
        report[f'DELE_{LV}_CA_completa'] = {'duration': round(len(a) / G.OUT_SR, 1), 'loudness': lrep, 'check_errors': errs, 'parts': ids}
        print(f"{'✓' if not errs else '✗'} DELE_{LV}_CA_completa {len(a) / G.OUT_SR / 60:.1f} 分钟；{lrep['integrated_lufs']} LUFS" + (f"；{errs}" if errs else ''), flush=True)
        rep_path.write_text(json.dumps(report, ensure_ascii=False, indent=1), 'utf-8')
    print('全部通过' if not fails else f'未通过：{"、".join(fails)}')
    sys.exit(1 if fails and not A.draft else 0)


if __name__ == '__main__':
    main()
