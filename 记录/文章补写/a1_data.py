# A1 文章补充数据：每篇 title_zh、note（_说明 里的特别判断）、nopause、sents=[(zh, [(h,pos,zh,surface),…]), …]
HAY = '有（hay：无人称形式）'
IR_A = '去（某地）；al = a + el'

A = {}

A['a1_01'] = dict(
    title_zh='我的家庭',
    note='第 2 句 hermano 原文没说长幼，根据第 4 句“在 colegio（中小学）上学”判断是弟弟，译作“弟弟”；第 5 句 por la tarde 和 cenar（吃晚饭）连用，指傍晚，译作“傍晚”；第 6 句 abuelos 原文不分祖父母、外祖父母，按口语译作“爷爷奶奶”；第 7 句 estamos unidos 说的是一家人关系亲密，译作“很亲密”。第 4 句 le gusta 只在这里列（第 7 句的 Me gusta 不再重复列）。',
    nopause={},
    sents=[
        ('我叫劳拉，今年二十岁。', [
            ('llamarse', 'prnl.', '名叫，叫做', 'Me llamo'),
            ('tener', 'tr.', '有；（年龄）……岁', 'tengo'),
            ('veinte', 'num.', '二十', 'veinte'),
            ('año', 'm.', '年；岁', 'años')]),
        ('我和父母、弟弟住在一栋小房子里。', [
            ('vivir', 'intr.', '居住，生活', 'Vivo'),
            ('casa', 'f.', '房子；家', 'casa'),
            ('pequeño', 'adj.', '小的', 'pequeña'),
            ('padre', 'm.', '父亲；（复数）父母', 'padres'),
            ('hermano', 'm.', '兄弟；这里指弟弟', 'hermano')]),
        ('我妈妈在医院工作，我爸爸是老师。', [
            ('madre', 'f.', '母亲，妈妈', 'madre'),
            ('trabajar', 'intr.', '工作', 'trabaja'),
            ('hospital', 'm.', '医院', 'hospital'),
            ('profesor', 'm.', '老师，教师', 'profesor')]),
        ('我弟弟在学校念书，他喜欢踢足球。', [
            ('estudiar', 'intr.', '学习，上学', 'estudia'),
            ('colegio', 'm.', '（中小学）学校', 'colegio'),
            ('le gusta + inf.', 'loc.', '他（她）喜欢做……', 'le gusta'),
            ('jugar al fútbol', 'loc.', '踢足球', 'jugar al fútbol')]),
        ('傍晚，我们一起吃晚饭，聊聊这一天的事。', [
            ('por la tarde', 'loc.', '下午；傍晚', 'Por la tarde'),
            ('cenar', 'intr.', '吃晚饭', 'cenamos'),
            ('junto', 'adj.', '一起的，在一起的', 'juntos'),
            ('hablar de', 'loc.', '谈论，聊（某事）', 'hablamos de')]),
        ('周末我们会去看望爷爷奶奶，或者去公园散步。', [
            ('fin de semana', 'm.', '周末', 'fines de semana'),
            ('visitar', 'tr.', '看望，拜访', 'visitamos'),
            ('abuelo', 'm.', '祖父；（复数）祖父母', 'abuelos'),
            ('dar un paseo', 'loc.', '散步', 'damos un paseo'),
            ('parque', 'm.', '公园', 'parque')]),
        ('我喜欢和家人一起度过时光，因为我们一家人总是很亲密。', [
            ('pasar tiempo', 'loc.', '度过时间，共处', 'pasar tiempo'),
            ('porque', 'conj.', '因为', 'porque'),
            ('siempre', 'adv.', '总是，一直', 'siempre'),
            ('estar unido', 'loc.', '团结，关系亲密', 'estamos unidos')]),
    ])

A['a1_02'] = dict(
    title_zh='平常的一天',
    note='第 5 句 cafetería 在大学语境里译作“学校餐厅”，comer 在西班牙指吃午饭；第 1 句把“a las + 钟点”作为句型列出，第 5、6 句的 A las dos、a las seis 不再重复列。第 4 句（课程列举）和第 7 句（preparo la cena, escucho música y leo… 一串并列动作）按列举处理，逗号不停顿。',
    nopause={
        '4': [{'after': 'español,', 'why': '列举课程（español, historia y arte），不停顿'}],
        '7': [{'after': 'la cena,', 'why': '列举一串并列动作（preparo…, escucho… y leo…），不停顿'}],
    },
    sents=[
        ('我每天七点起床。', [
            ('todos los días', 'loc.', '每天', 'Todos los días'),
            ('levantarse', 'prnl.', '起床', 'me levanto'),
            ('a las + 钟点', 'loc.', '在……点钟', 'a las'),
            ('siete', 'num.', '七', 'siete')]),
        ('我先洗个澡，然后早餐喝牛奶咖啡、吃烤面包片。', [
            ('primero', 'adv.', '首先，先', 'Primero'),
            ('ducharse', 'prnl.', '洗澡，淋浴', 'me ducho'),
            ('desayunar', 'tr.', '早餐吃（喝）', 'desayuno'),
            ('café con leche', 'm.', '牛奶咖啡', 'café con leche'),
            ('tostada', 'f.', '烤面包片', 'tostadas')]),
        ('之后我坐公交车去大学。', [
            ('después', 'adv.', '然后，之后', 'Después'),
            ('ir', 'intr.', '去', 'voy'),
            ('universidad', 'f.', '大学', 'universidad'),
            ('en autobús', 'loc.', '乘公交车', 'en autobús')]),
        ('我有西班牙语课、历史课和艺术课。', [
            ('tener', 'tr.', '有', 'Tengo'),
            ('clase', 'f.', '课', 'clases'),
            ('historia', 'f.', '历史', 'historia'),
            ('arte', 'm.', '艺术', 'arte')]),
        ('两点钟，我和同学们在学校餐厅吃午饭。', [
            ('comer', 'intr.', '吃饭；吃午饭', 'como'),
            ('con', 'prep.', '和……一起', 'con'),
            ('compañero', 'm.', '同学，同伴', 'compañeros'),
            ('cafetería', 'f.', '咖啡馆；（学校）餐厅', 'cafetería')]),
        ('下午我在图书馆学习，六点回家。', [
            ('por la tarde', 'loc.', '下午', 'Por la tarde'),
            ('estudiar', 'intr.', '学习', 'estudio'),
            ('biblioteca', 'f.', '图书馆', 'biblioteca'),
            ('volver a casa', 'loc.', '回家', 'vuelvo a casa')]),
        ('晚上我做晚饭、听音乐，睡前再看一会儿书。', [
            ('por la noche', 'loc.', '晚上', 'Por la noche'),
            ('preparar la cena', 'loc.', '做晚饭', 'preparo la cena'),
            ('escuchar', 'tr.', '听', 'escucho'),
            ('leer', 'intr.', '阅读，看书', 'leo'),
            ('antes de + inf.', 'loc.', '在（做某事）之前', 'antes de')]),
    ])

A['a1_03'] = dict(
    title_zh='我的城市',
    note='hay 的词头写 haber（无人称用法，按《新西汉词典》标 tr.），释义注明 hay 是无人称形式；第 3 句的 hay 不再重复列。第 2 句是地点列举，逗号不停顿。',
    nopause={
        '2': [{'after': 'grande,', 'why': '列举（una plaza grande, un mercado, dos parques y…），不停顿'},
              {'after': 'mercado,', 'why': '列举，不停顿'}],
    },
    sents=[
        ('我住在西班牙北部一座安静的城市。', [
            ('vivir', 'intr.', '居住，生活', 'Vivo'),
            ('ciudad', 'f.', '城市', 'ciudad'),
            ('tranquilo', 'adj.', '安静的，宁静的', 'tranquila'),
            ('norte', 'm.', '北方，北部', 'norte')]),
        ('这里有一个大广场、一个市场、两个公园和许多咖啡馆。', [
            ('haber', 'tr.', HAY, 'Hay'),
            ('plaza', 'f.', '广场', 'plaza'),
            ('mercado', 'm.', '市场，集市', 'mercado'),
            ('parque', 'm.', '公园', 'parques'),
            ('cafetería', 'f.', '咖啡馆', 'cafeterías')]),
        ('我家附近有一家药店和一个公交车站。', [
            ('cerca de', 'loc.', '在……附近', 'Cerca de'),
            ('casa', 'f.', '家；房子', 'casa'),
            ('farmacia', 'f.', '药店', 'farmacia'),
            ('parada de autobús', 'f.', '公交车站', 'parada de autobús')]),
        ('每个星期天，我都和朋友们去市中心。', [
            ('los domingos', 'loc.', '每个星期天', 'Los domingos'),
            ('ir', 'intr.', '去', 'voy'),
            ('centro', 'm.', '市中心', 'centro'),
            ('amigo', 'm.', '朋友', 'amigos')]),
        ('有时我们会去参观博物馆，然后喝杯热巧克力。', [
            ('a veces', 'loc.', '有时候', 'A veces'),
            ('visitar', 'tr.', '参观', 'visitamos'),
            ('museo', 'm.', '博物馆', 'museo'),
            ('tomar', 'tr.', '喝；吃', 'tomamos'),
            ('chocolate caliente', 'm.', '热巧克力', 'chocolate caliente')]),
        ('冬天很冷，雨也下得挺多，但到了春天，街道上到处是鲜花。', [
            ('invierno', 'm.', '冬天', 'invierno'),
            ('hacer frío', 'loc.', '（天气）冷', 'hace frío'),
            ('llover', 'intr.', '下雨', 'llueve'),
            ('bastante', 'adv.', '相当，挺', 'bastante'),
            ('primavera', 'f.', '春天', 'primavera')]),
        ('我喜欢我的城市，因为它很漂亮，这里的人也很友善。', [
            ('me gusta', 'loc.', '我喜欢', 'Me gusta'),
            ('porque', 'conj.', '因为', 'porque'),
            ('bonito', 'adj.', '漂亮的', 'bonita'),
            ('gente', 'f.', '人们（集合名词）', 'gente'),
            ('amable', 'adj.', '友善的，和蔼的', 'amable')]),
    ])

A['a1_04'] = dict(
    title_zh='在超市',
    note='hay 的词头写 haber（无人称用法，标 tr.）；第 1 句 ir a 释义注明 al = a + el。第 2 句是购物清单列举，逗号不停顿（冒号照常停顿）。第 6 句 para comer 照字面译作“做一份沙拉吃”，没有译成“当午饭”。第 3 句的 comprar 只在这里列，第 7 句句首的 Comprar 不再重复列。',
    nopause={
        '2': [{'after': 'leche,', 'why': '购物清单列举，不停顿'},
              {'after': 'huevos,', 'why': '列举，不停顿'},
              {'after': 'arroz,', 'why': '列举，不停顿'},
              {'after': 'tomates,', 'why': '列举，不停顿'}],
    },
    sents=[
        ('今天我去超市，因为家里没有吃的了。', [
            ('hoy', 'adv.', '今天', 'Hoy'),
            ('ir a', 'loc.', IR_A, 'voy al'),
            ('haber', 'tr.', HAY, 'hay'),
            ('comida', 'f.', '食物，吃的', 'comida')]),
        ('我带着一张清单：牛奶、鸡蛋、大米、西红柿、苹果和面包。', [
            ('llevar', 'tr.', '带着，携带', 'Llevo'),
            ('leche', 'f.', '牛奶', 'leche'),
            ('huevo', 'm.', '鸡蛋', 'huevos'),
            ('arroz', 'm.', '大米，米饭', 'arroz'),
            ('manzana', 'f.', '苹果', 'manzanas')]),
        ('在水果区，我还买了香蕉和橙子。', [
            ('fruta', 'f.', '水果', 'frutas'),
            ('comprar', 'tr.', '买', 'compro'),
            ('también', 'adv.', '也，还', 'también'),
            ('plátano', 'm.', '香蕉', 'plátanos'),
            ('naranja', 'f.', '橙子', 'naranjas')]),
        ('然后我去找食用油和意大利面。', [
            ('después', 'adv.', '然后，之后', 'Después'),
            ('buscar', 'tr.', '找，寻找', 'busco'),
            ('aceite', 'm.', '油，食用油', 'aceite'),
            ('pasta', 'f.', '意大利面', 'pasta')]),
        ('在收银台，我刷卡付款，然后把买的东西装进一个可重复使用的购物袋。', [
            ('caja', 'f.', '收银台', 'caja'),
            ('pagar con tarjeta', 'loc.', '刷卡付款', 'pago con tarjeta'),
            ('guardar', 'tr.', '收好，装进', 'guardo'),
            ('compra', 'f.', '买的东西', 'compra'),
            ('bolsa reutilizable', 'f.', '可重复使用的袋子', 'bolsa reutilizable')]),
        ('回到家后，我把买来的东西放进冰箱，再做一份沙拉吃。', [
            ('cuando', 'conj.', '当……的时候', 'Cuando'),
            ('llegar a casa', 'loc.', '到家', 'llego a casa'),
            ('poner', 'tr.', '放，摆', 'pongo'),
            ('nevera', 'f.', '冰箱', 'nevera'),
            ('ensalada', 'f.', '沙拉', 'ensalada')]),
        ('带着清单买东西，能帮我什么都不忘。', [
            ('lista', 'f.', '清单', 'lista'),
            ('ayudar a + inf.', 'loc.', '帮（某人）做某事', 'ayuda a'),
            ('olvidar', 'tr.', '忘记', 'olvidar'),
            ('nada', 'pron.', '（与 no 连用）什么也不', 'nada')]),
    ])

A['a1_05'] = dict(
    title_zh='我最好的朋友',
    note='Sofía 译作“索菲娅”。第 5 句 A las dos 是“对我们两个（女生）来说”（las dos 指“我”和 Sofía 两位女性），不是“两点钟”，单独列出提醒；nos gusta 也列在这一句。第 3 句是并列形容词，第 5 句是动词列举，逗号不停顿；第 7 句两个 si 条件从句和分号照常停顿。',
    nopause={
        '3': [{'after': 'alegre,', 'why': '并列形容词（alegre, inteligente y muy paciente），不停顿'}],
        '5': [{'after': 'dibujar,', 'why': '列举（dibujar, viajar y probar…），不停顿'}],
    },
    sents=[
        ('我最好的朋友叫索菲娅。', [
            ('mejor', 'adj.', '最好的；更好的', 'mejor'),
            ('amiga', 'f.', '（女性）朋友', 'amiga'),
            ('llamarse', 'prnl.', '名叫，叫做', 'se llama')]),
        ('她二十二岁，学的是设计。', [
            ('tener', 'tr.', '有；（年龄）……岁', 'Tiene'),
            ('veintidós', 'num.', '二十二', 'veintidós'),
            ('estudiar', 'tr.', '学，攻读（专业）', 'estudia'),
            ('diseño', 'm.', '设计', 'diseño')]),
        ('她性格开朗、聪明，而且很有耐心。', [
            ('ser', 'intr.', '是（表示性格特点）', 'Es'),
            ('alegre', 'adj.', '开朗的，快乐的', 'alegre'),
            ('inteligente', 'adj.', '聪明的', 'inteligente'),
            ('paciente', 'adj.', '有耐心的', 'paciente')]),
        ('我们是三年前在一节西班牙语课上认识的。', [
            ('conocerse', 'prnl.', '相识，互相认识', 'Nos conocimos'),
            ('clase', 'f.', '课', 'clase'),
            ('español', 'm.', '西班牙语', 'español'),
            ('hace + 时间段', 'loc.', '……以前', 'hace tres años')]),
        ('我们俩都喜欢画画、旅行，还有去尝试新的餐厅。', [
            ('a las dos', 'loc.', '对我们俩（女生）来说', 'A las dos'),
            ('nos gusta + inf.', 'loc.', '我们喜欢做……', 'nos gusta'),
            ('dibujar', 'intr.', '画画', 'dibujar'),
            ('viajar', 'intr.', '旅行', 'viajar'),
            ('probar', 'tr.', '尝试，品尝', 'probar')]),
        ('我们通常每周五下午见面。', [
            ('normalmente', 'adv.', '通常，一般', 'Normalmente'),
            ('quedar', 'intr.', '约好见面', 'quedamos'),
            ('los viernes', 'loc.', '每个星期五', 'los viernes'),
            ('por la tarde', 'loc.', '下午', 'por la tarde')]),
        ('如果天气好，我们就去市中心散步；如果下雨，我们就在家看电影。', [
            ('si', 'conj.', '如果', 'Si'),
            ('hacer buen tiempo', 'loc.', '天气好', 'hace buen tiempo'),
            ('pasear', 'intr.', '散步，逛', 'paseamos'),
            ('llover', 'intr.', '下雨', 'llueve'),
            ('película', 'f.', '电影', 'película')]),
        ('虽然我们的作息时间不一样，但我们几乎每天都聊天。', [
            ('aunque', 'conj.', '虽然，尽管', 'Aunque'),
            ('horario', 'm.', '作息时间，时间表', 'horarios'),
            ('casi', 'adv.', '几乎', 'casi'),
            ('todos los días', 'loc.', '每天', 'todos los días')]),
    ])

A['a1_06'] = dict(
    title_zh='一个周末',
    note='第 3 句 Max 译作“马克斯”，“mi perro, Max” 是同位语，逗号照常停顿；第 5 句 hermana 原文没说长幼，暂译“姐姐”，abuelos 按口语译作“爷爷奶奶”；第 6 句 horario 结合第 1 句的上课，译作“课表”。第 1 句 tener que 和第 7 句 tener tiempo de 是两个不同的固定搭配，分别列出。',
    nopause={},
    sents=[
        ('星期六我起得很晚，因为不用去上课。', [
            ('sábado', 'm.', '星期六', 'sábado'),
            ('despertarse', 'prnl.', '醒来', 'me despierto'),
            ('tarde', 'adv.', '晚，迟', 'tarde'),
            ('tener que + inf.', 'loc.', '必须，得（做某事）', 'tengo que')]),
        ('我悠闲地吃完早饭，然后打扫自己的房间。', [
            ('desayunar', 'intr.', '吃早饭', 'Desayuno'),
            ('tranquilamente', 'adv.', '从容地，悠闲地', 'tranquilamente'),
            ('limpiar', 'tr.', '打扫，清洁', 'limpio'),
            ('habitación', 'f.', '房间，卧室', 'habitación')]),
        ('下午我带着我的狗马克斯去公园。', [
            ('por la tarde', 'loc.', '下午', 'Por la tarde'),
            ('ir a', 'loc.', IR_A, 'voy al'),
            ('parque', 'm.', '公园', 'parque'),
            ('perro', 'm.', '狗', 'perro')]),
        ('之后我约几个朋友去喝点东西。', [
            ('después', 'adv.', '然后，之后', 'Después'),
            ('quedar con', 'loc.', '和（某人）约见面', 'quedo con'),
            ('amigo', 'm.', '朋友', 'amigos'),
            ('tomar algo', 'loc.', '喝点东西', 'tomar algo')]),
        ('星期天我和姐姐一起做饭，还给爷爷奶奶打电话。', [
            ('domingo', 'm.', '星期天', 'domingo'),
            ('cocinar', 'intr.', '做饭', 'cocino'),
            ('hermana', 'f.', '姐妹；这里指姐姐', 'hermana'),
            ('llamar', 'tr.', '给……打电话', 'llamo'),
            ('abuelo', 'm.', '祖父；（复数）祖父母', 'abuelos')]),
        ('晚上我收拾好书包，看看这一周的课表。', [
            ('por la noche', 'loc.', '晚上', 'Por la noche'),
            ('preparar', 'tr.', '准备，收拾', 'preparo'),
            ('mochila', 'f.', '书包，背包', 'mochila'),
            ('mirar', 'tr.', '看，查看', 'miro'),
            ('horario', 'm.', '课表，时间表', 'horario')]),
        ('我喜欢周末，因为我可以休息，还能做一些平时没时间做的事情。', [
            ('me gustan', 'loc.', '我喜欢（复数事物）', 'Me gustan'),
            ('fin de semana', 'm.', '周末', 'fines de semana'),
            ('poder', 'tr.', '能，可以', 'puedo'),
            ('descansar', 'intr.', '休息', 'descansar'),
            ('tener tiempo de + inf.', 'loc.', '有时间做某事', 'tengo tiempo de')]),
    ])

A['a1_07'] = dict(
    title_zh='我的房间',
    note='hay 的词头写 haber（无人称用法，标 tr.），第 2 句的 Hay 不列、留到第 4 句列，第 2 句改列 junto a、frente a 两个方位短语。foto（阴性）、mapa（阳性）是词尾和阴阳性不一致的常见词，词性照实标。第 3 句是物品列举，逗号不停顿；第 1 句 “grande, pero es cómoda” 是转折，照常停顿。',
    nopause={
        '3': [{'after': 'ordenador,', 'why': '列举（un ordenador, dos cuadernos y una lámpara），不停顿'}],
    },
    sents=[
        ('我的房间不是很大，但很舒适。', [
            ('habitación', 'f.', '房间，卧室', 'habitación'),
            ('grande', 'adj.', '大的', 'grande'),
            ('pero', 'conj.', '但是', 'pero'),
            ('cómodo', 'adj.', '舒适的', 'cómoda')]),
        ('窗边有一张床，门对面有一张书桌。', [
            ('cama', 'f.', '床', 'cama'),
            ('junto a', 'loc.', '在……旁边', 'junto a'),
            ('ventana', 'f.', '窗户', 'ventana'),
            ('escritorio', 'm.', '书桌，写字台', 'escritorio'),
            ('frente a', 'loc.', '在……对面', 'frente a')]),
        ('我的书桌上有一台电脑、两个笔记本和一盏台灯。', [
            ('sobre', 'prep.', '在……上面', 'Sobre'),
            ('tener', 'tr.', '有', 'tengo'),
            ('ordenador', 'm.', '电脑（西班牙用法）', 'ordenador'),
            ('cuaderno', 'm.', '笔记本，本子', 'cuadernos'),
            ('lámpara', 'f.', '灯，台灯', 'lámpara')]),
        ('墙上有我家人的照片和一张西班牙地图。', [
            ('pared', 'f.', '墙，墙壁', 'pared'),
            ('haber', 'tr.', HAY, 'hay'),
            ('foto', 'f.', '照片', 'fotos'),
            ('mapa', 'm.', '地图', 'mapa')]),
        ('我把衣服放在一个白色的衣柜里，把书放在书架上。', [
            ('guardar', 'tr.', '存放，收好', 'Guardo'),
            ('ropa', 'f.', '衣服', 'ropa'),
            ('armario', 'm.', '衣柜', 'armario'),
            ('blanco', 'adj.', '白色的', 'blanco'),
            ('estantería', 'f.', '书架，搁架', 'estantería')]),
        ('早上会有很多光线照进来。', [
            ('por la mañana', 'loc.', '早上，上午', 'Por la mañana'),
            ('entrar', 'intr.', '进入，照进来', 'entra'),
            ('mucho', 'adj.', '很多的', 'mucha'),
            ('luz', 'f.', '光，光线', 'luz')]),
        ('我喜欢让房间保持整洁，因为这样我能更好地学习。', [
            ('me gusta', 'loc.', '我喜欢', 'Me gusta'),
            ('mantener', 'tr.', '保持', 'mantener'),
            ('ordenado', 'adj.', '整齐的，整洁的', 'ordenada'),
            ('así', 'adv.', '这样', 'así'),
            ('mejor', 'adv.', '更好地', 'mejor')]),
    ])

A['a1_08'] = dict(
    title_zh='在餐厅',
    note='第 1、4 句 compañero(s) 原文没说是同学还是同事，暂译“同学”；第 1 句 voy a cenar 按“ir a + 不定式”（将要）列出；第 3 句的 pedir 只在这里列，第 5 句 pedimos 不再重复列，所以第 3、5 句各 3 个生词。第 8 句 “sencilla, pero muy agradable” 带 pero 转折，逗号照常停顿。',
    nopause={},
    sents=[
        ('星期五我要和同学们去一家意大利餐厅吃晚饭。', [
            ('viernes', 'm.', '星期五', 'viernes'),
            ('ir a + inf.', 'loc.', '将要，打算（做某事）', 'voy a'),
            ('cenar', 'intr.', '吃晚饭', 'cenar'),
            ('compañero', 'm.', '同学，同伴', 'compañeros'),
            ('restaurante italiano', 'm.', '意大利餐厅', 'restaurante italiano')]),
        ('服务员给我们安排了一张靠窗的桌子。', [
            ('camarero', 'm.', '服务员', 'camarero'),
            ('dar', 'tr.', '给', 'da'),
            ('mesa', 'f.', '桌子', 'mesa'),
            ('cerca de', 'loc.', '在……附近，靠近', 'cerca de')]),
        ('我点了一份蔬菜披萨和水。', [
            ('pedir', 'tr.', '点（菜），要', 'pido'),
            ('verdura', 'f.', '蔬菜', 'verduras'),
            ('agua', 'f.', '水（单数用 el agua）', 'agua')]),
        ('我的朋友点了番茄意面，我的同学选了一份沙拉。', [
            ('amiga', 'f.', '（女性）朋友', 'amiga'),
            ('pasta con tomate', 'f.', '番茄意面', 'pasta con tomate'),
            ('elegir', 'tr.', '选择，挑选', 'elige'),
            ('ensalada', 'f.', '沙拉', 'ensalada')]),
        ('我们点了蒜香面包，大家一起分着吃。', [
            ('para + inf.', 'loc.', '为了（做某事）', 'Para'),
            ('compartir', 'tr.', '分享，一起分', 'compartir'),
            ('pan de ajo', 'm.', '蒜香面包', 'pan de ajo')]),
        ('饭菜非常好吃，服务也很快。', [
            ('comida', 'f.', '饭菜，食物', 'comida'),
            ('estar', 'intr.', '（表示状态）是', 'está'),
            ('rico', 'adj.', '（食物）好吃的', 'rica'),
            ('rápido', 'adj.', '快的，迅速的', 'rápido')]),
        ('之后我们大家一起分摊了账单，然后走到广场。', [
            ('pagar la cuenta', 'loc.', '结账，买单', 'pagamos la cuenta'),
            ('entre todos', 'loc.', '大家一起（分摊）', 'entre todos'),
            ('caminar', 'intr.', '走路，步行', 'caminamos'),
            ('hasta', 'prep.', '到，直到', 'hasta')]),
        ('这是一个简单却非常愉快的夜晚。', [
            ('noche', 'f.', '夜晚，晚上', 'noche'),
            ('sencillo', 'adj.', '简单的，朴素的', 'sencilla'),
            ('pero', 'conj.', '但是', 'pero'),
            ('agradable', 'adj.', '令人愉快的', 'agradable')]),
    ])

A['a1_09'] = dict(
    title_zh='天气',
    note='标题和第 6 句的 tiempo 都是“天气”的意思（不是“时间”），在第 6 句列出。第 1 句 hace mucho sol 按“hacer sol”列出（surface 含 mucho）。第 2 句 llevar 在这里是“穿着”。本篇没有列举逗号，逗号都照常停顿。',
    nopause={},
    sents=[
        ('今天阳光明媚，气温也很宜人。', [
            ('hoy', 'adv.', '今天', 'Hoy'),
            ('hacer sol', 'loc.', '出太阳，阳光好', 'hace mucho sol'),
            ('temperatura', 'f.', '气温，温度', 'temperatura'),
            ('agradable', 'adj.', '宜人的，舒适的', 'agradable')]),
        ('早上我穿一件薄外套，不过到了中午天就热了。', [
            ('llevar', 'tr.', '穿着', 'llevo'),
            ('chaqueta', 'f.', '外套，夹克', 'chaqueta'),
            ('ligero', 'adj.', '轻薄的', 'ligera'),
            ('al mediodía', 'loc.', '在中午', 'al mediodía'),
            ('hacer calor', 'loc.', '（天气）热', 'hace calor')]),
        ('夏天我喜欢去海滩，在海里游泳。', [
            ('verano', 'm.', '夏天', 'verano'),
            ('me gusta', 'loc.', '我喜欢', 'me gusta'),
            ('playa', 'f.', '海滩', 'playa'),
            ('nadar', 'intr.', '游泳', 'nadar'),
            ('mar', 'm.', '大海', 'mar')]),
        ('秋天经常下雨，树上的叶子也会变色。', [
            ('otoño', 'm.', '秋天', 'otoño'),
            ('llover', 'intr.', '下雨', 'llueve'),
            ('con frecuencia', 'loc.', '经常', 'con frecuencia'),
            ('hoja', 'f.', '叶子', 'hojas'),
            ('cambiar de color', 'loc.', '变色', 'cambian de color')]),
        ('冬天天气寒冷，山上有时会下雪。', [
            ('invierno', 'm.', '冬天', 'invierno'),
            ('hacer frío', 'loc.', '（天气）冷', 'hace frío'),
            ('a veces', 'loc.', '有时候', 'a veces'),
            ('nevar', 'intr.', '下雪', 'nieva'),
            ('montaña', 'f.', '山', 'montañas')]),
        ('出门前，我会用手机查一下天气，好选择合适的衣服。', [
            ('antes de + inf.', 'loc.', '在（做某事）之前', 'Antes de'),
            ('salir de casa', 'loc.', '出门', 'salir de casa'),
            ('tiempo', 'm.', '天气', 'tiempo'),
            ('móvil', 'm.', '手机', 'móvil'),
            ('adecuado', 'adj.', '合适的，恰当的', 'adecuada')]),
    ])

A['a1_10'] = dict(
    title_zh='学习西班牙语',
    note='第 2 句 practicamos…, aprendemos… y hacemos… 是一串并列动作，按列举处理，逗号不停顿；第 5 句 pero 前的逗号照常停顿。第 6 句 conversar con la gente 译作“和那里的人交谈”（la gente 承接前面的“西班牙”）。第 1 句列 vez（次），第 7 句的 una sola vez 作为固定说法另列。',
    nopause={
        '2': [{'after': 'pronunciación,', 'why': '列举一串并列动作（practicamos…, aprendemos… y hacemos…），不停顿'}],
    },
    sents=[
        ('我每周学三次西班牙语。', [
            ('estudiar', 'tr.', '学习', 'Estudio'),
            ('español', 'm.', '西班牙语', 'español'),
            ('vez', 'f.', '次，回（复数 veces）', 'veces'),
            ('por semana', 'loc.', '每周', 'por semana')]),
        ('课上，我们练习发音、学习新单词，还做对话练习。', [
            ('practicar', 'tr.', '练习', 'practicamos'),
            ('pronunciación', 'f.', '发音', 'pronunciación'),
            ('aprender', 'tr.', '学，学会', 'aprendemos'),
            ('palabra', 'f.', '单词，词', 'palabras'),
            ('hacer diálogos', 'loc.', '做对话练习', 'hacemos diálogos')]),
        ('我的老师说话很慢，还会用例子讲解语法。', [
            ('profesora', 'f.', '（女）老师', 'profesora'),
            ('despacio', 'adv.', '慢慢地', 'despacio'),
            ('explicar', 'tr.', '解释，讲解', 'explica'),
            ('ejemplo', 'm.', '例子', 'ejemplos')]),
        ('在家里，我听西班牙歌曲，看带字幕的短视频。', [
            ('escuchar', 'tr.', '听', 'escucho'),
            ('canción', 'f.', '歌曲', 'canciones'),
            ('ver', 'tr.', '看', 'veo'),
            ('corto', 'adj.', '短的', 'cortos'),
            ('subtítulo', 'm.', '字幕', 'subtítulos')]),
        ('有时我会犯错，但我尽量大胆地开口说。', [
            ('a veces', 'loc.', '有时候', 'A veces'),
            ('cometer errores', 'loc.', '犯错', 'cometo errores'),
            ('intentar', 'tr.', '尽力，试图', 'intento'),
            ('sin miedo', 'loc.', '不害怕，大胆地', 'sin miedo')]),
        ('我的目标是能去西班牙各地旅行，和那里的人交谈。', [
            ('objetivo', 'm.', '目标', 'objetivo'),
            ('poder', 'tr.', '能，能够', 'poder'),
            ('viajar por', 'loc.', '在……各地旅行', 'viajar por'),
            ('conversar con', 'loc.', '和……交谈', 'conversar con'),
            ('gente', 'f.', '人们（集合名词）', 'gente')]),
        ('我觉得每天学一点，比一次学好几个小时更好。', [
            ('creer que', 'loc.', '认为，觉得', 'Creo que'),
            ('un poco', 'loc.', '一点儿', 'un poco'),
            ('cada día', 'loc.', '每天', 'cada día'),
            ('mejor que', 'loc.', '比……更好', 'mejor que'),
            ('una sola vez', 'loc.', '仅仅一次', 'una sola vez')]),
    ])
