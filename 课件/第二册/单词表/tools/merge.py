"""把三份归并结果（data/lex_*.tsv）和同形词、新意思的查对结果（data/known_*.tsv）合成第二册按课的单词表：
    python merge.py <第二册课件 content 目录>
第一册的结果由 book1.py 读进来：第一册学过的词不再算新词，第一册见过的动词形式也不再列。
输出 data/vocab.json（每课：新词、动词形式、已学词的新形式、生词表里前面学过的词、生词表里的短语、变位表要列的动词、常用表达；
书后：第一册动词的新时态）和 data/review.txt（要人工看的地方）。动词形式一律用 analyze.py 复核。"""
import json
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import analyze  # noqa: E402
import book1  # noqa: E402
import conj  # noqa: E402

SRC = Path(sys.argv[1])
DATA = Path(__file__).resolve().parent.parent / 'data'
ES_WORD = re.compile(r"[A-Za-zÁÉÍÓÚÑÜáéíóúñü]+")
POS = {'m.', 'f.', 'm., f.', 'm. pl.', 'f. pl.', 'adj.', 'adv.', 'prep.', 'conj.', 'art.', 'pron.', 'num.', 'interj.', 'v.', '地名'}
TRIVIAL = re.compile(r'(阴性|阳性)?(复数|单数)?')


def tidy(p):
    """归并时写成“词汇 el pato asado：烤鸭”的备注，改成和别处一样的“el pato asado 烤鸭”。"""
    return re.sub(r'^词汇 (.+?)：', r'\1 ', p)


GRAMMAR_NOTE = ('复数', '单数', '最高级', '短尾', '缩写', '阴性', '阳性', '序数', '指小', '指大')
ARTICLES = {'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas'}
PREPS = {'a', 'de', 'en', 'con', 'por', 'para', 'al', 'del'}
VOCAB_STOP = ARTICLES | PREPS | {'inf', 'pl', 'y', 'o', 'e', 'se', 'lo', 'le', 'uno'}

# 审读后要改的：形式 → (lemma, pos, zh, note)，None 表示照旧
FIX = {
    # 归并时拿不准（备注里有“？”）的，定下来
    'ido': ('ir', 'v.', None, '过去分词'),                                   # 第 1 课语法要点里是词尾 -ido；第 14 课 ¿Has ido…? 才是 ir 的分词
    'muerto': (None, None, None, '过去分词'),                                # 名词 el muerto 另立一条（EXTRA）
    'oído': (None, None, None, '过去分词'),                                  # 名词 oído（耳朵）另立一条（EXTRA）
    'sentado': ('sentado, sentada', 'adj.', '坐着的', ''),                    # 第 1 课语法要点：sentado 已是常用形容词
    'asustado': ('asustado, asustada', 'adj.', '受惊的，害怕的', ''),
    'mojado': ('mojado, mojada', 'adj.', '湿的', ''),
    'diplomático': (None, None, None, ''),                                   # 照课件生词表：外交官；外交的（和第一册国籍词一样作形容词）
    'deseo': (None, None, None, '陈述式现在时 第一人称单数；第二册新义'),     # 名词 deseo（愿望）另立一条（EXTRA）
    'perra': ('perro', 'm.', None, '阴性 perra：母狗'),                      # 和第二册第 6 课的 perro 合成一条（第一册只在语音练习里）
    'perrito': ('perro', 'm.', None, '指小词'),
    'perrazo': ('perro', 'm.', None, '指大词'),
    'metas': (None, None, None, '虚拟式现在时 第二人称单数；用于否定命令式 no te metas'),   # 原句 No te metas en eso
    'bolsillo': (None, None, None, '由 bolso（包）加 -illo 构成'),
    'tigre': (None, None, None, ''),                                         # 狗的名字“老虎”，和人名一样不收
}
# 第一册只在语音练习里出现过、第二册算新词的，备注（第一册的归并结果里没有）
AUTO_NOTE = {'segundo': '序数词'}
# 词形第一次作这个词用的课（第一次出现时只是语法要点里的词尾等）
FORM_LESSON = {'ido': 14}
# 归并结果里标了“第二册新义”、但新意思另由 EXTRA 列的（haber 作助动词）
NEWSENSE_DROP = {'haber'}
# 同形词、新义查对结果要改的：(词形, 课) → 改的栏目；None 表示删掉这一条
KNOWN_FIX = {
    ('hay', 11): {'zh': '（hay que + 不定式）必须，应该', 'note': '陈述式现在时 第三人称单数'},   # 第一册没有 hay que
    ('uno', 11): {'zh': '（泛指）人，某人', 'note': 'uno a otro（互相）见第 7 课'},          # 第 7 课的 uno a otro 另立一条（EXTRA）
    ('como', 4): {'zh': '作为；像……一样', 'note': '“像……一样”第 6 课起（libros como el mío）'},
    ('como', 6): None,
    ('cuarto', 13): {'note': '序数词'},
    # 意思由本课生词表里的短语给出（de pronto、mientras tanto、cada vez más、alguna vez、llegar a + inf.），不再单列
    ('pronto', 5): None, ('tanto', 7): None, ('vez', 12): None, ('vez', 13): None, ('llegar', 17): None, ('llegó', 17): None,
    # hace + 时间（……以前）第一册第 19 课已学；hace + 时间 + que（已经……了）另由 EXTRA 列
    ('hace', 10): None,
}
# 词条释义、课次要定下来的：(lemma, pos) → (课, 释义)
PIN = {('hombre', 'm.'): (None, '人；男人；人类')}             # 第一册只在语音练习里（男人）；第二册第 5 课起泛指人
# 归并按词形分条，漏掉的词条（同形的另一个词、第二册新义）
EXTRA = [
    # 第 13 课现在完成时：haber 作助动词（第一册只学了无人称的 hay）
    {'lemma': 'haber', 'pos': 'v.', 'zh': '（助动词）和过去分词构成复合时态', 'note': '第一册第 3 课学过无人称用法 hay（有），第 11 课学过 hay que（必须，应该）；第 13 课起作助动词：he comido（现在完成时），第 15 课 había comido（过去完成时）',
     'lesson': 13, 'newsense': True},
    {'lemma': 'muerto, muerta', 'pos': 'm., f.', 'zh': '死人', 'note': 'hacerse el muerto 装死', 'lesson': 5},
    {'lemma': 'oído', 'pos': 'm.', 'zh': '耳朵；听觉', 'note': 'al oído 在耳边', 'lesson': 5},
    {'lemma': 'deseo', 'pos': 'm.', 'zh': '愿望', 'note': '', 'lesson': 9},
    # 以下是两人审读补的（第一册见过同样的词形，按词形比对时漏掉了）
    {'lemma': 'tanto', 'pos': 'adv.', 'zh': '这么；那么（多）', 'note': 'No te quejes tanto. 别老抱怨了；另见第一册第 22 课 tanto, tanta（adj.）这么多的，那么多的', 'lesson': 5},
    {'lemma': 'uno, una', 'pos': 'pron.', 'zh': '（uno a otro）互相', 'note': '随性数变化：una a otra、unos a otros；另见第一册第 6 课 uno（num.）一', 'lesson': 7},
    {'lemma': 'escribirse', 'pos': 'v.', 'zh': '互相写信；通信', 'note': '', 'lesson': 7},
    {'lemma': 'quererse', 'pos': 'v.', 'zh': '相爱', 'note': '', 'lesson': 7},
    {'lemma': 'lo', 'pos': 'art.', 'zh': '（中性冠词，lo + 形容词）……的事，……的东西', 'note': 'lo bueno、lo importante、lo mejor；lo que ……的事情；另见第一册第 8 课 lo（pron.）他；它；您（宾格）', 'lesson': 8},
    {'lemma': 'un', 'pos': 'art.', 'zh': '（unos, unas + 数词）大约', 'note': '第一册第 4 课学过（一（个）），这里是新的意思：unos veinte años 二十岁左右', 'lesson': 8, 'newsense': True},
    {'lemma': 'encontrar', 'pos': 'v.', 'zh': '（encontrar + 宾语 + 形容词）觉得；认为', 'note': '第 4 课学过（找到），这里是新的意思：Encuentro interesante este libro.', 'lesson': 10, 'newsense': True},
    {'lemma': 'dentro', 'pos': 'adv.', 'zh': '（dentro de + 时间）……以后，过……', 'note': '第一册第 18 课学过（在里面；dentro de 在……里面），这里是新的意思：dentro de un par de días 过两天', 'lesson': 14, 'newsense': True},
    {'lemma': 'acabar', 'pos': 'v.', 'zh': '完成；结束', 'note': '第 3 课学过（acabar de + inf. 刚刚），这里是新的意思', 'lesson': 15, 'newsense': True},
    {'lemma': 'decidirse', 'pos': 'v.', 'zh': '（～ a + inf.）下决心', 'note': '', 'lesson': 16},
    {'lemma': 'éste', 'pos': 'pron.', 'zh': '后者', 'note': '第一册第 5 课学过（这个），这里是新的意思；和 aquél（前者）对用', 'lesson': 17, 'newsense': True},
    # 第二轮审读补的
    {'lemma': 'bueno, buena', 'pos': 'adj.', 'zh': '（estar）身体好的；（食物）好吃的', 'note': '第一册第 3 课学过（好的），这里是新的意思', 'lesson': 2, 'newsense': True},
    {'lemma': 'mejor', 'pos': 'adv.', 'zh': '更好地；最好', 'note': 'Mejor no. 最好别打（电话）；另见第一册第 16 课 mejor（adj.）更好的', 'lesson': 3},
    {'lemma': 'ni', 'pos': 'conj.', 'zh': '（加强否定）连……都（不）', 'note': '第一册第 15 课学过（也不），这里是新的意思：no sé ni cómo volver a casa 我连怎么回家都不知道',
     'lesson': 6, 'newsense': True},
    {'lemma': 'hacer', 'pos': 'v.', 'zh': '（hace + 时间 + que + 现在时）已经（多长时间）了',
     'note': '第一册第 7 课学过（做；干），第一册第 19 课学过 hace + 时间（……以前）；这里是新的意思：Hace tres años que vivo en Pekín. ＝ Llevo tres años viviendo en Pekín.',
     'lesson': 10, 'newsense': True},
    {'lemma': 'conseguir', 'pos': 'v.', 'zh': '（～ + inf.）经过努力做到；（～ que + 虚拟式）使得', 'note': '第 5 课学过（得到；获得），这里是新的意思',
     'lesson': 17, 'newsense': True},
]
# 已学词本课的新用法（不在归并结果里的）
NEWFORM_EXTRA = [{'form': 'mal', 'lemma': 'malo, mala', 'pos': 'adj.', 'note': 'malo 的短尾，用在阳性单数名词前（un mal día）', 'lesson': 6, 'where': '第一册第 16 课'}]
# 变位表下面加的说明
CONJ_NOTE = {'bastar': '常用第三人称：basta、bastan（Basta con eso. 这就够了）',
             'reír': 'rio、riais 按现行正字法不写重音（老版课本写 rió、riáis）', 'reírse': 'se rio、os riais 按现行正字法不写重音（老版课本写 rió、riáis）'}
# 审读后定下来的词条栏目：(lemma, pos, 课) → {栏目: 值}（最后套用，盖过程序生成的）
ENTRY_PIN = {
    ('carácter', 'm.', 13): {'note': '复数 caracteres（重音后移）'},          # el carácter chino 已在本课“生词表里的短语”
    ('muralla', 'f.', 13): {'note': ''}, ('pato', 'm.', 13): {'note': ''}, ('prestación', 'f.', 14): {'note': ''},
    ('cualquiera', 'adj.；pron.', 11): {'note': '用在名词前变为短尾 cualquier（cualquier día、cualquier cosa）'},
    ('acabar', 'v.', 3): {'zh': '（～ de + inf.）刚刚（做完某事）'},
    ('oír', 'v.', 4): {'zh': '（命令式 oye）喂，听我说（招呼用语）'},
    ('olvidarse', 'v.', 4): {'zh': '（～ de）忘记', 'note': 'olvidar algo ＝ olvidarse de algo'},
    ('mismo, misma', 'adj.', 4): {'zh': '同样的；（强调）自己，本身', 'note': '第一册第 1 课语音练习里出现过；“自己，本身”第 5 课起（sí mismo）'},
    ('meter', 'v.', 7): {'zh': '放进；装进'},
    ('meterse', 'v.', 7): {'zh': '（～ en）进入；介入；干预'},              # 第 16 课 se metieron dentro 也是“进入”
    ('interesar', 'v.', 8): {'zh': '使感兴趣'},
    ('decidir', 'v.', 12): {'zh': '决定'},                                  # 下决心是第 16 课的 decidirse
    ('chino', 'm.', 13): {'core': False},                                   # 生词表里是 el carácter chino（形容词）
    ('cuarto, cuarta', 'adj.', 13): {'core': False},                        # 生词表里是 compañero de cuarto（房间）
    ('tratar', 'v.', 13): {'zh': '（～ de + inf.）设法；尽力（做）'},
    ('voluntario, voluntaria', 'm., f.', 14): {'pos': 'm., f.；adj.'},
    ('ocurrirse', 'v.', 15): {'note': '只用第三人称，人用间接宾语代词表示：se me ocurre una idea 我想到一个主意'},
    ('dirigir', 'v.', 16): {'zh': '领导；指挥'}, ('retirar', 'v.', 16): {'zh': '撤走；收回'}, ('esconder', 'v.', 16): {'zh': '藏；隐藏'},
    ('tomar', 'v.', 16): {'core': True},                                    # 生词表 tomar… por…
    ('reina', 'f.', 17): {'zh': '女王；王后'},                               # la reina Isabel 是在位女王
    ('español, española', 'adj.', 18): {'zh': '西班牙人；西班牙的'},             # 国籍词的写法同第一册
    # 第二轮审读
    ('tomar', 'v.', 1): {'note': '第一册第 9 课学过（喝；吃），这里是新的意思；“拿，取”第 9 课起（Toma… 给你）'},
    ('guardar', 'v.', 3): {'zh': '保存；收好', 'note': '“保守”第 9 课起（guardar un secreto 保守秘密）'},
    ('inyección', 'f.', 1): {'note': 'poner una inyección 打针'},
    ('maleta', 'f.', 7): {'note': 'hacer la maleta 收拾行李'},
}
# 本课第一次作这个动词用的形式（词形前面已作别的词出现过）：(课, 形式, 原形, 说明)；说明的第一段要和 analyze.py 算的对上
VFORM_EXTRA = [
    (3, 'cena', 'cenar', '陈述式现在时 第三人称单数；无人称 se cena（人们吃晚饭）；和名词 cena 同形'),
    (5, 'fue', 'irse', '简单过去时 第三人称单数；se fue 走了；和 ser 的 fue 同形'),
    (10, 'sientan', 'sentirse', '虚拟式现在时 第三人称复数；第一册的 sientan 是 sentarse（坐下）'),
    (12, 'nieve', 'nevar', '虚拟式现在时 第三人称单数；Es posible que nieve；和名词 nieve（雪）同形'),
    (13, 'dura', 'durar', '陈述式现在时 第三人称单数；和形容词 dura 同形'),
    (15, 'había', 'haber', '过去未完成时 第一/第三人称单数；助动词，构成过去完成时'),
    (16, 'fueron', 'ser', '简单过去时 第三人称复数；用于被动语态 ser + 过去分词（fueron destruidos）；和 ir 的 fueron 同形'),
    (17, 'querido', 'querer', '过去分词；ha querido saber；和形容词 querido（亲爱的）同形'),
    # 第二轮审读：前面的课按另一个动词列过的（decidir / decidirse 等）
    (10, 'considero', 'considerar', '陈述式现在时 第一人称单数；Lo considero un amigo 我把他当作朋友；第 3 课的 considero 是 considerarse'),
    (14, 'llamo', 'llamar', '陈述式现在时 第一人称单数；te llamo 给你打电话；第 11 课的 llamo 是 llamarse'),
    (16, 'decidió', 'decidirse', '简单过去时 第三人称单数；se decidió a hablar 下决心去谈；第 12 课的 decidió 是 decidir'),
    (18, 'preparando', 'prepararse', '副动词；Nos estamos preparando 我们正在准备；第 12 课的 preparando 是 preparar'),
]
# 相互动词（“互相……”只用复数）。基本动词前面有变位表的，不另出表
RECIPROCAL = {'abrazarse', 'felicitarse', 'mirarse', 'saludarse', 'ayudarse', 'verse', 'escribirse', 'quererse', 'llamarse'}
# 只是重读的 i、u 加重音的（prohíbo、reúno），不算不规则
ACC_PRES = {'prohibir': 'i→í', 'reunir': 'u→ú'}
# 生词表里前面已出现的条目，“第一次出现”要特别说明的：(课, 条目) → 说明
SEEN_WHERE = {(6, 'malo, la'): '第一册第 16 课（坏的）；“（estar）病了”第 2 课',
              (6, 'bueno, na'): '第一册第 3 课（好的）；“（estar）身体好、好吃”第 2 课',
              (16, 'luchar'): '第 12 课（奋斗；斗争）；“战斗”本课第一次出现',
              (18, 'la sala'): '第一册第 3 课（客厅）；“大厅；房间”本课第一次出现'}
# 生词表里 X(se) 拆开的那一半前面学过的：释义用课件释义里属于这一半的部分（poner(se)〈放；穿上；变得〉→ poner 放）
SEEN_ZH = {(1, 'poner'): '放', (1, 'quitarse'): '脱下', (1, 'irse'): '离开，走掉', (7, 'saludar'): '打招呼', (18, 'preparar'): '准备'}
DROP_NOTES = set()
# 新动词变位表里额外加的动词：(动词, 课)。haber 第 13 课起作助动词，各人称都用
EXTRA_VERBS = [('haber', 13)]


def read_tsv(f, head):
    lines = f.read_text('utf-8').rstrip('\n').split('\n')
    assert lines[0] == head, (f, lines[0])
    out = []
    for ln in lines[1:]:
        b = ln.split('\t')
        n = head.count('\t') + 1
        assert len(b) in (n - 1, n), (f.name, b)     # Write 工具会去掉行尾的制表符：备注空的行少一栏
        out.append([x.strip() for x in (b + [''])[:n]])
    return out


def read_lex():
    rows = {}
    for f in sorted(DATA.glob('lex_L*.tsv')):
        src_forms = [e['form'] for e in json.loads((DATA / f.name.replace('lex_', 'forms_').replace('.tsv', '.json')).read_text('utf-8'))]
        body = read_tsv(f, 'form\tlemma\tpos\tzh\tnote')
        assert [b[0] for b in body] == src_forms, f'{f.name} 词形顺序和输入不一样'
        for b in body:
            rows[b[0]] = dict(zip(('form', 'lemma', 'pos', 'zh', 'note'), b))
    return rows


def read_known():
    out = []
    for f in sorted(DATA.glob('known_L*.tsv')):
        for b in read_tsv(f, 'form\tlesson\tlemma\tpos\tzh\tnote'):
            r = dict(zip(('form', 'lesson', 'lemma', 'pos', 'zh', 'note'), b))
            r['lesson'] = int(r['lesson'])
            segs = top_split(r['note'])
            assert segs[0] in ('同形词', '第二册新义'), (f.name, r)
            r['kind'] = segs[0]
            r['note'] = '；'.join(s for s in segs[1:] if s)
            out.append(r)
    return out


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
    c = c.replace('代词 ', '').replace('现在分词', '副动词')
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
    return out


def join_analyses(xs, pool=None):
    """过去未完成时、简单条件式、虚拟式现在时的第一、第三人称单数同形，写成一条（pool：analyze() 算出的全部可能；
    无人称动词只有第三人称，llueva 不写成“第一/第三”）。"""
    xs = list(dict.fromkeys(xs))
    pool = xs if pool is None else pool
    for t in ('过去未完成时', '简单条件式', '虚拟式现在时'):
        a, b = f'{t} 第一人称单数', f'{t} 第三人称单数'
        if (a in xs or b in xs) and a in pool and b in pool:
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
        tags += ['e→ie', 'e→i'] if core.endswith(('ir', 'ír')) else ['e→ie']      # divertir：divierto，divirtió
    elif core in conj.O_UE:
        tags += ['o→ue', 'o→u'] if core.endswith('ir') else ['o→ue']             # dormir：duermo，durmió
    elif core in conj.E_I:
        tags.append('e→i')
    elif core in conj.U_UE:
        tags.append('u→ue')
    conj.auto_irregular(core)
    if core in ACC_PRES:
        tags.append(ACC_PRES[core])
    elif core in conj.ACC_IAR:
        tags.append('i→í')
    elif core.endswith('uar') and core not in conj.NO_ACC_UAR:
        tags.append('u→ú')
    stem_changed = any(t in tags for t in ('e→ie', 'o→ue', 'e→i', 'u→ue'))
    beyond = any(core in s for s in (conj.YO, conj.PRES, conj.STRONG, conj.PRET, conj.IMPF, conj.TU, conj.FUT))
    if (beyond or (not conj.regular(lemma) and not stem_changed)) and not any(t in tags for t in ('i→í', 'u→ú')):
        tags.append('不规则')
    if lemma in RECIPROCAL:
        tags = ['相互动词' if t == '自复动词' else t for t in tags]
    return tags


def irregular_part(lemma):
    """不规则（含加重音）的过去分词：cubrir → cubierto，leer → leído；规则的返回空串。"""
    refl = lemma.endswith('se') and lemma[:-2].endswith(('ar', 'er', 'ir', 'ír'))
    inf = lemma[:-2] if refl else lemma
    part = conj.base_conj(inf)['part']
    return '' if part == inf[:-2] + ('ado' if inf.endswith('ar') else 'ido') else part


ENDS = {'ar': ('o as a amos áis an', 'é aste ó amos asteis aron', 'aba abas aba ábamos abais aban', 'e es e emos éis en', 'a e emos ad en', 'ando ado'),
        'er': ('o es e emos éis en', 'í iste ió imos isteis ieron', 'ía ías ía íamos íais ían', 'a as a amos áis an', 'e a amos ed an', 'iendo ido'),
        'ir': ('o es e imos ís en', 'í iste ió imos isteis ieron', 'ía ías ía íamos íais ían', 'a as a amos áis an', 'e a amos id an', 'iendo ido')}
IMP_P = ('tú', 'usted', 'nosotros', 'vosotros', 'ustedes')


def conj_table(lemma, aux=False):
    """变位表：6 个人称 × 陈述式现在时、简单过去时、过去未完成时、将来未完成时、简单条件式（上表），虚拟式现在时、肯定命令式、否定命令式（下表）；
    和规则变位不一样的格子标 irr（看不带自复代词的形式）。"""
    r = conj.conjugate(lemma, aux=aux)
    refl = r['reflexive']
    inf = lemma[:-2] if refl else lemma
    base = conj.base_conj(inf)
    stem, cl = inf[:-2], inf[-2:].replace('í', 'i')
    finf = inf[:-2] + 'ir' if inf.endswith('ír') else inf
    pres, pret, impf, subj, imp, gp = (x.split() for x in ENDS[cl])
    plain = {'pres': [stem + e for e in pres], 'pret': [stem + e for e in pret], 'impf': [stem + e for e in impf],
             'fut': [conj.nfc(finf + e) for e in conj.FUT_END], 'cond': [conj.nfc(finf + e) for e in conj.COND_END],
             'subj': [stem + e for e in subj], 'imp': dict(zip(IMP_P, (stem + e for e in imp))), 'ger': stem + gp[0], 'part': stem + gp[1]}
    plain['neg'] = dict(zip(IMP_P, (plain['subj'][i] for i in (1, 2, 3, 4, 5))))
    bneg = dict(zip(IMP_P, (base['subj'][i] for i in (1, 2, 3, 4, 5))))

    def imp_irr(pp):
        return base['imp'][pp] != plain['imp'][pp] or (refl and inf == 'ir' and pp == 'vosotros')

    top, bottom = [], []
    for i in range(6):
        row = []
        for k in ('pres', 'pret', 'impf', 'fut', 'cond'):
            shown = r[k][i]
            # 无人称的 hay：显示的 hay 和 base 的 ha 不一样，也标出来
            row.append({'f': shown, 'irr': shown != '—' and (base[k][i] != plain[k][i] or (not refl and shown != base[k][i]))})
        top.append(row)
        shown = r['subj'][i]
        row2 = [{'f': shown, 'irr': shown != '—' and base['subj'][i] != plain['subj'][i]}]
        if i == 0:
            row2 += [{'f': '—', 'irr': False}, {'f': '—', 'irr': False}]
        else:
            pp = IMP_P[i - 1]
            s1, s2 = r['imp'][pp], r['neg'][pp]
            row2.append({'f': s1, 'irr': s1 != '—' and imp_irr(pp)})
            row2.append({'f': s2, 'irr': s2 != '—' and bneg[pp] != plain['neg'][pp]})
        bottom.append(row2)
    return {'top': top, 'bottom': bottom, 'ger': {'f': r['ger'], 'irr': r['ger'] != plain['ger']},
            'part': {'f': r['part'], 'irr': r['part'] != plain['part']}, 'notes': r['notes'], 'reflexive': refl, 'aux': aux}


def book1_new_tenses():
    """书后速查表：第一册的每个动词，第二册新学的时态（将来未完成时 yo、简单条件式 yo、虚拟式现在时 yo 和 nosotros、过去分词）。
    只用第三人称单数的（llover、无人称的 haber）给第三人称单数。"""
    rows = []
    for v in sorted(book1.CONJ, key=es_key):
        e = next(x for L in book1.LESSONS for x in L['words'] if x['lemma'] == v and 'v.' in x['pos'].split('；'))
        t = conj_table(v)
        third = t['top'][0][3]['f'] == '—' and t['top'][2][3]['f'] != '—'
        k = 2 if third else 0
        rows.append({'verb': v, 'zh': e['zh'], 'lesson': e['lesson'], 'vtype': verb_type(v), 'third': third,
                     'fut': t['top'][k][3], 'cond': t['top'][k][4], 'subj1': t['bottom'][k][0], 'subj4': t['bottom'][3][0],
                     'part': t['part'], 'notes': t['notes']})
    return rows


def senses(zh):
    return {re.sub(r'（[^）]*）|\([^)]*\)', '', s).strip() for s in re.split(r'[，；、]', zh) if s.strip()}


def main():
    rows = read_lex()
    known = read_known()
    forms = json.loads((DATA / 'forms.json').read_text('utf-8'))
    sent = json.loads((DATA / 'sentences.json').read_text('utf-8'))
    review = []
    b1_heads = defaultdict(list)                      # 第一册词条按原形第一个词（同形的另一个词性提示用）
    for (l, p), e in book1.ENTRY.items():
        if not e['phon_only']:
            b1_heads[l.split(',')[0].strip().lower()].append((l, p, e))

    # 每个新词形：归并结果 + 课次
    items = []
    for e in forms:
        f = e['form']
        if e['b1']:
            # 第一册见过、但只在语音练习里出现过的词：第二册用到就算新词（归到第一册那一条）
            maps = book1.FORM.get(f, [])
            homo = any(r['form'] == f and r['kind'] == '同形词' for r in known)    # 查对时认定是另一个词的（lima → 地名 Lima）
            if maps and not homo and not any(book1.learned(l, p) for l, p, z in maps):
                for l, p, z in maps:
                    note = AUTO_NOTE.get(f, '不定式' if p == 'v.' and f == l else '')
                    items.append({'form': f, 'lemma': l, 'pos': p, 'zh': z, 'note': note, 'lesson': e['lesson'], 'count': e['count'], 'kind': None})
                review.append(f'第一册只在语音练习里出现过，算新词：{f} → ' + '；'.join(f'{l}（{p}）{z}' for l, p, z in maps) + f'，第 {e["lesson"]} 课')
            continue
        r = dict(rows[f])
        if f in FIX:
            for k, v in zip(('lemma', 'pos', 'zh', 'note'), FIX[f]):
                if v is not None:
                    r[k] = v
            r['fixed_note'] = FIX[f][3] is not None
        if r['lemma'] in NEWSENSE_DROP:
            r['note'] = '；'.join(s for s in top_split(r['note']) if s != '第二册新义')
        if '？' in r['note'] or '?' in r['note']:
            review.append(f'备注里还有问号：{f}\t{r["note"]}')
        if r['lemma'] in ('#跳过', '#人名'):
            continue
        assert r['pos'] in POS, (f, r['pos'])
        assert r['zh'], f
        r.update(lesson=FORM_LESSON.get(f, e['lesson']), count=e['count'], kind=None)
        items.append(r)
    used_kfix = set()
    for r in known:
        k = (r['form'], r['lesson'])
        if k in KNOWN_FIX:
            used_kfix.add(k)
            if KNOWN_FIX[k] is None:
                continue
            r.update(KNOWN_FIX[k])
        if '？' in r['note'] or '?' in r['note']:
            review.append(f'同形词、新义查对的备注里还有问号：{r["form"]} 第 {r["lesson"]} 课\t{r["note"]}')
    known = [r for r in known if KNOWN_FIX.get((r['form'], r['lesson']), 1) is not None]
    assert used_kfix == set(KNOWN_FIX), set(KNOWN_FIX) - used_kfix
    for r in known:
        assert r['pos'] in POS, r
        if not any(re.search(rf'(?<![\wáéíóúñü]){re.escape(r["form"])}(?![\wáéíóúñü])', u['es'], re.I)
                   for L in sent if L['lesson'] == r['lesson'] for u in L['units']):
            review.append(f'同形词、新义查对：第 {r["lesson"]} 课里没有 {r["form"]}')
        items.append(dict(r, count=0))

    # 动词形式复核
    for r in items:
        if r['pos'] != 'v.':
            continue
        lemma = r['lemma']
        an = analyze.analyze(r['form'], lemma)
        claim = claim_of(r['note'])
        if not an:
            review.append(f'变位程序认不出：{r["form"]} ← {lemma}\t{r["note"]}')
            r['analysis'] = claim
        else:
            ok = matches(claim, an)
            if ok:
                r['analysis'] = join_analyses(ok, an)
            else:
                r['analysis'] = join_analyses(an)
                review.append(f'形式说明对不上：{r["form"]} ← {lemma}\t归并写的「{claim}」，程序算的「{"；".join(an)}」')
        segs = top_split(r['note'])
        rest = [p for p in segs[1:] if p and '同形' not in p and p != '第二册新义']
        m = re.search(r'（(.*)）', segs[0])
        hints = [h if '+' in h else '连写代词 ' + h for h in (m.group(1).split('；') if m else []) if re.search(r'\s→\s|^→\s', h)]
        r['usage'] = '；'.join(hints + rest)

    # 归并结果和第一册词条对一下：原形写法差一点的（amigo ↔ amigo, amiga）
    for r in items:
        if book1.ENTRY.get((r['lemma'], r['pos'])):
            continue
        for l, p, e in b1_heads.get(r['lemma'].split(',')[0].strip().lower(), []):
            if p == r['pos'] and l != r['lemma']:
                review.append(f'原形和第一册写法不一样：{r["form"]} → {r["lemma"]}（{r["pos"]}），第一册是 {l}')

    # 词条：同一个 lemma + 词性 合成一条
    ent = defaultdict(list)
    for r in items:
        ent[(r['lemma'], r['pos'])].append(r)
    entries, newforms = [], []
    for (lemma, pos), rs in ent.items():
        head = lemma.split(',')[0].strip().lower()
        b1e = book1.ENTRY.get((lemma, pos))
        if b1e and not b1e['phon_only']:
            # 第一册学过的词：新意思单列一条；别的形式进“动词形式”或“已学词的新形式”
            ns = [r for r in rs if r.get('kind') == '第二册新义' or '第二册新义' in top_split(r['note'])]
            listed = set(senses(b1e['zh']))
            for n0 in sorted({r['lesson'] for r in ns}):           # 每课只列这一课新出现的意思（tomar 第 1 课“拿，取”，第 16 课“把……当成”）
                zs = []
                for r in sorted(ns, key=lambda r: r['form'] != head):
                    if r['lesson'] != n0:
                        continue
                    for part in top_split(r['zh']):            # 只取第一册和前面的课里没有的意思
                        if part.strip() and not senses(part) <= listed:
                            zs.append(part.strip())
                            listed |= senses(part)
                if not zs:
                    continue
                entries.append({'lemma': lemma, 'pos': pos, 'zh': '；'.join(zs), 'note': f'第一册第 {b1e["lesson"]} 课学过（{b1e["zh"]}），这里是新的意思',
                                'lesson': n0, 'core': False, 'vtype': [], 'forms': sorted({r['form'] for r in ns if r['lesson'] == n0}),
                                'newsense': True})
            if pos != 'v.':
                for r in rs:
                    if any(r is x for x in ns):
                        continue
                    segs = [p.strip() for p in r['note'].split('；')]
                    segs = [p for p in segs if p and not TRIVIAL.fullmatch(p) and p not in DROP_NOTES and p not in ('第二册新义', '序数词')]
                    if segs:
                        newforms.append({'form': r['form'], 'lemma': lemma, 'pos': pos, 'note': '；'.join(segs), 'lesson': r['lesson'],
                                         'where': f'第一册第 {b1e["lesson"]} 课'})
            continue
        lesson = min(r['lesson'] for r in rs)
        if (lemma, pos) in PIN and PIN[(lemma, pos)][0]:
            lesson = PIN[(lemma, pos)][0]
        best =sorted(rs, key=lambda r: (r['form'] != head, r['lesson']))[0]
        notes = []
        if b1e and b1e['phon_only']:
            notes.append(f'第一册第 {b1e["phon"]} 课语音练习里出现过')
        for r in sorted(rs, key=lambda r: (r['form'] != head, r['lesson'])):
            if pos == 'v.':
                continue
            segs = [p.strip() for p in r['note'].split('；')]
            segs = [tidy(p) for p in segs if p and not TRIVIAL.fullmatch(p) and p not in DROP_NOTES and p not in ('同形词', '第二册新义')]
            assert not any('？' in p for p in segs), r
            tagged = segs
            if r['form'] != head:
                segs = [p for p in segs if not any(p in n or (r['form'] in n and any(k in p for k in GRAMMAR_NOTE)) for n in notes)]
                tagged = [f'{r["form"]}：{p}' if any(k in p for k in GRAMMAR_NOTE) and not p.startswith('缩写') and r['form'] not in p
                          and not r.get('fixed_note') else p for p in segs]
            if r['form'] == head or r['lesson'] == lesson:
                notes += [p for p in tagged if p not in notes]
            elif segs:
                newforms.append({'form': r['form'], 'lemma': lemma, 'pos': pos, 'note': '；'.join(segs), 'lesson': r['lesson'], 'where': f'第 {lesson} 课'})
        # 同一个原形第一册学过另一个词性的，提一句（sobre 前置词 ↔ el sobre 信封）
        for l, p, e in b1_heads.get(head, []):
            if p != pos:
                notes = [x for x in notes if not x.startswith('第一册的 ')]   # 归并时写的“第一册的 X 是……”，和下面这句重复
                notes.append(f'另见第一册第 {e["lesson"]} 课 {l}（{p}）{e["zh"]}')
        zh = PIN[(lemma, pos)][1] if (lemma, pos) in PIN else best['zh']
        if pos == 'v.':
            zh = zh.replace('，', '；')
        if pos == 'v.' and irregular_part(lemma):
            notes.append(f'过去分词 {irregular_part(lemma)}')
        entries.append({'lemma': lemma, 'pos': pos, 'zh': zh, 'note': '；'.join(notes), 'lesson': lesson, 'core': False,
                        'vtype': verb_type(lemma) if pos == 'v.' else [], 'forms': sorted({r['form'] for r in rs}), 'newsense': False,
                        'phon': bool(b1e and b1e['phon_only']), 'pinned_zh': (lemma, pos) in PIN})

    for x in EXTRA:
        dup = [e for e in entries if e['lemma'] == x['lemma'] and e['pos'] == x['pos'] and e['lesson'] == x['lesson']]
        if dup:
            review.append(f'EXTRA 和归并结果重复，用 EXTRA：{x["lemma"]}（{x["pos"]}）第 {x["lesson"]} 课')
            entries = [e for e in entries if not any(e is d for d in dup)]
        e = dict({'core': False, 'vtype': [], 'forms': [x['lemma']], 'newsense': False}, **x)
        if e['pos'] == 'v.' and not e['newsense']:
            e['vtype'] = verb_type(e['lemma'])
            if irregular_part(e['lemma']):
                e['note'] = '；'.join(filter(None, [e['note'], f'过去分词 {irregular_part(e["lemma"])}']))
        entries.append(e)
    newforms += NEWFORM_EXTRA

    # 同一 lemma 在同一课有两个词性的，合成一行
    by = defaultdict(list)
    for e in entries:
        by[(e['lemma'], e['lesson'])].append(e)
    merged = []
    for k, es in by.items():
        if len(es) == 1:
            merged.append(es[0])
            continue
        es.sort(key=lambda e: e['pos'])
        m = dict(es[0])
        m['pos'] = '；'.join(e['pos'] for e in es)
        m['zh'] = '；'.join(dict.fromkeys(z for e in es for z in e['zh'].split('；')))
        m['note'] = '；'.join(dict.fromkeys(e['note'] for e in es if e['note']))
        m['forms'] = sorted({f for e in es for f in e['forms']})
        m['vtype'] = next((e['vtype'] for e in es if e['vtype']), [])
        m['newsense'] = all(e['newsense'] for e in es)
        merged.append(m)
        review.append(f'同课两个词性，合成一行：{m["lemma"]}（{m["pos"]}）{m["zh"]}')
    entries = merged
    for e in entries:
        head = e['lemma'].split(',')[0].strip().lower()
        for o in entries:
            see = f'另见第 {o["lesson"]} 课 {o["lemma"]}（{o["pos"]}）{o["zh"]}'
            if (o['lesson'] < e['lesson'] and o['pos'] != e['pos'] and o['lemma'].split(',')[0].strip().lower() == head
                    and see not in e['note'] and not e.get('newsense')):
                e['note'] = '；'.join(filter(None, [e['note'], see]))
    # 相互动词：只用复数；基本动词前面有变位表的不另出表
    b2_verbs = {e['lemma']: e['lesson'] for e in entries if e['pos'] == 'v.' and not e['newsense']}
    for e in entries:
        if e['lemma'] in RECIPROCAL and e['pos'] == 'v.' and not e['newsense']:
            base = e['lemma'][:-2]
            pres = conj.conjugate(e['lemma'])['pres']
            if base in book1.CONJ:
                where = f'第一册第 {book1.ENTRY[(base, "v.")]["lesson"]} 课 {base}'
            elif base in b2_verbs and b2_verbs[base] <= e['lesson']:
                where = f'{"本课" if b2_verbs[base] == e["lesson"] else f"第 {b2_verbs[base]} 课"} {base}'
            else:
                where = ''
            e['no_table'] = bool(where)
            e['note'] = '；'.join(filter(None, [f'只用复数：{pres[3]}、{pres[4]}、{pres[5]}' + (f'；变位同{where}' if where else ''), e['note']]))
        elif e['lemma'] in RECIPROCAL:
            e['note'] = '；'.join(filter(None, [e['note'], '相互动词，只用复数']))

    # 课件各课生词表：短语单列；单个词对到词条，本课新词加粗，前面学过的（第一册或第二册前面的课）单列一张表
    lem_idx, form_idx = defaultdict(list), defaultdict(list)
    for e in entries:
        for l in dict.fromkeys([e['lemma'].lower(), e['lemma'].split(',')[0].strip().lower()]):
            lem_idx[l].append(e)
        for f in e['forms']:
            form_idx[f].append(e)
    b1_lem = defaultdict(list)
    for (l, p), e in book1.ENTRY.items():
        if not e['phon_only']:
            for k in dict.fromkeys([l.lower(), l.split(',')[0].strip().lower()]):
                b1_lem[k].append({'lemma': l, 'pos': p, 'zh': e['zh'], 'lesson': e['lesson']})

    def b1_form(x):
        return [{'lemma': l, 'pos': p, 'zh': z, 'lesson': book1.ENTRY[(l, p)]['lesson']}
                for l, p, z in book1.FORM.get(x, []) if book1.learned(l, p)]

    def expand_fem(s):
        """课件生词表的简写 mexicano, na → mexicano, mexicana"""
        m = re.fullmatch(r'(\w+o), (\w+a)', s)
        if m and len(m[2]) < len(m[1]) and m[1][-len(m[2]):-1] == m[2][:-1] and not m[1].startswith(m[2][:-1] + 'o'):
            return f'{m[1]}, {m[1][:-len(m[2])]}{m[2]}'
        return s

    def norm_item(s):
        s = re.sub(r'[¿?¡!]', '', re.sub(r'\([^)]*\)', '', s))
        s = re.sub(r'^(el|la)\s*/\s*(el|la)\s+', '', s.strip())
        return ', '.join(re.sub(r'^(el|la|los|las)\s+', '', x.strip()) for x in s.split(',')).strip().lower()

    def content_tokens(part):
        p = re.sub(r'\([^)]*\)', '', part)
        return [x.lower() for x in ES_WORD.findall(p) if x.lower() not in VOCAB_STOP]

    def is_phrase(part):
        if '…' in part or '+' in part:
            return True
        p = re.sub(r'\([^)]*\)', '', part).strip()
        for cp in p.split(','):
            toks = [x.lower() for x in ES_WORD.findall(cp) if x.lower() not in ARTICLES]
            if not toks:
                continue
            if len([x for x in toks if x not in VOCAB_STOP]) >= 2:
                return True
            # 名词、副词 + 前置词（junto a）是短语；动词 + 前置词（ocuparse de）不是
            if toks[-1] in PREPS and len(toks) >= 2 and not re.search(r'(ar|er|ir|ír)(se)?$', toks[0]):
                return True
            if toks[0] in PREPS and len(toks) >= 2:                 # de pronto、con frecuencia
                return True
        return False

    used_pin = set()
    for e in entries:
        k = (e['lemma'], e['pos'], e['lesson'])
        if k in ENTRY_PIN:
            used_pin.add(k)
            e['pos0'] = e['pos']
            e.update({f: v for f, v in ENTRY_PIN[k].items() if f != 'core'})
            if 'zh' in ENTRY_PIN[k]:
                e['pinned_zh'] = True
    assert used_pin == set(ENTRY_PIN), set(ENTRY_PIN) - used_pin
    # 第一册学过、第二册又有新意思的：前面的课已经补过的新意思也写上（pasar 第 1 课“发生”，第 16 课“度过”）
    for e in entries:
        m = re.fullmatch(r'(第一册第 \d+ 课学过（.*?）)(，这里是新的意思.*)', e['note'])
        if not (e['newsense'] and m):
            continue
        prev = sorted((o for o in entries if o['newsense'] and o['lemma'] == e['lemma'] and o['pos'] == e['pos'] and o['lesson'] < e['lesson']),
                      key=lambda o: o['lesson'])
        if prev:
            e['note'] = m.group(1) + ''.join(f'、第 {o["lesson"]} 课学过（{o["zh"]}）' for o in prev) + m.group(2)
    seen, vphrases = defaultdict(list), defaultdict(list)
    used_seen_zh = set()

    def place(n, part, gloss, hit, hb1, split=False):
        """一条生词表条目对到的词条：本课新的加粗；前面学过的列进“生词表里前面学过的词”。
        split：poner(se) 这种拆开的一半，释义用那一条自己的（课件释义是两个词合写的）。"""
        hit = list({id(e): e for e in hit}.values())
        hb1 = list({(e['lemma'], e['pos']): e for e in hb1}.values())
        if re.match(r'(el|la|los|las) ', part):          # 带冠词的是名词
            hit = [e for e in hit if any(p.startswith(('m.', 'f.')) for p in e['pos'].split('；'))] or hit
            hb1 = [e for e in hb1 if e['pos'].startswith(('m.', 'f.'))] or hb1
        if not hit and not hb1:
            if not split:
                review.append(f'生词表条目找不到词条：第 {n} 课 {part}')
            return
        new = [e for e in hit if e['lesson'] == n]
        for e in new:
            e['core'] = True
            # 第一册只在语音练习里出现过的词：释义用本课课件生词表的（ruido 噪音，响声）
            if e.get('phon') and not e.get('pinned_zh') and not split and len(new) == 1:
                e['zh'] = gloss.replace('，', '；') if e['pos'] == 'v.' else gloss
        if new:
            return
        later = [e for e in hit if e['lesson'] > n]
        earlier = [e for e in hit if e['lesson'] < n]
        if later and not hb1 and not earlier:
            review.append(f'生词表条目的词排在后面的课：第 {n} 课 {part} → ' + '、'.join(f'{e["lemma"]} 第 {e["lesson"]} 课' for e in later))
            return
        earlier = [e for e in hit if e['lesson'] < n]
        if not earlier and not split and not any(senses(gloss) & senses(e['zh']) for e in hb1):
            review.append(f'生词表释义和第一册不一样：第 {n} 课 {part}「{gloss}」，第一册 ' +
                          '；'.join(f'{e["lemma"]}（{e["pos"]}）「{e["zh"]}」' for e in hb1))
        both = bool(earlier and hb1)                      # 第一册学过、第二册前面的课又有了新意思（malo、listo）：各注意思
        name = len(earlier) + len(hb1) > 1 and not both
        where = '、'.join(dict.fromkeys(
            [(f'{e["lemma"].split(",")[0]} ' if name else '') + f'第一册第 {e["lesson"]} 课' + (f'（{e["zh"]}）' if both else '') for e in hb1] +
            [(f'{e["lemma"].split(",")[0]} ' if name else '') + f'第 {e["lesson"]} 课' + (f'（{e["zh"]}）' if both else '') for e in earlier]))
        where = SEEN_WHERE.get((n, part), where)
        zh = '；'.join(dict.fromkeys(e['zh'] for e in hb1 + earlier)) if split else gloss
        if (n, part) in SEEN_ZH:
            used_seen_zh.add((n, part))
            zh = SEEN_ZH[(n, part)]
        seen[n].append({'item': expand_fem(part), 'zh': zh, 'where': where})

    def look(cs):
        return [e for c in cs for e in lem_idx.get(c, [])], [e for c in cs for e in b1_lem.get(c, [])]

    for f in sorted(SRC.glob('L*.json')):
        j = json.loads(f.read_text('utf-8'))
        n = j['lesson']
        for txt, gloss in j['vocab']:
            parts = [p.strip() for p in txt.split(';') if p.strip()]
            for part in parts:
                if is_phrase(part):
                    vphrases[n].append({'es': part, 'zh': gloss})
                    for x in content_tokens(part):
                        for e in form_idx.get(x, []) + lem_idx.get(x, []):
                            if e['lesson'] == n:
                                e['core'] = True
                    continue
                key = norm_item(expand_fem(part))
                alt = [] if ',' in key else [key[:-2] if key.endswith('se') else key + 'se']
                if '(se)' in part:
                    # poner(se)：两个词分开对（ponerse 本课新词加粗，poner 第一册学过单列一行）
                    for c in [key] + alt:
                        h, b = look([c])
                        place(n, c, gloss, h, b, split=True)
                    continue
                hit, hb1 = look([key])                   # 先按原样对（mirar 不对到 mirarse）
                if not hit and not hb1:
                    hit, hb1 = look(alt)
                if not hit and not hb1:
                    for x in content_tokens(part):
                        hit += form_idx.get(x, [])
                        hb1 += b1_form(x)
                place(n, part, gloss, hit, hb1)

    assert used_seen_zh == set(SEEN_ZH), set(SEEN_ZH) - used_seen_zh
    for e in entries:
        pin = ENTRY_PIN.get((e['lemma'], e['pos'], e['lesson'])) or ENTRY_PIN.get((e['lemma'], e.get('pos0'), e['lesson'])) or {}
        if 'core' in pin:
            e['core'] = pin['core']
        e.pop('pinned_zh', None)
        e.pop('pos0', None)

    # 按课整理
    lessons = []
    extra_verbs = defaultdict(list)
    for v, n in EXTRA_VERBS:
        extra_verbs[n].append(v)
    for f in sorted(SRC.glob('L*.json')):
        j = json.loads(f.read_text('utf-8'))
        n = j['lesson']
        words = sorted([e for e in entries if e['lesson'] == n], key=lambda e: es_key(e['lemma']))
        # 动词形式：新词形；第一册见过、但那时是另一个词的（puesto 第一册是名词“职位”，这里是 poner 的过去分词）
        vforms = [r for r in items if r['pos'] == 'v.' and r['lesson'] == n and r['form'] != r['lemma']
                  and (not r.get('kind') or (r['kind'] == '同形词' and book1.learned(r['lemma'], 'v.')))]
        verbs = [e['lemma'] for e in words if 'v.' in e['pos'].split('；') and not e['newsense'] and not e.get('no_table')] + extra_verbs.get(n, [])
        vf = [{'form': r['form'], 'lemma': r['lemma'], 'analysis': r['analysis'], 'usage': r.get('usage', '')} for r in vforms]
        for n0, form, lemma, desc in VFORM_EXTRA:
            if n0 != n:
                continue
            segs = desc.split('；')
            ok = matches(segs[0], analyze.analyze(form, lemma))
            assert ok, (form, lemma, analyze.analyze(form, lemma))
            assert not any(v['form'] == form and v['lemma'] == lemma for v in vf), form
            vf.append({'form': form, 'lemma': lemma, 'analysis': join_analyses(ok, analyze.analyze(form, lemma)), 'usage': '；'.join(segs[1:])})
        lessons.append({'lesson': n, 'title_es': j['title_es'], 'title_zh': j['title_zh'], 'words': words,
                        'vforms': sorted(vf,
                                         key=lambda r: (es_key(r['lemma']), es_key(r['form']))),
                        'newforms': sorted([x for x in newforms if x['lesson'] == n], key=lambda x: (es_key(x['lemma']), es_key(x['form']))),
                        'seen': seen.get(n, []), 'vphrases': vphrases.get(n, []), 'verbs': verbs, 'phrases': j.get('phrases', [])})
    conjs = {}
    for L in lessons:
        for v in L['verbs']:
            conjs[v] = conj_table(v, aux=(v == 'haber'))
            e = next((x for x in L['words'] if x['lemma'] == v and 'v.' in x['pos'].split('；')), None)
            # “互相……”的自复动词：这个意思只用复数人称
            if e and v.endswith('se') and e['zh'].startswith('互相'):
                conjs[v]['notes'].append(f'表示“{e["zh"].split("；")[0]}”时只用复数人称（nosotros、vosotros、ellos / ellas / ustedes）')
            if v in CONJ_NOTE:
                conjs[v]['notes'].append(CONJ_NOTE[v])
    out = {'lessons': lessons, 'conj': conjs, 'book1_verbs': book1_new_tenses()}
    (DATA / 'vocab.json').write_text(json.dumps(out, ensure_ascii=False, indent=1), 'utf-8')
    (DATA / 'review.txt').write_text('\n'.join(review) + '\n', 'utf-8')
    nw = sum(len(L['words']) for L in lessons)
    print(f'词条 {nw}，动词 {sum(len(L["verbs"]) for L in lessons)}，动词形式 {sum(len(L["vforms"]) for L in lessons)}，'
          f'已学词的新形式 {sum(len(L["newforms"]) for L in lessons)}，生词表短语 {sum(len(L["vphrases"]) for L in lessons)}，'
          f'第一册动词速查 {len(out["book1_verbs"])}；要人工看的 {len(review)} 处')
    print(' '.join(f'{L["lesson"]}:{len(L["words"])}' for L in lessons))


main()
