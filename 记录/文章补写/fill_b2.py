import json
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parents[2]   # 工具包根目录（本文件在 记录/文章补写/ 下）
DIR = KIT / '西班牙语' / '文章'
POS = {'m.': '阳性名词', 'f.': '阴性名词', 'adj.': '形容词', 'adv.': '副词', 'tr.': '及物动词', 'intr.': '不及物动词',
       'prnl.': '自复动词', 'prep.': '介词', 'conj.': '连词', 'num.': '数词', 'interj.': '感叹词', 'pron.': '代词',
       'loc.': '短语，固定搭配'}
DONE = ('zh：逐句中文翻译；w：生词栏（全部为补充词条，source=supplement），h 词头（词典原形）、pos 词性、zh 释义（取句中义）、'
        'surface 句中原样写法（在句中恰好出现一次）；同一词头只在第一次出现的句子里列。'
        'no_pause_commas：只登记列举（A, B y C）处不停顿的逗号，从句、句首状语、no…sino、mientras que 前的逗号照常停顿。')

A = {}

A['b2_01'] = dict(
    title_zh='弹性工作：机遇与挑战',
    note='conciliación 在这里指工作与家庭生活的兼顾（conciliación de la vida laboral y familiar），译作“兼顾工作与家庭”；'
         'desplazamientos 指上下班往返，译作“通勤”；disponibilidad permanente 译作“随时待命”；'
         'la vida profesional y la personal 中 la personal 省略了 vida，译作“个人生活”。本篇没有列举逗号，no_pause_commas 为空。',
    npc={},
    s=[
        ('数字工具的发展，让许多人得以在家办公，或者把办公室和其他场所结合起来工作。', [
            ('herramienta', 'f.', '工具', 'herramientas'),
            ('permitir que + subj.', 'loc.', '使得，让（后接虚拟式）', 'ha permitido que'),
            ('trabajar desde casa', 'loc.', '在家办公', 'trabajen desde casa'),
            ('combinar', 'tr.', '结合，兼顾', 'combinen'),
        ]),
        ('这种灵活性可以减少通勤，也便于兼顾工作与家庭，但同时也模糊了职业生活与个人生活之间的界限。', [
            ('desplazamiento', 'm.', '通勤，往返路程', 'desplazamientos'),
            ('facilitar', 'tr.', '使便利，促进', 'facilitar'),
            ('conciliación', 'f.', '工作与家庭的兼顾', 'conciliación'),
            ('difuminar', 'tr.', '使模糊，淡化', 'difumina'),
            ('frontera', 'f.', '界限，边界', 'frontera'),
        ]),
        ('当工作消息随时都可能发来时，员工可能会觉得自己的工作日永远没有尽头。', [
            ('laboral', 'adj.', '工作的，劳动的', 'laborales'),
            ('a cualquier hora', 'loc.', '随时，任何时候', 'a cualquier hora'),
            ('trabajador', 'm.', '劳动者，员工', 'trabajador'),
            ('jornada', 'f.', '工作日，一天的工作', 'jornada'),
        ]),
        ('因此，灵活性不应被混同于随时待命。', [
            ('por ello', 'loc.', '因此，所以', 'Por ello'),
            ('deber + inf.', 'loc.', '应当（条件式语气委婉）', 'debería'),
            ('confundirse con', 'loc.', '与……混淆，混同于', 'confundirse con'),
            ('disponibilidad', 'f.', '随时待命，可供调用', 'disponibilidad'),
        ]),
        ('企业需要设定明确的预期，而员工则要学会安排自己的时间，守护好自己的休息时间。', [
            ('establecer', 'tr.', '设立，确立', 'establecer'),
            ('expectativa', 'f.', '期望，预期', 'expectativas'),
            ('mientras que', 'loc.', '而，然而（表对比）', 'mientras que'),
            ('aprender a + inf.', 'loc.', '学会做某事', 'aprender a'),
            ('periodo de descanso', 'm.', '休息时间', 'periodos de descanso'),
        ]),
    ])

A['b2_02'] = dict(
    title_zh='只靠回收就够了吗？',
    note='标题 ¿Es suficiente con reciclar? 中“ser suficiente con + inf.”意为“只要……就够了”，译作“只靠回收就够了吗？”；'
         'administraciones 指政府、公共管理部门，不是“管理”；devolución y recogida 指包装的退还和回收体系；'
         '第 3 句 reutilizarse 是被动意义的自复形式，按句中用法标 prnl.；第 3 句 instalaciones 后的逗号引出新分句（y algunos materiales…），照常停顿。'
         '为少选同源词，reducción、transformación、producción 没有列入。',
    npc={
        '3': [{'after': 'energía,', 'why': '列举：energía, transporte e instalaciones（A, B e C）'}],
        '4': [{'after': 'reducción de residuos,', 'why': '列举：la reducción de residuos, la reparación y la reutilización（A, B y C）'}],
    },
    s=[
        ('回收常常被说成是应对垃圾问题的简单办法。', [
            ('reciclaje', 'm.', '回收利用', 'reciclaje'),
            ('soler + inf.', 'loc.', '通常，往往', 'suele'),
            ('presentarse como', 'loc.', '被说成，被看作', 'presentarse como'),
            ('residuo', 'm.', '垃圾，废弃物', 'residuos'),
        ]),
        ('回收虽然必要，但并不足以减少消费对环境造成的影响。', [
            ('resultar', 'intr.', '显得，是', 'resulta'),
            ('bastar para + inf.', 'loc.', '足以（做某事）', 'basta para'),
            ('impacto ambiental', 'm.', '环境影响', 'impacto ambiental'),
            ('consumo', 'm.', '消费', 'consumo'),
        ]),
        ('回收本身需要能源、运输和设施，而且有些材料无法无限次地重复利用。', [
            ('requerir', 'tr.', '需要，要求', 'requiere'),
            ('instalación', 'f.', '设施，设备', 'instalaciones'),
            ('reutilizarse', 'prnl.', '被重复利用', 'reutilizarse'),
            ('indefinidamente', 'adv.', '无限地，无限期地', 'indefinidamente'),
        ]),
        ('因此，应当优先做到减少垃圾、维修物品和重复使用产品。', [
            ('convenir', 'intr.', '宜，最好（做某事）', 'conviene'),
            ('priorizar', 'tr.', '优先考虑', 'priorizar'),
            ('reparación', 'f.', '修理，维修', 'reparación'),
            ('reutilización', 'f.', '再利用，重复使用', 'reutilización'),
        ]),
        ('企业可以设计更耐用的包装，而政府部门可以为退还和回收体系提供便利。', [
            ('envase', 'm.', '包装，容器', 'envases'),
            ('duradero', 'adj.', '耐用的，持久的', 'duraderos'),
            ('administración', 'f.', '政府部门，行政机关', 'administraciones'),
            ('devolución', 'f.', '退还，返还', 'devolución'),
            ('recogida', 'f.', '收集，回收', 'recogida'),
        ]),
        ('个人责任固然重要，但如果它能成为生产和消费领域更广泛变革的一部分，就会更加有效。', [
            ('importar', 'intr.', '重要，要紧', 'importa'),
            ('eficaz', 'adj.', '有效的，有成效的', 'eficaz'),
            ('formar parte de', 'loc.', '是……的一部分', 'forma parte de'),
            ('amplio', 'adj.', '广泛的，宽广的', 'amplia'),
        ]),
    ])

A['b2_03'] = dict(
    title_zh='城市住房',
    note='vivienda asequible 译作“负担得起的住房”；salarios modestos 译作“工资不高”（modesto 在这里是“微薄的”，不是“谦虚的”）；'
         'servicios esenciales 译作“基本服务设施”；第 4 句冒号后是三个不定式短语作主语的列举，列举的逗号不停顿。',
    npc={
        '4': [{'after': 'construir más,', 'why': '列举：construir más, rehabilitar edificios vacíos y ampliar el transporte…（A, B y C）'}],
    },
    s=[
        ('获得一套负担得起的住房，已成为大城市众多居民关注的核心问题。', [
            ('vivienda', 'f.', '住房，住宅', 'vivienda'),
            ('asequible', 'adj.', '（价格）负担得起的', 'asequible'),
            ('convertirse en', 'loc.', '变成，成为', 'se ha convertido en'),
            ('preocupación', 'f.', '担忧，关注的问题', 'preocupación'),
            ('numeroso', 'adj.', '众多的，大量的', 'numerosos'),
        ]),
        ('就业增长和服务的集中吸引了人口，而住房供应却并不总是以同样的速度增加。', [
            ('crecimiento', 'm.', '增长', 'crecimiento'),
            ('empleo', 'm.', '就业，工作', 'empleo'),
            ('atraer', 'tr.', '吸引', 'atraen'),
            ('oferta', 'f.', '供应，供给', 'oferta'),
            ('al mismo ritmo', 'loc.', '以同样的速度', 'al mismo ritmo'),
        ]),
        ('因此，房租可能会占去收入中过高的比例，在年轻人和工资不高的劳动者中尤其如此。', [
            ('en consecuencia', 'loc.', '因此，结果', 'En consecuencia'),
            ('alquiler', 'm.', '房租，租金', 'alquileres'),
            ('absorber', 'tr.', '吞掉，占去', 'absorber'),
            ('ingreso', 'm.', '收入（常用复数）', 'ingresos'),
            ('modesto', 'adj.', '微薄的，不高的', 'modestos'),
        ]),
        ('解决办法并不简单：多建住房、修缮空置的建筑、把交通延伸到城市周边地区，这些都是需要规划的措施。', [
            ('rehabilitar', 'tr.', '修缮，翻新（建筑）', 'rehabilitar'),
            ('vacío', 'adj.', '空的，空置的', 'vacíos'),
            ('ampliar', 'tr.', '扩大，延伸', 'ampliar'),
            ('periférico', 'adj.', '周边的，城郊的', 'periféricas'),
            ('medida', 'f.', '措施', 'medidas'),
        ]),
        ('目标应当是避免让住在工作地点或基本服务设施附近变成一种特权。', [
            ('deber + inf.', 'loc.', '应当（条件式语气委婉）', 'debería'),
            ('evitar que + subj.', 'loc.', '避免……（后接虚拟式）', 'evitar que'),
            ('servicio esencial', 'm.', '基本公共服务', 'servicios esenciales'),
            ('privilegio', 'm.', '特权', 'privilegio'),
        ]),
    ])

A['b2_04'] = dict(
    title_zh='教育中的人工智能',
    note='alumnado 是集合名词，指全体学生；第 4 句 en el que probablemente estarán presentes 的主语是这些工具，'
         '译作“一个很可能有它们存在的职业环境”；第 1、5 句是三个不定式短语的列举（A, B y C），列举的逗号不停顿。',
    npc={
        '1': [{'after': 'explicar conceptos,', 'why': '列举：explicar conceptos, proponer ejercicios y adaptar materiales（A, B y C）'}],
        '5': [{'after': 'verificar la información,', 'why': '列举：verificar la información, reconocer los límites… y utilizar la tecnología…（A, B y C）'}],
    },
    s=[
        ('人工智能工具可以帮助讲解概念、出练习题，并根据每个学生的节奏调整学习材料。', [
            ('herramienta', 'f.', '工具', 'herramientas'),
            ('ayudar a + inf.', 'loc.', '帮助做某事', 'ayudar a'),
            ('proponer', 'tr.', '提出；出（练习题）', 'proponer'),
            ('adaptar', 'tr.', '使适应，调整', 'adaptar'),
            ('al ritmo de', 'loc.', '按照……的节奏', 'al ritmo de'),
        ]),
        ('然而，它们是否有用，取决于如何把它们融入教学过程。', [
            ('sin embargo', 'loc.', '然而，不过', 'Sin embargo'),
            ('utilidad', 'f.', '用处，效用', 'utilidad'),
            ('depender de', 'loc.', '取决于', 'depende de'),
            ('integrarse en', 'loc.', '融入，被纳入', 'se integren en'),
        ]),
        ('如果学生用这些工具只是为了拿到答案而并不理解，就可能失去培养自己推理能力的机会。', [
            ('alumnado', 'm.', '（全体）学生', 'alumnado'),
            ('obtener', 'tr.', '获得，得到', 'obtener'),
            ('sin + inf.', 'loc.', '不（做某事），没有', 'sin comprenderlas'),
            ('propio', 'adj.', '自己的', 'propio'),
            ('razonamiento', 'm.', '推理，思考能力', 'razonamiento'),
        ]),
        ('另一方面，完全禁止这些工具，也无法让学生为一个很可能有它们存在的职业环境做好准备。', [
            ('por otra parte', 'loc.', '另一方面', 'Por otra parte'),
            ('por completo', 'loc.', '完全，彻底', 'por completo'),
            ('tampoco', 'adv.', '也不', 'tampoco'),
            ('entorno', 'm.', '环境', 'entorno'),
            ('en el que', 'loc.', '在其中（关系从句）', 'en el que'),
        ]),
        ('学校需要教学生核实信息、认清这些系统的局限，并以透明的方式使用技术。', [
            ('centro educativo', 'm.', '学校，教育机构', 'centros educativos'),
            ('enseñar a + inf.', 'loc.', '教（某人）做某事', 'enseñar a'),
            ('verificar', 'tr.', '核实，查证', 'verificar'),
            ('límite', 'm.', '局限，限度', 'límites'),
            ('de manera + adj.', 'loc.', '以……的方式', 'de manera'),
        ]),
    ])

A['b2_05'] = dict(
    title_zh='即时文化',
    note='inmediatez 指“凡事要求立刻得到”，标题译作“即时文化”；第 2 句 aunque antes fuera habitual 用虚拟式过去时表让步，译作“尽管以前这很平常”；'
         '第 5 句 aquello que 出现两次（surface 不唯一），没有列入生词栏；no…, sino… 的 surface 取 sino。',
    npc={
        '1': [{'after': 'productos,', 'why': '列举：productos, respuestas y contenidos（A, B y C）'}],
        '3': [{'after': 'aprender un idioma,', 'why': '列举：aprender un idioma, construir una relación o desarrollar una investigación（A, B o C）'}],
    },
    s=[
        ('数字服务让我们习惯了以越来越快的速度收到商品、回复和各种内容。', [
            ('acostumbrar a + inf.', 'loc.', '使（某人）习惯于', 'acostumbrado a'),
            ('contenido', 'm.', '内容', 'contenidos'),
            ('rapidez', 'f.', '迅速，速度', 'rapidez'),
            ('cada vez mayor', 'loc.', '越来越大（快）的', 'cada vez mayor'),
        ]),
        ('这种便利改变了我们的期待：短暂的等待都可能让我们觉得是浪费时间，尽管以前这很平常。', [
            ('comodidad', 'f.', '便利，舒适', 'comodidad'),
            ('expectativa', 'f.', '期待，预期', 'expectativas'),
            ('espera', 'f.', '等待', 'espera'),
            ('parecer', 'intr.', '让（某人）觉得', 'parecernos'),
            ('pérdida de tiempo', 'f.', '浪费时间', 'pérdida de tiempo'),
        ]),
        ('当我们把这种逻辑套用到需要耐心的活动上时，问题就出现了，比如学习一门语言、建立一段关系或开展一项研究。', [
            ('trasladar', 'tr.', '转移，套用', 'trasladamos'),
            ('paciencia', 'f.', '耐心', 'paciencia'),
            ('construir una relación', 'loc.', '建立关系', 'construir una relación'),
            ('desarrollar una investigación', 'loc.', '开展研究', 'desarrollar una investigación'),
        ]),
        ('重要的成果往往取决于缓慢而反复的过程。', [
            ('soler + inf.', 'loc.', '通常，往往', 'suelen'),
            ('depender de', 'loc.', '取决于', 'depender de'),
            ('lento', 'adj.', '缓慢的', 'lentos'),
            ('repetido', 'adj.', '反复的，重复的', 'repetidos'),
        ]),
        ('重拾等待的能力并不意味着拒绝技术，而是要分清哪些事情可以加快，哪些事情需要时间慢慢成熟。', [
            ('implicar', 'tr.', '意味着', 'implica'),
            ('rechazar', 'tr.', '拒绝，排斥', 'rechazar'),
            ('no…, sino…', 'loc.', '不是……而是……', 'sino'),
            ('distinguir entre', 'loc.', '区分，分清', 'distinguir entre'),
            ('madurar', 'intr.', '成熟', 'madurar'),
        ]),
    ])

A['b2_06'] = dict(
    title_zh='文化遗产的保护',
    note='patrimonio 在文中包括建筑、传统和公共空间，标题译作“文化遗产的保护”，第 1 句 patrimonio histórico 译作“历史遗产”；'
         'actual 是假朋友（当前的，不是“实际的”）；escenario turístico 译作“旅游布景”；elementos irrecuperables 译作“无法复原的东西”；'
         '为少选同源词，conservación、restauración、transformación 没有列入。',
    npc={
        '2': [{'after': 'Los edificios,', 'why': '列举：Los edificios, las tradiciones y los espacios públicos（A, B y C）'}],
        '3': [{'after': 'vivienda,', 'why': '列举：de vivienda, movilidad y actividad económica（A, B y C）'}],
    },
    s=[
        ('保护历史遗产远远不只是维护古老的建筑外立面。', [
            ('patrimonio histórico', 'm.', '历史遗产', 'patrimonio histórico'),
            ('suponer', 'tr.', '意味着', 'supone'),
            ('mucho más que', 'loc.', '远不只是', 'mucho más que'),
            ('fachada', 'f.', '（建筑）正面，外立面', 'fachadas'),
        ]),
        ('建筑、传统和公共空间都是集体记忆的一部分，有助于解释一个社区是如何演变而来的。', [
            ('espacio público', 'm.', '公共空间', 'espacios públicos'),
            ('formar parte de', 'loc.', '是……的一部分', 'forman parte de'),
            ('memoria colectiva', 'f.', '集体记忆', 'memoria colectiva'),
            ('ayudar a + inf.', 'loc.', '有助于，帮助', 'ayudan a'),
            ('evolucionar', 'intr.', '演变，发展', 'ha evolucionado'),
        ]),
        ('然而，保护工作可能会与当下在住房、出行和经济活动方面的需求发生冲突。', [
            ('no obstante', 'loc.', '然而，不过', 'No obstante'),
            ('entrar en conflicto con', 'loc.', '与……发生冲突', 'entrar en conflicto con'),
            ('actual', 'adj.', '当前的（≠实际的）', 'actuales'),
            ('movilidad', 'f.', '出行，交通', 'movilidad'),
        ]),
        ('过于僵化的修复可能会把一个街区变成旅游布景，而毫无章法的改造则可能毁掉无法复原的东西。', [
            ('rígido', 'adj.', '僵化的，死板的', 'rígida'),
            ('escenario', 'm.', '舞台，布景', 'escenario'),
            ('mientras que', 'loc.', '而（表对比）', 'mientras que'),
            ('sin criterios', 'loc.', '毫无章法，不加考量', 'sin criterios'),
            ('irrecuperable', 'adj.', '无法挽回的，不可复原的', 'irrecuperables'),
        ]),
        ('规划应当在保护和日常使用之间寻求平衡，并让居民参与到影响自身生活环境的决策中来。', [
            ('buscar un equilibrio', 'loc.', '寻求平衡', 'buscar un equilibrio'),
            ('cotidiano', 'adj.', '日常的', 'cotidiano'),
            ('incorporar', 'tr.', '吸纳，使参与', 'incorporando'),
            ('afectar a', 'loc.', '影响', 'afectan a'),
            ('entorno', 'm.', '周边环境', 'entorno'),
        ]),
    ])

A['b2_07'] = dict(
    title_zh='数字鸿沟',
    note='第 3 句 también lo están 里的 lo 是中性代词，代替前面的表语 afectadas；第 4 句 no consiste en…, sino en… 拆成 consistir en 和 no…, sino… 两条；'
         'canales presenciales 译作“线下服务渠道”；formación 在这里是“培训”；为少选同源词，excluir、modernización 没有列入。',
    npc={
        '2': [{'after': 'conexión,', 'why': '列举：conexión, dispositivos adecuados o habilidades informáticas（A, B o C）'}],
        '5': [{'after': 'canales presenciales,', 'why': '列举：Mantener canales presenciales, ofrecer formación accesible y crear páginas sencillas（A, B y C）'}],
    },
    s=[
        ('在线服务的普及简化了许多手续，从预约到办理银行业务都是如此。', [
            ('en línea', 'loc.', '在线，网上', 'en línea'),
            ('trámite', 'm.', '手续', 'trámites'),
            ('desde… hasta…', 'loc.', '从……到……', 'desde'),
            ('solicitar una cita', 'loc.', '预约，申请预约', 'solicitar una cita'),
            ('realizar operaciones bancarias', 'loc.', '办理银行业务', 'realizar operaciones bancarias'),
        ]),
        ('然而，这种数字化可能会把那些缺少网络连接、合适的设备或电脑技能的人排除在外。', [
            ('sin embargo', 'loc.', '然而，不过', 'Sin embargo'),
            ('quien', 'pron.', '……的人（无先行词）', 'quienes'),
            ('carecer de', 'loc.', '缺乏，缺少', 'carecen de'),
            ('dispositivo', 'm.', '设备，装置', 'dispositivos'),
        ]),
        ('受影响的不只是老年人：住在信号覆盖差的地区的人，或者买不起新设备的人，同样受到影响。', [
            ('afectado', 'adj.', '受影响的', 'afectadas'),
            ('lo', 'pron.', '代替前面的表语', 'lo'),
            ('cobertura', 'f.', '（信号）覆盖', 'cobertura'),
            ('permitirse', 'prnl.', '负担得起', 'permitirse'),
            ('equipo actualizado', 'm.', '新款设备', 'equipos actualizados'),
        ]),
        ('解决办法不在于阻止现代化，而在于让现代化的设计面向所有人。', [
            ('consistir en', 'loc.', '在于', 'consiste en'),
            ('frenar', 'tr.', '阻止，遏制', 'frenar'),
            ('no…, sino…', 'loc.', '不是……而是……', 'sino'),
            ('diseñar', 'tr.', '设计（-la 指现代化）', 'diseñarla'),
        ]),
        ('保留线下服务渠道、提供人人可及的培训、设计简单易用的网页，这些措施能让人们利用技术，而不让技术变成障碍。', [
            ('canal presencial', 'm.', '线下（面对面）渠道', 'canales presenciales'),
            ('formación', 'f.', '培训', 'formación'),
            ('aprovechar', 'tr.', '利用', 'aprovechar'),
            ('convertir algo en', 'loc.', '把……变成', 'convertirla en'),
            ('barrera', 'f.', '障碍', 'barrera'),
        ]),
    ])

A['b2_08'] = dict(
    title_zh='倾听的重要性',
    note='第 1 句 la otra 指 la otra persona（对方）；第 5 句 donde 的先行词既可理解为前面两个领域，也可只指 relaciones personales，'
         '译文用“在这些场合”保留这一含混；interpretaciones apresuradas 译作“草率的理解”；第 3 句是三个动词短语的列举，列举的逗号不停顿。',
    npc={
        '3': [{'after': 'prestar atención,', 'why': '列举：prestar atención, preguntar… y resumir…（A, B y C）'}],
    },
    s=[
        ('在讨论中，很多人会在对方还在说话的时候就开始准备自己的回答。', [
            ('discusión', 'f.', '讨论，争论', 'discusión'),
            ('mientras', 'conj.', '当……的时候', 'mientras'),
            ('otro', 'pron.', '另一个；（此处）对方', 'la otra'),
            ('todavía', 'adv.', '还，仍然', 'todavía'),
        ]),
        ('这种习惯可能会让对话变成一场比赛，而不是理解不同观点的机会。', [
            ('hábito', 'm.', '习惯', 'hábito'),
            ('hacer que + subj.', 'loc.', '使得（后接虚拟式）', 'hacer que'),
            ('convertirse en', 'loc.', '变成，成为', 'se convierta en'),
            ('en lugar de', 'loc.', '而不是，代替', 'en lugar de'),
            ('punto de vista', 'm.', '观点，看法', 'puntos de vista'),
        ]),
        ('积极倾听意味着集中注意力，有不明白的地方就提问，并在回应之前把自己理解的内容概括一遍。', [
            ('escuchar activamente', 'loc.', '积极倾听', 'Escuchar activamente'),
            ('implicar', 'tr.', '意味着，需要', 'implica'),
            ('prestar atención', 'loc.', '集中注意力，留意', 'prestar atención'),
            ('resumir', 'tr.', '总结，概括', 'resumir'),
            ('lo que', 'pron.', '……的东西（内容）', 'lo que'),
        ]),
        ('这并不意味着要认同一切，而是承认对方值得被理解。', [
            ('estar de acuerdo con', 'loc.', '同意，赞同', 'estar de acuerdo con'),
            ('no…, sino…', 'loc.', '不是……而是……', 'sino'),
            ('reconocer', 'tr.', '承认', 'reconocer'),
            ('merecer', 'tr.', '值得', 'merece'),
        ]),
        ('这种做法无论在职场上还是在人际关系中都很有用，在这些场合，许多冲突都源于草率的理解。', [
            ('resultar', 'intr.', '显得，证明是', 'resulta'),
            ('tanto… como…', 'loc.', '无论……还是……', 'tanto'),
            ('ámbito laboral', 'm.', '职场，工作领域', 'ámbito laboral'),
            ('nacer de', 'loc.', '源于，产生于', 'nacen de'),
            ('apresurado', 'adj.', '仓促的，草率的', 'apresuradas'),
        ]),
    ])

A['b2_09'] = dict(
    title_zh='少消费，选得更好',
    note='第 4 句 lo nuevo 是“lo + 形容词”的名词化结构；decisiones más conscientes 译作“更加审慎的决定”；第 6 句 las hagan viables 中 las 指 elecciones；'
         'elección 复数也有“选举”义，释义里作了区分；第 3 句是三个不定式短语的列举，列举的逗号不停顿。',
    npc={
        '2': [{'after': 'gastos,', 'why': '列举：gastos, desorden y residuos（A, B y C）'}],
        '3': [{'after': 'antes de comprar,', 'why': '列举：evaluar…, comparar… y reparar…（A, B y C）'}],
    },
    s=[
        ('广告往往把购买新产品和改善我们的生活联系在一起。', [
            ('publicidad', 'f.', '广告', 'publicidad'),
            ('soler + inf.', 'loc.', '通常，往往', 'suele'),
            ('asociar', 'tr.', '把……与……联系起来', 'asociar'),
            ('mejora', 'f.', '改善，提高', 'mejora'),
        ]),
        ('然而，囤积物品并不能保证带来更大的满足感，还可能造成开支、杂乱和垃圾。', [
            ('sin embargo', 'loc.', '然而，不过', 'Sin embargo'),
            ('acumular', 'tr.', '积攒，囤积', 'acumular'),
            ('garantizar', 'tr.', '保证，确保', 'garantiza'),
            ('gasto', 'm.', '开支，花费', 'gastos'),
            ('desorden', 'm.', '杂乱，无序', 'desorden'),
        ]),
        ('一种替代做法是：购物前先评估自己的真实需求，比较产品的耐用程度，并修理那些还能用的东西。', [
            ('consistir en', 'loc.', '在于，就是', 'consiste en'),
            ('evaluar', 'tr.', '评估', 'evaluar'),
            ('necesidad real', 'f.', '真实需求', 'necesidades reales'),
            ('durabilidad', 'f.', '耐用性', 'durabilidad'),
            ('reparar', 'tr.', '修理', 'reparar'),
        ]),
        ('这种态度并不要求放弃一切新事物，而是要做出更加审慎的决定。', [
            ('exigir', 'tr.', '要求', 'exige'),
            ('renunciar a', 'loc.', '放弃', 'renunciar a'),
            ('lo + adj.', 'loc.', '……的东西（名词化）', 'lo nuevo'),
            ('no…, sino…', 'loc.', '不是……而是……', 'sino'),
            ('consciente', 'adj.', '有意识的，审慎的', 'conscientes'),
        ]),
        ('这种态度还能推动企业提供可维修的产品和维护保养服务。', [
            ('impulsar', 'tr.', '推动，促使', 'impulsar'),
            ('ofrecer', 'tr.', '提供', 'ofrecer'),
            ('reparable', 'adj.', '可修理的', 'reparables'),
            ('mantenimiento', 'm.', '维护，保养', 'mantenimiento'),
        ]),
        ('负责任的消费取决于个人的选择，但也需要有让这些选择切实可行的条件。', [
            ('consumo responsable', 'm.', '负责任的消费', 'consumo responsable'),
            ('depender de', 'loc.', '取决于', 'depende de'),
            ('elección', 'f.', '选择（复数也指选举）', 'elecciones'),
            ('viable', 'adj.', '可行的', 'viables'),
        ]),
    ])

A['b2_10'] = dict(
    title_zh='错误的价值',
    note='第 3 句 siempre que + 虚拟式表条件（只要），不是“每当”；第 5 句 donde sea posible 用虚拟式；'
         '第 4 句的 ni 作为子串也出现在 significa 里，不能单列，译文用“也不”体现；第 5 句承接上句“不意味着……”，译作“它意味着……”；'
         '第 5 句是三个动词短语的列举，列举的逗号不停顿。',
    npc={
        '5': [{'after': 'reconocer fallos,', 'why': '列举：reconocer fallos, corregirlos y compartir lo aprendido（A, B y C）'}],
    },
    s=[
        ('在许多教育和职场环境中，犯错被看作能力不足的信号。', [
            ('entorno', 'm.', '环境', 'entornos'),
            ('interpretarse como', 'loc.', '被理解为，被视为', 'se interpreta como'),
            ('señal', 'f.', '信号，迹象', 'señal'),
            ('incapacidad', 'f.', '无能，能力不足', 'incapacidad'),
        ]),
        ('这种观念可能导致人们回避挑战、隐瞒问题，直到为时已晚。', [
            ('visión', 'f.', '看法，观念', 'visión'),
            ('llevar a + inf.', 'loc.', '导致（某人）做某事', 'llevar a'),
            ('desafío', 'm.', '挑战', 'desafíos'),
            ('ocultar', 'tr.', '隐瞒，掩盖', 'ocultar'),
            ('resultar demasiado tarde', 'loc.', '为时已晚', 'resulta demasiado tarde'),
        ]),
        ('实际上，只要能诚实地加以分析，错误就能提供关于哪些策略行不通的信息。', [
            ('en realidad', 'loc.', '实际上，其实', 'En realidad'),
            ('funcionar', 'intr.', '奏效，起作用', 'han funcionado'),
            ('siempre que + subj.', 'loc.', '只要（后接虚拟式）', 'siempre que'),
            ('con honestidad', 'loc.', '诚实地', 'con honestidad'),
        ]),
        ('这并不意味着为粗心大意开脱，也不意味着无视其后果。', [
            ('significar', 'tr.', '意味着', 'significa'),
            ('justificar', 'tr.', '为……开脱，辩解', 'justificar'),
            ('falta de cuidado', 'f.', '粗心，疏忽', 'falta de cuidado'),
            ('ignorar', 'tr.', '无视，忽视', 'ignorar'),
        ]),
        ('它意味着营造一种环境，让人可以承认失误、改正失误，并分享从中学到的东西。', [
            ('ser posible', 'loc.', '有可能（sea 为虚拟式）', 'sea posible'),
            ('fallo', 'm.', '失误，差错', 'fallos'),
            ('corregir', 'tr.', '纠正，改正', 'corregirlos'),
            ('lo aprendido', 'loc.', '学到的东西', 'lo aprendido'),
        ]),
        ('那些把每一次错误都转化为改进机会的组织，往往更能适应不断变化的形势。', [
            ('convertir algo en', 'loc.', '把……转化为', 'convierten'),
            ('oportunidad de mejora', 'f.', '改进的机会', 'oportunidad de mejora'),
            ('soler + inf.', 'loc.', '通常，往往', 'suelen'),
            ('adaptarse', 'prnl.', '适应', 'adaptarse'),
            ('cambiante', 'adj.', '多变的，变化中的', 'cambiantes'),
        ]),
    ])


def main(ids):
    for pid in ids:
        a = A[pid]
        path = DIR / f'{pid}.json'
        d = json.loads(path.read_text('utf-8'))
        sents = [s for para in d['paras'] for s in para]
        assert len(sents) == len(a['s']), (pid, len(sents), len(a['s']))
        used = set()
        for s, (zh, ws) in zip(sents, a['s']):
            s['zh'] = zh
            items = [{'h': h, 'pos': p, 'zh': g, 'surface': sf, 'source': 'supplement'} for h, p, g, sf in ws]
            items.sort(key=lambda w: s['es'].find(w['surface']))
            s['w'] = items
            used.update(p for _, p, _, _ in ws)
        d['title_zh'] = a['title_zh']
        old = d['_说明']
        assert 'zh、w 待补' in old, old
        d['_说明'] = old.replace('zh、w 待补。', DONE + a['note'])
        d['pos_legend'] = {k: v for k, v in POS.items() if k in used}
        d['no_pause_commas'] = a['npc']
        path.write_text(json.dumps(d, ensure_ascii=False, indent=1) + '\n', 'utf-8')
        print('wrote', pid)


if __name__ == '__main__':
    main(sys.argv[1:] or sorted(A))
