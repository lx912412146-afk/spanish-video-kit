"""全书生词一致性检查：python vocab_audit.py [输出文件]

对每个单元，把录音稿台词和学生用书例句框（西语部分）里的词，和“A1 全书、本单元及以前各单元生词表”比对，
列出找不到的词：可能是没列进生词表，或者用在了正式教之前（后面单元才列）。
变位、阴阳性、单复数用粗略的规则还原（不是完整的词形还原），所以结果需要人工判断。
"""
import json
import re
import sys
import unicodedata
from pathlib import Path

B = Path(__file__).resolve().parent.parent
UNITS = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10']
A1 = B.parent / 'A1教程'                  # A1 教程在 A2 旁边（仓库里就是这样放的）
A1_UNITS = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']

# 虚词、人名地名、数字词等不查的词（课文里大量出现，生词表里不一定逐个列）
STOP = set('''a al ante con de del desde en entre hacia hasta para por sin sobre según tras y e o u ni pero que si
el la los las lo un una unos unas yo tú usted él ella nosotros nosotras vosotros vosotras ellos ellas ustedes
me te se nos os le les mi mis tu tus su sus nuestro nuestra nuestros nuestras vuestro vuestra
no sí ya muy más menos también tampoco bien mal aquí allí ahí hoy
cero uno dos tres cuatro cinco seis siete ocho nueve diez'''.split())
IRREG = {
    'ser': 'soy eres es somos sois son sea seas',
    'estar': 'estoy estás está estamos estáis están',
    'tener': 'tengo tienes tiene tenemos tenéis tienen',
    'ir': 'voy vas va vamos vais van',
    'haber': 'hay he has ha hemos habéis han',
    'hacer': 'hago haces hace hacemos hacéis hacen hecho',
    'salir': 'salgo',
    'poner': 'pongo pones pone ponemos ponéis ponen puesto',
    'venir': 'vengo vienes viene venimos venís vienen',
    'decir': 'digo dices dice decimos decís dicen dicho',
    'saber': 'sé sabes sabe sabemos sabéis saben',
    'ver': 'veo ves ve vemos veis ven visto',
    'dar': 'doy das da damos dais dan',
    'conocer': 'conozco',
    'escribir': 'escrito', 'abrir': 'abierto', 'volver': 'vuelto', 'romper': 'roto',
}
FORM2LEMMA = {f: l for l, fs in IRREG.items() for f in fs.split()}
ENDINGS = ['amos', 'áis', 'an', 'as', 'a', 'o', 'emos', 'éis', 'en', 'es', 'e', 'imos', 'ís', 'ando', 'iendo', 'ado', 'ada',
           'ados', 'adas', 'ido', 'ida', 'idos', 'idas', 'ar', 'er', 'ir',
           # A2：简单过去时、过去未完成时、命令式（vosotros）
           'é', 'aste', 'ó', 'asteis', 'aron', 'í', 'iste', 'ió', 'isteis', 'ieron',
           'aba', 'abas', 'ábamos', 'abais', 'aban', 'ía', 'ías', 'íamos', 'íais', 'ían', 'ad', 'ed', 'id']
# A2 的不规则形式：词首（词根）→ 原形
A2_STEMS = [('fu', ('ir', 'ser')), ('estuv', ('estar',)), ('tuv', ('tener',)), ('hic', ('hacer',)), ('hiz', ('hacer',)),
            ('pud', ('poder',)), ('pus', ('poner',)), ('quis', ('querer',)), ('vin', ('venir',)), ('dij', ('decir',)),
            ('sup', ('saber',)), ('traj', ('traer',)), ('anduv', ('andar',)),
            ('tendr', ('tener',)), ('pondr', ('poner',)), ('saldr', ('salir',)), ('vendr', ('venir',)), ('podr', ('poder',)),
            ('sabr', ('saber',)), ('habr', ('haber',)), ('querr', ('querer',)), ('har', ('hacer',)), ('dir', ('decir',))]
A2_FORMS = {'di': 'dar decir', 'diste': 'dar', 'dio': 'dar', 'dimos': 'dar', 'disteis': 'dar', 'dieron': 'dar',
            'vi': 'ver', 'viste': 'ver vestir', 'vio': 'ver', 'vimos': 'ver', 'visteis': 'ver', 'vieron': 'ver',
            'era': 'ser', 'eras': 'ser', 'éramos': 'ser', 'erais': 'ser', 'eran': 'ser',
            'iba': 'ir', 'ibas': 'ir', 'íbamos': 'ir', 'ibais': 'ir', 'iban': 'ir',
            'veía': 'ver', 'veías': 'ver', 'veíamos': 'ver', 'veíais': 'ver', 'veían': 'ver',
            'hecho': 'hacer', 'dicho': 'decir', 'visto': 'ver', 'puesto': 'poner', 'escrito': 'escribir', 'vuelto': 'volver',
            'abierto': 'abrir', 'roto': 'romper', 'muerto': 'morir', 'descubierto': 'descubrir', 'ido': 'ir', 'dado': 'dar',
            'ten': 'tener', 'ven': 'venir', 'pon': 'poner', 'sal': 'salir', 'haz': 'hacer', 've': 'ir ver', 'sé': 'ser saber',
            'yendo': 'ir', 'diciendo': 'decir', 'durmiendo': 'dormir', 'pidiendo': 'pedir', 'viniendo': 'venir',
            'sintiendo': 'sentir', 'pudiendo': 'poder', 'leyendo': 'leer', 'oyendo': 'oír', 'trayendo': 'traer',
            'había': 'haber', 'habían': 'haber', 'hubo': 'haber', 'habrá': 'haber'}


def strip_acc(w):
    return ''.join(c for c in unicodedata.normalize('NFD', w) if unicodedata.category(c) != 'Mn').replace('ñ', 'ñ')


def candidates(tok):
    t = tok.lower()
    out = {t, strip_acc(t)}
    if t in FORM2LEMMA:
        out.add(FORM2LEMMA[t])
    for suf in ('se', 'me', 'te', 'nos', 'os', 'lo', 'la', 'los', 'las', 'le', 'les'):   # 原形动词后连写代词
        if t.endswith(suf) and len(t) > len(suf) + 2 and re.search(r'(ar|er|ir)$', t[:-len(suf)]):
            out.add(t[:-len(suf)])
    # 复数、阴性
    for a, b in (('es', ''), ('s', ''), ('a', 'o'), ('as', 'o'), ('as', 'a'), ('os', 'o'), ('ces', 'z')):
        if t.endswith(a) and len(t) > len(a) + 1:
            out.add(t[:-len(a)] + b)
    # A2：不规则形式、拼写变化（busqué、llegué、empecé）、第三人称变音（pidió、durmió）、y（leyó）、将来时、命令式和副动词后连写代词
    base = strip_acc(t)
    for f, ls in A2_FORMS.items():
        if t == f or base == strip_acc(f):
            out.update(ls.split())
    for st, ls in A2_STEMS:
        if base.startswith(st) and len(base) > len(st):
            out.update(ls)
    for a, b in (('que', 'car'), ('gue', 'gar'), ('ce', 'zar')):
        if base.endswith(a) and len(base) > len(a) + 1:
            out.add(base[:-len(a)] + b)
    for a, bs in (('yo', ('er', 'ir')), ('yeron', ('er', 'ir')), ('yendo', ('er', 'ir'))):
        if base.endswith(a):
            out.update(base[:-len(a)] + b for b in bs)
    for e in ('e', 'as', 'a', 'emos', 'eis', 'an'):          # 将来时：原形＋词尾
        if base.endswith(e) and re.search(r'(ar|er|ir)$', base[:-len(e)]):
            out.add(base[:-len(e)])
    for suf in ('selo', 'sela', 'selos', 'selas', 'melo', 'mela', 'telo', 'tela', 'se', 'me', 'te', 'nos', 'os',
                'lo', 'la', 'los', 'las', 'le', 'les'):     # acuéstate、leyéndolo、cómpralo
        if base.endswith(suf) and len(base) > len(suf) + 2:
            rest = base[:-len(suf)]
            out.add(rest)
            for e in ENDINGS + ['ando', 'iendo', 'yendo']:
                if rest.endswith(strip_acc(e)) and len(rest) > len(e) + 1:
                    stem = rest[:-len(strip_acc(e))]
                    for v in (stem, stem.replace('ie', 'e'), stem.replace('ue', 'o'), stem.replace('i', 'e'), stem.replace('u', 'o')):
                        out.update({v + 'ar', v + 'er', v + 'ir', v + 'arse', v + 'erse', v + 'irse'})
    # 动词词尾 → 原形；词根元音变化（现在时 ie/ue，过去时第三人称 i/u）
    for e in ENDINGS:
        if t.endswith(e) and len(t) > len(e) + 1:
            stem = t[:-len(e)]
            for v in (stem, stem.replace('ie', 'e'), stem.replace('ue', 'o'), strip_acc(stem), stem.replace('i', 'e'), stem.replace('u', 'o')):
                for inf in ('ar', 'er', 'ir'):
                    out.add(v + inf)
                    out.add(v + inf + 'se')
    return out


def vocab_sets(book=B, units=UNITS):
    """{单元: 这个单元生词表里的词形集合}"""
    res = {}
    for u in units:
        words = set()
        txt = (book / 'student' / f'u{u}.md').read_text('utf-8')
        inside = False
        for raw in txt.split('\n'):
            t = raw.strip()
            if t.replace(' ', '') == '|西语|词性|中文|':
                inside = True
                continue
            if inside and t.startswith('|'):
                if re.match(r'^\|[\s:|-]+\|$', t):
                    continue
                head = re.sub(r'\*\*', '', t.strip('|').split('|')[0]).strip()
                m = re.match(r'^(.+?), -(a|as|es)$', head)
                forms = [head]
                if m:                                         # alumno, -a → alumno、alumna；inglés, -a → inglés、inglesa
                    base = m.group(1)
                    fem = base[:-1] + m.group(2) if base.endswith('o') else strip_acc(base) + m.group(2)
                    forms = [base, fem]
                for f in forms:
                    for w in re.findall(r"[a-záéíóúñü]+", f.lower()):
                        words.add(w)
                        words.add(strip_acc(w))
                    words.add(f.lower())
            else:
                inside = False
        res[u] = words
    return res


def texts(u):
    """这个单元录音稿台词和学生用书例句框的西语部分。"""
    out = []
    for raw in (B / 'audio' / f'u{u}.md').read_text('utf-8').split('\n'):
        m = re.match(r'^> [^:：｜]+: (.+?)｜', raw.strip())
        if m:
            out.append(m.group(1))
    for raw in (B / 'student' / f'u{u}.md').read_text('utf-8').split('\n'):
        t = raw.strip()
        if t.startswith('- ') or (t and not t.startswith(('>', '|', '#', '!', '@'))):
            # 练习题、列表和正文里的西语片段（去掉“×”错句；中文讲解里提到的西语词也算用到）
            if '×' not in t:
                out.append(' '.join(re.findall(r"[A-Za-zÁÉÍÓÚÑÜáéíóúñü¿¡?!,. ]{3,}", t)))
        if t.startswith('> ') and '｜' in t and not t.startswith('> ×'):
            es = t[2:].split('｜')[0].lstrip('√ ')
            out.append(re.sub(r'^[^:：]{1,20}[:：]\s*', '', es))     # 去掉“Carmen: ”这样的说话人
    return out


def names():
    """全书句中大写的词（人名、地名等）和录音稿里的角色名。"""
    n = set()
    for u in UNITS:
        for f in (B / 'audio' / f'u{u}.md', B / 'student' / f'u{u}.md'):
            for raw in f.read_text('utf-8').split('\n'):
                t = raw.strip()
                if t.startswith('- 角色：'):
                    for part in re.split(r'[；;]', t[5:]):
                        n.update(w.lower() for w in re.findall(r"[A-Za-zÁÉÍÓÚÑáéíóúñü]+", part.split('＝')[0]))
                for m in re.finditer(r"(?<=[a-záéíóúñü,] )([A-ZÁÉÍÓÚÑ][a-záéíóúñü]+)", t):
                    n.add(m.group(1).lower())
    return n


def main():
    vs = vocab_sets()
    a1 = set().union(*vocab_sets(A1, A1_UNITS).values())
    nm = names()
    report = {}
    for i, u in enumerate(UNITS):
        known = a1.union(*(vs[x] for x in UNITS[:i + 1]))
        later = {x: vs[x] for x in UNITS[i + 1:]}
        miss = {}
        for line in texts(u):
            for tok in re.findall(r"[A-Za-zÁÉÍÓÚÑÜáéíóúñü]+", line):
                if tok[:1].isupper() and tok.lower() not in STOP and not line.startswith(tok):
                    continue                                  # 句中大写：人名地名
                tl = tok.lower()
                if tl in STOP or len(tl) <= 2 or tl in nm:
                    continue
                c = candidates(tl)
                if c & known:
                    continue
                where = next((x for x, s in later.items() if c & s), None)
                miss.setdefault(tl, {'count': 0, 'later_unit': where, 'example': line[:80]})
                miss[tl]['count'] += 1
        report[u] = dict(sorted(miss.items()))
        print(f'单元 {u}：{len(miss)} 个词在本单元及以前的生词表里找不到'
              + (f'（其中 {sum(1 for v in miss.values() if v["later_unit"])} 个在后面单元的生词表里）' if miss else ''))
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else B / 'audio_build' / 'vocab_audit.json'
    out.write_text(json.dumps(report, ensure_ascii=False, indent=1), 'utf-8')
    print('结果写在', out)


if __name__ == '__main__':
    main()
