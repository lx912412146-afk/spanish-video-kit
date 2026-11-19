"""SIELE 模拟卷录音：听力 6 段（每个 tarea 一段，另拼一段完整版）、口语 6 段（Tarea 4 两个话题各一段）。

    SIELE_KIT=… SIELE_ASR=… SIELE_ROOT=… python tools/make_audio.py <输出目录> [ca] [eio] [--draft] [--only SIELE3_CA_T2 …]

- 文字来自 content/ca.json、content/eio.json；播音员（男1）只报 tarea、题号和时间，不读题目。
- 时间按考试规格.md：读题 30/30/30/45/45/50 秒；T1、T4、T5、T6 两遍之间 10 秒；T2、T3 每段连放两遍、中间 5 秒、放完 10 秒作答；
  T5 片段之间 5 秒；每个 tarea 最后 30 秒检查。口语：提示音（一声＝开始说，两声＝时间到）之间是作答时间。
- 对话里同一人连续两句停 0.35 秒，换人停 0.6 秒；少于 3 个词的短句（¡Vale!、¡Qué suerte!）和后一句合成一片，免得识别和语气出问题。
- 每一片都用 Parakeet 识别核对，有出入换种子重合成（asrcheck.py，同 B1—B2 听力练习）；成品 −16 LUFS、MP3 128k，查响度、峰值、电磁音。
输出：SIELE3_CA_T1…T6.mp3、SIELE3_CA_completa.mp3、SIELE3_EIO_T1/T2/T3/T4_tema1/T4_tema2/T5.mp3；核对/report.json（每段时长、每片识别结果）。
"""
import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import asrcheck as X  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument('out')
ap.add_argument('parts', nargs='*', default=['ca', 'eio'])
ap.add_argument('--draft', action='store_true')
ap.add_argument('--only', nargs='*')
A = ap.parse_args()
OUT = Path(A.out).resolve()
C = X.ROOT / 'content'
G, SR = X.G, X.SR
NAR = '男1'
SENT_GAP, TURN_GAP, LEAD, TAIL, LABEL_GAP, LINE_GAP = 0.35, 0.6, 1.0, 1.5, 0.8, 0.6
NUM = ['cero', 'uno', 'dos', 'tres', 'cuatro', 'cinco', 'seis', 'siete', 'ocho', 'nueve', 'diez']
EIO_LABEL_GAP = TURN_GAP   # 口语：播音员报完题号换考官说话，和对话里换人一样停 0.6 秒
SECS = {30: 'treinta segundos', 35: 'treinta y cinco segundos', 45: 'cuarenta y cinco segundos', 50: 'cincuenta segundos', 60: 'un minuto'}


def chunks(es):
    """句子切分；少于 3 个词的短句并进后一句（最后一句就并进前一句）。"""
    ss = X.sentences(es)
    out, carry = [], ''
    for s in ss:
        s = (carry + ' ' + s).strip() if carry else s
        if len(re.findall(r'\w+', s)) < 3:
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


# ---------------------------------------------------------------- 每段录音的“剧本”：[('say', 声音, 文字) | ('lines', [(声音, 文字)]) | ('sil', 秒) | ('beep', 声数)]
def ca_tracks():
    ca = json.loads((C / 'ca.json').read_text('utf-8'))
    tr = []
    for t in ca['tareas']:
        n = t['n']
        ev = [('say', NAR, ('Comprensión auditiva. ' if n == 1 else '') + f'Tarea {NUM[n]}.'), ('sil', LINE_GAP),
              ('say', NAR, f"Tiene {SECS[t['lectura_s']]} para leer las preguntas."), ('sil', t['lectura_s'])]
        segs = lambda a: [(s['v'], s['es']) for s in a['segs']]
        if n in (2, 3):
            for a in t['audio']:
                ev += [('say', NAR, a['label'] + '.'), ('sil', LABEL_GAP), ('lines', segs(a)), ('sil', t['entre_s']), ('lines', segs(a)), ('sil', t['respuesta_s'])]
        elif n == 5:
            def once():
                e = []
                for k, a in enumerate(t['audio']):
                    if k:
                        e.append(('sil', t['entre_fragmentos_s']))
                    e += [('say', NAR, a['label'] + '.'), ('sil', LABEL_GAP), ('lines', segs(a))]
                return e
            ev += once() + [('sil', t['entre_s'])] + once()
        else:
            a = t['audio'][0]
            ev += [('lines', segs(a)), ('sil', t['entre_s']), ('lines', segs(a))]
        ev += [('sil', 30), ('say', NAR, 'Fin de la prueba de comprensión auditiva.' if n == 6 else f'Fin de la tarea {NUM[n]}.')]
        # 放慢只用在录音材料上；播音员的提示按原速（逐片识别核对的就是原速），Tarea 1 放慢到 0.9 时 Tiene treinta 会被认成 Tien 30
        tr.append({'id': f'SIELE3_CA_T{n}', 'tempo': {1: 0.9, 2: 0.95, 3: 0.98}.get(n, 1.0), 'nar_tempo': 1.0, 'events': ev})
    return tr


def eio_tracks():
    eio = json.loads((C / 'eio.json').read_text('utf-8'))
    t1, _, _, t4, _ = eio['tareas']
    beep_talk = lambda sec: [('beep', 1), ('sil', sec), ('beep', 2)]
    tr = []
    ev = [('say', NAR, 'Expresión e interacción orales.'), ('sil', LINE_GAP), ('say', NAR, 'Tarea uno.'), ('sil', 15)]
    for k, q in enumerate(t1['preguntas']):
        if k:
            ev.append(('sil', 5))
        ev += [('say', NAR, f"Pregunta {NUM[q['n']]}."), ('sil', EIO_LABEL_GAP), ('lines', [(t1['voz'], q['es'])]), ('sil', 2.0),
               ('lines', [(t1['voz'], q['es'])]), ('sil', 1.0)] + beep_talk(q['segundos'])
    ev += [('sil', 1.5), ('say', NAR, 'Fin de la tarea uno.')]
    tr.append({'id': 'SIELE3_EIO_T1', 'tempo': 0.95, 'events': ev})
    ev = [('say', NAR, 'Tarea dos.'), ('sil', LINE_GAP), ('say', NAR, 'Ahora elija una de las dos imágenes. Tiene treinta segundos.'), ('sil', 30),
          ('say', NAR, 'Ahora tiene dos minutos para preparar su descripción.'), ('sil', 120),
          ('say', NAR, 'Puede empezar a hablar. Tiene entre uno y dos minutos.'), ('sil', 1.0)] + beep_talk(120) + \
         [('sil', 1.5), ('say', NAR, 'Fin de la tarea dos.')]
    tr.append({'id': 'SIELE3_EIO_T2', 'tempo': 1.0, 'events': ev})
    ev = [('say', NAR, 'Tarea tres.'), ('sil', LINE_GAP)]
    for k, p in enumerate(('primera', 'segunda')):
        if k:
            ev.append(('sil', 1.5))
        ev += [('say', NAR, f'Parte {p}. Ahora elija una de las dos situaciones. Tiene un minuto.'), ('sil', 60),
               ('say', NAR, 'Deje su mensaje ahora. Tiene un minuto y treinta segundos.'), ('sil', 1.0)] + beep_talk(90)
    ev += [('sil', 1.5), ('say', NAR, 'Fin de la tarea tres.')]
    tr.append({'id': 'SIELE3_EIO_T3', 'tempo': 1.0, 'events': ev})
    for tema in t4['temas']:
        ev = [('say', NAR, 'Tarea cuatro.'), ('sil', LINE_GAP), ('say', NAR, f"Tema {NUM[tema['n']]}: {tema['titulo'][0].lower() + tema['titulo'][1:]}."),
              ('sil', LINE_GAP), ('say', NAR, f"Lea el texto. Tiene {SECS[t4['lectura_s']]}."), ('sil', t4['lectura_s'])]
        for k, q in enumerate(tema['preguntas']):
            if k:
                ev.append(('sil', 5))
            ev += [('say', NAR, f'Pregunta {NUM[k + 1]}.'), ('sil', EIO_LABEL_GAP), ('lines', [(t4['voz'], q['es'])]), ('sil', 2.0),
                   ('lines', [(t4['voz'], q['es'])]), ('sil', 1.0)] + beep_talk(60)
        ev += [('sil', 1.5), ('say', NAR, 'Fin de la tarea cuatro.')]
        tr.append({'id': f"SIELE3_EIO_T4_tema{tema['n']}", 'tempo': 1.0, 'events': ev})
    ev = [('say', NAR, 'Tarea cinco.'), ('sil', LINE_GAP), ('say', NAR, 'Ahora elija una de las dos afirmaciones.'), ('sil', LINE_GAP), ('say', NAR, 'Tiene cuarenta y cinco segundos para elegir.'), ('sil', 45),
          ('say', NAR, 'Ahora tiene dos minutos para preparar su intervención.'), ('sil', 120),
          ('say', NAR, 'Puede empezar a hablar. Tiene entre tres y cuatro minutos.'), ('sil', 1.0)] + beep_talk(240) + \
         [('sil', 1.5), ('say', NAR, 'Fin de la prueba de expresión e interacción orales.')]
    tr.append({'id': 'SIELE3_EIO_T5', 'tempo': 1.0, 'events': ev})
    return tr


def units(track):
    u = []
    for e in track['events']:
        if e[0] == 'say':
            u.append((e[1], e[2]))
        elif e[0] == 'lines':
            u += [(v, s) for v, es in e[1] for s in chunks(es)]
    return list(dict.fromkeys(u))


# ---------------------------------------------------------------- 提示音、拼接
def tone(freq, dur, amp=0.12):
    t = np.arange(int(dur * SR)) / SR
    a = (amp * np.sin(2 * np.pi * freq * t)).astype(np.float32)
    f = int(0.02 * SR)
    a[:f] *= np.linspace(0, 1, f, dtype=np.float32)
    a[-f:] *= np.linspace(1, 0, f, dtype=np.float32)
    return a


BEEP = {1: tone(1000, 0.35), 2: np.concatenate([tone(700, 0.22), X.silence(0.12), tone(700, 0.22)])}


def assemble(track, got, tempo):
    out, items, speech, t = [], [], [], 0.0

    def add(seg, text=None, beep=False):
        nonlocal t
        if text is not None:
            items.append({'k': len(items) + 1, 'start': round(t, 3), 'end': round(t + len(seg) / SR, 3), 'text': text})
            speech.append(('say', t, t + len(seg) / SR))
        elif beep or len(seg) > 1.2 * SR:
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
        elif e[0] == 'beep':
            add(BEEP[e[1]], beep=True)
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
    """从成品（48 kHz，母带处理之后）里切出朗读部分，作答停顿和提示音换成 0.6 秒静音：量短时响度用，量的就是听到的声音。
    （原来直接拼 24 kHz 的未处理片段、再按 48 kHz 编码，等于加倍速、升八度、没经过压缩去量，B1—B2 听力练习沿用的也是这个写法。）
    一整段作答停顿（前后的短停顿、提示音、作答时间连在一起）只算一个 0.6 秒：原来每一小段各换成 0.6 秒，口语每题之间剩下 3 秒多静音。"""
    R = G.OUT_SR
    say = [i for i, x in enumerate(spans) if x[0] == 'say']
    spans = spans[say[0]:say[-1] + 1]                 # 同工具包 loudness.py：只量第一句开始到最后一句结束
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
    tracks = (ca_tracks() if 'ca' in A.parts else []) + (eio_tracks() if 'eio' in A.parts else [])
    if A.only:
        tracks = [t for t in tracks if t['id'] in A.only]
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / '核对').mkdir(exist_ok=True)
    rep_path = OUT / '核对' / 'report.json'
    report = json.loads(rep_path.read_text('utf-8')) if rep_path.exists() else {}
    rec = X.Recognizer()
    req = {u for t in tracks for u in units(t)}
    print(f'{len(tracks)} 段录音，{len(req)} 个合成片段', flush=True)
    got = X.synth(req, rec, lambda m: print(m, flush=True))
    fails, full = [], []
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
        if t['id'].startswith('SIELE3_CA_'):
            full.append((a48, items))
    if len(full) == 6 and not any(f.startswith('SIELE3_CA_') for f in fails):
        gap = np.zeros(int(3 * G.OUT_SR), np.float32)
        parts, its, t0 = [], [], 0.0
        for a48, items in full:
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
        (OUT / 'SIELE3_CA_completa.mp3').write_bytes(mp3)
        report['SIELE3_CA_completa'] = {'duration': round(len(a) / G.OUT_SR, 1), 'loudness': lrep, 'check_errors': errs}
        print(f"{'✓' if not errs else '✗'} SIELE3_CA_completa {len(a) / G.OUT_SR / 60:.1f} 分钟；{lrep['integrated_lufs']} LUFS" + (f"；{errs}" if errs else ''), flush=True)
    rep_path.write_text(json.dumps(report, ensure_ascii=False, indent=1), 'utf-8')
    print('全部通过' if not fails else f'未通过：{"、".join(fails)}')
    sys.exit(1 if fails and not A.draft else 0)


if __name__ == '__main__':
    main()
