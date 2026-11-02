"""把三份归并结果（data/lex_*.tsv）合成按课的单词表：python merge.py <课件 content 目录>
输出 data/vocab.json（每课：新词、语音练习词、动词形式、变位表要列的动词、常用表达）和 data/review.txt（要人工看的地方）。
动词形式一律用 analyze.py 复核：归并时写的形式说明对得上才用，对不上的列进 review.txt。"""
import json
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import analyze  # noqa: E402
import conj  # noqa: E402

SRC = Path(sys.argv[1])
DATA = Path(__file__).resolve().parent.parent / 'data'
ES_WORD = re.compile(r"[A-Za-zÁÉÍÓÚÑÜáéíóúñü]+")
POS = {'m.', 'f.', 'm., f.', 'm. pl.', 'f. pl.', 'adj.', 'adv.', 'prep.', 'conj.', 'art.', 'pron.', 'num.', 'interj.', 'v.', '地名'}

# 第 1 课语音部分拆开的音节、元音字母（A·na、al·to、me·sa、to·ma·te、sal·sa）和语法要点里的词尾（-a、-o），不是这几个词；
# 按第一次在课文、例句、常用表达、词汇里作词用的课算
SYLLABLE_ONLY = {'a': 7, 'al': 7, 'e': 4, 'o': 8, 'me': 8, 'te': 8, 'sal': 15}   # sal 是 salir 的命令式，只在第 15 课语法和练习里
TRIVIAL = re.compile(r'(阴性|阳性)?(复数|单数)?')
VOCAB_STOP = {'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas', 'de', 'a', 'al', 'del', 'en', 'con', 'por', 'para', 'y', 'o', 'e',
              'lo', 'le', 'se', 'mi', 'tu', 'su', 'que', 'inf', 'pl', 'adv', 'ra', 'sa', 'gua', 'ña', 'cia'}
GRAMMAR_NOTE = ('复数', '单数', '最高级', '短尾', '缩写', '阴性', '阳性', '序数')

# 三组归并的人各自处理、要统一的地方：形式 → (lemma, pos, zh, note)，None 表示照旧
FIX = {
    # 国籍、地方的人：统一作形容词，释义“……人；……的”
    'mexicano': ('mexicano, mexicana', 'adj.', '墨西哥人；墨西哥的', None),
    'mexicanos': ('mexicano, mexicana', 'adj.', None, None),
    'mexicana': ('mexicano, mexicana', 'adj.', None, None),
    'mexicanas': ('mexicano, mexicana', 'adj.', None, None),
    'extranjero': ('extranjero, extranjera', 'adj.', '外国人；外国的', None),
    'extranjeros': ('extranjero, extranjera', 'adj.', None, None),
    'extranjera': ('extranjero, extranjera', 'adj.', None, None),
    'extranjeras': ('extranjero, extranjera', 'adj.', None, None),
    # señor 和 señora 合成一条
    'señor': ('señor, señora', 'm., f.', '先生；女士', None),
    # 序数词统一作形容词
    'segundo': ('segundo, segunda', 'adj.', None, '序数词'),
    # 拿不准的几条，定下来
    'poco': (None, None, None, 'un poco (de)：一点儿'),
    'paz': (None, None, None, 'calle de la Paz 和平街（街名）'),
    'vía': (None, None, None, 'Gran Vía 格兰大道（马德里街名）'),
    'a': (None, None, None, ''),
    'al': (None, None, None, 'a 与 el 的缩合'),
    'e': (None, None, None, '用在 i-、hi- 开头的词前，代替 y'),
    'o': (None, None, None, ''),
    'me': (None, None, None, '直接宾语代词；第 10 课起也作间接宾语代词（与格）'),
    'te': (None, None, None, '直接宾语代词；第 10 课起也作间接宾语代词（与格）'),
    'nos': (None, None, None, '直接宾语代词；第 10 课起也作间接宾语代词（与格）'),
    'os': (None, None, None, '直接宾语代词；第 10 课起也作间接宾语代词（与格）'),
    'lo': (None, None, '他；它；您（宾格）', '直接宾语代词，阳性单数'),
    'se': (None, None, None, '自复代词，第三人称（se llama）；第 10 课起 le、les 在 lo、la、los、las 前也变成 se'),
    'sal': (None, None, None, '命令式 tú'),
    # 两组审读改的
    'aquéllos': (None, None, '那个（远指）', None),                       # 原形是单数，和 éste 这个、ése 那个一致
    'padres': (None, None, None, '也指父母'),
    'la': (None, None, None, '定冠词 el, la, los, las；其中 la、los、las 第 8 课起也作宾格代词'),
    'los': (None, None, None, '定冠词 el, la, los, las；其中 la、los、las 第 8 课起也作宾格代词'),
    'las': (None, None, None, '定冠词 el, la, los, las；其中 la、los、las 第 8 课起也作宾格代词'),
    'chicos': (None, None, '男孩，小伙子；女孩，姑娘', None),
    'cerca': (None, None, '近；在附近', 'cerca de 在……附近'),
    'cuánto': (None, 'adj.', None, ''),                                  # 第 12 课 ¿Cuánto es? 第 6 课的 cuánto 已经讲了代词用法
    'abuelos': (None, None, None, 'abuelos 也指（外）祖父母'),
    'tíos': (None, None, None, 'tíos 也指叔叔阿姨'),
    'fines': (None, None, None, '复数；los fines de semana 每逢周末'),
    'les': (None, None, '他们；她们；您几位（间接宾语）', None),          # 和 ustedes 您几位 一致
    'madrileños': ('madrileño, madrileña', 'adj.', '马德里人；马德里的', '复数'),
    'segunda': ('segundo, segunda', 'adj.', None, '序数词'),
    'largo': ('largo, larga', 'adj.', '长的', '… metros de largo 长……米'),   # 第 18 课 de largo，第 19 课 un día largo，都是这个词
    'española': ('español', 'm.', None, '形容词 español, española：西班牙人；西班牙的'),   # 和 francés 一样并到第 7 课的 español
    'sucísimo': (None, None, None, 'sucísimo：绝对最高级（-io 只留一个 i）'),
    'tanto': (None, None, None, 'tanto, -a, -os, -as + 名词 + que 那么多……以至于……；也作副词：动词 + tanto + que'),
    'tanta': (None, None, None, ''),
    'primera': (None, None, None, '序数词；阳性单数名词前变为 primer'),
    'tercera': (None, None, None, '序数词；阳性单数名词前变为 tercer'),
    'mundo': (None, None, None, 'todo el mundo 大家，人人'),
    'sol': (None, None, None, 'Puerta del Sol 太阳门（马德里的广场）'),
    'luces': (None, None, None, '复数 luces'),
    'canciones': (None, None, None, '复数 canciones（不带重音符号）'),
}

# 语音练习里拆成音节写的词（al·to、sal·sa、po·e·ta、mu·se·o）：抽词时没认出来，按这一课的语音练习词算
DRILL_SPLIT = {'alto': 1, 'salsa': 1, 'poeta': 2, 'museo': 2}
PHON_EXTRA = [
    {'lemma': 'salsa', 'pos': 'f.', 'zh': '调味汁', 'note': '', 'phon': 1},
    {'lemma': 'poeta', 'pos': 'm.', 'zh': '诗人', 'note': '', 'phon': 2},
]



# 归并按“第一次出现”分条，la、los、las 第 3 课先作冠词出现，第 8 课作宾格代词时要另立一条
EXTRA = [
    {'lemma': 'la', 'pos': 'pron.', 'zh': '她；它；您（宾格）', 'note': '直接宾语代词，阴性单数', 'lesson': 8},
    {'lemma': 'los', 'pos': 'pron.', 'zh': '他们；它们；您几位（宾格）', 'note': '直接宾语代词，阳性复数', 'lesson': 8},
    {'lemma': 'las', 'pos': 'pron.', 'zh': '她们；它们；您几位（宾格）', 'note': '直接宾语代词，阴性复数', 'lesson': 8},
    # 第 9 课 el mío es pequeño：mío 也作物主代词，和 tuyo、suyo 一样两个词性合成一行
    {'lemma': 'mío', 'pos': 'pron.', 'zh': '我的', 'note': '物主代词 el mío, la mía, los míos, las mías', 'lesson': 9},
    # 和动词同形、名词第 15 课才出现的（第 13 课 almuerzo、第 14 课 desayuno 是动词 almorzar、desayunar）
    {'lemma': 'almuerzo', 'pos': 'm.', 'zh': '午饭', 'note': '', 'lesson': 15},
    {'lemma': 'desayuno', 'pos': 'm.', 'zh': '早饭', 'note': '', 'lesson': 15},
    # 第 14 课 Como vivo lejos…：连词 como（同形的 como 是 comer 的变位）
    {'lemma': 'como', 'pos': 'conj.', 'zh': '因为；由于', 'note': '引导原因从句，放在主句前', 'lesson': 14},
]
# 同形的动词形式：词形第一次出现时是另一个动词的（ve、ven 第 8 课是 ver，di 第 15 课是 decir，llama 第 1 课是 llamarse）
VFORM_EXTRA = [('llama', 'llamar', 15, '命令式 tú'), ('ven', 'venir', 15, '命令式 tú'), ('ve', 'ir', 15, '命令式 tú'),
               ('di', 'dar', 20, '简单过去时 第一人称单数')]
# 已学词本课的新用法
NEWFORM_EXTRA = [{'form': 'claro', 'lemma': 'claro, clara', 'pos': 'adj.', 'note': '作副词：清楚地（habló despacio y claro）', 'lesson': 20}]
# 生词表里前面已出现的条目，课次要说明的
SEEN_WHERE = {(24, 'hace + 时间'): 'hacer 第 7 课；hace + 时间 第 19 课',
              (22, 'de niño, de niña'): 'niño 第 6 课；de niño, de niña 第 21 课常用表达'}
DROP_NOTES = {'mano 是阴性名词'}
# 同形词的第二个意思：词形第一次出现时是另一个意思，课件生词表在后面的课才列这个意思（la mañana 早晨、tarde 晚）
# 第 12 课 ¿Es cara? 是 caro 的阴性，la cara（脸）课文里第 14 课才用、才列进生词表
# 第 15 课 Llama a Ana 是 llamar（不是第 1 课的 llamarse）；副词 mucho 第 12 课 Sí, mucho 就用了（muchísimo 第 23 课）
PIN = {('mañana', 'f.'): (8, '早晨；上午'), ('tarde', 'adv.'): (11, '晚；迟'), ('cara', 'f.'): (14, '脸'),
       ('llamar', 'v.'): (15, '叫；打电话'), ('mucho', 'adv.'): (12, '很；非常；很多')}


def read_lex():
    rows = {}
    for f in sorted(DATA.glob('lex_L*.tsv')):
        src_forms = [e['form'] for e in json.loads((DATA / f.name.replace('lex_', 'forms_').replace('.tsv', '.json')).read_text('utf-8'))]
        lines = f.read_text('utf-8').rstrip('\n').split('\n')
        assert lines[0] == 'form\tlemma\tpos\tzh\tnote', f
        body = [ln.split('\t') for ln in lines[1:]]
        assert [b[0] for b in body] == src_forms, f'{f.name} 词形顺序和输入不一样'
        for b in body:
            assert len(b) in (4, 5), b          # Write 工具会去掉行尾的制表符：备注空的行只有 4 栏
            b = (b + [''])[:5]
            rows[b[0]] = dict(zip(('form', 'lemma', 'pos', 'zh', 'note'), (x.strip() for x in b)))
    return rows


def es_key(s):
    """西语字母顺序：不计重音，ñ 排在 n 后面。"""
    s = s.lower().replace('ñ', 'n~')
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')


def top_split(note):
    """按括号外的“；”分段（括号里也可能有“；”）。"""
    out, depth, cur = [], 0, ''
    for ch in note:
        depth += (ch == '（') - (ch == '）')
        if ch == '；' and depth == 0:
            out.append(cur)
            cur = ''
        else:
            cur += ch
    return out + [cur]


def claim_of(note):
    """归并时写的形式说明（备注第一段，去掉括号里的说明）。"""
    c = re.sub(r'（[^）]*）', '', top_split(note)[0]).strip()
    c = c.replace('代词 ', '').replace('现在分词', '副动词').replace('（未加', '')
    return c


def matches(claim, analyses):
    """claim 和 analyze() 的结果对得上的那几条。"""
    if not claim:
        return []
    out = []
    for a in analyses:
        if a == claim:
            out.append(a)
        elif claim.startswith('命令式 + ') and a.startswith('命令式 ') and a.endswith(claim[len('命令式'):]):
            out.append(a)
        elif '第一/第三人称单数' in claim and a in (claim.replace('第一/第三', '第一'), claim.replace('第一/第三', '第三')):
            out.append(a)
        elif claim == '陈述式现在时 无人称形式' and a == '陈述式现在时 第三人称单数':
            out.append(a)
    return out


def join_analyses(xs):
    """过去未完成时第一、第三人称单数同形，写成一条。"""
    xs = list(dict.fromkeys(xs))
    for t in ('过去未完成时', '虚拟式现在时'):
        a, b = f'{t} 第一人称单数', f'{t} 第三人称单数'
        if a in xs or b in xs:
            i = xs.index(a) if a in xs else xs.index(b)
            xs[i] = f'{t} 第一/第三人称单数'
            xs = [x for k, x in enumerate(xs) if k == i or x not in (a, b)]
    return '；'.join(xs)


def verb_type(lemma):
    refl = lemma.endswith('se') and lemma[:-2].endswith(('ar', 'er', 'ir', 'ír'))
    inf = lemma[:-2] if refl else lemma
    pre, core = conj.compound(inf)
    tags = []
    if refl:
        tags.append('自复动词')
    if core in conj.E_IE:
        tags.append('e→ie')
    elif core in conj.O_UE:
        tags.append('o→ue')
    elif core in conj.E_I:
        tags.append('e→i')
    elif core in conj.U_UE:
        tags.append('u→ue')
    conj.auto_irregular(core)
    if core in conj.ACC_IAR:
        tags.append('i→í')
    elif core.endswith('uar') and core not in conj.NO_ACC_UAR:
        tags.append('u→ú')
    stem_changed = any(t in tags for t in ('e→ie', 'o→ue', 'e→i', 'u→ue'))
    beyond = any(core in s for s in (conj.YO, conj.PRES, conj.STRONG, conj.PRET, conj.IMPF, conj.TU))
    if (beyond or (not conj.regular(lemma) and not stem_changed)) and not any(t in tags for t in ('i→í', 'u→ú')):
        tags.append('不规则')
    return tags


ENDS = {'ar': ('o as a amos áis an', 'é aste ó amos asteis aron', 'aba abas aba ábamos abais aban', 'a e emos ad en', 'ando ado'),
        'er': ('o es e emos éis en', 'í iste ió imos isteis ieron', 'ía ías ía íamos íais ían', 'e a amos ed an', 'iendo ido'),
        'ir': ('o es e imos ís en', 'í iste ió imos isteis ieron', 'ía ías ía íamos íais ían', 'e a amos id an', 'iendo ido')}
IMP_P = ('tú', 'usted', 'nosotros', 'vosotros', 'ustedes')


def conj_table(lemma):
    """变位表：6 个人称 × 现在时、简单过去时、过去未完成时、命令式；和规则变位不一样的格子标 irr（看不带自复代词的形式）。"""
    r = conj.conjugate(lemma)
    refl = r['reflexive']
    inf = lemma[:-2] if refl else lemma
    base = conj.base_conj(inf)
    stem, cl = inf[:-2], inf[-2:].replace('í', 'i')
    pres, pret, impf, imp, gp = (x.split() for x in ENDS[cl])
    plain = {'pres': [stem + e for e in pres], 'pret': [stem + e for e in pret], 'impf': [stem + e for e in impf],
             'imp': dict(zip(IMP_P, (stem + e for e in imp))), 'ger': stem + gp[0], 'part': stem + gp[1]}
    rows = []
    for i in range(6):
        row = []
        for k in ('pres', 'pret', 'impf'):
            shown = r[k][i]
            row.append({'f': shown, 'irr': shown != '—' and base[k][i] != plain[k][i]})
        if i == 0:
            row.append({'f': '—', 'irr': False})
        else:
            pp = IMP_P[i - 1]
            shown = r['imp'][pp]
            row.append({'f': shown, 'irr': shown != '—' and (base['imp'][pp] != plain['imp'][pp] or (refl and inf == 'ir' and pp == 'vosotros'))})
        rows.append(row)
    # 无人称动词 hay：现在时 full 里是 hay，base 是 ha
    for i, row in enumerate(rows):
        for k, c in zip(('pres', 'pret', 'impf'), row):
            if c['f'] not in ('—', base[k][i]) and not refl:
                c['irr'] = True
    return {'rows': rows, 'ger': {'f': r['ger'], 'irr': r['ger'] != plain['ger']}, 'part': {'f': r['part'], 'irr': r['part'] != plain['part']},
            'notes': r['notes'], 'reflexive': refl}


def main():
    rows = read_lex()
    forms = json.loads((DATA / 'forms.json').read_text('utf-8'))
    sent = json.loads((DATA / 'sentences.json').read_text('utf-8'))
    review = []

    first_real, first_sent = {}, {}
    for L in sent:
        for u in L['units']:
            for w in ES_WORD.findall(u['es']):
                if u['src'] != '语音':
                    first_real.setdefault(w.lower(), L['lesson'])
                if u['src'] in ('课文', '语法例句', '常用表达', '词汇'):
                    first_sent.setdefault(w.lower(), L['lesson'])

    # 课件各课生词表：每条去掉括号里的说明、冠词和虚词，剩下的实词算“在这一课的生词表里”
    voc, vocab_lessons = {}, defaultdict(set)
    for f in sorted(SRC.glob('L*.json')):
        j = json.loads(f.read_text('utf-8'))
        for w in j['vocab']:
            allt = [x.lower() for x in ES_WORD.findall(re.sub(r'\([^)]*\)', '', w[0]))]
            toks = [x for x in allt if x not in VOCAB_STOP] or allt          # 生词表里单列的虚词（y、de、en、o、para）
            voc.setdefault(j['lesson'], []).append((w[0], toks))
            for x in toks:
                vocab_lessons[x].add(j['lesson'])

    # 每个词形：归并结果 + 课次
    items = []
    for e in forms:
        f = e['form']
        r = dict(rows[f])
        if f in FIX:
            for k, v in zip(('lemma', 'pos', 'zh', 'note'), FIX[f]):
                if v is not None:
                    r[k] = v
            r['fixed_note'] = FIX[f][3] is not None          # 定下来的备注照原样用，不再加“词形：”
        if '？' in r['note']:
            review.append(f'备注里还有问号：{f}\t{r["note"]}')
        if r['lemma'] in ('#跳过', '#人名'):
            continue
        assert r['pos'] in POS, (f, r['pos'])
        assert r['zh'], f
        real = first_real.get(f)
        anyl = e['lesson']
        if f in SYLLABLE_ONLY:
            real = anyl = SYLLABLE_ONLY[f]
            assert first_sent.get(f, real) == real, (f, first_sent.get(f))
        if f in DRILL_SPLIT:
            anyl = min(anyl, DRILL_SPLIT[f])
        r.update(lesson=real, phon=anyl if real is None or anyl < real else None, vocab=vocab_lessons.get(f, set()), count=e['count'])
        items.append(r)

    # 动词形式复核
    for r in items:
        if r['pos'] != 'v.':
            continue
        lemma = r['lemma']
        an = analyze.analyze(r['form'], lemma)
        if not an:
            review.append(f'变位程序认不出：{r["form"]} ← {lemma}\t{r["note"]}')
            r['analysis'] = claim_of(r['note'])
            continue
        claim = claim_of(r['note'])
        ok = matches(claim, an)
        if ok:
            r['analysis'] = join_analyses(ok)
        else:
            r['analysis'] = join_analyses(an)
            review.append(f'形式说明对不上：{r["form"]} ← {lemma}\t归并写的「{claim}」，程序算的「{"；".join(an)}」')
        segs = top_split(r['note'])
        rest = [p for p in segs[1:] if p and '同形' not in p]
        # 括号里写了连写代词以后的样子的（quiten + se → quítense、→ enseñémosela），留下来
        m = re.search(r'（(.*)）', segs[0])
        hints = [h if '+' in h else '连写代词 ' + h for h in (m.group(1).split('；') if m else []) if re.search(r'\s→\s|^→\s', h)]
        r['usage'] = '；'.join(hints + rest)

    extra_vforms = []
    for f, lemma, n, claim in VFORM_EXTRA:
        an = analyze.analyze(f, lemma)
        assert claim in an, (f, lemma, an)
        assert any(re.search(rf'\b{f}\b', u['es'], re.I) for L in sent if L['lesson'] == n for u in L['units']), (f, n)
        extra_vforms.append({'form': f, 'lemma': lemma, 'analysis': claim, 'usage': '', 'lesson': n})

    # 词条：同一个 lemma + 词性 合成一条
    ent = defaultdict(list)
    for r in items:
        ent[(r['lemma'], r['pos'])].append(r)
    entries, newforms = [], []
    for (lemma, pos), rs in ent.items():
        head = lemma.split(',')[0].strip().lower()
        real = [r['lesson'] for r in rs if r['lesson']]
        lesson = min(real) if real else None
        if (lemma, pos) in PIN:
            lesson = PIN[(lemma, pos)][0]
        ph = [r['phon'] for r in rs if r['phon'] and (lesson is None or r['phon'] < lesson)]
        best = sorted(rs, key=lambda r: (not r['vocab'], r['form'] != head, r['lesson'] or 99))[0]
        notes = []
        for r in sorted(rs, key=lambda r: (r['form'] != head, r['lesson'] or 99)):
            if pos == 'v.':
                continue
            segs = [p.strip().replace('指示代词（旧版带重音）', '指示代词 ').replace('  ', ' ') for p in r['note'].split('；')]
            segs = [p for p in segs if p and not TRIVIAL.fullmatch(p) and p not in DROP_NOTES]
            assert not any('？' in p for p in segs), r
            tagged = segs
            if r['form'] != head:
                segs = [p for p in segs if not any(p in n or (r['form'] in n and any(k in p for k in GRAMMAR_NOTE)) for n in notes)]
                tagged = [f'{r["form"]}：{p}' if any(k in p for k in GRAMMAR_NOTE) and not p.startswith('缩写') and r['form'] not in p
                          and not r.get('fixed_note') else p for p in segs]
            if r['form'] == head or r['lesson'] == lesson or r['lesson'] is None:
                notes += [p for p in tagged if p not in notes]
            elif segs:                                       # 新形式那一行开头就是词形，备注不再重复
                newforms.append({'form': r['form'], 'lemma': lemma, 'pos': pos, 'note': '；'.join(segs), 'lesson': r['lesson']})
        zh = PIN[(lemma, pos)][1] if (lemma, pos) in PIN else best['zh']
        if pos == 'v.':
            zh = zh.replace('，', '；')            # 动词释义的几个意思统一用分号隔开
        entries.append({'lemma': lemma, 'pos': pos, 'zh': zh, 'note': '；'.join(notes), 'lesson': lesson,
                        'phon': min(ph) if ph else None, 'core': False,
                        'vtype': verb_type(lemma) if pos == 'v.' else [],
                        'forms': sorted({r['form'] for r in rs})})

    for x in EXTRA:
        entries.append(dict(x, phon=None, core=False, vtype=[], forms=[x['lemma']]))
    newforms += NEWFORM_EXTRA
    for x in PHON_EXTRA:
        assert x['lemma'] not in rows, x
        entries.append(dict(x, lesson=None, core=False, vtype=[], forms=[x['lemma']]))

    # 同一 lemma 在同一课有两个词性的，合成一行
    by = defaultdict(list)
    for e in entries:
        by[(e['lemma'], e['lesson'], e['phon'])].append(e)
    merged = []
    for k, es in by.items():
        if len(es) == 1:
            merged.append(es[0])
            continue
        es.sort(key=lambda e: e['pos'])
        m = dict(es[0])
        m['pos'] = '；'.join(e['pos'] for e in es)
        m['zh'] = '；'.join(dict.fromkeys(z for e in es for z in e['zh'].split('；')))
        m['note'] = '；'.join(e['note'] for e in es if e['note'])
        m['forms'] = sorted({f for e in es for f in e['forms']})
        merged.append(m)
        review.append(f'同课两个词性，合成一行：{m["lemma"]}（{m["pos"]}）{m["zh"]}')
    entries = merged

    # 课件各课生词表的每一条对到词条：先按原形整条对（caro, cara），对不上再按里面的实词对。
    # 对到本课新词的，新词表里加粗；全都是前面课里出现过的，单列一行“前面已经出现过”
    lem_idx, form_idx = defaultdict(list), defaultdict(list)
    for e in entries:
        if e['lesson']:
            lem_idx[e['lemma'].lower()].append(e)
            for f in e['forms']:
                form_idx[f].append(e)

    def expand_fem(s):
        """课件生词表的简写 sucio, cia → sucio, sucia"""
        m = re.fullmatch(r'(\w+o), (\w+a)', s)
        if m and len(m[2]) < len(m[1]) and m[1][-len(m[2]):-1] == m[2][:-1] and not m[1].startswith(m[2][:-1] + 'o'):
            return f'{m[1]}, {m[1][:-len(m[2])]}{m[2]}'
        return s

    def norm_item(s):
        s = re.sub(r'[¿?¡!]', '', re.sub(r'\([^)]*\)', '', s))
        return ', '.join(re.sub(r'^(el|la|los|las)\s+', '', x.strip()) for x in s.split(',')).strip().lower()

    seen = defaultdict(list)
    for n, its in voc.items():
        for txt, toks in its:
            hit = lem_idx.get(norm_item(txt)) or [min(form_idx[x], key=lambda e: e['lesson']) for x in toks if form_idx.get(x)]
            hit = list({id(e): e for e in hit}.values())
            if re.match(r'(el|la|los|las) ', txt):          # 带冠词的是名词（la tarde 不是副词 tarde）
                hit = [e for e in hit if e['pos'].startswith(('m.', 'f.'))] or hit
            if not hit:
                review.append(f'生词表条目找不到词条：第 {n} 课 {txt}')
                continue
            new = [e for e in hit if e['lesson'] == n]
            for e in new:
                e['core'] = True
            if not new:
                if any(e['lesson'] > n for e in hit):
                    review.append(f'生词表条目的词排在后面的课：第 {n} 课 {txt}')
                if len(hit) == 1 and norm_item(expand_fem(txt)) == hit[0]['lemma'].lower():
                    where = f'第 {hit[0]["lesson"]} 课'
                else:                                         # 按里面的词对上的，写明是哪个词（lejísimos → lejos 第 14 课）
                    where = '、'.join(f'{e["lemma"].split(",")[0]} 第 {e["lesson"]} 课' for e in hit)
                where = SEEN_WHERE.get((n, txt), where)
                seen[n].append({'item': expand_fem(txt), 'where': where})

    # 按课整理
    lessons = []
    for f in sorted(SRC.glob('L*.json')):
        j = json.loads(f.read_text('utf-8'))
        n = j['lesson']
        words = sorted([e for e in entries if e['lesson'] == n], key=lambda e: es_key(e['lemma']))
        phon = sorted([e for e in entries if e['phon'] == n], key=lambda e: es_key(e['lemma']))
        vforms = sorted([r for r in items if r['pos'] == 'v.' and r['lesson'] == n and r['form'] != r['lemma']],
                        key=lambda r: (es_key(r['lemma']), es_key(r['form'])))
        verbs = [e['lemma'] for e in words if e['pos'] == 'v.']
        lessons.append({'lesson': n, 'title_es': j['title_es'], 'title_zh': j['title_zh'],
                        'words': words, 'phon': phon,
                        'vforms': sorted([{'form': r['form'], 'lemma': r['lemma'], 'analysis': r['analysis'], 'usage': r.get('usage', '')} for r in vforms]
                                         + [{k: x[k] for k in ('form', 'lemma', 'analysis', 'usage')} for x in extra_vforms if x['lesson'] == n],
                                         key=lambda r: (es_key(r['lemma']), es_key(r['form']))),
                        'newforms': sorted([x for x in newforms if x['lesson'] == n], key=lambda x: (es_key(x['lemma']), es_key(x['form']))),
                        'seen': seen.get(n, []), 'verbs': verbs, 'phrases': j.get('phrases', [])})
    conjs = {v: conj_table(v) for L in lessons for v in L['verbs']}
    out = {'lessons': lessons, 'conj': conjs}
    (DATA / 'vocab.json').write_text(json.dumps(out, ensure_ascii=False, indent=1), 'utf-8')
    (DATA / 'review.txt').write_text('\n'.join(review) + '\n', 'utf-8')
    nw = sum(len(L['words']) for L in lessons)
    print(f'词条 {nw}（另有只在语音练习出现的 {sum(len(L["phon"]) for L in lessons)}），动词 {sum(len(L["verbs"]) for L in lessons)}，'
          f'动词形式 {sum(len(L["vforms"]) for L in lessons)}；要人工看的 {len(review)} 处')
    print(' '.join(f'{L["lesson"]}:{len(L["words"])}' for L in lessons))


main()
