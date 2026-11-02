"""西语动词变位（第一册学到的时态）：陈述式现在时、简单过去时、过去未完成时、肯定命令式；另外算现在虚拟式（命令式由它来）、副动词、过去分词，只用来核对课件里出现的词形。
conjugate('levantarse') → {'pres': [...6], 'pret': [...6], 'impf': [...6], 'imp': {'tú':…, 'usted':…, 'nosotros':…, 'vosotros':…, 'ustedes':…}, 'subj': [...6], 'ger':…, 'part':…, 'notes': [...]}
不规则的都在下面的表里写明；表里没有的按规则变位（所以每个动词都要在 check 里核对过）。"""
import re
import unicodedata

PERS = ['yo', 'tú', 'él / ella / usted', 'nosotros / nosotras', 'vosotros / vosotras', 'ellos / ellas / ustedes']
REFL = ['me', 'te', 'se', 'nos', 'os', 'se']

# ---- 词根变化（现在时、虚拟式；-ir 动词另有简单过去时第三人称、虚拟式 nosotros / vosotros、副动词的 e→i、o→u）
E_IE = set('''pensar empezar comenzar despertar cerrar sentar nevar merendar calentar recomendar atravesar confesar gobernar apretar negar
regar fregar tropezar acertar temblar sembrar querer entender perder encender defender extender atender tender ascender descender
preferir sentir mentir divertir convertir sugerir advertir herir hervir referir consentir invertir'''.split())
O_UE = set('''contar costar encontrar recordar probar mostrar soñar acostar almorzar volar sonar rogar colgar aprobar comprobar demostrar
renovar acordar poder volver devolver envolver llover mover resolver doler morder soler oler torcer dormir morir'''.split())
E_I = set('pedir vestir repetir servir seguir conseguir elegir corregir despedir impedir medir competir reír sonreír freír perseguir'.split())
U_UE = {'jugar'}
I_IE = {'adquirir'}

# ---- 现在时第一人称单数不规则（其余人称照词根变化或规则）
YO = {'tener': 'tengo', 'venir': 'vengo', 'decir': 'digo', 'hacer': 'hago', 'poner': 'pongo', 'salir': 'salgo', 'traer': 'traigo',
      'caer': 'caigo', 'oír': 'oigo', 'valer': 'valgo', 'saber': 'sé', 'ver': 'veo', 'dar': 'doy', 'estar': 'estoy', 'caber': 'quepo',
      'conocer': 'conozco', 'parecer': 'parezco', 'ofrecer': 'ofrezco', 'agradecer': 'agradezco', 'nacer': 'nazco', 'crecer': 'crezco',
      'aparecer': 'aparezco', 'desaparecer': 'desaparezco', 'obedecer': 'obedezco', 'merecer': 'merezco', 'pertenecer': 'pertenezco',
      'establecer': 'establezco', 'reconocer': 'reconozco', 'conducir': 'conduzco', 'traducir': 'traduzco', 'producir': 'produzco',
      'reducir': 'reduzco', 'introducir': 'introduzco', 'satisfacer': 'satisfago'}
# 整个现在时不规则
PRES = {'ser': 'soy eres es somos sois son', 'estar': 'estoy estás está estamos estáis están', 'ir': 'voy vas va vamos vais van',
        'dar': 'doy das da damos dais dan', 'ver': 'veo ves ve vemos veis ven', 'haber': 'he has ha hemos habéis han',
        'oír': 'oigo oyes oye oímos oís oyen', 'reír': 'río ríes ríe reímos reís ríen', 'sonreír': 'sonrío sonríes sonríe sonreímos sonreís sonríen',
        'decir': 'digo dices dice decimos decís dicen', 'oler': 'huelo hueles huele olemos oléis huelen',
        'reunir': 'reúno reúnes reúne reunimos reunís reúnen', 'prohibir': 'prohíbo prohíbes prohíbe prohibimos prohibís prohíben'}
# 简单过去时的不规则词根（词尾 -e -iste -o -imos -isteis -ieron；j 后面是 -eron）
STRONG = {'tener': 'tuv', 'estar': 'estuv', 'andar': 'anduv', 'poder': 'pud', 'poner': 'pus', 'saber': 'sup', 'caber': 'cup', 'haber': 'hub',
          'querer': 'quis', 'venir': 'vin', 'hacer': 'hic', 'decir': 'dij', 'traer': 'traj', 'conducir': 'conduj', 'traducir': 'traduj',
          'producir': 'produj', 'reducir': 'reduj', 'introducir': 'introduj', 'satisfacer': 'satisfic'}
PRET = {'ser': 'fui fuiste fue fuimos fuisteis fueron', 'ir': 'fui fuiste fue fuimos fuisteis fueron',
        'dar': 'di diste dio dimos disteis dieron', 'ver': 'vi viste vio vimos visteis vieron'}
IMPF = {'ser': 'era eras era éramos erais eran', 'ir': 'iba ibas iba íbamos ibais iban', 'ver': 'veía veías veía veíamos veíais veían'}
SUBJ = {'ser': 'sea seas sea seamos seáis sean', 'estar': 'esté estés esté estemos estéis estén', 'ir': 'vaya vayas vaya vayamos vayáis vayan',
        'dar': 'dé des dé demos deis den', 'saber': 'sepa sepas sepa sepamos sepáis sepan', 'haber': 'haya hayas haya hayamos hayáis hayan',
        'caber': 'quepa quepas quepa quepamos quepáis quepan', 'ver': 'vea veas vea veamos veáis vean'}
TU = {'decir': 'di', 'hacer': 'haz', 'ir': 've', 'poner': 'pon', 'salir': 'sal', 'ser': 'sé', 'tener': 'ten', 'venir': 'ven', 'valer': 'vale',
      'satisfacer': 'satisfaz'}
PART = {'hacer': 'hecho', 'decir': 'dicho', 'ver': 'visto', 'poner': 'puesto', 'escribir': 'escrito', 'abrir': 'abierto', 'volver': 'vuelto',
        'morir': 'muerto', 'romper': 'roto', 'cubrir': 'cubierto', 'descubrir': 'descubierto', 'resolver': 'resuelto', 'devolver': 'devuelto',
        'envolver': 'envuelto', 'imprimir': 'impreso', 'freír': 'frito', 'satisfacer': 'satisfecho'}
GER = {'ir': 'yendo', 'poder': 'pudiendo', 'decir': 'diciendo', 'venir': 'viniendo', 'oír': 'oyendo', 'reír': 'riendo', 'sonreír': 'sonriendo'}
ACC_IAR = set('enviar esquiar confiar guiar fiar vaciar criar variar ampliar fotografiar desafiar'.split())   # -iar 带重音（envío）
NO_ACC_UAR = set('averiguar apaciguar adecuar evacuar'.split())                                   # -uar 不带重音（其余 continúo、efectúo）
IMPERSONAL = {'llover': 'llueve llovió llovía', 'nevar': 'nieva nevó nevaba', 'haber': 'hay hubo había'}   # 天气动词、无人称 hay：只有第三人称单数
NO_PRET_IMP = {'soler'}                                                                             # soler 不用简单过去时和命令式
PREFIX = ('man', 'ob', 'con', 'de', 'sos', 'entre', 'ad', 'pro', 'su', 'dis', 'ex', 'com', 'im', 'super', 're', 'pre', 'inter', 'des', 'contra')
BASES = ('tener', 'poner', 'venir', 'hacer', 'traer', 'volver', 'mover', 'seguir', 'pedir', 'sentir')
NO_PREFIX_SPLIT = {'devolver': 'volver', 'envolver': 'volver', 'deshacer': 'hacer', 'rehacer': 'hacer'}


ZC_EXCEPT = {'hacer', 'deshacer', 'rehacer', 'satisfacer', 'cocer', 'recocer', 'escocer', 'mecer', 'decir', 'bendecir', 'maldecir',
             'predecir', 'contradecir'}


def auto_irregular(inf):
    """-cer、-cir 前面是元音的（apetecer、lucir、conducir）第一人称是 -zco，-ducir 的简单过去时是 -duj-：没列进 YO、STRONG 的照这条补上。"""
    if (inf not in YO and inf not in ZC_EXCEPT and len(inf) > 4 and inf[-3] == 'c' and inf[-2:] in ('er', 'ir')
            and inf[-4] in 'aeiouáéíóú'):
        YO[inf] = inf[:-3] + 'zco'
    if inf.endswith('ducir') and inf not in STRONG:
        STRONG[inf] = inf[:-3] + 'j'


def strip_acc(s):
    """去掉重音符号，保留 ñ 和 ü（结果重新合成，长度不变）。"""
    return unicodedata.normalize('NFC', ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn' or c in '̈̃'))


def nfc(s):
    return unicodedata.normalize('NFC', s)


def compound(inf):
    """mantener → ('man', 'tener')：带前缀的派生动词照基本动词变；venir 的 convenir 之类同。"""
    if inf in NO_PREFIX_SPLIT:
        b = NO_PREFIX_SPLIT[inf]
        return inf[:-len(b)], b
    for b in BASES:
        if inf.endswith(b) and inf != b and inf[:-len(b)] in PREFIX:
            return inf[:-len(b)], b
    return '', inf


VOW = set('aeiouáéíóúü')
STRONG_V = set('aeoáéíóú')


def nuclei(w):
    """元音核（字母下标的列表）。qu、gu 在 e、i 前的 u 不发音；词尾在元音后的 y 算元音。"""
    w = w.lower()
    out, cur, prev = [], [], None
    for i, c in enumerate(w):
        is_v = c in VOW
        if c == 'u' and i and w[i - 1] in 'qg' and i + 1 < len(w) and w[i + 1] in 'eiéí':
            is_v = False
        if c == 'y' and i == len(w) - 1 and i and w[i - 1] in VOW:
            is_v = True
        if not is_v:
            if cur:
                out.append(cur)
            cur, prev = [], None
            continue
        if cur and prev is not None and (prev in STRONG_V and (c in STRONG_V)):
            out.append(cur)
            cur = []
        cur.append(i)
        prev = c
    if cur:
        out.append(cur)
    return out


def stressed(w):
    """重读元音的下标：有重音符号就是它；否则按规则（元音、n、s 结尾重读倒数第二个音节，其余重读最后一个）。"""
    for i, c in enumerate(w):
        if c in 'áéíóú':
            return i
    ns = nuclei(w)
    if not ns:
        return None
    nu = ns[-2] if len(ns) >= 2 and w[-1] in 'aeiouns' else ns[-1]
    strong = [i for i in nu if w[i] in STRONG_V]
    return strong[0] if strong else nu[-1]


ACUTE = {'a': 'á', 'e': 'é', 'i': 'í', 'o': 'ó', 'u': 'ú'}


def attach(base, clitics, drop=''):
    """命令式后面连写代词：base 的重读位置不变，必要时补重音符号（levanta + te → levántate；dé + me → deme）。drop：先去掉词尾的 s 或 d。"""
    pos = stressed(base)
    b = base[:-1] if drop and base.endswith(drop) else base
    new = strip_acc(b) + clitics
    if stressed(new) != pos:
        new = new[:pos] + ACUTE[new[pos]] + new[pos + 1:]
    return nfc(new)


def spell(stem, ending):
    """拼写变化：c→qu、g→gu、z→c（e 前），g→j、gu→g、c→z（a、o 前）——由调用处决定用不用。"""
    return stem + ending


def front(stem):
    """词根后面接 e、é 的拼写：buscar → busqué，llegar → llegué，empezar → empecé，averiguar → averigüé。"""
    if stem.endswith('c'):
        return stem[:-1] + 'qu'
    if stem.endswith('gu'):
        return stem[:-2] + 'gü'
    if stem.endswith('g'):
        return stem + 'u'
    if stem.endswith('z'):
        return stem[:-1] + 'c'
    return stem


def back(stem):
    """-er、-ir 动词的词根后面接 o、a 的拼写：coger → cojo，seguir → sigo，vencer → venzo。"""
    if stem.endswith('gu'):
        return stem[:-1]
    if stem.endswith('g'):
        return stem[:-1] + 'j'
    if stem.endswith('c'):
        return stem[:-1] + 'z'
    return stem


def change_stem(stem, kind):
    """把词根里最后一个 e / o / u / i 换成 ie / ue / i（kind 是 'ie'、'ue'、'i'、'u'）。"""
    src = {'ie': 'e', 'ue': 'o', 'i': 'e', 'u': 'o', 'uue': 'u', 'iie': 'i'}[kind]
    dst = {'ie': 'ie', 'ue': 'ue', 'i': 'i', 'u': 'u', 'uue': 'ue', 'iie': 'ie'}[kind]
    k = stem.rfind(src)
    if k < 0:
        raise ValueError(stem)
    out = stem[:k] + dst + stem[k + 1:]
    if kind == 'ue' and k == 0:
        out = 'h' + out          # oler → huelo
    if kind in ('ie', 'i') and out.startswith('ie') and k == 0:
        out = 'y' + out[1:]      # errar → yerro（这里用不到）
    return out


def base_conj(inf):
    """不带自复代词的变位。"""
    auto_irregular(inf)
    pre, core = compound(inf)
    if pre:
        r = base_conj(core)
        out = {}
        for k, v in r.items():
            if isinstance(v, list):
                out[k] = [x if x in ('—',) else add_prefix(pre, x, core, k) for x in v]
            elif isinstance(v, dict):
                out[k] = {p: add_prefix(pre, x, core, 'imp') for p, x in v.items()}
            elif isinstance(v, str):
                out[k] = pre + v
            else:
                out[k] = v
        return out
    end = inf[-2:]
    stem = inf[:-2]
    if inf.endswith('ír'):
        end, stem = 'ir', inf[:-2]
    kind = None
    if inf in E_IE:
        kind = 'ie'
    elif inf in O_UE:
        kind = 'ue'
    elif inf in E_I:
        kind = 'i'
    elif inf in U_UE:
        kind = 'uue'
    elif inf in I_IE:
        kind = 'iie'
    # 现在时
    if end == 'ar':
        en = ['o', 'as', 'a', 'amos', 'áis', 'an']
    elif end == 'er':
        en = ['o', 'es', 'e', 'emos', 'éis', 'en']
    else:
        en = ['o', 'es', 'e', 'imos', 'ís', 'en']
    uir = end == 'ir' and stem.endswith('u') and not stem.endswith('gu') and not stem.endswith('qu')   # construir → construyo
    if inf in PRES:
        pres = PRES[inf].split()
    else:
        pres = []
        for i, e in enumerate(en):
            s = stem
            if kind and i in (0, 1, 2, 5):
                s = change_stem(stem, kind)
            if inf in ACC_IAR and i in (0, 1, 2, 5):
                s = s[:-1] + 'í'
            if end == 'ar' and stem.endswith('u') and inf not in NO_ACC_UAR and i in (0, 1, 2, 5):
                s = s[:-1] + 'ú'
            if uir and i in (0, 1, 2, 5):
                s = s + 'y'
            if i == 0 and end in ('er', 'ir'):
                s = back(s) if (s.endswith('g') or s.endswith('gu') or (s.endswith('c') and len(s) > 1 and s[-2] not in VOW)) else s
            pres.append(nfc(s + e))
        if inf in YO:
            pres[0] = YO[inf]
        if inf in ('tener', 'venir'):
            pres = [YO[inf]] + [change_stem(stem, 'ie') + e for e in en[1:3]] + [stem + e for e in en[3:5]] + [change_stem(stem, 'ie') + en[5]]
    # 简单过去时
    if inf in PRET:
        pret = PRET[inf].split()
    elif inf in STRONG:
        st = STRONG[inf]
        pret = [st + 'e', st + 'iste', (st[:-1] + 'z' if inf == 'hacer' else st) + 'o', st + 'imos', st + 'isteis',
                st + ('eron' if st.endswith('j') else 'ieron')]
    elif end == 'ar':
        pret = [nfc(front(stem) + 'é'), stem + 'aste', nfc(stem + 'ó'), stem + 'amos', stem + 'asteis', stem + 'aron']
    else:
        s3 = stem
        if end == 'ir' and kind in ('ie', 'i'):
            s3 = change_stem(stem, 'i')
        elif end == 'ir' and kind == 'ue':
            s3 = change_stem(stem, 'u')
        if stem and stem[-1] in 'aeo' or uir:     # leer → leyó，oír → oyó，construir → construyó
            yo = 'í' if not uir else 'í'
            pret = [nfc(stem + 'í'), nfc(stem + ('iste' if uir else 'íste')), nfc(stem + 'yó'), nfc(stem + ('imos' if uir else 'ímos')),
                    nfc(stem + ('isteis' if uir else 'ísteis')), stem + 'yeron']
            if inf in ('reír', 'sonreír', 'freír'):
                s = stem[:-1]                    # re-ír → reí, reíste, rio
                pret = [nfc(s + 'eí'), nfc(s + 'eíste'), s + 'io', nfc(s + 'eímos'), nfc(s + 'eísteis'), s + 'ieron']
        else:
            pret = [nfc(stem + 'í'), stem + 'iste', nfc(s3 + 'ió'), stem + 'imos', stem + 'isteis', s3 + 'ieron']
    # 过去未完成时
    if inf in IMPF:
        impf = IMPF[inf].split()
    elif end == 'ar':
        impf = [stem + 'aba', stem + 'abas', stem + 'aba', nfc(stem + 'ábamos'), stem + 'abais', stem + 'aban']
    else:
        impf = [nfc(stem + x) for x in ('ía', 'ías', 'ía', 'íamos', 'íais', 'ían')]
    # 现在虚拟式（命令式 usted、ustedes、nosotros 由它来）
    if inf in SUBJ:
        subj = SUBJ[inf].split()
    else:
        s1 = pres[0][:-1]                      # 第一人称单数去掉 -o（hablo → habl，tengo → teng，pienso → piens）
        se = ['e', 'es', 'e', 'emos', 'éis', 'en'] if end == 'ar' else ['a', 'as', 'a', 'amos', 'áis', 'an']
        subj = []
        for i, e in enumerate(se):
            s, from_stem = s1, False
            if i in (3, 4):
                # nosotros / vosotros：第一人称不规则的（tengo、conozco、digo、oigo）照第一人称；-ar、-er 词根变化动词用原来的词根；
                # -ir 词根变化动词 e→i、o→u；词根带重音的（envío、continúo、reúno）去掉重音
                if inf in YO or inf in ('decir', 'oír'):
                    s = s1
                elif kind in ('ie', 'i') and end == 'ir':
                    s, from_stem = change_stem(stem, 'i'), True
                elif kind == 'ue' and end == 'ir':
                    s, from_stem = change_stem(stem, 'u'), True
                elif kind:
                    s, from_stem = stem, True
                else:
                    s = strip_acc(s1)
                if from_stem and end in ('er', 'ir') and (s.endswith(('g', 'gu')) or (s.endswith('c') and s[-2] not in VOW)):
                    s = back(s)                    # seguir → sigamos，elegir → elijamos
                if inf in ('reír', 'sonreír', 'freír'):
                    s = stem[:-1] + 'i'
            if end == 'ar':
                s = front(s)                       # busque、pague、empiece、averigüe
            subj.append(nfc(s + e))
    # 命令式
    tu = TU.get(inf) or pres[2]
    vos = inf[:-1] + 'd'                       # hablad、comed、vivid、oíd
    imp = {'tú': tu, 'usted': subj[2], 'nosotros': 'vamos' if inf == 'ir' else subj[3], 'vosotros': nfc(vos), 'ustedes': subj[5]}
    # 副动词、过去分词（只用来核对）
    if inf in GER:
        ger = GER[inf]
    elif end == 'ar':
        ger = stem + 'ando'
    else:
        gs = stem
        if end == 'ir' and kind in ('ie', 'i'):
            gs = change_stem(stem, 'i')
        elif end == 'ir' and kind == 'ue':
            gs = change_stem(stem, 'u')
        ger = gs + ('yendo' if (stem and stem[-1] in 'aeo') or uir else 'iendo')
    if inf in PART:
        part = PART[inf]
    elif end == 'ar':
        part = stem + 'ado'
    else:
        part = nfc(stem + ('ído' if stem and stem[-1] in 'aeo' else 'ido'))
    return {'pres': pres, 'pret': pret, 'impf': impf, 'subj': subj, 'imp': imp, 'ger': ger, 'part': part}


def add_prefix(pre, form, core, k):
    """派生动词加前缀：重读位置不变，必要时补重音（ten → mantén，pon → compón，di → predí 这里用不到）。"""
    w = pre + form
    if form in ('ten', 'pon', 'ven') and k == 'imp':
        return attach_accent_last(w)
    return w


def attach_accent_last(w):
    """单音节命令式加前缀以后变成以 n 结尾的尖音词：mantén、compón、convén。"""
    i = max(i for i, c in enumerate(w) if c in 'aeiou')
    return w[:i] + ACUTE[w[i]] + w[i + 1:]


def conjugate(lemma):
    refl = lemma.endswith('se') and lemma[:-2].endswith(('ar', 'er', 'ir', 'ír'))
    inf = lemma[:-2] if refl else lemma
    r = base_conj(inf)
    notes = []
    if inf in IMPERSONAL:
        a, b, c = IMPERSONAL[inf].split()
        r['pres'] = ['—', '—', a, '—', '—', '—']
        r['pret'] = ['—', '—', b, '—', '—', '—']
        r['impf'] = ['—', '—', c, '—', '—', '—']
        r['imp'] = {p: '—' for p in r['imp']}
        notes.append('只用第三人称单数' if inf != 'haber' else '无人称用法 hay（有）只用第三人称单数')
    if inf in NO_PRET_IMP:
        r['pret'] = ['—'] * 6
        r['imp'] = {p: '—' for p in r['imp']}
        notes.append('一般不用简单过去时和命令式')
    if refl:
        r['pres'] = [x if x == '—' else f'{p} {x}' for p, x in zip(REFL, r['pres'])]
        r['pret'] = [x if x == '—' else f'{p} {x}' for p, x in zip(REFL, r['pret'])]
        r['impf'] = [x if x == '—' else f'{p} {x}' for p, x in zip(REFL, r['impf'])]
        im = r['imp']
        r['imp'] = {'tú': attach(im['tú'], 'te'), 'usted': attach(im['usted'], 'se'), 'nosotros': attach(im['nosotros'], 'nos', drop='s'),
                    'vosotros': 'idos' if inf == 'ir' else attach(im['vosotros'], 'os', drop='d'), 'ustedes': attach(im['ustedes'], 'se')}
        if inf in IMPERSONAL or inf in NO_PRET_IMP:
            r['imp'] = {p: '—' for p in r['imp']}
    r['notes'] = notes
    r['reflexive'] = refl
    return r


def regular(lemma):
    """完全按规则变位的动词（排版时标出不规则的形式用）。"""
    refl = lemma.endswith('se') and lemma[:-2].endswith(('ar', 'er', 'ir', 'ír'))
    inf = lemma[:-2] if refl else lemma
    pre, core = compound(inf)
    auto_irregular(core)
    return not (core in E_IE or core in O_UE or core in E_I or core in U_UE or core in I_IE or core in YO or core in PRES or core in STRONG
                or core in PRET or core in IMPF or core in SUBJ or core in TU or core in ACC_IAR or core in IMPERSONAL or core in NO_PRET_IMP
                or (core.endswith('uar') and core not in NO_ACC_UAR) or (core.endswith('uir') and not core.endswith(('guir', 'quir'))))


if __name__ == '__main__':
    import sys
    for v in sys.argv[1:]:
        r = conjugate(v)
        print(v, r['notes'])
        for k in ('pres', 'pret', 'impf', 'subj'):
            print(f'  {k}:', ', '.join(r[k]))
        print('  imp:', ', '.join(f'{p} {x}' for p, x in r['imp'].items()), '| ger', r['ger'], '| part', r['part'])
