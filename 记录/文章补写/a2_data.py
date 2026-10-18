# A2 文章数据：每句 (zh, [(surface, h, pos, 释义), ...])
COMMON = ('zh：逐句中文翻译；w：生词栏（全部为补充词条，source=supplement），h 词头（词典原形）、pos 词性、zh 释义（取句中义）、'
          'surface 句中原形；同一个词头只在第一次出现的句子里列。A2 选词重点：过去时（简单过去时、未完成过去时、现在完成时）的不规则变位，'
          '描述经历和习惯的常用搭配，生活场景词汇。')

DATA = {
 'a2_01': {
  'title_zh': '我的第一份工作',
  'note': ('特别判断：第 6 句 el trabajo era cansado 是 ser cansado（累人的），不是 estar cansado（疲倦的），释义按“累人的”；'
           'primer 词头写原形 primero；me gustó 词头写 gustar（intr.），surface 连同 me 一起标出；con más seguridad 词头写 con (más) seguridad。'
           'no_pause_commas：第 5 句 a trabajar en equipo, a organizar… y a resolver… 是列举，逗号不停顿；'
           '第 4 句 y, después de una semana, 是插入语，两边照常停顿。'),
  'npc': {'5': [{'after': 'en equipo,', 'why': '列举：aprendí [a trabajar en equipo], [a organizar mi tiempo] y [a resolver pequeños problemas]（A, B y C）'}]},
  's': [
   ('去年夏天，我在车站附近的一家咖啡馆找到了我的第一份工作。', [
     ('El verano pasado', 'el verano pasado', 'loc.', '去年夏天'),
     ('conseguí', 'conseguir', 'tr.', '得到，找到（工作）'),
     ('primer', 'primero', 'adj.', '第一的'),
     ('cerca de', 'cerca de', 'loc.', '在……附近'),
     ('estación', 'estación', 'f.', '车站')]),
   ('我早上八点开始上班，两点下班。', [
     ('Empezaba', 'empezar', 'intr.', '开始（上班）'),
     ('a las ocho', 'a las + 钟点', 'loc.', '在……点钟'),
     ('de la mañana', 'de la mañana', 'loc.', '早上，上午'),
     ('terminaba', 'terminar', 'intr.', '结束，下班')]),
   ('一开始我很紧张，因为我不熟悉菜单，有些顾客点的东西我也很难听懂。', [
     ('Al principio', 'al principio', 'loc.', '起初，一开始'),
     ('estaba nervioso', 'estar nervioso', 'loc.', '感到紧张'),
     ('conocía', 'conocer', 'tr.', '熟悉，了解'),
     ('me costaba', 'costarle a uno + inf.', 'loc.', '（某人）觉得做……很难'),
     ('pedidos', 'pedido', 'm.', '（顾客的）点单')]),
   ('同事们帮了我很多，一周以后，我已经能更有把握地接待顾客了。', [
     ('compañeros', 'compañero', 'm.', '同事，伙伴'),
     ('ayudaron', 'ayudar', 'tr.', '帮助'),
     ('después de', 'después de', 'loc.', '在……之后'),
     ('atender', 'atender', 'tr.', '接待，招呼（顾客）'),
     ('con más seguridad', 'con (más) seguridad', 'loc.', '（更）有把握地，自信地')]),
   ('我学会了团队合作、规划自己的时间以及解决小问题。', [
     ('Aprendí a', 'aprender a + inf.', 'loc.', '学会（做某事）'),
     ('trabajar en equipo', 'trabajar en equipo', 'loc.', '团队合作'),
     ('organizar', 'organizar', 'tr.', '安排，规划'),
     ('resolver', 'resolver', 'tr.', '解决'),
     ('problemas', 'problema', 'm.', '问题，难题')]),
   ('虽然工作很累人，但我很喜欢拥有自己的钱。', [
     ('Aunque', 'aunque', 'conj.', '虽然，尽管'),
     ('cansado', 'cansado', 'adj.', '累人的，使人疲劳的'),
     ('me gustó', 'gustar', 'intr.', '使（某人）喜欢'),
     ('propio', 'propio', 'adj.', '自己的'),
     ('dinero', 'dinero', 'm.', '钱')]),
  ]},
 'a2_02': {
  'title_zh': '萨拉曼卡之行',
  'note': ('特别判断：Plaza Mayor 译“马约尔广场”（萨拉曼卡主广场的通行译名）；chocolate con churros 译“热巧克力配吉事果”，'
           '作名词短语跟中心词 chocolate 标 m.；fachada 译“正立面”；sábado、domingo 只列名词本身（el + 星期 = 在星期几）。'
           'no_pause_commas：无。第 7 句 cansados, pero muy contentos 由 pero 引出转折，照常停顿，未按并列形容词登记。'),
  'npc': {},
  's': [
   ('上个月，我和两个朋友在萨拉曼卡度过了一个周末。', [
     ('El mes pasado', 'el mes pasado', 'loc.', '上个月'),
     ('pasé', 'pasar', 'tr.', '度过（时间）'),
     ('fin de semana', 'fin de semana', 'm.', '周末'),
     ('amigos', 'amigo', 'm.', '朋友')]),
   ('我们星期六上午到达，把行李箱放在了酒店。', [
     ('Llegamos', 'llegar', 'intr.', '到达'),
     ('sábado', 'sábado', 'm.', '星期六'),
     ('por la mañana', 'por la mañana', 'loc.', '上午，早上'),
     ('dejamos', 'dejar', 'tr.', '放下，存放'),
     ('maletas', 'maleta', 'f.', '行李箱')]),
   ('然后我们步行到马约尔广场，在那里吃了热巧克力配吉事果当早餐。', [
     ('caminamos', 'caminar', 'intr.', '步行，走路'),
     ('hasta', 'hasta', 'prep.', '直到，到（某处）'),
     ('donde', 'donde', 'adv.', '在那里（关系副词）'),
     ('desayunamos', 'desayunar', 'tr.', '早餐吃'),
     ('chocolate con churros', 'chocolate con churros', 'm.', '热巧克力配吉事果')]),
   ('我们参观了大学，看到了那历史悠久、细节繁复的正立面。', [
     ('Visitamos', 'visitar', 'tr.', '参观'),
     ('vimos', 'ver', 'tr.', '看到，看见'),
     ('fachada', 'fachada', 'f.', '（建筑物的）正面'),
     ('llena de', 'lleno de', 'loc.', '充满……的，满是'),
     ('detalles', 'detalle', 'm.', '细节')]),
   ('下午，我们走进一座大教堂，还登上一座塔楼眺望全城。', [
     ('entramos en', 'entrar en', 'loc.', '进入，走进'),
     ('catedral', 'catedral', 'f.', '大教堂'),
     ('subimos a', 'subir a', 'loc.', '登上，爬上'),
     ('torre', 'torre', 'f.', '塔，塔楼'),
     ('contemplar', 'contemplar', 'tr.', '凝望，眺望')]),
   ('星期天，我们买了些纪念品，在一家传统餐馆吃了饭。', [
     ('domingo', 'domingo', 'm.', '星期天'),
     ('compramos', 'comprar', 'tr.', '买'),
     ('recuerdos', 'recuerdo', 'm.', '纪念品'),
     ('comimos', 'comer', 'intr.', '吃饭')]),
   ('我们回到家时很累，但非常开心。', [
     ('Volvimos a casa', 'volver a casa', 'loc.', '回家'),
     ('cansados', 'cansado', 'adj.', '疲倦的，累的'),
     ('contentos', 'contento', 'adj.', '高兴的，满意的')]),
  ]},
 'a2_03': {
  'title_zh': '更健康的生活',
  'note': ('特别判断：第 6 句 consigo 是 conseguir 的现在时第一人称（conseguir + inf. 做到），不是代词 consigo（与自己）；'
           'he notado 为现在完成时，词头写 notar；第 2 句 antes（以前）与第 3 句 antes de（在……之前）是不同词头。'
           'no_pause_commas：第 2 句 dormía poco, comía a cualquier hora y casi nunca hacía ejercicio 是三个过去习惯的列举，逗号不停顿；'
           '第 6 句 especialmente cuando… 是插入成分，两边照常停顿。'),
  'npc': {'2': [{'after': 'dormía poco,', 'why': '列举：[dormía poco], [comía a cualquier hora] y [casi nunca hacía ejercicio]（A, B y C，三个过去习惯）'}]},
  's': [
   ('几个月前，我决定改变一些习惯。', [
     ('Hace unos meses', 'hace + 时间', 'loc.', '……以前'),
     ('decidí', 'decidir', 'tr.', '决定'),
     ('cambiar', 'cambiar', 'tr.', '改变'),
     ('hábitos', 'hábito', 'm.', '习惯')]),
   ('以前我睡得很少，吃饭不分时间，而且几乎从不运动。', [
     ('Antes', 'antes', 'adv.', '以前，从前'),
     ('dormía', 'dormir', 'intr.', '睡觉'),
     ('a cualquier hora', 'a cualquier hora', 'loc.', '随时，不分时间'),
     ('casi nunca', 'casi nunca', 'loc.', '几乎从不'),
     ('hacía ejercicio', 'hacer ejercicio', 'loc.', '锻炼，做运动')]),
   ('现在我尽量在十一点前睡觉，并且在家做饭。', [
     ('intento', 'intentar', 'tr.', '尽量，试图'),
     ('acostarme', 'acostarse', 'prnl.', '上床睡觉'),
     ('antes de', 'antes de', 'loc.', '在……之前'),
     ('preparo', 'preparar', 'tr.', '准备，做（饭）'),
     ('en casa', 'en casa', 'loc.', '在家')]),
   ('我每周有三天会出去散步半小时。', [
     ('a la semana', 'a la semana', 'loc.', '每周（……次）'),
     ('salgo a', 'salir a + inf.', 'loc.', '出去（做某事）'),
     ('caminar', 'caminar', 'intr.', '散步，步行'),
     ('durante', 'durante', 'prep.', '在……期间，持续'),
     ('media hora', 'media hora', 'f.', '半小时')]),
   ('我还会带一瓶水去上班，好多喝点水。', [
     ('También', 'también', 'adv.', '也，还'),
     ('llevo', 'llevar', 'tr.', '带，携带'),
     ('botella de agua', 'botella de agua', 'f.', '一瓶水，水瓶'),
     ('beber', 'beber', 'intr.', '喝（水）')]),
   ('我并不总能完成所有的目标，尤其是工作很多的时候，但我发现自己的精力更充沛了。', [
     ('consigo', 'conseguir + inf.', 'loc.', '做到，成功（做某事）'),
     ('cumplir', 'cumplir', 'tr.', '完成，实现（目标）'),
     ('objetivos', 'objetivo', 'm.', '目标'),
     ('especialmente', 'especialmente', 'adv.', '尤其，特别是'),
     ('he notado', 'notar', 'tr.', '注意到，发觉')]),
   ('对我来说，小的改变更容易坚持下去。', [
     ('Para mí', 'para mí', 'loc.', '对我来说'),
     ('cambios', 'cambio', 'm.', '改变，变化'),
     ('fáciles de', 'fácil de + inf.', 'loc.', '容易（做）的'),
     ('mantener', 'mantener', 'tr.', '保持，坚持')]),
  ]},
 'a2_04': {
  'title_zh': '网上购物',
  'note': ('特别判断：第 1 句 Cada vez compro más 整体标为 cada vez más（越来越……，中间插入动词）；第 4 句 dos días después 词头写“时间 + después”；'
           '第 3 句把 política de devolución 作为名词短语列出，第 5 句的 devolución 不再重复列；compra/comprar 太基础未列。'
           'no_pause_commas：无（第 3、4、6、7 句的逗号分别在句首状语、pero 分句、aunque 从句处，照常停顿）。'),
  'npc': {},
  's': [
   ('我在网上买的东西越来越多，因为在家就能比较价格，很方便。', [
     ('Cada vez compro más', 'cada vez más', 'loc.', '越来越（多）'),
     ('por internet', 'por internet', 'loc.', '通过网络，在网上'),
     ('cómodo', 'cómodo', 'adj.', '方便的，舒适的'),
     ('precios', 'precio', 'm.', '价格'),
     ('desde casa', 'desde casa', 'loc.', '在家，足不出户')]),
   ('上周我订购了一双鞋和一个双肩包。', [
     ('La semana pasada', 'la semana pasada', 'loc.', '上周'),
     ('pedí', 'pedir', 'tr.', '订购，下单'),
     ('zapatos', 'zapato', 'm.', '鞋'),
     ('mochila', 'mochila', 'f.', '双肩背包')]),
   ('买之前，我看了其他顾客的评价，还查看了退货政策。', [
     ('Antes de', 'antes de + inf.', 'loc.', '在（做）……之前'),
     ('leí', 'leer', 'tr.', '读，阅读'),
     ('opiniones', 'opinión', 'f.', '意见；（顾客）评价'),
     ('comprobé', 'comprobar', 'tr.', '核实，查看'),
     ('política de devolución', 'política de devolución', 'f.', '退货政策')]),
   ('两天后包裹到了，可是鞋子太小了。', [
     ('paquete', 'paquete', 'm.', '包裹'),
     ('llegó', 'llegar', 'intr.', '到达，寄到'),
     ('dos días después', '时间 + después', 'loc.', '（多久）之后'),
     ('demasiado', 'demasiado', 'adv.', '太，过于')]),
   ('我申请了退货，并通过电子邮件收到了操作说明。', [
     ('Solicité', 'solicitar', 'tr.', '申请'),
     ('recibí', 'recibir', 'tr.', '收到'),
     ('instrucciones', 'instrucción', 'f.', '说明，指示'),
     ('por correo electrónico', 'por correo electrónico', 'loc.', '通过电子邮件')]),
   ('虽然流程很简单，但在可能的情况下，我还是更喜欢去店里试穿衣服。', [
     ('Aunque', 'aunque', 'conj.', '虽然，尽管'),
     ('sencillo', 'sencillo', 'adj.', '简单的'),
     ('prefiero', 'preferir', 'tr.', '更喜欢，宁愿'),
     ('probarme', 'probarse', 'prnl.', '试穿'),
     ('ropa', 'ropa', 'f.', '衣服')]),
   ('网上购物能节省时间，但必须谨慎。', [
     ('en línea', 'en línea', 'loc.', '在线，网上'),
     ('ahorra', 'ahorrar', 'tr.', '节省'),
     ('hay que', 'hay que + inf.', 'loc.', '必须，得（做）'),
     ('con cuidado', 'con cuidado', 'loc.', '小心地，谨慎地')]),
  ]},
 'a2_05': {
  'title_zh': '新室友',
  'note': ('特别判断：叙述者是女性（cada una、cocinamos juntas）；compañera de piso 按句中阴性写词头，标 f.；'
           'Elena 译“埃莱娜”；第 5 句 invitáramos 是虚拟式过去时，超出 A2 重点，释义里注明形式；'
           'avisarnos、se escuchan 是相互意义的代词式动词，标 prnl.；calendario 在此指值日表。'
           'no_pause_commas：第 4 句 limpiar la cocina, sacar la basura y comprar productos comunes 是列举，逗号不停顿；'
           '第 6 句 de vez en cuando 是插入语，两边照常停顿。'),
  'npc': {'4': [{'after': 'la cocina,', 'why': '列举：[limpiar la cocina], [sacar la basura] y [comprar productos comunes]（A, B y C）'}]},
  's': [
   ('两个月前，搬来了一位新室友。', [
     ('Hace dos meses', 'hace + 时间', 'loc.', '……以前'),
     ('llegó', 'llegar', 'intr.', '来到，到来'),
     ('nueva', 'nuevo', 'adj.', '新的'),
     ('compañera de piso', 'compañera de piso', 'f.', '合租室友（女）')]),
   ('她叫埃莱娜，在一家牙科诊所工作。', [
     ('Se llama', 'llamarse', 'prnl.', '名叫'),
     ('trabaja en', 'trabajar en', 'loc.', '在……工作'),
     ('clínica', 'clínica', 'f.', '诊所'),
     ('dental', 'dental', 'adj.', '牙科的，牙齿的')]),
   ('一开始，我们不得不谈一谈家务的事，因为我们俩的习惯各不相同。', [
     ('Al principio', 'al principio', 'loc.', '起初，一开始'),
     ('tuvimos que', 'tener que + inf.', 'loc.', '不得不，必须'),
     ('hablar sobre', 'hablar sobre', 'loc.', '谈论（某事）'),
     ('tareas de casa', 'tareas de casa', 'f.', '家务活'),
     ('costumbres', 'costumbre', 'f.', '习惯')]),
   ('我们决定制定一张值日表，安排打扫厨房、倒垃圾和购买公用物品。', [
     ('Decidimos', 'decidir', 'tr.', '决定'),
     ('calendario', 'calendario', 'm.', '日程表，值日表'),
     ('limpiar', 'limpiar', 'tr.', '打扫，清洁'),
     ('sacar la basura', 'sacar la basura', 'loc.', '倒垃圾'),
     ('comunes', 'común', 'adj.', '共同的，公用的')]),
   ('我们还约定，邀请别人来的时候要互相告知一声。', [
     ('acordamos', 'acordar', 'tr.', '商定，约定'),
     ('avisarnos', 'avisarse', 'prnl.', '互相告知'),
     ('invitáramos', 'invitar', 'tr.', '邀请（虚拟式过去时）'),
     ('alguien', 'alguien', 'pron.', '某人，别人')]),
   ('现在我们相处得相当不错，偶尔还会一起做饭。', [
     ('convivimos', 'convivir', 'intr.', '共同生活，相处'),
     ('bastante', 'bastante', 'adv.', '相当，挺'),
     ('de vez en cuando', 'de vez en cuando', 'loc.', '偶尔，有时'),
     ('cocinamos', 'cocinar', 'intr.', '做饭'),
     ('juntas', 'junto', 'adj.', '一起的，在一起')]),
   ('我明白了，当规则明确、两个人又能互相倾听时，合住一套房子会更容易。', [
     ('He aprendido', 'aprender', 'tr.', '学到，明白'),
     ('compartir', 'compartir', 'tr.', '合用，分享'),
     ('vivienda', 'vivienda', 'f.', '住房，住所'),
     ('están claras', 'estar claro', 'loc.', '清楚，明确'),
     ('se escuchan', 'escucharse', 'prnl.', '互相倾听')]),
  ]},
 'a2_06': {
  'title_zh': '公共交通',
  'note': ('特别判断：cita 译“约会”（泛指约好的事，释义写“约会，预约”）；tráfico 译“交通拥堵”；ayudaría 是条件式，释义写“（会）有助于”；'
           'soler + inf. 按“动词 + 不定式”迂说结构标 loc.；Los fines de semana 作时间状语整体标 loc.。'
           'no_pause_commas：无（Sin embargo、Por eso 后和 cuando 从句两边的逗号照常停顿）。'),
  'npc': {},
  's': [
   ('在我的城市，很多人坐公交车去上班或上大学。', [
     ('mucha gente', 'mucha gente', 'f.', '很多人'),
     ('utiliza', 'utilizar', 'tr.', '使用，利用'),
     ('autobús', 'autobús', 'm.', '公交车'),
     ('ir al trabajo', 'ir al trabajo', 'loc.', '去上班')]),
   ('这比开车便宜，而且不用找停车位。', [
     ('más barato que', 'más + adj. + que', 'loc.', '比……更……'),
     ('conducir', 'conducir', 'intr.', '开车'),
     ('no hay que', 'no hay que + inf.', 'loc.', '不必，不用'),
     ('aparcamiento', 'aparcamiento', 'm.', '停车位，停车场')]),
   ('不过，在高峰时段，车上往往挤得满满的，有时还会晚点。', [
     ('Sin embargo', 'sin embargo', 'loc.', '然而，不过'),
     ('horas punta', 'hora punta', 'f.', '高峰时段'),
     ('suelen', 'soler + inf.', 'loc.', '通常，往往'),
     ('llenos', 'lleno', 'adj.', '满的，挤满的'),
     ('llegan tarde', 'llegar tarde', 'loc.', '迟到，晚点')]),
   ('所以，有重要约会的时候，我会留足时间出门。', [
     ('Por eso', 'por eso', 'loc.', '所以，因此'),
     ('cita', 'cita', 'f.', '约会，预约'),
     ('salgo de casa', 'salir de casa', 'loc.', '出门'),
     ('con tiempo', 'con tiempo', 'loc.', '提前，留有余地'),
     ('suficiente', 'suficiente', 'adj.', '足够的')]),
   ('周末如果天气好，我更喜欢骑自行车出行。', [
     ('Los fines de semana', 'los fines de semana', 'loc.', '每逢周末'),
     ('prefiero', 'preferir', 'tr.', '更喜欢，宁愿'),
     ('moverme', 'moverse', 'prnl.', '出行，走动'),
     ('en bicicleta', 'en bicicleta', 'loc.', '骑自行车'),
     ('hace buen tiempo', 'hacer buen tiempo', 'loc.', '天气好')]),
   ('我觉得，改善公共交通会有助于减少交通拥堵和污染。', [
     ('Creo que', 'creer que', 'loc.', '认为，觉得'),
     ('mejorar', 'mejorar', 'tr.', '改善'),
     ('ayudaría a', 'ayudar a + inf.', 'loc.', '（会）有助于'),
     ('reducir', 'reducir', 'tr.', '减少'),
     ('contaminación', 'contaminación', 'f.', '污染')]),
  ]},
 'a2_07': {
  'title_zh': '一次家庭庆祝会',
  'note': ('特别判断：原文没说 abuela、tíos、prima 是父系还是母系，按母系统一译作“外婆”“舅舅舅妈”“表姐”（年龄长幼原文也没说，暂作“表姐”），'
           '释义写成中性的“祖母（奶奶或外婆）”“堂（表）姐妹”等；paella 用通行译名“西班牙海鲜饭”；'
           '第 7 句 las personas que quiero 的 querer 是“爱”；第 4 句列 después de + inf.，第 5 句 fotos 单独列 foto（以 -o 结尾的阴性名词）。'
           'no_pause_commas：无。'),
  'npc': {},
  's': [
   ('星期天，我们给外婆过了生日。', [
     ('domingo', 'domingo', 'm.', '星期天'),
     ('celebramos', 'celebrar', 'tr.', '庆祝'),
     ('cumpleaños', 'cumpleaños', 'm.', '生日（单复数同形）'),
     ('abuela', 'abuela', 'f.', '祖母（奶奶或外婆）')]),
   ('全家人都聚到了舅舅舅妈家。', [
     ('Toda la familia', 'toda la familia', 'f.', '全家人'),
     ('se reunió', 'reunirse', 'prnl.', '相聚，聚集'),
     ('en casa de', 'en casa de', 'loc.', '在……家'),
     ('tíos', 'tío', 'm.', '叔叔，舅舅（复数含其妻）')]),
   ('表姐做了一个巧克力蛋糕，我爸爸给大家做了西班牙海鲜饭。', [
     ('prima', 'prima', 'f.', '堂（表）姐妹'),
     ('preparó', 'preparar', 'tr.', '做，准备'),
     ('tarta de chocolate', 'tarta de chocolate', 'f.', '巧克力蛋糕'),
     ('cocinó', 'cocinar', 'tr.', '烹饪，做（饭菜）'),
     ('paella', 'paella', 'f.', '西班牙海鲜饭')]),
   ('饭后，我们看了些老照片，还听外婆讲了她年轻时的故事。', [
     ('Después de', 'después de + inf.', 'loc.', '（做完）……之后'),
     ('vimos', 'ver', 'tr.', '看'),
     ('antiguas', 'antiguo', 'adj.', '旧的，老的'),
     ('historias', 'historia', 'f.', '故事；经历'),
     ('juventud', 'juventud', 'f.', '青年时代，青春')]),
   ('当我们送给她一本收录了不同年代照片的相册时，她很感动。', [
     ('se emocionó', 'emocionarse', 'prnl.', '感动，激动'),
     ('regalamos', 'regalar', 'tr.', '赠送（礼物）'),
     ('álbum', 'álbum', 'm.', '相册'),
     ('fotos', 'foto', 'f.', '照片'),
     ('épocas', 'época', 'f.', '时期，年代')]),
   ('那不是一场奢华的聚会，但我们一起度过了好几个小时。', [
     ('fue', 'ser', 'intr.', '是'),
     ('fiesta', 'fiesta', 'f.', '聚会，派对'),
     ('lujosa', 'lujoso', 'adj.', '豪华的，奢侈的'),
     ('pasamos', 'pasar', 'tr.', '度过（时间）'),
     ('juntos', 'junto', 'adj.', '一起的，在一起')]),
   ('对我来说，这类庆祝活动最重要的，是和我爱的人一起度过时光。', [
     ('Para mí', 'para mí', 'loc.', '对我来说'),
     ('lo más importante', 'lo más importante', 'loc.', '最重要的（事）'),
     ('celebraciones', 'celebración', 'f.', '庆祝活动'),
     ('compartir tiempo', 'compartir tiempo', 'loc.', '共度时光'),
     ('quiero', 'querer', 'tr.', '爱，喜爱')]),
  ]},
 'a2_08': {
  'title_zh': '从错误中学习',
  'note': ('特别判断：mi profesora 译“我的老师”（女老师，中文不必标性别）；第 2 句 conocía la respuesta 释义取“知道”；'
           '第 3 句 eran 是间接引语里的未完成过去时，列在 ser；largo 是假朋友（“长的”，不是英语 large），释义里注明；'
           'no… sino… 只能标连续的 sino，释义写出整个结构；seguir practicando 词头写 seguir + gerundio。'
           'no_pause_commas：无（句首状语、pero/sino 前的逗号照常停顿）。'),
  'npc': {},
  's': [
   ('我刚开始学西班牙语的时候，不好意思开口说话，因为怕说错。', [
     ('empecé a', 'empezar a + inf.', 'loc.', '开始（做某事）'),
     ('me daba vergüenza', 'dar vergüenza', 'loc.', '（某人）感到难为情'),
     ('temía', 'temer', 'tr.', '害怕，担心'),
     ('equivocarme', 'equivocarse', 'prnl.', '弄错，犯错')]),
   ('所以，很多时候我知道答案，却不举手。', [
     ('Por eso', 'por eso', 'loc.', '所以，因此'),
     ('muchas veces', 'muchas veces', 'loc.', '很多次，常常'),
     ('conocía', 'conocer', 'tr.', '知道'),
     ('respuesta', 'respuesta', 'f.', '答案，回答'),
     ('levantaba la mano', 'levantar la mano', 'loc.', '举手')]),
   ('有一天，我的老师对我说，犯错是学习过程中很正常的一部分。', [
     ('Un día', 'un día', 'loc.', '有一天'),
     ('dijo', 'decir', 'tr.', '说，告诉'),
     ('errores', 'error', 'm.', '错误'),
     ('eran', 'ser', 'intr.', '是'),
     ('aprendizaje', 'aprendizaje', 'm.', '学习（过程）')]),
   ('从那以后，我尽量多参与，并把不懂的表达记下来。', [
     ('Desde entonces', 'desde entonces', 'loc.', '从那时起'),
     ('intento', 'intentar', 'tr.', '尽量，试图'),
     ('anoto', 'anotar', 'tr.', '记下'),
     ('expresiones', 'expresión', 'f.', '表达，说法'),
     ('entiendo', 'entender', 'tr.', '懂，理解')]),
   ('我仍然会弄混一些动词时态，但现在已经能进行更长的对话了。', [
     ('Todavía', 'todavía', 'adv.', '仍然，还'),
     ('confundo', 'confundir', 'tr.', '混淆，弄混'),
     ('tiempos verbales', 'tiempo verbal', 'm.', '动词时态'),
     ('mantener conversaciones', 'mantener una conversación', 'loc.', '进行对话，交谈'),
     ('largas', 'largo', 'adj.', '长的（≠英语 large）')]),
   ('我已经明白，进步并不意味着把一切都做得完美，而是坚持练习，并从每一次困难中学习。', [
     ('He comprendido', 'comprender', 'tr.', '理解，明白'),
     ('progresar', 'progresar', 'intr.', '进步'),
     ('sino', 'sino', 'conj.', '而是（no…sino…）'),
     ('seguir practicando', 'seguir + gerundio', 'loc.', '继续（做某事）'),
     ('aprender de', 'aprender de', 'loc.', '从……中学习')]),
  ]},
 'a2_09': {
  'title_zh': '没有手机的一天',
  'note': ('特别判断：第 3 句 había visto 是过去完成时（visto 为不规则过去分词），词头写 ver；librería 是假朋友（书店，不是图书馆），释义里注明；'
           'banco 取“长椅”义并注明也指银行；teléfono de casa 译“座机”；第 7 句 pero sí 是强调肯定（“但确实要”）；utilizar 在第 1 句已列，第 7 句的 utilizarlo 不再列，改列同义词 usar。'
           'no_pause_commas：无（porque、pero 前和句首状语后的逗号照常停顿）。'),
  'npc': {},
  's': [
   ('上周六，我决定一整天都不用手机。', [
     ('El sábado pasado', 'el sábado pasado', 'loc.', '上周六'),
     ('decidí', 'decidir', 'tr.', '决定'),
     ('sin', 'sin', 'prep.', '没有，不（+inf.）'),
     ('utilizar', 'utilizar', 'tr.', '使用，利用'),
     ('móvil', 'móvil', 'm.', '手机')]),
   ('一开始感觉很奇怪，因为我平时一起床就看消息。', [
     ('Al principio', 'al principio', 'loc.', '起初，一开始'),
     ('extraño', 'extraño', 'adj.', '奇怪的'),
     ('mensajes', 'mensaje', 'm.', '消息，短信'),
     ('nada más', 'nada más + inf.', 'loc.', '一……就……'),
     ('levantarme', 'levantarse', 'prnl.', '起床')]),
   ('吃完早饭后，我出去散步，发现了一家以前从没见过的书店。', [
     ('Después de', 'después de + inf.', 'loc.', '（做完）……之后'),
     ('salí a', 'salir a + inf.', 'loc.', '出去（做某事）'),
     ('descubrí', 'descubrir', 'tr.', '发现'),
     ('librería', 'librería', 'f.', '书店（≠图书馆）'),
     ('había visto', 'ver', 'tr.', '看见，见过')]),
   ('我买了一本小说，在公园的长椅上读了好几页。', [
     ('Compré', 'comprar', 'tr.', '买'),
     ('novela', 'novela', 'f.', '小说'),
     ('leí', 'leer', 'tr.', '读，阅读'),
     ('varias', 'varios', 'adj.', '好几个，若干'),
     ('banco', 'banco', 'm.', '长椅（也指银行）')]),
   ('下午，我照着一份新食谱做了菜，还用家里的座机给一个朋友打了电话。', [
     ('Por la tarde', 'por la tarde', 'loc.', '下午'),
     ('cociné', 'cocinar', 'tr.', '烹饪，做（菜）'),
     ('receta', 'receta', 'f.', '食谱，菜谱'),
     ('llamé a', 'llamar a', 'loc.', '给……打电话'),
     ('teléfono de casa', 'teléfono de casa', 'm.', '座机，家庭电话')]),
   ('我发现自己有了更多时间，也没那么分心了。', [
     ('Me di cuenta de', 'darse cuenta de', 'loc.', '意识到，发觉'),
     ('tenía', 'tener', 'tr.', '有'),
     ('menos', 'menos', 'adv.', '更少，较少'),
     ('distraído', 'distraído', 'adj.', '分心的，心不在焉的')]),
   ('我并不想停止使用手机，但确实想更有意识地使用它。', [
     ('dejar de', 'dejar de + inf.', 'loc.', '停止（做某事）'),
     ('usar', 'usar', 'tr.', '使用，用'),
     ('pero sí', 'pero sí', 'loc.', '但确实（要）'),
     ('de forma', 'de forma + adj.', 'loc.', '以……的方式'),
     ('consciente', 'consciente', 'adj.', '有意识的，清醒的')]),
  ]},
 'a2_10': {
  'title_zh': '一次山间远足',
  'note': ('特别判断：第 1 句 El pasado otoño 的 pasado 放在名词前（与 el otoño pasado 同义），单列 pasado；hicimos una excursión 词头写 hacer una excursión，'
           '所以第 8 句的 excursión 不再列；bocadillo 译“三明治”（西班牙的长面包夹馅三明治）；第 5 句 se veían 是无人称/被动的 se，词头写 verse；'
           'cubierto 是 cubrir 的不规则过去分词，按 cubierto de 列；第 7 句 terminamos cansados 的 terminar 取“最后（落得）”义。'
           'no_pause_commas：第 2 句 agua, fruta, bocadillos y ropa de abrigo 是列举，两个逗号都不停顿。'),
  'npc': {'2': [{'after': 'agua,', 'why': '列举：llevamos [agua], [fruta], [bocadillos] y [ropa de abrigo]（A, B, C y D）'},
                {'after': 'fruta,', 'why': '同上，列举的第二个逗号'}]},
  's': [
   ('去年秋天，我们去山里远足了一次。', [
     ('pasado', 'pasado', 'adj.', '上一个的（可放名词前）'),
     ('otoño', 'otoño', 'm.', '秋天'),
     ('hicimos una excursión', 'hacer una excursión', 'loc.', '去远足，郊游'),
     ('montaña', 'montaña', 'f.', '山，山区')]),
   ('我们很早就出发了，带了水、水果、三明治和保暖的衣服。', [
     ('Salimos', 'salir', 'intr.', '出发，出门'),
     ('temprano', 'temprano', 'adv.', '早，早早地'),
     ('llevamos', 'llevar', 'tr.', '带，携带'),
     ('bocadillos', 'bocadillo', 'm.', '（长面包）三明治'),
     ('ropa de abrigo', 'ropa de abrigo', 'f.', '御寒衣物')]),
   ('一开始路很好走，但后来我们遇到了一段相当陡的上坡。', [
     ('Al principio', 'al principio', 'loc.', '起初，一开始'),
     ('camino', 'camino', 'm.', '路，小路'),
     ('encontramos', 'encontrar', 'tr.', '遇到，碰到'),
     ('subida', 'subida', 'f.', '上坡，上坡路'),
     ('empinada', 'empinado', 'adj.', '陡峭的')]),
   ('我们停下来好几次，休息一下，欣赏风景。', [
     ('Paramos', 'parar', 'intr.', '停下'),
     ('varias veces', 'varias veces', 'loc.', '好几次'),
     ('descansar', 'descansar', 'intr.', '休息'),
     ('paisaje', 'paisaje', 'm.', '风景，景色')]),
   ('从山顶上可以看到一些小村庄，还有一片长满树木的山谷。', [
     ('cima', 'cima', 'f.', '山顶'),
     ('se veían', 'verse', 'prnl.', '能看到，看得见'),
     ('pueblos', 'pueblo', 'm.', '村镇，村庄'),
     ('valle', 'valle', 'm.', '山谷'),
     ('cubierto de', 'cubierto de', 'loc.', '覆盖着……的')]),
   ('开始下山之前，我们在那儿吃了饭。', [
     ('Comimos', 'comer', 'intr.', '吃饭'),
     ('allí', 'allí', 'adv.', '那里'),
     ('antes de', 'antes de + inf.', 'loc.', '在（做）……之前'),
     ('descenso', 'descenso', 'm.', '下山，下降')]),
   ('虽然最后我们都很累，但这次经历很值得。', [
     ('Aunque', 'aunque', 'conj.', '虽然，尽管'),
     ('terminamos', 'terminar', 'intr.', '最后（落得）'),
     ('cansados', 'cansado', 'adj.', '疲倦的，累的'),
     ('mereció la pena', 'merecer la pena', 'loc.', '值得')]),
   ('从那以后，我们每个月都尽量组织一次远足。', [
     ('Desde entonces', 'desde entonces', 'loc.', '从那以后'),
     ('intentamos', 'intentar', 'tr.', '尽量，试图'),
     ('organizar', 'organizar', 'tr.', '组织'),
     ('cada mes', 'cada mes', 'loc.', '每个月')]),
  ]},
}
