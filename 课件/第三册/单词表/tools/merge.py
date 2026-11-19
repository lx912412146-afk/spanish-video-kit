"""把三份归并结果（data/lex_*.tsv）和同形词、新意思的查对结果（data/known_*.tsv）合成第三册按课的单词表：
    python merge.py <第三册课件 content 目录>
第一、二册的结果由 prior.py 读进来：前两册学过的词不再算新词，前两册见过的动词形式也不再列。
输出 data/vocab.json（每课：新词、动词形式、已学词的新形式、生词表里前面学过的词、生词表里的短语、变位表要列的动词、常用表达；
书后：前两册动词的虚拟式过去未完成时）和 data/review.txt（要人工看的地方）。动词形式一律用 analyze.py 复核。"""
import json
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import analyze  # noqa: E402
import prior  # noqa: E402
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
    # 第 3 课 nos bebemos una botella：代词式动词按归并规则写 -se（beberse 喝掉）
    'bebemos': ('beberse', 'v.', '喝掉，喝光', '陈述式现在时 第一人称复数'),
    # ～ 代替词头 materno，lengua ～ 读成 lengua materno，阴阳性不对，写全
    'materna': (None, None, '母亲的；（lengua materna）母语', None),
    # 固定搭配统一用 ～ 代替词头（ejemplo“（por ～）例如”）
    'supuesto': (None, None, '（por ～）当然', None),
    # 和第 8 课 chile 那一条的“另见”写法一致
    'chile': (None, None, None, '另见第 8 课 chile（m.）（美洲）辣椒'),
    # 第 14 课 subieron los bloques：及物用法“把……运上去”，前两册只学过“上去；登上”
    'subieron': ('subir', 'v.', '把……运上去；搬上去', '简单过去时 第三人称复数；第三册新义'),
    # 第 5 课 Dios（上帝）和第 18 课 los dioses（众神）是同一个词，合成一条
    'dios': ('dios', 'm.', '上帝；神', '大写 Dios 指上帝'),
    'dioses': ('dios', 'm.', '神', '复数'),
    # 第 14 课 Alcalá de Henares 是一个地名，不拆成两条
    'alcalá': ('Alcalá de Henares', '地名', '阿尔卡拉-德埃纳雷斯', ''),
    'henares': ('#跳过', '', '地名 Alcalá de Henares 的一部分', ''),
    'cairo': ('El Cairo', '地名', '开罗', ''),
    # 第 16 课 las salas de Goya（展厅）：第二册第 18 课生词表已经有 la sala“大厅；房间”，不算新意思
    'salas': ('sala', 'f.', '客厅', '复数'),
    # costar 的几个新意思分课列：第 10 课 le costó mucho convencer（费力），第 14 课 costó veinte años de trabajo（花费），第 17 课 costarle la vida（使付出代价）
    'costó': ('costar', 'v.', '费力，费劲', '简单过去时 第三人称单数；第三册新义'),
    # 第 7 课 bajo cero 的 cero 和第 1 课 ceros 是同一个词（名词“零”），不另列数词
    'cero': ('cero', 'm.', '零', ''),
    # 民族、国籍、地方的词按“X人；X的”写，作形容词（体例见使用说明）
    'aztecas': ('azteca', 'adj.', '阿兹特克人；阿兹特克的', '复数'),
    'mayas': ('maya', 'adj.', '玛雅人；玛雅的', '复数'),
    'peruana': (None, None, '秘鲁人；秘鲁的', None),
    'poblano': (None, None, '普埃布拉人；普埃布拉的', None),
    'criollo': ('criollo, criolla', 'adj.', '土生白人；土生白人的', None),
    'criollos': ('criollo, criolla', 'adj.', '土生白人；土生白人的', '复数'),
    'criolla': ('criollo, criolla', 'adj.', '土生白人；土生白人的', '阴性'),
    # 第 13 课 entretener 是及物动词，和 entretenerse（消遣；耽搁）分开写
    'entretener': (None, None, '使消遣，使娱乐；耽搁（某人）', None),
    # 第 15 课“离开”是 apartarse 的意思，apartar 写及物的“使离开”
    'apartar': (None, None, '挪开；使离开', None),
    # 地区用法统一写在后面的圆括号里（第 12 课 extrañar“想念（拉美）”）
    'manejar': (None, None, '操作，使用；开车（拉美）', None),
    # 第 17 课 el molino de viento 只写一次
    'molinos': (None, None, None, '复数'),
    # 第 15 课生词表 fijar(se) en〈固定；注意〉：Fíjate bien en este verso
    'fíjate': (None, None, '（～ en）注意', None),
}
# 第一册只在语音练习里出现过、第三册算新词的，备注（第一册的归并结果里没有）
AUTO_NOTE = {}
# 词形第一次作这个词用的课（第一次出现时只是语法要点里的词尾等）
FORM_LESSON = {}
# 归并结果里标了“第三册新义”、但不算新意思的（haber 作助动词第二册第 13 课已学）
NEWSENSE_DROP = {'haber'}
# 同形词、新义查对结果要改的：(词形, 课) → 改的栏目；None 表示删掉这一条
KNOWN_FIX = {
    # 第 14 课生词表 costar〈值；费力〉，“费力”第 10 课已经列了；本课课文 costó unos veinte años de trabajo 是“花费（时间、劳力）”
    ('costar', 14): {'zh': '花费（时间、劳力）'},
    ('cambio', 9): {'zh': '（en ～）相反，而'},
}
# 词条释义、课次要定下来的：(lemma, pos) → (课, 释义)
PIN = {
    # 第 9 课生词表 alzar(se)〈举起；建起；起义〉：alzarse 列在第 9 课；课文第 14 课才用（se alzan tres grandes pirámides 矗立）
    ('alzarse', 'v.'): (9, '起义'),
    # 第 4 课课件释义“安排”，本课的用例是 No disponemos de mucho tiempo（有，拥有）
    ('disponer', 'v.'): (4, '安排；（～ de）拥有'),
    # 介词搭配统一写“（～ de）”
    ('acordarse', 'v.'): (None, '（～ de）记得'),
    # 第 15 课只在书名 «Canto general»（《漫歌》）里出现，是“总的，全面的”
    ('general', 'adj.'): (None, '总的，全面的；一般的'),
    # 课件 X(se) 的释义分给两个词：convertir(se) en〈（使）变成〉、admirar(se)〈钦佩，欣赏；惊叹〉、renovar(se)〈更新；复原〉；
    # 带前置词的照课件写进释义（consistir en、convertir(se) en，和 fijarse“（～ en）注意”一样）
    ('consistir', 'v.'): (None, '（～ en）在于；由……构成'),
    ('convertir', 'v.'): (None, '（～ en）使变成'),
    ('convertirse', 'v.'): (None, '（～ en）变成'),
    ('admirar', 'v.'): (None, '钦佩，欣赏'),
    ('renovar', 'v.'): (None, '更新'),
    ('renovarse', 'v.'): (None, '复原'),
    # 释义只写词义，los Reyes Magos 留在备注里（和 católico、molino 一样）
    ('mago, maga', 'm., f.'): (None, '术士，魔法师'),
}
# 归并按词形分条，漏掉的词条（同形的另一个词、第三册新义）
EXTRA = [
    # 第 17 课 Se cree caballero（自以为是骑士）：creerse，归并按词形分条，cree 归到了 creer（第 14 课 Se cree que… 是无人称句）
    {'lemma': 'creerse', 'pos': 'v.', 'zh': '自以为（是）', 'note': '', 'lesson': 17},
    # 第 8 课 el mole poblano, que lleva chiles y chocolate：llevar“（菜肴）含有”（newsense 的备注由程序按前两册写）
    {'lemma': 'llevar', 'pos': 'v.', 'zh': '（菜肴）含有，放有', 'note': '', 'lesson': 8, 'newsense': True, 'forms': ['lleva']},
    # 第 8 课语法要点专门讲了副词 hasta“甚至”（Hasta los niños conocen el chocolate），前两册只学过前置词
    {'lemma': 'hasta', 'pos': 'adv.', 'zh': '甚至，连……也', 'note': '另见第一册第 1 课 hasta（prep.）直到', 'lesson': 8},
    # 第 8 课 El tomate pertenece a la misma familia que la patata（同属茄科）
    {'lemma': 'familia', 'pos': 'f.', 'zh': '（生物分类的）科', 'note': '', 'lesson': 8, 'newsense': True},
    # 第 9 课 en medio de la selva：medio“中间”（第 11 课生词表才列短语 en medio de）
    {'lemma': 'medio', 'pos': 'm.', 'zh': '中间；（en ～ de）在……中间', 'note': '第 5 课学过（二分之一），这里是新的意思', 'lesson': 9, 'newsense': True},
    # 第 1 课练习 estudiar medicina（学医），前两册只学过“药”
    {'lemma': 'medicina', 'pos': 'f.', 'zh': '医学', 'note': '', 'lesson': 1, 'newsense': True},
    # 第 2 课 Hace muchos siglos…（好几百年前）；第二册学的是 hace + 时间 + que（已经……了）
    {'lemma': 'hacer', 'pos': 'v.', 'zh': '（hace + 时间）……以前', 'note': '', 'lesson': 2, 'newsense': True},
    # 第 2 课语法要点 ir + 形容词、过去分词（iba desnudo、va vestido de negro）：“这里 ir 不一定表示‘去’”
    {'lemma': 'ir', 'pos': 'v.', 'zh': '（+ 形容词、过去分词）处于（某种状态）', 'note': '', 'lesson': 2, 'newsense': True},
    # 第 5 课 antes de que el agua bajara（水退下去），第 7 课 la temperatura baja（气温下降）
    {'lemma': 'bajar', 'pos': 'v.', 'zh': '（水位、温度等）下降', 'note': '', 'lesson': 5, 'newsense': True},
    # 第 5 课 pero bueno, te cuento…；第 8 课 Bueno, ¿desearían tomar algo?：感叹词
    {'lemma': 'bueno', 'pos': 'interj.', 'zh': '好吧；那么', 'note': '另见第一册第 3 课 bueno, buena（adj.）好的', 'lesson': 5},
    # 第 14 课 se alzan tres grandes pirámides：alzarse“矗立”（第 9 课生词表的意思是“起义”）
    {'lemma': 'alzarse', 'pos': 'v.', 'zh': '矗立', 'note': '第 9 课学过（起义），这里是新的意思', 'lesson': 14, 'newsense': True},
    # 课件生词表 X(se) 里 -se 那一半另有意思、课文没用到的，照课件列出：establecer(se)〈建立，设立；定居〉、disculpar(se)〈原谅；道歉〉、admirar(se)〈钦佩，欣赏；惊叹〉
    {'lemma': 'establecerse', 'pos': 'v.', 'zh': '定居', 'note': '', 'lesson': 10},
    {'lemma': 'disculparse', 'pos': 'v.', 'zh': '道歉', 'note': '', 'lesson': 10},
    {'lemma': 'admirarse', 'pos': 'v.', 'zh': '惊叹', 'note': '', 'lesson': 16},
    # 第 11 课 Cuba y Puerto Rico：归并按词形把 Puerto Rico 拆成了 puerto、rico
    {'lemma': 'Puerto Rico', 'pos': '地名', 'zh': '波多黎各', 'note': '', 'lesson': 11},
    # 第 11 课 el poder español disminuyó：名词 poder，前两册只学过动词
    {'lemma': 'poder', 'pos': 'm.', 'zh': '权力；政权', 'note': '另见第一册第 8 课 poder（v.）能；可以', 'lesson': 11},
    # 第 11 课 Hidalgo llamó al pueblo a la lucha：pueblo“人民”
    {'lemma': 'pueblo', 'pos': 'm.', 'zh': '人民', 'note': '', 'lesson': 11, 'newsense': True},
    # 第 14 课 El sol sale por el este：名词 este“东方”，前两册只学过指示形容词
    {'lemma': 'este', 'pos': 'm.', 'zh': '东，东方', 'note': '另见第一册第 5 课 este（adj.）这；这个', 'lesson': 14},
    # 第 15 课 Es extraño, sí：形容词 extraño（第 12 课的 extraño 是 extrañar 的变位）
    {'lemma': 'extraño, extraña', 'pos': 'adj.', 'zh': '奇怪的', 'note': '', 'lesson': 15},
    # 第 16 课 Cualquiera que lo mire se pregunta qué está pintando：preguntarse，归并把 pregunta 当成了名词
    {'lemma': 'preguntarse', 'pos': 'v.', 'zh': '自问；（心里）琢磨', 'note': '', 'lesson': 16},
    # 第 17 课 se vuelve loco：volverse“变得”
    {'lemma': 'volverse', 'pos': 'v.', 'zh': '变得，变成', 'note': 'volverse loco 发疯', 'lesson': 17},
    # 第 17 课 En 1605 salió la primera parte del Quijote：salir“出版，问世”
    {'lemma': 'salir', 'pos': 'v.', 'zh': '（书等）出版，问世', 'note': '', 'lesson': 17, 'newsense': True},
    # 第 18 课 aprendieron a trabajar los metales：trabajar“加工”
    {'lemma': 'trabajar', 'pos': 'v.', 'zh': '加工（金属等）', 'note': '', 'lesson': 18, 'newsense': True},
    # 第 18 课 Gracias a él, aprendieron…：gracias a“多亏”，前两册只学过感叹词 gracias
    # 第 10 课 Aun sabiendo los peligros, decidió partir：partir“出发”（第 1 课只有 a partir de）
    {'lemma': 'partir', 'pos': 'v.', 'zh': '出发，动身', 'note': '第 1 课学过（（a ～ de）从……起），这里是新的意思', 'lesson': 10, 'newsense': True},
    # 第 10 课 Murió en 1506 creyendo, al parecer, que…：名词 parecer
    {'lemma': 'parecer', 'pos': 'm.', 'zh': '（al parecer）看来，似乎', 'note': '另见第一册第 16 课 parecer（v.）使觉得；好像', 'lesson': 10},
    # 第 12 课 Las familias recuerdan a sus difuntos：recordar“纪念，怀念”
    {'lemma': 'recordar', 'pos': 'v.', 'zh': '怀念，纪念（死者等）', 'note': '', 'lesson': 12, 'newsense': True},
    # 第 17 课常用表达 Superó muchas dificultades a lo largo de su vida
    {'lemma': 'largo, larga', 'pos': 'adj.', 'zh': '（a lo largo de）在……的整个期间；沿着', 'note': '', 'lesson': 17, 'newsense': True},
    {'lemma': 'gracias', 'pos': 'f. pl.', 'zh': '（gracias a）多亏，由于', 'note': '另见第一册第 3 课 gracias（interj.）谢谢', 'lesson': 18},
]
# 已学词本课的新用法（不在归并结果里的）
NEWFORM_EXTRA = []
# 变位表下面加的说明
CONJ_NOTE = {'bastar': '常用第三人称：basta、bastan（Basta con eso. 这就够了）',
             'reír': 'rio、riais 按现行正字法不写重音（老版课本写 rió、riáis）', 'reírse': 'se rio、os riais 按现行正字法不写重音（老版课本写 rió、riáis）',
             'sonreír': 'sonriáis 照写重音（两个音节以上）'}
# 审读后定下来的词条栏目：(lemma, pos, 课) → {栏目: 值}（最后套用，盖过程序生成的）
ENTRY_PIN = {
    # 第 5 课 como（+ 数量）大约：课件生词表没有单列（只有短语 tanto… como），不加粗；备注把第一册的连词 como 也写上
    ('como', 'adv.', 5): {'core': False, 'note': '第一册第 14 课学过连词（因为；由于）、第二册第 4 课学过（作为；像……一样），这里是新的意思'},
    # 阴性名词，重读 a- 开头，单数前用 el（和第一册 agua 的写法一样）
    ('arca', 'f.', 5): {'note': '阴性，单数前用 el（el arca）'},
    # 第 11 课常用表达 Me da igual; haz lo que quieras.
    ('igual', 'adj.', 11): {'note': 'me da igual 我无所谓'},
    # 第 10—12 课 San Salvador、San Martín、San Fermín：单词表别处没有解释 San
    ('santo, santa', 'adj.', 12): {'note': 'la Semana Santa 圣周（复活节前一周）；San Fermín 圣费尔明：San 是 santo 的短尾，用在大多数男性圣徒名字前'},
    # 第 17 课 lo cual 用得最多
    ('toro', 'm.', 12): {'note': 'la plaza de toros 斗牛场'},
    ('merecer', 'v.', 15): {'note': 'merecer la pena 值得（做）'},
    ('duda', 'f.', 16): {'note': 'no cabe duda (de que) 毫无疑问'},
    ('fusilamiento', 'm.', 16): {'note': '画名 Los fusilamientos del 3 de mayo《1808年5月3日夜枪杀起义者》'},
    ('cual', 'pron.', 17): {'note': '关系代词 el cual, la cual, los cuales, las cuales；lo cual 指前面整句话或整件事'},
}
# 本课第一次作这个动词用的形式（词形前面已作别的词出现过）：(课, 形式, 原形, 说明)；说明的第一段要和 analyze.py 算的对上
VFORM_EXTRA = [
    (17, 'cree', 'creerse', '陈述式现在时 第三人称单数'),
    (16, 'pregunta', 'preguntarse', '陈述式现在时 第三人称单数'),
    (17, 'vuelve', 'volverse', '陈述式现在时 第三人称单数'),
    # 第 18 课 Últimamente ando muy ocupado：ando 第 3 课在语法表里作词尾 -ando 跳过了
    (18, 'ando', 'andar', '陈述式现在时 第一人称单数'),
    # 词形前面已作另一个原形出现过、本课第一次作这个原形用的（自复 ↔ 非自复、名词 ↔ 过去分词），审读和程序筛查找出来的
    (1, 'vayas', 'irse', '虚拟式现在时 第二人称单数'),              # Siento que te vayas
    (2, 'llevó', 'llevarse', '简单过去时 第三人称单数'),            # Alguien se llevó mi paraguas
    (3, 'hace', 'hacerse', '陈述式现在时 第三人称单数'),            # hay gente que se hace millonaria
    (3, 'rompió', 'romperse', '简单过去时 第三人称单数'),           # Se le rompió el vaso
    (3, 'olvidé', 'olvidar', '简单过去时 第一人称单数'),            # Olvidé las llaves en casa
    (5, 'duermes', 'dormirse', '陈述式现在时 第二人称单数'),        # si no te duermes ya
    (7, 'fueron', 'irse', '简单过去时 第三人称复数'),               # todos se fueron
    (9, 'siento', 'sentirse', '陈述式现在时 第一人称单数'),         # me siento como si hubiera viajado
    (13, 'dedica', 'dedicar', '陈述式现在时 第三人称单数'),         # ¿Y a qué dedica él su tiempo libre?
    (16, 'invitado', 'invitar', '过去分词'),                        # Gracias por haberme invitado
    (16, 'explico', 'explicarse', '陈述式现在时 第一人称单数'),     # No me explico cómo pudo pintar…
    (16, 'queda', 'quedarse', '陈述式现在时 第三人称单数'),         # se queda admirado
    (18, 'quedaba', 'quedar', '过去未完成时 第三人称单数'),         # ya no quedaba nada
    (18, 'escondió', 'esconder', '简单过去时 第三人称单数'),        # lo escondió dentro de una caña
]
# 相互动词（“互相……”只用复数）。基本动词前面有变位表的，不另出表
RECIPROCAL = {'abrazarse', 'felicitarse', 'mirarse', 'saludarse', 'ayudarse', 'verse', 'escribirse', 'quererse', 'llamarse'}
# 只是重读的 i、u 加重音的（prohíbo、reúno），不算不规则
ACC_PRES = {'prohibir': 'i→í', 'reunir': 'u→ú'}
# 生词表里前面已出现的条目，“第一次出现”要特别说明的：(课, 条目) → 说明
SEEN_WHERE = {(1, 'unos, unas'): '第一册第 4 课（不定冠词）；“（+ 数词）大约”第二册第 8 课'}
# 生词表里 X(se) 拆开的那一半前面学过的：释义用课件释义里属于这一半的部分（poner(se)〈放；穿上；变得〉→ poner 放）
SEEN_ZH = {(13, 'dedicar a'): '把……用于', (1, 'contar'): '数；讲述', (2, 'llevar'): '带', (2, 'llevarse'): '拿走，带走', (3, 'hacer'): '做', (3, 'hacerse'): '变成，成为', (4, 'negar'): '否认',
           (6, 'deber'): '应该'}
DROP_NOTES = set()
# 课件生词表 X(se) 的 -se 那一半课文没用到、课件释义也没有单给它的意思，不另列
SPLIT_UNUSED = {'registrarse', 'formarse', 'vincularse', 'destacarse', 'adelantarse'}
# 生词表里对不到词条的条目，指定对哪个词：(课, 条目) → [原形]（unos, unas 是第一册的不定冠词 un 的复数）
VOCAB_LEMMA = {(1, 'unos, unas'): ['un']}
# 生词表里“动词 + 前置词”意思已经变了的，当短语列（dar con 找到，不是 dar 给）
VOCAB_PHRASE = {'dar con'}
# 新动词变位表里额外加的动词：(动词, 课)
EXTRA_VERBS = []
# 使用说明里举的“第三册新义”的例子（词条原形的第一个词）
NEWSENSE_EXAMPLES = ['importar', 'despertar']   # importar“进口”、despertar“引起（兴趣等）”：意思和前两册学的差得远，一看就明白


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
            assert segs[0] in ('同形词', '第三册新义'), (f.name, r)
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
    """过去未完成时、简单条件式、虚拟式现在时、虚拟式过去未完成时的第一、第三人称单数同形，写成一条（pool：analyze() 算出的全部可能；
    无人称动词只有第三人称，llueva 不写成“第一/第三”）。"""
    xs = list(dict.fromkeys(xs))
    pool = xs if pool is None else pool
    for t in ('过去未完成时', '简单条件式', '虚拟式现在时', '虚拟式过去未完成时', '虚拟式过去未完成时 -se 形式'):
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
    elif core in conj.I_IE:
        tags.append('i→ie')
    conj.auto_irregular(core)
    if core in ACC_PRES:
        tags.append(ACC_PRES[core])
    elif core in conj.ACC_IAR:
        tags.append('i→í')
    elif core.endswith('uar') and core not in conj.NO_ACC_UAR:
        tags.append('u→ú')
    stem_changed = any(t in tags for t in ('e→ie', 'o→ue', 'e→i', 'u→ue', 'i→ie'))
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


SRA_END = {'ar': 'ara aras ara áramos arais aran', 'er': 'iera ieras iera iéramos ierais ieran', 'ir': 'iera ieras iera iéramos ierais ieran'}
SSE_END = {'ar': 'ase ases ase ásemos aseis asen', 'er': 'iese ieses iese iésemos ieseis iesen', 'ir': 'iese ieses iese iésemos ieseis iesen'}


def conj_table(lemma, aux=False):
    """变位表：6 个人称 × 陈述式现在时、简单过去时、过去未完成时、将来未完成时、简单条件式（上表），
    虚拟式现在时、虚拟式过去未完成时（-ra、-se）、肯定命令式、否定命令式（下表）；
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
             'subj': [stem + e for e in subj], 'imp': dict(zip(IMP_P, (stem + e for e in imp))), 'ger': stem + gp[0], 'part': stem + gp[1],
             'sra': [stem + e for e in SRA_END[cl].split()], 'sse': [stem + e for e in SSE_END[cl].split()]}
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
        row2 = []
        for k in ('subj', 'sra', 'sse'):
            shown = r[k][i]
            row2.append({'f': shown, 'irr': shown != '—' and base[k][i] != plain[k][i]})
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


def prior_new_tenses():
    """书后速查表：第一、二册出过变位表的每个动词，第三册新学的虚拟式过去未完成时：简单过去时第三人称复数（从它推出）、
    -ra 形式的 yo 和 nosotros、-se 形式的 yo。只用第三人称单数的（llover）给第三人称单数（third = 'sg'）；
    只用第三人称的（ocurrirse：se me ocurrió una idea、se me ocurrieron dos ideas）简单过去时给 ellos，-ra、-se 给第三人称单数（third = '3'）；
    haber 两册都有变位表（第一册无人称 hay，第二册助动词），按助动词列。"""
    rows = []
    for v in sorted(prior.VERBS_TABLE, key=es_key):
        book, lesson = prior.VERBS_TABLE[v]
        aux = v == 'haber'
        t = conj_table(v, aux=aux)
        third = ('sg' if t['top'][5][1]['f'] == '—' else '3') if t['top'][0][1]['f'] == '—' and t['top'][2][1]['f'] != '—' else ''
        k = 2 if third else 0
        e = prior.ENTRY[(v, 'v.')]
        rows.append({'verb': v, 'zh': '（助动词）构成复合时态；有' if aux else e['zh'], 'book': book, 'lesson': lesson, 'vtype': verb_type(v),
                     'third': third, 'pret6': t['top'][2 if third == 'sg' else 5][1], 'sra1': t['bottom'][k][1], 'sra4': t['bottom'][3][1],
                     'sse1': t['bottom'][k][2], 'notes': [n for n in t['notes'] if 'soliera' in n]})
    return rows


def learned_note(e):
    """前两册学过的意思：第一册第 9 课学过（进来；经过）、第二册第 1 课学过（发生）"""
    return '、'.join(f'{prior.BOOK_ZH[b]}第 {n} 课学过（{z}）' for b, n, z in e['senses'])


def senses(zh):
    return {re.sub(r'（[^）]*）|\([^)]*\)', '', s).strip() for s in re.split(r'[，；、]', zh) if s.strip()}


def main():
    rows = read_lex()
    known = read_known()
    forms = json.loads((DATA / 'forms.json').read_text('utf-8'))
    sent = json.loads((DATA / 'sentences.json').read_text('utf-8'))
    review = []
    b1_heads = defaultdict(list)                      # 前两册词条按原形第一个词（同形的另一个词性提示用）
    for (l, p), e in prior.ENTRY.items():
        if not e['phon_only']:
            b1_heads[l.split(',')[0].strip().lower()].append((l, p, e))

    # 每个新词形：归并结果 + 课次
    items = []
    for e in forms:
        f = e['form']
        if e['prev']:
            # 第一册见过、但只在语音练习里出现过（第二册也没学）的词：第三册用到就算新词（归到第一册那一条）
            maps = prior.FORM.get(f, [])
            homo = any(r['form'] == f and r['kind'] == '同形词' for r in known)    # 查对时认定是另一个词的（lima → 地名 Lima）
            if maps and not homo and not any(prior.learned(l, p) for l, p, z in maps):
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
            r['note'] = '；'.join(s for s in top_split(r['note']) if s != '第三册新义')
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
    # 查对时列成“同形词”的动词形式，前两册已经作这个动词见过的（visto ← ver、ven ← venir），不算新形式
    seen_v = lambda r: (r['pos'] == 'v.' and r['kind'] == '同形词' and r['lemma'] in prior.VFORM.get(r['form'], set()))
    for r in known:
        if seen_v(r):
            review.append(f'同形词查对：{r["form"]} ← {r["lemma"]} 前两册已经作这个动词见过，不列')
    known = [r for r in known if not seen_v(r)]
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
        rest = [p for p in segs[1:] if p and '同形' not in p and p != '第三册新义']
        m = re.search(r'（(.*)）', segs[0])
        hints = [h if '+' in h else '连写代词 ' + h for h in (m.group(1).split('；') if m else []) if re.search(r'\s→\s|^→\s', h)]
        r['usage'] = '；'.join(hints + rest)

    # 归并结果和前两册词条对一下：原形写法差一点的（amigo ↔ amigo, amiga）
    for r in items:
        if prior.ENTRY.get((r['lemma'], r['pos'])):
            continue
        for l, p, e in b1_heads.get(r['lemma'].split(',')[0].strip().lower(), []):
            if p == r['pos'] and l != r['lemma']:
                review.append(f'原形和前两册写法不一样：{r["form"]} → {r["lemma"]}（{r["pos"]}），{prior.where(e)}是 {l}')

    # 词条：同一个 lemma + 词性 合成一条
    ent = defaultdict(list)
    for r in items:
        ent[(r['lemma'], r['pos'])].append(r)
    entries, newforms = [], []
    for (lemma, pos), rs in ent.items():
        head = lemma.split(',')[0].strip().lower()
        b1e = prior.ENTRY.get((lemma, pos))
        if b1e and not b1e['phon_only']:
            # 前两册学过的词：新意思单列一条；别的形式进“动词形式”或“已学词的新形式”
            ns = [r for r in rs if r.get('kind') == '第三册新义' or '第三册新义' in top_split(r['note'])]
            listed = set().union(*(senses(z) for b, l, z in b1e['senses'])) if b1e['senses'] else set(senses(b1e['zh']))
            for n0 in sorted({r['lesson'] for r in ns}):           # 每课只列这一课新出现的意思（tomar 第 1 课“拿，取”，第 16 课“把……当成”）
                zs = []
                for r in sorted(ns, key=lambda r: r['form'] != head):
                    if r['lesson'] != n0:
                        continue
                    for part in top_split(r['zh']):            # 只取前两册和前面的课里没有的意思
                        if part.strip() and not senses(part) <= listed:
                            zs.append(part.strip())
                            listed |= senses(part)
                if not zs:
                    continue
                entries.append({'lemma': lemma, 'pos': pos, 'zh': '；'.join(zs), 'note': learned_note(b1e) + '，这里是新的意思',
                                'lesson': n0, 'core': False, 'vtype': [], 'forms': sorted({r['form'] for r in ns if r['lesson'] == n0}),
                                'newsense': True})
            if pos != 'v.':
                for r in rs:
                    if any(r is x for x in ns):
                        continue
                    segs = [p.strip() for p in r['note'].split('；')]
                    segs = [p for p in segs if p and not TRIVIAL.fullmatch(p) and p not in DROP_NOTES and p not in ('第三册新义', '序数词')]
                    if segs:
                        newforms.append({'form': r['form'], 'lemma': lemma, 'pos': pos, 'note': '；'.join(segs), 'lesson': r['lesson'],
                                         'where': prior.where(b1e)})
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
            segs = [tidy(p) for p in segs if p and not TRIVIAL.fullmatch(p) and p not in DROP_NOTES and p not in ('同形词', '第三册新义')]
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
        # 同一个原形前两册学过另一个词性的，提一句（sobre 前置词 ↔ el sobre 信封）
        for l, p, e in b1_heads.get(head, []):
            if p != pos:
                notes = [x for x in notes if not x.startswith(('第一册的 ', '第二册的 ', '前两册的 '))]   # 归并时写的“第一册的 X 是……”，和下面这句重复
                notes.append(f'另见{prior.where(e)} {l}（{p}）{e["zh"]}')
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
        if e['newsense'] and not e['note']:
            e['note'] = learned_note(prior.ENTRY[(e['lemma'], e['pos'])]) + '，这里是新的意思'
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
            if base in prior.VERBS_TABLE:
                bk, bl = prior.VERBS_TABLE[base]
                where = f'{prior.BOOK_ZH[bk]}第 {bl} 课 {base}'
            elif base in b2_verbs and b2_verbs[base] <= e['lesson']:
                where = f'{"本课" if b2_verbs[base] == e["lesson"] else f"第 {b2_verbs[base]} 课"} {base}'
            else:
                where = ''
            e['no_table'] = bool(where)
            e['note'] = '；'.join(filter(None, [f'只用复数：{pres[3]}、{pres[4]}、{pres[5]}' + (f'；变位同{where}' if where else ''), e['note']]))
        elif e['lemma'] in RECIPROCAL:
            e['note'] = '；'.join(filter(None, [e['note'], '相互动词，只用复数']))

    # 课件各课生词表：短语单列；单个词对到词条，本课新词加粗，前面学过的（前两册或第三册前面的课）单列一张表
    lem_idx, form_idx = defaultdict(list), defaultdict(list)
    for e in entries:
        for l in dict.fromkeys([e['lemma'].lower(), e['lemma'].split(',')[0].strip().lower()]):
            lem_idx[l].append(e)
        for f in e['forms']:
            form_idx[f].append(e)
    b1_lem = defaultdict(list)
    for (l, p), e in prior.ENTRY.items():
        if not e['phon_only']:
            for k in dict.fromkeys([l.lower(), l.split(',')[0].strip().lower()]):
                b1_lem[k].append({'lemma': l, 'pos': p, 'zh': e['zh'], 'zh_all': '；'.join(z for b, n0, z in e['senses']) or e['zh'],
                                  'lesson': e['lesson'], 'where': prior.where(e)})

    def b1_form(x):
        return [{'lemma': l, 'pos': p, 'zh': z, 'zh_all': '；'.join(z0 for b, n0, z0 in prior.ENTRY[(l, p)]['senses']) or z,
                 'lesson': prior.ENTRY[(l, p)]['lesson'], 'where': prior.where(prior.ENTRY[(l, p)])}
                for l, p, z in prior.FORM.get(x, []) if prior.learned(l, p)]

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
        if '…' in part or '+' in part or part in VOCAB_PHRASE:
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
    # 前两册学过、第三册又有新意思的：第三册前面的课已经补过的新意思也写上
    for e in entries:
        parts = e['note'].split('，这里是新的意思', 1)
        if not (e['newsense'] and len(parts) == 2 and '学过（' in parts[0]):
            continue
        prev = sorted((o for o in entries if o['newsense'] and o['lemma'] == e['lemma'] and o['pos'] == e['pos'] and o['lesson'] < e['lesson']),
                      key=lambda o: o['lesson'])
        if prev:
            e['note'] = parts[0] + ''.join(f'、第 {o["lesson"]} 课学过（{o["zh"]}）' for o in prev) + '，这里是新的意思' + parts[1]
    seen, vphrases = defaultdict(list), defaultdict(list)
    used_seen_zh, used_vlem = set(), set()

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
        if not earlier and not split and not any(senses(gloss) & senses(e['zh_all']) for e in hb1):
            review.append(f'生词表释义和前两册不一样：第 {n} 课 {part}「{gloss}」，前两册 ' +
                          '；'.join(f'{e["lemma"]}（{e["pos"]}）「{e["zh_all"]}」' for e in hb1))
        both = bool(earlier and hb1)                      # 前两册学过、第三册前面的课又有了新意思：各注意思
        name = len(earlier) + len(hb1) > 1 and not both
        where = '、'.join(dict.fromkeys(
            [(f'{e["lemma"].split(",")[0]} ' if name else '') + e['where'] + (f'（{e["zh"]}）' if both else '') for e in hb1] +
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
                    # poner(se)：两个词分开对（ponerse 本课新词加粗，poner 第一册学过单列一行）；
                    # dedicar(se) a：后面的前置词先去掉再对，列的时候带上（dedicar a、dedicarse a）
                    m = re.fullmatch(r'(.+?)\s+(a|de|en|con|por|para)', key)
                    base, prep = (m[1], ' ' + m[2]) if m else (key, '')
                    for c in [base, base + 'se']:
                        h, b = look([c])
                        if not h and not b and c not in SPLIT_UNUSED:
                            review.append(f'生词表 {part} 拆开的 {c} 找不到词条（课文里没用到）')
                        place(n, c + prep, gloss, h, b, split=True)
                    continue
                if (n, part) in VOCAB_LEMMA:
                    used_vlem.add((n, part))
                    place(n, part, gloss, *look(VOCAB_LEMMA[(n, part)]))
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
    assert used_vlem == set(VOCAB_LEMMA), set(VOCAB_LEMMA) - used_vlem
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
                  and (not r.get('kind') or r['kind'] == '同形词')]
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
    ha = conj.conjugate('haber', aux=True)
    # 使用说明里“新的意思”举的例子：NEWSENSE_EXAMPLES 指定的词条（没指定就取前两条释义短的）
    ns_all = [e for L in lessons for e in L['words'] if e['newsense']]
    pick = [e for k in NEWSENSE_EXAMPLES for e in ns_all if e['lemma'].split(',')[0] == k][:3] or [e for e in ns_all if len(e['zh']) <= 8][:2]
    out = {'lessons': lessons, 'conj': conjs, 'prior_verbs': prior_new_tenses(),
           'haber_aux': {k: ha[k] for k in ('fut', 'cond', 'subj', 'sra', 'sse')},
           'newsense_examples': [f'{e["lemma"].split(",")[0]}“{e["zh"].split("；")[0]}”' for e in pick]}
    (DATA / 'vocab.json').write_text(json.dumps(out, ensure_ascii=False, indent=1), 'utf-8')
    (DATA / 'review.txt').write_text('\n'.join(review) + '\n', 'utf-8')
    nw = sum(len(L['words']) for L in lessons)
    print(f'词条 {nw}，动词 {sum(len(L["verbs"]) for L in lessons)}，动词形式 {sum(len(L["vforms"]) for L in lessons)}，'
          f'已学词的新形式 {sum(len(L["newforms"]) for L in lessons)}，生词表短语 {sum(len(L["vphrases"]) for L in lessons)}，'
          f'前两册动词速查 {len(out["prior_verbs"])}；要人工看的 {len(review)} 处')
    print(' '.join(f'{L["lesson"]}:{len(L["words"])}' for L in lessons))


main()
