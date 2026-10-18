"""Fill title_zh / zh / w / pos_legend / no_pause_commas / _说明 for c1_01..c1_10."""
import json
import sys
from pathlib import Path

ART = Path(sys.argv[1])

POS = {'m.': '阳性名词', 'f.': '阴性名词', 'adj.': '形容词', 'adv.': '副词', 'tr.': '及物动词', 'intr.': '不及物动词',
       'prnl.': '自复动词', 'prep.': '介词', 'conj.': '连词', 'num.': '数词', 'interj.': '感叹词', 'pron.': '代词',
       'loc.': '短语，固定搭配'}

COMMON = ('es：原文（原样，按句号切句）；zh：逐句中文翻译（书面语）；w：生词栏（全部为补充词条，source=supplement），'
          'h 词头（词典原形）、pos 词性（按句中用法）、zh 句中义释义、surface 句中原形（在句中恰好出现一次）；'
          '每句 4–5 个，侧重抽象词汇、论述性连接语、动词＋介词结构和名词化表达，不选一眼可懂的同源词；同一词头只在首次出现的句子列出。'
          'no_pause_commas：名词性列举（A, B y C）的逗号不停顿；并列的动词短语（谓语或不定式短语）按 es01 的先例'
          '（四级规则：较长的谓语并列仍然停顿）照常停顿；从句、句首状语、插入语两边照常停顿。')


def NP(after, why):
    return {'after': after, 'why': why}


DATA = {}

# ------------------------------------------------------------------ c1_01
DATA['c1_01'] = dict(
    title_zh='作为稀缺资源的注意力',
    note='本篇没有名词性列举，no_pause_commas 为 {}（第 2 句冒号、desde 前的逗号，第 6 句 por tanto 两边都照常停顿）。'
         '特别判断：第 2 句 no solo 后没有 sino también，而是用冒号承接，译作“不只是……：它们还……”；'
         'permanencia 指用户在平台上的停留时长；第 3 句 no…sino 的 sino 单列为 conj.。',
    npc={},
    sents=[
        ('在以信息为基础的经济中，注意力已经成为一种被争夺的资源。', [
            ('basado en', 'loc.', '以……为基础的', 'basada en'),
            ('convertirse en', 'loc.', '变成，成为', 'se ha convertido en'),
            ('recurso', 'm.', '资源', 'recurso'),
            ('disputado', 'adj.', '被争夺的', 'disputado'),
        ]),
        ('数字平台不只是提供内容：它们还设计了从消息通知到自动播放等种种机制，用来延长我们的停留时间。', [
            ('no solo', 'loc.', '不仅，不只', 'no solo'),
            ('destinado a', 'loc.', '旨在，用于', 'destinados a'),
            ('prolongar', 'tr.', '延长', 'prolongar'),
            ('permanencia', 'f.', '停留，逗留', 'permanencia'),
            ('reproducción automática', 'f.', '自动播放', 'reproducción automática'),
        ]),
        ('其结果未必是普遍的专注力丧失，而是一个系统性地将专注切割得支离破碎的环境。', [
            ('incapacidad', 'f.', '无能力，不能', 'incapacidad'),
            ('sino', 'conj.', '（no…sino）而是', 'sino'),
            ('entorno', 'm.', '环境', 'entorno'),
            ('fragmentar', 'tr.', '使碎片化，割裂', 'fragmenta'),
            ('de manera sistemática', 'loc.', '系统性地', 'de manera sistemática'),
        ]),
        ('面对这种态势，把全部责任都归于个人是不够的。', [
            ('frente a', 'loc.', '面对，针对', 'Frente a'),
            ('dinámica', 'f.', '态势，动态', 'dinámica'),
            ('atribuir', 'tr.', '把……归于', 'atribuir'),
            ('resultar', 'intr.', '（+adj.）显得，是', 'resulta'),
        ]),
        ('教育可以培养专注的习惯，但也有必要探讨服务的设计，以及那些奖励屏幕使用时长的经济激励机制。', [
            ('fomentar', 'tr.', '促进，培养', 'fomentar'),
            ('debatir sobre', 'loc.', '就……进行讨论', 'debatir sobre'),
            ('incentivo', 'm.', '激励（措施）', 'incentivos'),
            ('premiar', 'tr.', '奖励', 'premian'),
            ('tiempo de pantalla', 'm.', '屏幕使用时间', 'tiempo de pantalla'),
        ]),
        ('因此，要找回注意力，既需要个人的抉择，也需要结构性的变革。', [
            ('recuperar', 'tr.', '找回，恢复', 'Recuperar'),
            ('exigir', 'tr.', '要求，需要', 'exige'),
            ('por tanto', 'loc.', '因此', 'por tanto'),
            ('estructural', 'adj.', '结构性的', 'estructurales'),
        ]),
    ])

# ------------------------------------------------------------------ c1_02
DATA['c1_02'] = dict(
    title_zh='互联互通的悖论',
    note='特别判断：第 1 句 Nunca había sido tan 作为过去完成时结构整体列出（从未如此……过）；'
         '第 5 句 depender menos de… que de… 译作“与其说取决于……不如说取决于……”；'
         'disponibilidad mutua 指彼此随时能为对方腾出时间、作出回应，意译为“彼此的随时相伴”。',
    npc={'5': [NP('la atención,', '列举：la atención, la confianza y la disponibilidad mutua（A, B y C）')]},
    sents=[
        ('与远在数千公里之外的人沟通，从未像今天这样简单；然而，联系的便利并不能保证关系的深度。', [
            ('nunca había sido tan + adj.', 'loc.', '从未如此……过', 'Nunca había sido tan'),
            ('a miles de kilómetros', 'loc.', '在数千公里之外', 'a miles de kilómetros'),
            ('sin embargo', 'loc.', '然而', 'sin embargo'),
            ('facilidad', 'f.', '容易，便利', 'facilidad'),
            ('vínculo', 'm.', '纽带，（人际）关系', 'vínculos'),
        ]),
        ('数字通信让人们得以维系珍贵的关系，尤其是在距离使人难以经常见面的时候。', [
            ('mantener', 'tr.', '维持，维系', 'mantener'),
            ('valioso', 'adj.', '宝贵的，珍贵的', 'valiosas'),
            ('impedir', 'tr.', '阻碍，使无法', 'impide'),
            ('encuentro', 'm.', '见面，相聚', 'encuentros'),
        ]),
        ('与此同时，大量的互动可能营造出一种亲近的错觉，而这种错觉并不总能转化为真正的支持。', [
            ('al mismo tiempo', 'loc.', '与此同时', 'Al mismo tiempo'),
            ('abundancia', 'f.', '大量，丰富', 'abundancia'),
            ('ilusión', 'f.', '错觉，幻觉', 'ilusión'),
            ('cercanía', 'f.', '亲近，接近', 'cercanía'),
            ('traducirse en', 'loc.', '转化为，体现为', 'se traduce en'),
        ]),
        ('问题的关键不在于美化过去，也不在于排斥新技术，而在于认识到每一种媒介都有利于某些特定的关系形式。', [
            ('consistir en', 'loc.', '在于', 'consiste en'),
            ('rechazar', 'tr.', '拒绝，排斥', 'rechazar'),
            ('medio', 'm.', '媒介，手段', 'medio'),
            ('favorecer', 'tr.', '有利于，促成', 'favorece'),
            ('determinado', 'adj.', '（前置）某些，特定的', 'determinadas'),
        ]),
        ('一段关系的质量，与其说取决于消息的多少，不如说取决于维系它的关注、信任和彼此的随时相伴。', [
            ('depender menos de… que de…', 'loc.', '与其说取决于…不如说…', 'depende menos de'),
            ('disponibilidad', 'f.', '随时相伴，有空', 'disponibilidad'),
            ('mutuo', 'adj.', '相互的', 'mutua'),
            ('sostener', 'tr.', '支撑，维系', 'sostienen'),
        ]),
    ])

# ------------------------------------------------------------------ c1_03
DATA['c1_03'] = dict(
    title_zh='作为协商空间的城市',
    note='特别判断：第 2 句开头的名词列举登记为不停顿；第 5 句 hace visibles…, escucha…, evalúa… 是三个并列谓语，'
         '按四级规则照常停顿；第 4 句 reducir algo a 的 a 与动词不相邻，surface 只标 Reducir；'
         '第 3 句 quienes 指“（步行的）人”，词头写 quien。',
    npc={'2': [NP('Residentes,', '列举：Residentes, comerciantes, turistas, conductores y peatones（名词并列）'),
               NP('comerciantes,', '同上，列举的第二个逗号'),
               NP('turistas,', '同上，列举的第三个逗号')]},
    sents=[
        ('城市不只是建筑与基础设施的集合；它是一个不同群体围绕有限资源的使用不断进行协商的空间。', [
            ('simplemente', 'adv.', '仅仅，只不过', 'simplemente'),
            ('conjunto', 'm.', '集合，整体', 'conjunto'),
            ('infraestructura', 'f.', '基础设施', 'infraestructuras'),
            ('negociar', 'tr.', '协商，谈判', 'negocian'),
        ]),
        ('居民、商户、游客、司机和行人都可能有正当的利益诉求，然而这些利益却会彼此冲突。', [
            ('comerciante', 'm.', '商户，商人', 'comerciantes'),
            ('conductor', 'm.', '司机，驾驶员', 'conductores'),
            ('peatón', 'm.', '行人', 'peatones'),
            ('legítimo', 'adj.', '正当的，合理的', 'legítimos'),
            ('entrar en conflicto', 'loc.', '发生冲突', 'entran en conflicto'),
        ]),
        ('例如，扩大步行区能改善步行者的体验，但也可能引起那些依赖车辆通行的商家的担忧。', [
            ('zona peatonal', 'f.', '步行区', 'zonas peatonales'),
            ('quien', 'pron.', '（……的）人', 'quienes'),
            ('suscitar', 'tr.', '引起，激起', 'suscitar'),
            ('negocio', 'm.', '商家，店铺', 'negocios'),
            ('depender de', 'loc.', '依赖，取决于', 'dependen del'),
        ]),
        ('把这些争论简化为进步与抵制之间的对立，会妨碍人们理解其复杂性。', [
            ('reducir algo a', 'loc.', '把……简化为', 'Reducir'),
            ('oposición', 'f.', '对立', 'oposición'),
            ('resistencia', 'f.', '抵制，阻力', 'resistencia'),
            ('impedir', 'tr.', '妨碍，使无法', 'impide'),
        ]),
        ('最稳健的城市规划，是那种让每种方案的成本与收益清晰可见、倾听受影响者的意见，并在措施实施之后评估其效果的规划。', [
            ('sólido', 'adj.', '稳健的，扎实的', 'sólida'),
            ('aquel que', 'pron.', '那种……的（人或物）', 'aquella que'),
            ('hacer visible', 'loc.', '使……清晰可见', 'hace visibles'),
            ('afectado', 'm.', '受影响者', 'afectados'),
            ('aplicar medidas', 'loc.', '实施措施', 'aplicar las medidas'),
        ]),
    ])

# ------------------------------------------------------------------ c1_04
DATA['c1_04'] = dict(
    title_zh='语言与身份认同',
    note='特别判断：第 4 句 más bien 承接否定，译作“更确切地说”；al ofrecer 的 al + inf. 表方式，译作“通过”；'
         '第 5 句 preguntar, revisar… y aprender… 是并列的不定式短语，按四级规则照常停顿；'
         'competencia 在此是“能力”（不是“竞争”）。',
    npc={'2': [NP('convenciones sociales,', '列举：convenciones sociales, referencias culturales y maneras particulares…（名词短语并列）')]},
    sents=[
        ('学习一门外语所涉及的，远不止背单词、掌握语法结构。', [
            ('lengua extranjera', 'f.', '外语', 'lengua extranjera'),
            ('implicar', 'tr.', '意味着，涉及', 'implica'),
            ('mucho más que', 'loc.', '远不止', 'mucho más que'),
            ('dominar', 'tr.', '掌握，精通', 'dominar'),
        ]),
        ('它还意味着接触种种社会惯例、文化典故，以及组织经验的独特方式。', [
            ('suponer', 'tr.', '意味着', 'supone'),
            ('entrar en contacto con', 'loc.', '接触', 'entrar en contacto con'),
            ('convención', 'f.', '惯例，常规', 'convenciones'),
            ('referencia cultural', 'f.', '文化典故，文化参照', 'referencias culturales'),
            ('particular', 'adj.', '特有的，独特的', 'particulares'),
        ]),
        ('学习另一门语言的人可能会发现，某些想法在表达时带有难以翻译的细微差别，或者同一句话会因语境不同而产生不同的含义。', [
            ('quien', 'pron.', '（泛指）……的人', 'Quien'),
            ('cierto', 'adj.', '（前置）某些', 'ciertas'),
            ('matiz', 'm.', '细微差别', 'matices'),
            ('difícil de + inf.', 'loc.', '难以……的', 'difíciles de'),
            ('adquirir', 'tr.', '获得，具有', 'adquiere'),
        ]),
        ('这一过程并不迫使人放弃自身的身份认同；更确切地说，它能通过提供新的视角来拓展这种认同。', [
            ('obligar a + inf.', 'loc.', '迫使（做某事）', 'obliga a'),
            ('propio', 'adj.', '（后置）自己的', 'propia'),
            ('más bien', 'loc.', '更确切地说，而是', 'más bien'),
            ('ampliar', 'tr.', '扩大，拓展', 'ampliarla'),
            ('al + inf.', 'loc.', '通过……；在……时', 'al ofrecer'),
        ]),
        ('当说话者接受自己有可能误解某个情境，并愿意提问、反思自己的预设、从互动中学习时，跨文化能力便由此产生。', [
            ('competencia intercultural', 'f.', '跨文化能力', 'competencia intercultural'),
            ('surgir', 'intr.', '产生，出现', 'surge'),
            ('interpretar mal', 'loc.', '误解，曲解', 'interpretar mal'),
            ('estar dispuesto a', 'loc.', '愿意（做某事）', 'está dispuesto a'),
            ('suposición', 'f.', '假设，预设', 'suposiciones'),
        ]),
    ])

# ------------------------------------------------------------------ c1_05
DATA['c1_05'] = dict(
    title_zh='工作与人生意义',
    note='特别判断：第 3 句后半句省略了 puede interpretarse（el fracaso profesional [puede interpretarse] como…），'
         '译文补出“也可能被看作”；第 4 句 convertirlo 的 lo 指 trabajo，译作“把工作变成”；'
         'realizar 是“从事、进行”，不是“意识到”。',
    npc={'2': [NP('propósito,', '列举：propósito, reconocimiento y pertenencia（A, B y C）')],
         '5': [NP('Las relaciones,', '列举：Las relaciones, la participación comunitaria, el aprendizaje y el ocio（名词并列）'),
               NP('la participación comunitaria,', '同上，列举的第二个逗号')]},
    sents=[
        ('有些社会里，职业往往是人们向他人介绍自己的主要方式之一；在这样的社会中，工作与身份认同之间的关系日益紧密。', [
            ('intensificarse', 'prnl.', '加强，加剧', 'se ha intensificado'),
            ('soler + inf.', 'loc.', '通常，往往', 'suele'),
            ('funcionar como', 'loc.', '充当，起……作用', 'funcionar como'),
            ('presentarse', 'prnl.', '介绍自己，亮相', 'presentarse'),
            ('ante los demás', 'loc.', '在别人面前', 'ante los demás'),
        ]),
        ('这种关联能带来目标感、认可和归属感，但当一个人失去工作或经历一段身心耗竭的时期时，它也会让人变得脆弱。', [
            ('aportar', 'tr.', '带来，提供', 'aportar'),
            ('reconocimiento', 'm.', '认可，承认', 'reconocimiento'),
            ('pertenencia', 'f.', '归属（感）', 'pertenencia'),
            ('atravesar', 'tr.', '经历，度过', 'atraviesa'),
            ('agotamiento', 'm.', '精疲力竭，倦怠', 'agotamiento'),
        ]),
        ('如果个人价值完全以生产效率来衡量，那么休息就可能被视为懒惰，职业上的失败也可能被看作个人的缺陷。', [
            ('medirse por', 'loc.', '以……来衡量', 'se mide'),
            ('interpretarse como', 'loc.', '被理解为，被视为', 'interpretarse como'),
            ('pereza', 'f.', '懒惰', 'pereza'),
            ('fracaso', 'm.', '失败', 'fracaso'),
        ]),
        ('有必要区分两件事：从事一份有意义的工作，和把工作变成意义的唯一来源。', [
            ('convenir', 'intr.', '（+inf.）宜，最好', 'Conviene'),
            ('distinguir entre', 'loc.', '区分，辨别', 'distinguir entre'),
            ('realizar', 'tr.', '从事，进行', 'realizar'),
            ('convertir algo en', 'loc.', '把……变成', 'convertirlo en'),
            ('fuente', 'f.', '来源，源泉', 'fuente'),
        ]),
        ('人际关系、社区参与、学习和休闲，同样有助于成就充实的人生。', [
            ('aprendizaje', 'm.', '学习（过程）', 'aprendizaje'),
            ('ocio', 'm.', '休闲，闲暇', 'ocio'),
            ('contribuir a', 'loc.', '有助于，促成', 'contribuyen a'),
            ('pleno', 'adj.', '充实的，圆满的', 'plena'),
        ]),
    ])

# ------------------------------------------------------------------ c1_06
DATA['c1_06'] = dict(
    title_zh='集体记忆及其沉默',
    note='特别判断：第 2 句 que determinan 的先行词理解为前面列举的全部因素（语法上也可只指 decisiones políticas），'
         '译文按前者处理；第 4 句 sustituir A por B 是“用 B 取代 A”，注意方向；'
         '第 4 句 ampliar…, reconocer… y diferenciar… 是并列的不定式短语，按四级规则照常停顿；'
         '第 5 句较短，只列 4 个。',
    npc={'2': [NP('relatos familiares,', '列举：relatos familiares, monumentos, celebraciones, instituciones educativas y decisiones políticas（名词并列）'),
               NP('monumentos,', '同上，列举的第二个逗号'),
               NP('celebraciones,', '同上，列举的第三个逗号')]},
    sents=[
        ('集体记忆并不是一座让所有事件都占据同等位置的中立档案馆。', [
            ('memoria colectiva', 'f.', '集体记忆', 'memoria colectiva'),
            ('archivo', 'm.', '档案（馆）', 'archivo'),
            ('en el que', 'loc.', '在其中（关系从句）', 'en el que'),
            ('acontecimiento', 'm.', '（重大）事件', 'acontecimientos'),
        ]),
        ('它是通过家族讲述、纪念碑、庆典、教育机构以及政治决策建构起来的，这些因素决定了什么被铭记、什么被置于边缘。', [
            ('construirse', 'prnl.', '被建构，形成', 'Se construye'),
            ('mediante', 'prep.', '通过，借助', 'mediante'),
            ('relato', 'm.', '叙述，讲述', 'relatos'),
            ('quedar al margen', 'loc.', '被边缘化，被排除', 'queda al margen'),
        ]),
        ('因此，重新审视公共历史可能引发分歧：人们争论的不只是事实，还有一个社会希望传承的身份认同与价值观。', [
            ('por ello', 'loc.', '因此', 'Por ello'),
            ('revisar', 'tr.', '重新审视，修订', 'revisar'),
            ('desacuerdo', 'm.', '分歧，异议', 'desacuerdos'),
            ('no solo… sino también…', 'loc.', '不仅……而且……', 'no solo'),
            ('transmitir', 'tr.', '传递，传承', 'transmitir'),
        ]),
        ('解决之道不在于用另一种同样封闭的叙事取代单一叙事，而在于拓宽史料来源、承认以往被忽视的经历，并把历史研究与宣传性的简单化区分开来。', [
            ('consistir en', 'loc.', '在于', 'consiste en'),
            ('sustituir A por B', 'loc.', '用B取代A', 'sustituir'),
            ('ignorado', 'adj.', '被忽视的', 'ignoradas'),
            ('diferenciar A de B', 'loc.', '把A与B区分开', 'diferenciar'),
            ('propagandístico', 'adj.', '宣传性的', 'propagandística'),
        ]),
        ('民主的记忆需要多元性与严谨性。', [
            ('memoria democrática', 'f.', '民主记忆', 'memoria democrática'),
            ('necesitar', 'tr.', '需要', 'necesita'),
            ('pluralidad', 'f.', '多元性', 'pluralidad'),
            ('rigor', 'm.', '严谨，严密', 'rigor'),
        ]),
    ])

# ------------------------------------------------------------------ c1_07
DATA['c1_07'] = dict(
    title_zh='超越个人层面的可持续性',
    note='特别判断：第 1 句 como 后面三个不定式短语（reducir…, separar… o utilizar…）按四级规则照常停顿；'
         '第 5 句 hagan 是虚拟式（que 引导的关系从句表目的、结果）；administraciones 指各级政府部门；'
         'separar residuos 译作“垃圾分类”。',
    npc={'4': [NP('ciudadanos,', '列举：ciudadanos, empresas y administraciones（A, B y C）')],
         '5': [NP('inversiones,', '列举：inversiones, regulación e innovación（A, B y C）')]},
    sents=[
        ('可持续发展的宣传活动往往聚焦于个人行动，比如减少用水、垃圾分类或使用可重复使用的购物袋。', [
            ('campaña', 'f.', '运动，宣传活动', 'campañas'),
            ('soler + inf.', 'loc.', '通常，往往', 'suelen'),
            ('concentrarse en', 'loc.', '集中于，聚焦于', 'concentrarse en'),
            ('separar residuos', 'loc.', '垃圾分类', 'separar residuos'),
            ('reutilizable', 'adj.', '可重复使用的', 'reutilizables'),
        ]),
        ('这些做法固然有其价值，但当基础设施和生产模式保持原封不动时，它们的作用范围就很有限。', [
            ('alcance', 'm.', '影响范围，作用', 'alcance'),
            ('infraestructura', 'f.', '基础设施', 'infraestructuras'),
            ('modelo de producción', 'm.', '生产模式', 'modelos de producción'),
            ('permanecer', 'intr.', '保持，仍然（处于）', 'permanecen'),
            ('intacto', 'adj.', '原封不动的', 'intactos'),
        ]),
        ('一个人也许想乘坐公共交通出行，却发现没有合理的交通衔接；也许想购买经久耐用的产品，却遇上高得令人望而却步的价格。', [
            ('desplazarse', 'prnl.', '出行，移动', 'desplazarse'),
            ('conexión', 'f.', '（交通）衔接，线路', 'conexión'),
            ('duradero', 'adj.', '耐用的', 'duraderos'),
            ('encontrarse con', 'loc.', '遇到，碰上', 'encontrarse con'),
            ('prohibitivo', 'adj.', '（价格）高得难以承受', 'prohibitivos'),
        ]),
        ('因此，环境责任应当由公民、企业和政府部门共同分担。', [
            ('por tanto', 'loc.', '因此', 'Por tanto'),
            ('ambiental', 'adj.', '环境的', 'ambiental'),
            ('distribuirse', 'prnl.', '（被）分摊，分配', 'distribuirse'),
            ('administración', 'f.', '政府部门，行政机构', 'administraciones'),
        ]),
        ('变革需要日常的抉择，但也需要投资、监管与创新，让人们能够选择影响更小的方案，同时不把过高的成本强加给资源较少的人。', [
            ('cotidiano', 'adj.', '日常的', 'cotidianas'),
            ('hacer posible', 'loc.', '使……成为可能', 'hagan posible'),
            ('imponer', 'tr.', '强加', 'imponer'),
            ('desproporcionado', 'adj.', '不成比例的，过高的', 'desproporcionados'),
            ('disponer de', 'loc.', '拥有，具备', 'disponen de'),
        ]),
    ])

# ------------------------------------------------------------------ c1_08
DATA['c1_08'] = dict(
    title_zh='对信息的信任',
    note='特别判断：第 5 句 disciplina 指上一句所说的一整套求证做法，意译为“严谨的求证习惯”；'
         '第 3 句 que la repita 为虚拟式（先行词是不确定的“某篇报道”）；'
         '第 4 句 identificar…, comprobar…, distinguir… y considerar… 是并列的不定式短语，按四级规则照常停顿；'
         'prueba 在此是“证据”，不是“考试”。',
    npc={},
    sents=[
        ('信息的丰富并不能消除不确定性；有时，它反而会使不确定性倍增。', [
            ('abundancia', 'f.', '大量，丰富', 'abundancia'),
            ('incertidumbre', 'f.', '不确定性', 'incertidumbre'),
            ('en ocasiones', 'loc.', '有时', 'en ocasiones'),
            ('multiplicar', 'tr.', '使倍增', 'multiplica'),
        ]),
        ('新闻以极快的速度传播，而那些专为激起愤慨或恐惧而设计的内容，可能比细致入微的解释传播得更广。', [
            ('circular', 'intr.', '流传，传播', 'circulan'),
            ('a gran velocidad', 'loc.', '以极快的速度', 'a gran velocidad'),
            ('indignación', 'f.', '愤慨，义愤', 'indignación'),
            ('difundirse', 'prnl.', '传播，扩散', 'difundirse'),
            ('matizado', 'adj.', '细致入微的', 'matizadas'),
        ]),
        ('面对这种局面，核实一个说法所需要的，不只是再找一篇重复该说法的报道。', [
            ('ante', 'prep.', '面对，在……面前', 'Ante'),
            ('panorama', 'm.', '局面，形势', 'panorama'),
            ('afirmación', 'f.', '说法，断言', 'afirmación'),
            ('algo más que', 'loc.', '不仅仅是', 'algo más que'),
            ('repetir', 'tr.', '重复（虚拟式）', 'repita'),
        ]),
        ('我们必须找出原始出处、核对日期、把数据与解读区分开来，并思考哪些证据可能推翻这一结论。', [
            ('fuente original', 'f.', '原始出处', 'fuente original'),
            ('comprobar', 'tr.', '核对，查证', 'comprobar'),
            ('distinguir A de B', 'loc.', '把A与B区分开', 'distinguir'),
            ('prueba', 'f.', '证据', 'pruebas'),
            ('refutar', 'tr.', '驳倒，推翻', 'refutar'),
        ]),
        ('这种严谨的求证习惯并不能保证绝对的确定，但能降低因为熟悉或意识形态上的亲近而接受某个说法的可能性。', [
            ('disciplina', 'f.', '严格的做法，自律', 'disciplina'),
            ('certeza', 'f.', '确定（性）', 'certeza'),
            ('familiaridad', 'f.', '熟悉，熟识', 'familiaridad'),
            ('afinidad ideológica', 'f.', '意识形态上的亲近', 'afinidad ideológica'),
        ]),
        ('媒介素养应当被视为一项基本的公民能力。', [
            ('alfabetización mediática', 'f.', '媒介素养', 'alfabetización mediática'),
            ('deber + inf.', 'loc.', '（条件式）应当', 'debería'),
            ('entenderse como', 'loc.', '被理解为，被视为', 'entenderse como'),
            ('competencia ciudadana', 'f.', '公民能力', 'competencia ciudadana'),
        ]),
    ])

# ------------------------------------------------------------------ c1_09
DATA['c1_09'] = dict(
    title_zh='创新及其意外后果',
    note='特别判断：第 4 句 aunque sí 中的 sí 起强调作用，译作“不过……确实”；'
         '第 3 句 transformar empleos y desigualdades 意译为“重塑就业与不平等的格局”；'
         '第 5 句 reconocerlo, distribuir… y aprender… 是并列的不定式短语，按四级规则照常停顿；'
         'datos sensibles 是“敏感数据”（sensible 不是“明智的”），evidencia 在此是“证据”。',
    npc={'1': [NP('mayor eficiencia,', '列举：mayor eficiencia, reducción de costes o creación de nuevos servicios（名词短语并列）')],
         '4': [NP('evaluación,', '列举：evaluación, transparencia y corrección（A, B y C）')]},
    sents=[
        ('创新通常依据其直接收益来评价：更高的效率、更低的成本，或是新服务的创造。', [
            ('soler + inf.', 'loc.', '通常，往往', 'suele'),
            ('a partir de', 'loc.', '依据，根据', 'a partir de'),
            ('beneficio', 'm.', '好处，收益', 'beneficios'),
            ('reducción de costes', 'f.', '成本降低', 'reducción de costes'),
        ]),
        ('然而，一项技术可能会产生一些副作用，而这些副作用只有在大规模采用时才会显现出来。', [
            ('sin embargo', 'loc.', '然而', 'Sin embargo'),
            ('efecto secundario', 'm.', '副作用', 'efectos secundarios'),
            ('hacerse visible', 'loc.', '显现，变得明显', 'se hacen visibles'),
            ('adoptar', 'tr.', '采用', 'adopta'),
            ('a gran escala', 'loc.', '大规模地', 'a gran escala'),
        ]),
        ('一款方便人们获取某项服务的应用，同时也可能把敏感数据集中起来；一种将任务自动化的工具可以腾出时间，但也可能重塑就业与不平等的格局。', [
            ('al mismo tiempo', 'loc.', '与此同时', 'al mismo tiempo'),
            ('dato sensible', 'm.', '敏感数据', 'datos sensibles'),
            ('herramienta', 'f.', '工具', 'herramienta'),
            ('liberar tiempo', 'loc.', '腾出时间', 'liberar tiempo'),
            ('desigualdad', 'f.', '不平等', 'desigualdades'),
        ]),
        ('预见所有后果是不可能的，不过，设计评估、透明与纠错机制确实是合理的。', [
            ('anticipar', 'tr.', '预见，预料', 'Anticipar'),
            ('aunque sí', 'loc.', '不过……确实', 'aunque sí'),
            ('resultar', 'intr.', '（+adj.）显得，是', 'resulta'),
            ('corrección', 'f.', '纠正，修正', 'corrección'),
        ]),
        ('负责任的创新不在于规避风险，而在于正视风险、公平地分摊其代价，并从证据中学习。', [
            ('consistir en', 'loc.', '在于', 'consiste en'),
            ('reconocer', 'tr.', '承认，正视', 'reconocerlo'),
            ('distribuir', 'tr.', '分配，分摊', 'distribuir'),
            ('de manera justa', 'loc.', '公平地', 'de manera justa'),
            ('evidencia', 'f.', '证据', 'evidencia'),
        ]),
    ])

# ------------------------------------------------------------------ c1_10
DATA['c1_10'] = dict(
    title_zh='作为抵抗方式的耐心',
    note='特别判断：第 2 句 resistirse a abandonar… 意译为“克制住……放弃……的冲动”；'
         '第 3 句 Aprender una lengua, investigar… o construir… 是并列的不定式短语，按四级规则照常停顿，'
         '后面 repetición, revisión y tolerancia 是名词列举，登记为不停顿；第 5 句 Su valor 的 su 指耐心。',
    npc={'3': [NP('repetición,', '列举：repetición, revisión y tolerancia a la incertidumbre（A, B y C）')]},
    sents=[
        ('在一个推崇速度的环境里，耐心可能看起来像是一种被动的美德。', [
            ('valorar', 'tr.', '重视，推崇', 'valora'),
            ('rapidez', 'f.', '快速，迅速', 'rapidez'),
            ('parecer', 'intr.', '显得，看起来', 'parecer'),
            ('virtud', 'f.', '美德', 'virtud'),
        ]),
        ('然而，在一项复杂的任务上坚持不懈，意味着一个主动的抉择：克制住因成果不能立竿见影就放弃整个过程的冲动。', [
            ('no obstante', 'loc.', '然而，不过', 'No obstante'),
            ('perseverar en', 'loc.', '坚持（做）', 'perseverar en'),
            ('implicar', 'tr.', '意味着', 'implica'),
            ('resistirse a', 'loc.', '抗拒，不肯（做）', 'resistirse a'),
        ]),
        ('学习一门语言、研究一个问题或建立一段互信的关系，都需要重复、修正，以及对不确定性的包容。', [
            ('relación de confianza', 'f.', '互信关系', 'relación de confianza'),
            ('requerir', 'tr.', '需要，要求', 'requiere'),
            ('revisión', 'f.', '检查修正，复查', 'revisión'),
            ('tolerancia a', 'f.', '对……的容忍', 'tolerancia a'),
            ('incertidumbre', 'f.', '不确定性', 'incertidumbre'),
        ]),
        ('耐心也不应被混同于接受不公正的条件，或是无限期地拖延一个必要的决定。', [
            ('tampoco', 'adv.', '也不', 'tampoco'),
            ('confundirse con', 'loc.', '与……混淆', 'confundirse con'),
            ('posponer', 'tr.', '推迟，拖延', 'posponer'),
            ('indefinidamente', 'adv.', '无限期地', 'indefinidamente'),
        ]),
        ('耐心的价值在于分清无谓的拖延与一个过程发展所需的时间。', [
            ('residir en', 'loc.', '在于', 'reside en'),
            ('distinguir entre', 'loc.', '区分，辨别', 'distinguir entre'),
            ('demora', 'f.', '拖延，耽搁', 'demora'),
            ('improductivo', 'adj.', '无成效的，徒劳的', 'improductiva'),
            ('desarrollarse', 'prnl.', '发展，展开', 'desarrollarse'),
        ]),
        ('面对必须不断拿出成果的压力，耐心让人得以守护深度工作，并看到那些并不总是显而易见的进步。', [
            ('frente a', 'loc.', '面对', 'Frente a'),
            ('presión por + inf.', 'f.', '（急于）做……的压力', 'presión por'),
            ('permitir', 'tr.', '使能够，让', 'permite'),
            ('trabajo profundo', 'm.', '深度工作', 'trabajo profundo'),
            ('avance', 'm.', '进展，进步', 'avances'),
        ]),
    ])


def dump(p):
    """indent=1 like the skeleton, but each vocabulary item on one line (like es02.json)."""
    items = {}
    for para in p['paras']:
        for s in para:
            new = []
            for w in s['w']:
                key = f'@@W{len(items)}@@'
                items[key] = json.dumps(w, ensure_ascii=False)
                new.append(key)
            s['w'] = new
    txt = json.dumps(p, ensure_ascii=False, indent=1)
    for key, val in items.items():
        txt = txt.replace(f'"{key}"', val)
    return txt + '\n'


for pid, d in DATA.items():
    path = ART / f'{pid}.json'
    p = json.loads(path.read_text('utf-8'))
    sents = [s for para in p['paras'] for s in para]
    assert len(sents) == len(d['sents']), (pid, len(sents), len(d['sents']))
    used = set()
    for s, (zh, ws) in zip(sents, d['sents']):
        s['zh'] = zh
        s['w'] = []
        for h, pos, gz, sf in ws:
            assert pos in POS, (pid, h, pos)
            used.add(pos)
            s['w'].append({'h': h, 'pos': pos, 'zh': gz, 'surface': sf, 'source': 'supplement'})
    p['title_zh'] = d['title_zh']
    p['pos_legend'] = {t: POS[t] for t in POS if t in used}
    p['no_pause_commas'] = d['npc']
    no = p['no']
    p['_说明'] = (f'西班牙语分级阅读文章集（用户 2026-10-18 发来的 Word 文档《西班牙语A1-C1分级阅读文章集》）C1 第 {no} 篇'
                 f'《{p["title_es"]} {d["title_zh"]}》。' + COMMON + d['note'])
    path.write_text(dump(p), 'utf-8')
    print(pid, 'written', len(sents), 'sentences')
