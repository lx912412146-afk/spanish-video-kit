"""把三份归并结果（data/lex_*.tsv）和同形词、新意思的查对结果（data/known_*.tsv）合成第四册按课的单词表：
    python merge.py <第四册课件 content 目录>
第一、二、三册的结果由 prior.py 读进来：前三册学过的词不再算新词，前三册见过的动词形式也不再列。
输出 data/vocab.json（每课：新词、动词形式、已学词的新形式、生词表里前面学过的词、生词表里的短语、变位表要列的动词、常用表达；
书后：前三册出过变位表的动词索引）和 data/review.txt（要人工看的地方）。动词形式一律用 analyze.py 复核。"""
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
    # 第 16 课 para que no se perdieran las pinturas：被动意义的 se，归 perder（照前三册的释义）
    'perdieran': (None, None, None, '虚拟式过去未完成时 第三人称复数'),
    # 第 9 课 Cuando nos juntamos：juntarse（课件生词表 juntar(se)〈使聚集；聚会，相聚〉，juntar 另有一条）
    'juntamos': (None, None, None, '陈述式现在时 第一人称复数'),
    # 第 5 课 nos perdimos de vista：短语 perder de vista（本课生词表）的相互用法，归 perder
    'perdimos': ('perder', 'v.', '丢失；错过', '简单过去时 第一人称复数'),
    # 第 16 课课文 la UNESCO declaró la cueva…是 declarar；常用表达 se declaró un incendio 是 declararse，另列（见 EXTRA）
    'declaró': (None, None, None, '简单过去时 第三人称单数'),
    # 第 17 课 hacerlas más resistentes：hacer + 形容词“使变得”第 17 课才出现（新义见 EXTRA），这一行照前三册
    'hacerlas': (None, None, '做；干', '不定式 + 代词 las'),
    # 专名的标准写法是 al-Ándalus（课文 existió al-Ándalus）
    'ándalus': ('al-Ándalus', '地名', '安达卢斯', '穆斯林统治时期的西班牙'),
    # 第 5 课 unos cuantos viejos como él：名词 un viejo 第一册第 24 课练习已经用过（见 KNOWN_FIX），归第一册的 viejo, vieja，不另列
    'viejos': ('viejo, vieja', 'adj.', '旧的；老的', '复数'),
    # 民族词写作形容词（体例同国籍词）：第 15 课 la cultura judía、los judíos…；los visigodos
    'judíos': ('judío, judía', 'adj.', '犹太人；犹太的', '复数'),
    'visigodos': ('visigodo, visigoda', 'adj.', '西哥特人；西哥特的', '复数'),
    # 第 10 课语法 cualquiera 的复数 cualesquiera（少用；dos días cualesquiera），列进“已学词的新形式”
    'cualesquiera': (None, None, None, '复数，少用（dos días cualesquiera）'),
    # 第 8 课 las gentes de las dos Américas：gente 第一册学的是集合名词“人们”，复数列进“已学词的新形式”
    'gentes': (None, None, None, '复数 las gentes：各族人民'),
}
# 第一册只在语音练习里出现过、第四册算新词的，备注（第一册的归并结果里没有）
AUTO_NOTE = {}
# 词形第一次作这个词用的课（第一次出现时只是语法要点里的词尾等）
FORM_LESSON = {}
# 归并结果里标了“第四册新义”、但不算新意思的（haber 作助动词第二册第 13 课已学）
NEWSENSE_DROP = {'haber'}
# 同形词、新义查对结果要改的：(词形, 课) → 改的栏目；None 表示删掉这一条
KNOWN_FIX = {
    # 前面几册的课件已经用过，不算第四册的新意思：por cierto（第二册第 8 课课文）、por fin（第二册第 1、15、16、17 课）、
    # sacar fotos（第一册第 24 课生词表）、副词 tarde（第一册第 11、16、17 课 Es tarde）、名词 un viejo（第一册第 24 课练习）、
    # caro, cara（第一册第 12 课已学）
    ('cierto', 1): None,
    ('fin', 1): None,
    ('sacar', 3): None,
    ('tarde', 2): None,
    ('viejo', 5): None,
    ('cara', 12): None,
    # 词尾、人名不是同形词，不列
    ('da', 4): None,
    ('cruz', 6): None,
    # 国籍词写作形容词，释义给出“……人”和“……的”（体例见使用说明）
    ('inglés', 13): {'lemma': 'inglés, inglesa', 'pos': 'adj.', 'zh': '英国人；英国的'},
    ('francés', 10): {'zh': '法国人；法国的'},
}
# 词条释义、课次要定下来的：(lemma, pos) → (课, 释义)
PIN = {
    # rueda ～ 读成 rueda dentado，性不一致，写全
    ('dentado, dentada', 'adj.'): (None, '有齿的；（rueda dentada）齿轮'),
    # 第 14 课课文 En los parques eólicos…（风电场）
    ('eólico, eólica', 'adj.'): (None, '风的；风力的；（parque ～）风电场'),
    # 国籍、民族词释义写“……人；……的”
    ('judío, judía', 'adj.'): (None, '犹太人；犹太的'),
    ('africano, africana', 'adj.'): (None, '非洲人；非洲的'),
    ('europeo, europea', 'adj.'): (None, '欧洲人；欧洲的'),
    # 第 17 课只有 los seres vivos（生物）；ser humano 本册没用到
    ('ser', 'm.'): (None, '存在物；（～ vivo）生物'),
    # 第 8 课 la población indígena（形容词；名词“原住民”另见第 6 课）
    ('indígena', 'adj.'): (None, '土著的，原住民的'),
    # 第 4 课 Coge el paraguas、第 12 课 Cogimos el autobús；“抓”本册没用到
    ('coger', 'v.'): (None, '拿，取；乘坐'),
    # 第 4 课 nos llegó al alma（打动了我们的心）
    ('alma', 'f.'): (None, '灵魂；心灵；（llegar al ～）打动人心'),
}
# 归并按词形分条，漏掉的词条（同形的另一个词、第四册新义）
EXTRA = [
    # 课件生词表 X(se) 里 -se 那一半另有意思、课文没用到的，照课件列出：separar(se)〈分开；分离〉、gozar(se)〈享有；喜悦〉、
    # distinguir(se)〈区分；出众〉、estirar(se)〈拉长；伸展（身体）〉、arrastrar(se)〈拖，拽；爬行〉、animar(se)〈鼓励；振作〉、
    # asombrar(se)〈使惊奇；感到惊奇〉、procurar(se)〈设法，力求；谋得〉
    {'lemma': 'separarse', 'pos': 'v.', 'zh': '分离', 'note': '', 'lesson': 3},
    {'lemma': 'gozarse', 'pos': 'v.', 'zh': '喜悦', 'note': '', 'lesson': 5},
    {'lemma': 'distinguirse', 'pos': 'v.', 'zh': '出众', 'note': '', 'lesson': 8},
    {'lemma': 'estirarse', 'pos': 'v.', 'zh': '伸展（身体）', 'note': '', 'lesson': 9},
    {'lemma': 'arrastrarse', 'pos': 'v.', 'zh': '爬行', 'note': '', 'lesson': 9},
    {'lemma': 'animarse', 'pos': 'v.', 'zh': '振作', 'note': '', 'lesson': 10},
    {'lemma': 'asombrarse', 'pos': 'v.', 'zh': '感到惊奇', 'note': '', 'lesson': 14},
    {'lemma': 'procurarse', 'pos': 'v.', 'zh': '谋得', 'note': '', 'lesson': 18},
    # 第 12 课常用表达 Se armó de valor y le dijo la verdad：armarse（课文 armó un escándalo 是 armar），归并按词形分条漏掉了
    {'lemma': 'armarse', 'pos': 'v.', 'zh': '武装起来；（～ de valor）鼓起勇气', 'note': '', 'lesson': 12},
    # 第 16 课常用表达 Anoche se declaró un incendio en el bosque：declararse“（火灾等）发生”（课件生词表 declarar(se)）
    {'lemma': 'declararse', 'pos': 'v.', 'zh': '（火灾等）发生', 'note': '', 'lesson': 16},
    # 归并按词形分条、同形词查对只看第一次出现的课，漏掉的：第 17 课语法重点 el hecho de que 的名词 hecho（hecho 第 4 课作过去分词出现过），
    # 第 10 课 Es el estadio en que se jugó la final（阴性名词 la final 决赛；final 第 2 课 al final 出现过）
    {'lemma': 'hecho', 'pos': 'm.', 'zh': '事实；（el ～ de que）……这件事', 'note': '另见 hacer 的过去分词 hecho', 'lesson': 17},
    {'lemma': 'final', 'pos': 'f.', 'zh': '决赛', 'note': '另见第一册第 14 课 final（m.）末尾；结尾', 'lesson': 10},
    # 第 7 课课文 no tienen seguro médico（名词“保险”；词形 seguro 第 1 课作形容词出现过），前三册只有形容词 seguro, segura
    {'lemma': 'seguro', 'pos': 'm.', 'zh': '保险；（～ médico）医疗保险', 'note': '另见第二册第 8 课 seguro, segura（adj.）确信的；可靠的', 'lesson': 7},
    # 前三册没有的意思（前三册课件里都查过）：第 14 课 el viento hace girar enormes molinos（使役），第 15 课 hicieron de Toledo su capital，
    # 第 12 课 ella llevaba su pulsera de oro（戴着），第 15 课语法要点 Debió de perder el tren（推测），
    # 第 16 课 Tenían miedo a que se perdieran las pinturas（毁掉），第 16 课练习 Corre la noticia de que…（传开）
    {'lemma': 'hacer', 'pos': 'v.', 'zh': '（+ 原形动词）使，让', 'note': '', 'lesson': 14, 'newsense': True, 'forms': ['hace']},
    {'lemma': 'hacer', 'pos': 'v.', 'zh': '（～ de A B）把 A 变成 B，把 A 定为 B', 'note': '', 'lesson': 15, 'newsense': True, 'forms': ['hicieron']},
    # 第 17 课 genes añadidos para hacerlas más resistentes（hacer + 形容词；前三册只有 hacerse rico / famoso“变得”）
    {'lemma': 'hacer', 'pos': 'v.', 'zh': '（+ 形容词）使变得', 'note': '', 'lesson': 17, 'newsense': True, 'forms': ['hacerlas']},
    {'lemma': 'llevar', 'pos': 'v.', 'zh': '穿着；戴着', 'note': '', 'lesson': 12, 'newsense': True, 'forms': ['llevaba']},
    {'lemma': 'deber', 'pos': 'v.', 'zh': '（～ de + 原形动词）大概，想必（表示推测）', 'note': '', 'lesson': 15, 'newsense': True, 'forms': ['debió']},
    {'lemma': 'perder', 'pos': 'v.', 'zh': '（东西）损毁，消失', 'note': '', 'lesson': 16, 'newsense': True, 'forms': ['perdieran']},
    {'lemma': 'correr', 'pos': 'v.', 'zh': '（消息）传开，流传', 'note': '', 'lesson': 16, 'newsense': True, 'forms': ['corre']},
    # 第 9 课课文 A su lado, me sentía seguro（安心；课件生词表 seguro, ra〈安全的；确信的〉），前三册只学过“确信的；可靠的”
    {'lemma': 'seguro, segura', 'pos': 'adj.', 'zh': '安全的；安心的', 'note': '', 'lesson': 9, 'newsense': True, 'forms': ['seguro']},
    # 第 3 课课文 distribuidos de forma muy desigual（分布不均匀；课件生词表 desigual〈不均匀的；不平等的〉），前三册只在语法表里学过“不同的；不平等的”
    {'lemma': 'desigual', 'pos': 'adj.', 'zh': '不均匀的', 'note': '', 'lesson': 3, 'newsense': True, 'forms': ['desigual']},
    # 课文、练习用到、前三册没出现过的固定说法（前三册课件都查过）：第 1 课 un amigo de verdad，第 2 课 conducir el módulo a mano，
    # 第 5 课 eso es lo que más me duele，第 7 课 Es decir, más de veinte millones…、libros de segunda mano，第 9 课 de pronto se fue la luz
    {'lemma': 'verdad', 'pos': 'f.', 'zh': '（de ～）真正的；真的', 'note': '', 'lesson': 1, 'newsense': True, 'forms': ['verdad']},
    {'lemma': 'mano', 'pos': 'f.', 'zh': '（a ～）用手，手动', 'note': '', 'lesson': 2, 'newsense': True, 'forms': ['mano']},
    {'lemma': 'doler', 'pos': 'v.', 'zh': '（精神上）使难过，使痛心', 'note': '', 'lesson': 5, 'newsense': True, 'forms': ['duele']},
    {'lemma': 'decir', 'pos': 'v.', 'zh': '（es ～）也就是说', 'note': '', 'lesson': 7, 'newsense': True, 'forms': ['decir']},
    {'lemma': 'mano', 'pos': 'f.', 'zh': '（de segunda ～）二手的', 'note': '', 'lesson': 7, 'newsense': True, 'forms': ['mano']},
    {'lemma': 'irse', 'pos': 'v.', 'zh': '（～ la luz）停电', 'note': '', 'lesson': 9, 'newsense': True, 'forms': ['fue']},
    # 第 4 课课文 se alza la Torre del Oro（词都学过，专名照第 3 课 Salto Ángel 列出）
    {'lemma': 'Torre del Oro', 'pos': '地名', 'zh': '黄金塔', 'note': '塞维利亚瓜达尔基维尔河边的古塔', 'lesson': 4},
]
# 已学词本课的新用法（不在归并结果里的）
NEWFORM_EXTRA = []
# 变位表下面加的说明
CONJ_NOTE = {'bastar': '常用第三人称：basta、bastan（Basta con eso. 这就够了）',
             'reír': 'rio、riais 按现行正字法不写重音（老版课本写 rió、riáis）', 'reírse': 'se rio、os riais 按现行正字法不写重音（老版课本写 rió、riáis）',
             'sonreír': 'sonriáis 照写重音（两个音节以上）',
             'huir': 'hui、huis 是单音节，按现行正字法不写重音（老版课本写 huí、huís）'}
# 审读后定下来的词条栏目：(lemma, pos, 课) → {栏目: 值}（最后套用，盖过程序生成的）
ENTRY_PIN = {
    # 课件生词表 medio (por medio de)〈手段，媒介（借助，通过）〉，课文 Por medio de ruedas dentadas…
    ('medio', 'm.', 13): {'zh': '手段，媒介；（por ～ de）借助，通过；（～s de comunicación）媒体'},
    # 第 14 课常用表达 No quiero correr ese riesgo.
    ('riesgo', 'm.', 14): {'note': 'correr un riesgo 冒险'},
    # 第 1 课只在语法表的谚语 Quien calla, otorga 里出现（同意，默许）；“授予，给予”是第 10 课生词表的释义
    ('otorgar', 'v.', 1): {'zh': '同意，默许；授予，给予', 'note': 'Quien calla, otorga. 沉默就是同意（谚语）'},
    # 第 3 课生词表 cortar(se)〈切，割；切断〉，第 3 课只用了 cortar；cortarse 第 9 课练习 su hijo se cortó 才用到
    ('cortarse', 'v.', 9): {'note': '另见第三册第 7 课 cortar（切断；割；剪）；第 3 课生词表里写作 cortar(se)'},
    # 第三册第 17 课生词表 el molino de viento〈风车〉、常用表达 los molinos de viento；第四册新的只是“风力发电机”
    ('molino', 'm.', 14): {'zh': '风力发电机', 'note': '第三册第 17 课学过（磨坊；（～ de viento）风车），这里是新的意思'},
    # 第一册第 8 课语音练习里的 técnico 是名词“技术员”（第 17 课 técnica 同样注了）
    ('técnico, técnica', 'adj.', 13): {'note': '第一册第 8 课语音练习里出现过（技术员）'},
    # 第 9 课课文 Dentro había una notita…（指小词）
    ('nota', 'f.', 9): {'note': '第一册第 24 课学过（分数），这里是新的意思；课文里是指小词 notita'},
    # 阴性名词，单数前用 el（体例同第三册 el águila）
    ('alma', 'f.', 4): {'note': '阴性名词，单数前用 el：el alma'},
}
# 本课第一次作这个动词用的形式（词形前面已作别的词出现过）：(课, 形式, 原形, 说明)；说明的第一段要和 analyze.py 算的对上
VFORM_EXTRA = [
    # 词形前面已作另一个原形出现过、本课第一次作这个原形用的（程序筛查找出来的）
    (2, 'sé', 'saberse', '陈述式现在时 第一人称单数'),              # ¡Me lo sé de memoria!
    (12, 'armó', 'armarse', '简单过去时 第三人称单数'),           # Se armó de valor
    (16, 'declaró', 'declararse', '简单过去时 第三人称单数'),     # se declaró un incendio
    (12, 'estremeció', 'estremecer', '简单过去时 第三人称单数'),  # Aquel grito nos estremeció a todos（课文 Se estremeció 是 estremecerse）
    (1, 'agradecido', 'agradecer', '过去分词'),                  # ¿le has agradecido a Pablo…?（lo agradecido que estás 是形容词）
    (9, 'cortó', 'cortarse', '简单过去时 第三人称单数'),          # su hijo se cortó（第 3 课 La nieve cortó la carretera 是 cortar）
    (9, 'juntamos', 'juntar', '陈述式现在时 第一人称复数'),       # Juntamos dinero para comprarle un regalo（课文 Cuando nos juntamos 是 juntarse）
]
# 相互动词（“互相……”只用复数）。基本动词前面有变位表的，不另出表
# （llamarse 第一册是“名叫”，不是相互动词，书后索引里按自复动词标）
RECIPROCAL = {'abrazarse', 'felicitarse', 'mirarse', 'saludarse', 'ayudarse', 'verse', 'escribirse', 'quererse',
              'conocerse'}   # 第 6 课 el año en que nos conocimos（互相认识）
# 只是重读的 i、u 加重音的（prohíbo、reúno），不算不规则
ACC_PRES = {'prohibir': 'i→í', 'reunir': 'u→ú'}
# 生词表里前面已出现的条目，“第一次出现”要特别说明的：(课, 条目) → 说明
SEEN_WHERE = {}
# 生词表里 X(se) 拆开的那一半前面学过的：释义用课件释义里属于这一半的部分（poner(se)〈放；穿上；变得〉→ poner 放）
SEEN_ZH = {(12, 'encerrarse'): '闭门不出',   # 课件 encerrar(se)〈关起来；闭门不出〉
           (1, 'salvarse'): '得救，脱险',          # salvar(se)〈救；得救，脱险〉
           (3, 'elevar'): '举起（“举起”是新的意思，课文没用到）',   # elevar(se)〈举起；升高〉；第三册学的是“提高；提升（职位）”
           # 课件释义里有前面没学过、课文也没用到的意思的，注明（第二轮审读）
           (1, 'la dirección'): '方向；地址；领导（“领导”是新的意思，课文没用到）',
           (2, 'conducir'): '驾驶；引导（“引导”是新的意思，课文没用到）',
           (2, 'descubrir'): '发现；揭露（“揭露”是新的意思，课文没用到）',
           (4, 'aficionado, da'): '爱好者；业余的（“业余的”是新的意思，课文没用到）',
           (6, 'duro, ra'): '硬的；艰苦的；严厉的（“严厉的”是新的意思，课文没用到）',
           (6, 'la razón'): '理由；道理；理智（“理智”是新的意思，课文没用到）',
           (7, 'total'): '全部的；总数（形容词“全部的”是新的意思，课文没用到）',
           (13, 'calcular'): '计算；估计（“估计”是新的意思，课文没用到）',
           (3, 'cortar'): '切，割；切断',          # cortar(se)〈切，割；切断〉（cortarse 第 9 课才用到）
           (6, 'quemar'): '烧',                    # quemar(se)〈烧；烫伤；晒伤〉
           (6, 'sorprender'): '使惊讶',            # sorprender(se)〈使惊讶；（se）吃惊〉
           (17, 'contener'): '包含，容纳',         # contener(se)〈包含，容纳；克制〉
           (17, 'resistir'): '抵抗，经受',         # resistir(se)〈抵抗，经受；不肯〉
           (17, 'mejorar'): '改善',                # mejorar(se)〈改善；（病）好转〉
           (18, 'aburrir'): '使厌烦',              # aburrir(se)〈使厌烦；感到无聊〉
           (9, 'la sierra'): '山脉；锯子（“锯子”是新的意思，课文没用到）'}   # 第 3 课学的是“山脉；山区”
DROP_NOTES = set()
# 生词表 X(se) 拆开的一半前面学过、可课件释义没单给它意思、本课也没用到的，不列进“前面学过的词”：defender(se)〈保卫；为……辩护〉
SEEN_DROP = {(17, 'defenderse')}
# 课件生词表 X(se) 的 -se 那一半课文没用到、课件释义也没有单给它的意思，不另列
SPLIT_UNUSED = {'distribuirse', 'disfrutarse', 'controlarse', 'reducirse'}
# 生词表里对不到词条的条目，指定对哪个词：(课, 条目) → [原形]
VOCAB_LEMMA = {}
# 生词表里“动词 + 前置词”意思已经变了的，当短语列（dar con 找到，不是 dar 给）
VOCAB_PHRASE = {'dar con'}
# 生词表条目括号里只是说明、不是另一个词的：前置词（carecer (de)）、de + inf.、复数（el gen (pl. genes)）
PAREN_KEEP = re.compile(r'(a|de|en|con|por|para)( \+ inf\.)?|pl\. .+|se')
# 新动词变位表里额外加的动词：(动词, 课)
EXTRA_VERBS = []
# 使用说明里举的“第四册新义”的例子（词条原形的第一个词）
NEWSENSE_EXAMPLES = ['papel', 'carrera']   # papel“作用；角色”（前面学过“纸”）、carrera“赛跑”（前面学过“大学学业；职业”）


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
            assert segs[0] in ('同形词', '第四册新义'), (f.name, r)
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


def prior_verbs_index():
    """书后索引：前三册出过变位表的每个动词（第四册没有新的时态，变位表到原来那一册查）：原形、释义、类型、在哪一册哪一课。
    haber 第一册（无人称 hay）、第二册（助动词）都有变位表，按第一次出表的写。"""
    rows = []
    for v in sorted(prior.VERBS_TABLE, key=es_key):
        book, lesson = prior.VERBS_TABLE[v]
        e = prior.ENTRY[(v, 'v.')]
        rows.append({'verb': v, 'zh': e['zh'].replace('，', '；'), 'book': book, 'lesson': lesson,
                     'vtype': verb_type(v)})
    return rows


def learned_note(e):
    """前三册学过的意思：第一册第 9 课学过（进来；经过）、第二册第 1 课学过（发生）"""
    return '、'.join(f'{prior.BOOK_ZH[b]}第 {n} 课学过（{z}）' for b, n, z in e['senses'])


def senses(zh):
    return {re.sub(r'（[^）]*）|\([^)]*\)', '', s).strip() for s in re.split(r'[，；、]', zh) if s.strip()}


def main():
    rows = read_lex()
    known = read_known()
    forms = json.loads((DATA / 'forms.json').read_text('utf-8'))
    sent = json.loads((DATA / 'sentences.json').read_text('utf-8'))
    review = []
    b1_heads = defaultdict(list)                      # 前三册词条按原形第一个词（同形的另一个词性提示用）
    for (l, p), e in prior.ENTRY.items():
        if not e['phon_only']:
            b1_heads[l.split(',')[0].strip().lower()].append((l, p, e))

    # 每个新词形：归并结果 + 课次
    items = []
    for e in forms:
        f = e['form']
        if e['prev']:
            # 第一册见过、但只在语音练习里出现过（第二、三册也没学）的词：第四册用到就算新词（归到第一册那一条）
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
            r['note'] = '；'.join(s for s in top_split(r['note']) if s != '第四册新义')
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
    # 查对时列成“同形词”的动词形式，前三册已经作这个动词见过的（visto ← ver、ven ← venir），不算新形式
    seen_v = lambda r: (r['pos'] == 'v.' and r['kind'] == '同形词' and r['lemma'] in prior.VFORM.get(r['form'], set()))
    for r in known:
        if seen_v(r):
            review.append(f'同形词查对：{r["form"]} ← {r["lemma"]} 前三册已经作这个动词见过，不列')
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
        rest = [p for p in segs[1:] if p and '同形' not in p and p != '第四册新义']
        m = re.search(r'（(.*)）', segs[0])
        hints = [h if '+' in h else '连写代词 ' + h for h in (m.group(1).split('；') if m else []) if re.search(r'\s→\s|^→\s', h)]
        r['usage'] = '；'.join(hints + rest)

    # 归并结果和前三册词条对一下：原形写法差一点的（amigo ↔ amigo, amiga）
    for r in items:
        if prior.ENTRY.get((r['lemma'], r['pos'])):
            continue
        for l, p, e in b1_heads.get(r['lemma'].split(',')[0].strip().lower(), []):
            if p == r['pos'] and l != r['lemma']:
                review.append(f'原形和前三册写法不一样：{r["form"]} → {r["lemma"]}（{r["pos"]}），{prior.where(e)}是 {l}')

    # 词条：同一个 lemma + 词性 合成一条
    ent = defaultdict(list)
    for r in items:
        ent[(r['lemma'], r['pos'])].append(r)
    entries, newforms = [], []
    for (lemma, pos), rs in ent.items():
        head = lemma.split(',')[0].strip().lower()
        b1e = prior.ENTRY.get((lemma, pos))
        if b1e and not b1e['phon_only']:
            # 前三册学过的词：新意思单列一条；别的形式进“动词形式”或“已学词的新形式”
            ns = [r for r in rs if r.get('kind') == '第四册新义' or '第四册新义' in top_split(r['note'])]
            listed = set().union(*(senses(z) for b, l, z in b1e['senses'])) if b1e['senses'] else set(senses(b1e['zh']))
            for n0 in sorted({r['lesson'] for r in ns}):           # 每课只列这一课新出现的意思（tomar 第 1 课“拿，取”，第 16 课“把……当成”）
                zs = []
                for r in sorted(ns, key=lambda r: r['form'] != head):
                    if r['lesson'] != n0:
                        continue
                    for part in top_split(r['zh']):            # 只取前三册和前面的课里没有的意思
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
                    segs = [p for p in segs if p and not TRIVIAL.fullmatch(p) and p not in DROP_NOTES and p not in ('第四册新义', '序数词')]
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
            segs = [tidy(p) for p in segs if p and not TRIVIAL.fullmatch(p) and p not in DROP_NOTES and p not in ('同形词', '第四册新义')]
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
        # 同一个原形前三册学过另一个词性的，提一句（sobre 前置词 ↔ el sobre 信封）
        others = defaultdict(list)                       # 同一处学的几个词性、释义一样的合成一句（cualquiera adj., pron.）
        for l, p, e in b1_heads.get(head, []):
            if p != pos:
                others[(prior.where(e), l, e['zh'])].append(p)
        if others:
            notes = [x for x in notes if not x.startswith(('第一册的 ', '第二册的 ', '第三册的 ', '前两册的 ', '前三册的 '))]   # 归并时写的“第一册的 X 是……”，和下面这句重复
            notes += [f'另见{w} {l}（{"；".join(ps)}）{z}' for (w, l, z), ps in others.items()]
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
    # 新的自复动词（或不带 se 的动词）前三册学过另一个的，提一句（unirse ↔ 第三册 unir、escaparse ↔ escapar）
    for e in entries:
        if e['pos'] != 'v.' or e['newsense']:
            continue
        v = e['lemma']
        if v in RECIPROCAL:                               # 相互动词下面另写“变位同……”，带上基本动词的意思
            continue
        other = v[:-2] if v.endswith('se') and v[:-2].endswith(('ar', 'er', 'ir', 'ír')) else v + 'se'
        pe = prior.ENTRY.get((other, 'v.'))
        if pe and prior.learned(other, 'v.'):
            see = f'另见{prior.where(pe)} {other}（{pe["zh"]}）'
            if see not in e['note']:
                e['note'] = '；'.join(filter(None, [e['note'], see]))
    # 相互动词：只用复数；基本动词前面有变位表的不另出表
    b2_verbs = {e['lemma']: e['lesson'] for e in entries if e['pos'] == 'v.' and not e['newsense']}
    for e in entries:
        if e['lemma'] in RECIPROCAL and e['pos'] == 'v.' and not e['newsense']:
            base = e['lemma'][:-2]
            pres = conj.conjugate(e['lemma'])['pres']
            if base in prior.VERBS_TABLE:
                bk, bl = prior.VERBS_TABLE[base]
                pe = prior.ENTRY.get((base, 'v.'))
                where = f'{prior.BOOK_ZH[bk]}第 {bl} 课 {base}' + (f'（{pe["zh"]}）' if pe else '')
            elif base in b2_verbs and b2_verbs[base] <= e['lesson']:
                where = f'{"本课" if b2_verbs[base] == e["lesson"] else f"第 {b2_verbs[base]} 课"} {base}'
            else:
                where = ''
            e['no_table'] = bool(where)
            e['note'] = '；'.join(filter(None, [f'只用复数：{pres[3]}、{pres[4]}、{pres[5]}' + (f'；变位同{where}' if where else ''), e['note']]))
        elif e['lemma'] in RECIPROCAL:
            e['note'] = '；'.join(filter(None, [e['note'], '相互动词，只用复数']))

    # 课件各课生词表：短语单列；单个词对到词条，本课新词加粗，前面学过的（前三册或第四册前面的课）单列一张表
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
        p = re.sub(r'\([^)]*\)', '', part).strip()      # cesar (de + inf.) 是一个词，括号里只是用法
        if '…' in p or '+' in p or part in VOCAB_PHRASE:
            return True
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
    # 前三册学过、第四册又有新意思的：第四册前面的课已经补过的新意思也写上
    for e in entries:
        parts = e['note'].split('，这里是新的意思', 1)
        if not (e['newsense'] and len(parts) == 2 and '学过（' in parts[0]):
            continue
        prev = sorted((o for o in entries if o['newsense'] and o['lemma'] == e['lemma'] and o['pos'] == e['pos'] and o['lesson'] < e['lesson']),
                      key=lambda o: o['lesson'])
        if prev:
            e['note'] = parts[0] + ''.join(f'、第 {o["lesson"]} 课学过（{o["zh"]}）' for o in prev) + '，这里是新的意思' + parts[1]
    seen, vphrases = defaultdict(list), defaultdict(list)
    used_seen_zh, used_vlem, used_seen_drop = set(), set(), set()

    def place(n, part, gloss, hit, hb1, split=False):
        """一条生词表条目对到的词条：本课新的加粗；前面学过的列进“生词表里前面学过的词”。
        split：poner(se) 这种拆开的一半，释义用那一条自己的（课件释义是两个词合写的）。"""
        hit = list({id(e): e for e in hit}.values())
        hb1 = list({(e['lemma'], e['pos']): e for e in hb1}.values())
        if re.match(r'(el|la|los|las) ', part):          # 带冠词的是名词
            nh = [e for e in hit if any(p.startswith(('m.', 'f.')) for p in e['pos'].split('；'))]
            nb = [e for e in hb1 if e['pos'].startswith(('m.', 'f.'))]
            if (hit or hb1) and not nh and not nb:        # 只对到形容词、动词：名词可能漏了（el seguro médico 的 seguro 保险）
                review.append(f'生词表带冠词的条目只对到非名词：第 {n} 课 {part} → ' +
                              '、'.join(f'{e["lemma"]}（{e["pos"]}）' for e in hit + hb1))
            hit, hb1 = nh or hit, nb or hb1
        if not hit and not hb1:
            if not split:
                review.append(f'生词表条目找不到词条：第 {n} 课 {part}')
            return
        new = [e for e in hit if e['lesson'] == n]
        for e in new:
            e['core'] = True
            # 第一册只在语音练习里出现过的词：释义用本课课件生词表的（ruido 噪音，响声）
            if e.get('phon') and not e.get('pinned_zh') and not split and gloss and len(new) == 1:
                e['zh'] = gloss.replace('，', '；') if e['pos'] == 'v.' else gloss
        if new:
            return
        later = [e for e in hit if e['lesson'] > n]
        earlier = [e for e in hit if e['lesson'] < n]
        if later and not hb1 and not earlier:
            review.append(f'生词表条目的词排在后面的课：第 {n} 课 {part} → ' + '、'.join(f'{e["lemma"]} 第 {e["lesson"]} 课' for e in later))
            return
        earlier = [e for e in hit if e['lesson'] < n]
        if not earlier and not split and gloss and not any(senses(gloss) & senses(e['zh_all']) for e in hb1):
            review.append(f'生词表释义和前三册不一样：第 {n} 课 {part}「{gloss}」，前三册 ' +
                          '；'.join(f'{e["lemma"]}（{e["pos"]}）「{e["zh_all"]}」' for e in hb1))
        both = bool(earlier and hb1)                      # 前三册学过、第四册前面的课又有了新意思：各注意思
        name = len(earlier) + len(hb1) > 1 and not both
        where = '、'.join(dict.fromkeys(
            [(f'{e["lemma"].split(",")[0]} ' if name else '') + e['where'] + (f'（{e["zh"]}）' if both else '') for e in hb1] +
            [(f'{e["lemma"].split(",")[0]} ' if name else '') + f'第 {e["lesson"]} 课' + (f'（{e["zh"]}）' if both else '') for e in earlier]))
        where = SEEN_WHERE.get((n, part), where)
        zh = '；'.join(dict.fromkeys(e['zh'] for e in hb1 + earlier)) if split or gloss is None else gloss
        if (n, part) in SEEN_ZH:
            used_seen_zh.add((n, part))
            zh = SEEN_ZH[(n, part)]
        if (n, part) in SEEN_DROP:
            used_seen_drop.add((n, part))
            return
        item = expand_fem(part)
        lems = {e['lemma'] for e in hb1 + earlier}
        if len(lems) == 1 and next(iter(lems)).startswith(item + ', '):     # 课件只写了阳性的（aburrido）照词条写全
            item = next(iter(lems))
        seen[n].append({'item': item, 'zh': zh, 'where': where})

    def look(cs):
        return [e for c in cs for e in lem_idx.get(c, [])], [e for c in cs for e in b1_lem.get(c, [])]

    for f in sorted(SRC.glob('L*.json')):
        j = json.loads(f.read_text('utf-8'))
        n = j['lesson']
        for txt, gloss0 in j['vocab']:
            parts = [p.strip() for p in txt.split(';') if p.strip()]
            # 第四册生词表常把派生词、短语写在括号里：agradecer (agradecido)〈感谢（感激的）〉、medio (por medio de)〈手段，媒介（借助，通过）〉。
            # 括号里的词单独对（本课新词加粗，前面学过的列进“前面学过的词”），释义按括号拆开；前置词、复数之类的说明照旧不拆
            pairs = []
            for part in parts:
                # sumar / restar〈加；减〉：两个词，各对各的（el / la descendiente 是一个词的两种冠词，不拆）
                xy = re.fullmatch(r'([a-záéíóúñü]+) / ([a-záéíóúñü]+)', part)
                if xy and not {xy[1], xy[2]} & ARTICLES and len(gloss0.split('；')) == 2:
                    pairs += [(xy[1], gloss0.split('；')[0]), (xy[2], gloss0.split('；')[1])]
                    continue
                m = re.fullmatch(r'(.+?)\s*\(([^()]+)\)', part)
                if len(parts) == 1 and m and not PAREN_KEEP.fullmatch(m[2].strip()):
                    gm = re.fullmatch(r'(.+?)（([^（）]+)）', gloss0)
                    # 释义没有括号的（aburrir(se) (aburrido)〈使厌烦；感到无聊〉），括号里的词释义用前面学过的（gloss 记 None）
                    pairs += [(m[1].strip(), gm[1] if gm else gloss0), (m[2].strip(), re.sub(r'^名：', '', gm[2]) if gm else None)]
                else:
                    pairs.append((part, gloss0))
            for part, gloss in pairs:
                if is_phrase(part):
                    vphrases[n].append({'es': part, 'zh': gloss or gloss0})
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
    assert used_seen_drop == SEEN_DROP, SEEN_DROP - used_seen_drop
    assert used_vlem == set(VOCAB_LEMMA), set(VOCAB_LEMMA) - used_vlem
    for e in entries:
        pin = ENTRY_PIN.get((e['lemma'], e['pos'], e['lesson'])) or ENTRY_PIN.get((e['lemma'], e.get('pos0'), e['lesson'])) or {}
        if 'core' in pin:
            e['core'] = pin['core']
        e.pop('pinned_zh', None)
        e.pop('pos0', None)

    # 释义括号里的搭配，词条本身写成 ～（（llamar a la puerta）→（～ a la puerta））
    for L0 in [entries]:
        for e in L0:
            h = e['lemma'].split(',')[0].strip()
            if len(h) >= 3 and ' ' not in h:
                e['zh'] = re.sub(r'（[^（）]*）', lambda m: re.sub(rf'(?<![\wáéíóúñü]){re.escape(h)}(?![\wáéíóúñü])', '～', m[0]), e['zh'])

    # 专有名词的新形式照原形大写（las dos Américas ← América）
    for x in newforms:
        if x['lemma'][:1].isupper():
            x['form'] = x['form'][:1].upper() + x['form'][1:]

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
    out = {'lessons': lessons, 'conj': conjs, 'prior_verbs': prior_verbs_index(),
           'haber_aux': {k: ha[k] for k in ('fut', 'cond', 'subj', 'sra', 'sse')},
           'newsense_examples': [f'{e["lemma"].split(",")[0]}“{e["zh"].split("；")[0]}”' for e in pick]}
    (DATA / 'vocab.json').write_text(json.dumps(out, ensure_ascii=False, indent=1), 'utf-8')
    (DATA / 'review.txt').write_text('\n'.join(review) + '\n', 'utf-8')
    nw = sum(len(L['words']) for L in lessons)
    print(f'词条 {nw}，动词 {sum(len(L["verbs"]) for L in lessons)}，动词形式 {sum(len(L["vforms"]) for L in lessons)}，'
          f'已学词的新形式 {sum(len(L["newforms"]) for L in lessons)}，生词表短语 {sum(len(L["vphrases"]) for L in lessons)}，'
          f'前三册动词索引 {len(out["prior_verbs"])}；要人工看的 {len(review)} 处')
    print(' '.join(f'{L["lesson"]}:{len(L["words"])}' for L in lessons))


main()
