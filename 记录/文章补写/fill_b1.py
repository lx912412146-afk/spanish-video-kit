"""Fill zh / w / pos_legend / no_pause_commas / _说明 for b1_01..b1_10. es text is never touched."""
import json
import sys
from pathlib import Path

KIT = Path(__file__).resolve().parents[2]   # 工具包根目录（本文件在 记录/文章补写/ 下）
DIR = KIT / '西班牙语' / '文章'

POS = {'m.': '阳性名词', 'f.': '阴性名词', 'adj.': '形容词', 'adv.': '副词', 'tr.': '及物动词', 'intr.': '不及物动词',
       'prnl.': '自复动词', 'prep.': '介词', 'conj.': '连词', 'num.': '数词', 'interj.': '感叹词', 'pron.': '代词',
       'loc.': '短语，固定搭配'}

SE = 'sin embargo', 'loc.', '然而，不过'

DATA = {
 'b1_01': {
  'title_zh': '合理安排时间的重要性',
  'note': '特别判断：第 3 句 siempre que 后接虚拟式，“se distingan” 是被动 se + 虚拟式，词条写成 distinguir A de B 并注明；'
          '第 4 句 conviene + inf. 译作“最好……”；reservar 这里是“留出”，不是“预订”，故意列出。'
          '第 1 句的 suficiente 做成 ser suficiente para + inf.（足以）这个结构。',
  'npc': {'5': [{'after': 'el trabajo,', 'why': '列举：entre el trabajo, la familia y la vida personal（A, B y C）'}]},
  's': [
   ('很多人觉得，一天的时间不足以让他们履行所有的职责。', [
     ('sentir', 'tr.', '觉得，感到（e→ie）', 'sienten'),
     ('ser suficiente para + inf.', 'loc.', '足以（做某事）', 'son suficientes para'),
     ('cumplir con', 'loc.', '履行，完成（职责等）', 'cumplir con'),
     ('responsabilidad', 'f.', '责任，职责', 'responsabilidades')]),
   ('问题并不总是缺少时间，而是使用时间的方式。', [
     ('falta', 'f.', '缺乏，不足', 'falta'),
     ('sino', 'conj.', '而是（no…sino…）', 'sino'),
     ('manera', 'f.', '方式，方法', 'manera'),
     ('utilizar', 'tr.', '使用（lo 指 tiempo）', 'utilizarlo')]),
   ('列一张任务清单会有帮助，前提是要把紧急的事和重要的事区分开来。', [
     ('lista de tareas', 'f.', '任务清单', 'lista de tareas'),
     ('siempre que', 'loc.', '只要（+虚拟式）', 'siempre que'),
     ('distinguir A de B', 'loc.', '区分A与B（被动，虚拟式）', 'se distingan'),
     ('urgente', 'adj.', '紧急的', 'urgentes')]),
   ('最好也留出一些休息时间，因为不停地工作并不能保证更好的结果。', [
     ('convenir + inf.', 'loc.', '（做……）为宜，最好', 'conviene'),
     ('reservar', 'tr.', '留出，预留', 'reservar'),
     ('descanso', 'm.', '休息', 'descanso'),
     ('sin parar', 'loc.', '不停地', 'sin parar')]),
   ('当我们安排一周的日程时留有一定的弹性，就更容易应对突发情况，并在工作、家庭和个人生活之间保持平衡。', [
     ('cierto', 'adj.', '一定的（置于名词前）', 'cierta'),
     ('resultar', 'intr.', '显得，结果是', 'resulta'),
     ('afrontar', 'tr.', '面对，应对', 'afrontar'),
     ('imprevisto', 'm.', '意外情况', 'imprevistos'),
     ('mantener un equilibrio', 'loc.', '保持平衡', 'mantener un equilibrio')]),
  ]},
 'b1_02': {
  'title_zh': '在国外生活',
  'note': '特别判断：第 3 句 la persona 泛指搬到国外的人，译作“移居者”；acostumbrarse a 和 costumbre 同源，两个都列，方便对照；'
          '第 2 句较长，给 5 个词条；第 4 句较短，只给 3 个（es normal + inf.、sentir nostalgia、echar de menos）。',
  'npc': {},
  's': [
   ('搬到另一个国家生活可能是一段令人兴奋的经历，不过也需要耐心。', [
     ('mudarse', 'prnl.', '搬家，迁居', 'Mudarse'),
     ('emocionante', 'adj.', '令人兴奋的', 'emocionante'),
     ('aunque', 'conj.', '不过，虽然', 'aunque'),
     ('exigir', 'tr.', '需要，要求', 'exige')]),
   ('在最初的几个星期里，即使是最简单的事，比如开银行账户或预约看病，也可能变得很复杂。', [
     ('incluso', 'adv.', '甚至，即使', 'incluso'),
     ('sencillo', 'adj.', '简单的', 'sencillas'),
     ('cuenta bancaria', 'f.', '银行账户', 'cuenta bancaria'),
     ('pedir una cita médica', 'loc.', '预约看病', 'pedir una cita médica'),
     ('resultar', 'intr.', '变得，显得', 'resultar')]),
   ('此外，移居者还必须适应新的习俗，并学会用另一种语言交流。', [
     ('acostumbrarse a', 'loc.', '习惯于，适应', 'acostumbrarse a'),
     ('costumbre', 'f.', '习俗，习惯', 'costumbres'),
     ('aprender a + inf.', 'loc.', '学会做某事', 'aprender a'),
     ('comunicarse', 'prnl.', '交流，沟通', 'comunicarse')]),
   ('感到思乡、想念朋友，这是很正常的。', [
     ('es normal + inf.', 'loc.', '……是正常的', 'Es normal'),
     ('sentir nostalgia', 'loc.', '思乡，怀念', 'sentir nostalgia'),
     ('echar de menos', 'loc.', '想念（某人）', 'echar de menos')]),
   ('不过，参加当地活动、保持开放的心态，能让人更容易适应。', [
     ('sin embargo', 'loc.', '然而，不过', 'Sin embargo'),
     ('participar en', 'loc.', '参加，参与', 'participar en'),
     ('actitud abierta', 'f.', '开放的心态', 'actitud abierta'),
     ('facilitar', 'tr.', '使容易，促进', 'facilita')]),
   ('随着时间的推移，这些差异不再像是障碍，而是变成了学习的机会。', [
     ('con el tiempo', 'loc.', '随着时间推移', 'Con el tiempo'),
     ('dejar de + inf.', 'loc.', '不再（做某事）', 'dejan de'),
     ('obstáculo', 'm.', '障碍', 'obstáculos'),
     ('convertirse en', 'loc.', '变成，成为', 'se convierten en')]),
  ]},
 'b1_03': {
  'title_zh': '图书馆的价值',
  'note': '特别判断：第 3 句句首的 Muchas 是代词，指前文的 bibliotecas，单列为 pron.；第 2 句 encuentro 译作“交流”（人与人相聚、碰面）；'
          'sino 只在第 2 句列，第 6 句不重复；第 4 句 podrían 是条件式，词条注明。',
  'npc': {'2': [{'after': 'de estudio,', 'why': '列举：espacios de estudio, encuentro y participación cultural（A, B y C）'}],
          '3': [{'after': 'talleres,', 'why': '列举：talleres, clubes de lectura y actividades para niños（A, B y C）'}]},
  's': [
   ('虽然如今我们可以获取海量的数字信息，但图书馆仍然发挥着重要的作用。', [
     ('aunque', 'conj.', '虽然，尽管', 'Aunque'),
     ('tener acceso a', 'loc.', '能获取，能使用', 'tenemos acceso a'),
     ('una enorme cantidad de', 'loc.', '大量的，海量的', 'una enorme cantidad de'),
     ('seguir + 副动词', 'loc.', '仍在……，继续……', 'siguen'),
     ('desempeñar una función', 'loc.', '发挥作用', 'desempeñando una función')]),
   ('图书馆不只是存放书籍的地方，更是学习、交流和参与文化活动的空间。', [
     ('únicamente', 'adv.', '仅仅，只', 'únicamente'),
     ('guardar', 'tr.', '存放（se 表被动）', 'se guardan'),
     ('sino', 'conj.', '而是（no…sino…）', 'sino'),
     ('encuentro', 'm.', '相聚，交流', 'encuentro')]),
   ('很多图书馆都开设工作坊、读书会和儿童活动。', [
     ('mucho', 'pron.', '许多（此处指图书馆）', 'Muchas'),
     ('ofrecer', 'tr.', '提供，开设', 'ofrecen'),
     ('taller', 'm.', '工作坊，研习班', 'talleres'),
     ('club de lectura', 'm.', '读书会', 'clubes de lectura')]),
   ('此外，图书馆让人们能够免费获取一些资源，而这些资源有些人可能负担不起。', [
     ('permitir + inf.', 'loc.', '使能够，允许', 'permiten'),
     ('acceder a', 'loc.', '获取，使用', 'acceder'),
     ('gratuitamente', 'adv.', '免费地', 'gratuitamente'),
     ('poder', 'tr.', '能够（此为条件式）', 'podrían')]),
   ('在一个充满各种干扰的社会里，图书馆提供了一个能让人静心专注的安静环境。', [
     ('abundar', 'intr.', '大量存在，比比皆是', 'abundan'),
     ('distracción', 'f.', '使人分心的事', 'distracciones'),
     ('entorno', 'm.', '环境', 'entorno'),
     ('concentrarse', 'prnl.', '集中注意力', 'concentrarse')]),
   ('图书馆的未来不在于与互联网竞争，而在于把数字资源与共享空间的价值结合起来。', [
     ('depender de', 'loc.', '取决于', 'depende de'),
     ('competir con', 'loc.', '与……竞争', 'competir con'),
     ('combinar A con B', 'loc.', '把A与B结合', 'combinar'),
     ('compartido', 'adj.', '共享的', 'compartido')]),
  ]},
 'b1_04': {
  'title_zh': '负责任的旅游',
  'note': '特别判断：第 3 句 comercios 指“商店”而不是“商业”，故意列出；第 4 句 dañen 是关系从句里的虚拟式（先行词不确指）；'
          '第 3 句三个谓语并列（utilizan…, respetan… y compran…）按列举处理，逗号不停顿。',
  'npc': {'3': [{'after': 'transporte público,', 'why': '列举：si utilizan…, respetan… y compran…（三个谓语 A, B y C）'}]},
  's': [
   ('旅游业能创造就业，让人了解其他文化，但如果在缺乏规划的情况下发展，也可能带来问题。', [
     ('generar empleo', 'loc.', '创造就业', 'genera empleo'),
     ('permitir + inf.', 'loc.', '使能够，让', 'permite'),
     ('desarrollarse', 'prnl.', '发展', 'se desarrolla'),
     ('planificación', 'f.', '规划', 'planificación')]),
   ('在一些旅游目的地，游客增多推高了房价，还带来噪音或垃圾堆积的问题。', [
     ('destino', 'm.', '（旅游）目的地', 'destinos'),
     ('encarecer', 'tr.', '使涨价', 'encarece'),
     ('vivienda', 'f.', '住房', 'vivienda'),
     ('ruido', 'm.', '噪音', 'ruido'),
     ('residuo', 'm.', '垃圾，废弃物', 'residuos')]),
   ('游客如果乘坐公共交通、遵守当地规定、在小商店购物，就能为减少这些影响出一份力。', [
     ('contribuir a', 'loc.', '有助于，为……出力', 'contribuir a'),
     ('reducir', 'tr.', '减少', 'reducir'),
     ('respetar', 'tr.', '遵守，尊重', 'respetan'),
     ('norma', 'f.', '规定，规范', 'normas'),
     ('comercio', 'm.', '商店，店铺', 'comercios')]),
   ('避免破坏自然区域的行为也很重要。', [
     ('evitar', 'tr.', '避免', 'evitar'),
     ('comportamiento', 'm.', '行为，举止', 'comportamientos'),
     ('dañar', 'tr.', '损害（此为虚拟式）', 'dañen'),
     ('espacio natural', 'm.', '自然区域', 'espacios naturales')]),
   ('负责任地旅行并不意味着放弃享受，而是要明白：我们到访的地方，是那些常年生活在那里的人的家园。', [
     ('de forma responsable', 'loc.', '负责任地', 'de forma responsable'),
     ('renunciar a', 'loc.', '放弃', 'renunciar a'),
     ('sino', 'conj.', '而是（no…sino…）', 'sino'),
     ('hogar', 'm.', '家，家园', 'hogares'),
     ('quienes', 'pron.', '……的人（们）', 'quienes')]),
  ]},
 'b1_05': {
  'title_zh': '食物与记忆',
  'note': '特别判断：第 2 句 dulce 是名词“甜点”；transportarnos、recordarnos、ayudarles 都是不定式后接代词，释义里注明代词所指；'
          '第 6 句 mesa 借指“一起吃饭”，译文保留“餐桌”。',
  'npc': {},
  's': [
   ('味道和气味与我们的记忆紧密相连。', [
     ('sabor', 'm.', '味道', 'sabores'),
     ('olor', 'm.', '气味', 'olores'),
     ('estrechamente', 'adv.', '紧密地', 'estrechamente'),
     ('relacionado con', 'loc.', '与……有关的', 'relacionados con'),
     ('recuerdo', 'm.', '记忆，回忆', 'recuerdos')]),
   ('一碗汤可以把我们带回祖父母的厨房，而一份甜点则能让我们想起童年时的某个节日。', [
     ('transportar', 'tr.', '带到（nos 指我们）', 'transportarnos'),
     ('mientras que', 'loc.', '而（表对比）', 'mientras que'),
     ('dulce', 'm.', '甜食，甜点', 'dulce'),
     ('recordar', 'tr.', '使想起（nos 指我们）', 'recordarnos'),
     ('infancia', 'f.', '童年', 'infancia')]),
   ('因此，食物的作用不仅仅是提供营养，它还传递着家庭的故事和习俗。', [
     ('por eso', 'loc.', '因此，所以', 'Por eso'),
     ('cumplir una función', 'loc.', '起……作用', 'cumple'),
     ('nutritivo', 'adj.', '营养的', 'nutritiva'),
     ('transmitir', 'tr.', '传递，传承', 'transmite'),
     ('costumbre', 'f.', '习俗，传统', 'costumbres')]),
   ('人们移居国外后，做家乡菜能帮助他们与故土保持联系。', [
     ('emigrar', 'intr.', '移居国外', 'emigran'),
     ('receta', 'f.', '食谱，菜谱', 'recetas'),
     ('ayudar a + inf.', 'loc.', '帮助（les 指他们）做', 'ayudarles a'),
     ('vínculo', 'm.', '纽带，联系', 'vínculo'),
     ('lugar de origen', 'm.', '故乡，原籍', 'lugar de origen')]),
   ('同时，和别人分享这些菜肴，也能促进文化交流。', [
     ('al mismo tiempo', 'loc.', '同时', 'Al mismo tiempo'),
     ('compartir', 'tr.', '分享', 'compartir'),
     ('favorecer', 'tr.', '促进，有利于', 'favorece'),
     ('intercambio cultural', 'm.', '文化交流', 'intercambio cultural')]),
   ('就这样，餐桌变成了一个建立人际关系的地方。', [
     ('mesa', 'f.', '餐桌；借指共餐', 'mesa'),
     ('convertirse en', 'loc.', '变成，成为', 'se convierte'),
     ('así', 'adv.', '就这样，因此', 'así'),
     ('construir', 'tr.', '建立（se 表被动）', 'se construyen')]),
  ]},
 'b1_06': {
  'title_zh': '小组学习',
  'note': '特别判断：第 3 句 reunión 指小组碰头讨论，译作“小组讨论”；una sola persona 的 sola 前置，意思是“唯一的”，单列 solo adj.；'
          '第 2、4 句的 para que、consistir en que 后接虚拟式，释义里注明；第 5 句 no solo…sino que 以 sino que 为标注位置。',
  'npc': {'5': [{'after': 'a escuchar,', 'why': '列举：aprende a escuchar, argumentar y colaborar（A, B y C）'}]},
  's': [
   ('和别人一起学习可以加深对一门学科的理解，因为每个学生都会带来自己的知识和不同的讲解方式。', [
     ('materia', 'f.', '科目，学科', 'materia'),
     ('ya que', 'loc.', '因为，既然', 'ya que'),
     ('aportar', 'tr.', '贡献，带来', 'aporta'),
     ('conocimiento', 'm.', '知识', 'conocimientos'),
     ('distinto', 'adj.', '不同的', 'distintas')]),
   ('不过，要让小组有效运作，就必须确立目标、分配任务。', [
     ('sin embargo', 'loc.', '然而，不过', 'Sin embargo'),
     ('para que', 'loc.', '为了，以便（+虚拟式）', 'para que'),
     ('funcionar', 'intr.', '运转（此为虚拟式）', 'funcione'),
     ('repartir', 'tr.', '分配', 'repartir')]),
   ('如果大家同时说话，或者只有一个人包揽全部工作，小组讨论就会失去效率。', [
     ('al mismo tiempo', 'loc.', '同时', 'al mismo tiempo'),
     ('solo', 'adj.', '唯一的，单独的', 'sola'),
     ('reunión', 'f.', '碰头，聚会', 'reunión'),
     ('perder eficacia', 'loc.', '失去效果', 'pierde eficacia')]),
   ('一个好办法是：每个成员各准备一部分，然后讲给其他人听。', [
     ('consistir en que', 'loc.', '在于（+虚拟式）', 'consiste en que'),
     ('miembro', 'm.', '成员', 'miembro'),
     ('explicar', 'tr.', '讲解（la 指那部分）', 'la explique'),
     ('los demás', 'pron.', '其他人，别人', 'los demás')]),
   ('这样一来，小组不仅能复习知识，还能学会倾听、论证与合作。', [
     ('de esta manera', 'loc.', '这样一来', 'De esta manera'),
     ('repasar', 'tr.', '复习', 'repasa'),
     ('no solo…sino que', 'loc.', '不仅……而且……', 'sino que'),
     ('aprender a + inf.', 'loc.', '学会做某事', 'aprende a'),
     ('argumentar', 'intr.', '论证，说理', 'argumentar')]),
  ]},
 'b1_07': {
  'title_zh': '社区小商店',
  'note': '特别判断：第 2 句 trato personal 译作“贴心的个人服务”；第 5 句 los hace diferentes 的 los 指小商店，'
          '词条写成 hacer + 宾语 + adj.；comercio de barrio 标题译作“社区小商店”。',
  'npc': {'2': [{'after': 'trato personal,', 'why': '列举：trato personal, conocimiento del vecindario y productos…（A, B y C）'}]},
  's': [
   ('在很多城市，小商店很难与大型连锁店和数字平台竞争。', [
     ('tener dificultades para', 'loc.', '难以（做某事）', 'tienen dificultades para'),
     ('competir con', 'loc.', '与……竞争', 'competir con'),
     ('cadena', 'f.', '连锁店', 'cadenas'),
     ('plataforma digital', 'f.', '数字平台', 'plataformas digitales')]),
   ('不过，它们有一些未必体现在价格上的优势：贴心的个人服务、对街坊的了解，以及精心挑选的商品。', [
     ('sin embargo', 'loc.', '然而，不过', 'Sin embargo'),
     ('ventaja', 'f.', '优势，好处', 'ventajas'),
     ('reflejarse en', 'loc.', '体现在……上', 'se reflejan en'),
     ('trato personal', 'm.', '贴心的个人服务', 'trato personal'),
     ('vecindario', 'm.', '街坊，社区', 'vecindario')]),
   ('在这些店里购物，有助于让一个地区的经济活动保持活力。', [
     ('establecimiento', 'm.', '商店，店铺', 'establecimientos'),
     ('ayudar a + inf.', 'loc.', '有助于', 'ayudar a'),
     ('mantener vivo', 'loc.', '使保持活力', 'mantener viva'),
     ('zona', 'f.', '地区，片区', 'zona')]),
   ('为了适应变化，一些商家已经开始使用社交网络和送货服务。', [
     ('adaptarse', 'prnl.', '适应', 'adaptarse'),
     ('empezar a + inf.', 'loc.', '开始做某事', 'han empezado a'),
     ('redes sociales', 'f.', '社交网络', 'redes sociales'),
     ('servicio de entrega', 'm.', '送货服务', 'servicios de entrega')]),
   ('挑战在于把新工具与让它们与众不同的东西结合起来：与顾客的亲近，以及顾客的信任。', [
     ('reto', 'm.', '挑战', 'reto'),
     ('herramienta', 'f.', '工具', 'herramientas'),
     ('aquello que', 'loc.', '……的东西（中性）', 'aquello que'),
     ('hacer + 宾语 + adj.', 'loc.', '使……变得', 'los hace'),
     ('cercanía', 'f.', '亲近，贴近', 'cercanía')]),
  ]},
 'b1_08': {
  'title_zh': '社交网络的影响',
  'note': '特别判断：第 2 句 comparación 译作“攀比心理”；第 5 句 seguir 指在社交网络上“关注”账号；'
          '第 3 句 “…seleccionados, no la vida completa…” 的逗号是对比附加语，按说明照常停顿，不登记。',
  'npc': {'1': [{'after': 'noticias,', 'why': '列举：descubrir noticias, ideas o proyectos interesantes（A, B o C）'}]},
  's': [
   ('社交网络让我们能与远方的人保持联系，还能发现有趣的新闻、想法或项目。', [
     ('redes sociales', 'f.', '社交网络', 'redes sociales'),
     ('permitir + inf.', 'loc.', '使能够，让', 'permiten'),
     ('mantener el contacto con', 'loc.', '与……保持联系', 'mantener el contacto con'),
     ('descubrir', 'tr.', '发现', 'descubrir')]),
   ('然而，频繁使用社交网络也可能引发攀比心理和焦虑。', [
     ('no obstante', 'loc.', '然而，不过', 'No obstante'),
     ('constante', 'adj.', '持续的，频繁的', 'constante'),
     ('generar', 'tr.', '引起，产生', 'generar'),
     ('ansiedad', 'f.', '焦虑', 'ansiedad')]),
   ('屏幕上出现的图像，展示的往往是精挑细选的瞬间，而不是一个人生活的全貌。', [
     ('aparecer', 'intr.', '出现', 'aparecen'),
     ('pantalla', 'f.', '屏幕', 'pantalla'),
     ('soler + inf.', 'loc.', '通常，往往', 'suelen'),
     ('mostrar', 'tr.', '展示，显示', 'mostrar')]),
   ('因此，拿自己的日常生活和这些图像比较，可能会产生一种并不公正的失败感。', [
     ('comparar A con B', 'loc.', '把A和B比较', 'comparar'),
     ('rutina', 'f.', '日常生活', 'rutina'),
     ('injusto', 'adj.', '不公正的', 'injusta'),
     ('fracaso', 'm.', '失败', 'fracaso')]),
   ('一个解决办法是，检查我们在各种应用上花了多少时间，并谨慎选择要关注的账号。', [
     ('revisar', 'tr.', '检查，审视', 'revisar'),
     ('dedicar tiempo a', 'loc.', '把时间花在……上', 'dedicamos a'),
     ('con cuidado', 'loc.', '谨慎地，仔细地', 'con cuidado'),
     ('cuenta', 'f.', '账号', 'cuentas'),
     ('seguir', 'tr.', '关注（账号）', 'seguimos')]),
   ('如果我们有目的地使用科技，并给自己设定明确的界限，科技就会很有用。', [
     ('útil', 'adj.', '有用的', 'útil'),
     ('utilizar', 'tr.', '使用（la 指科技）', 'la utilizamos'),
     ('con intención', 'loc.', '有目的地', 'con intención'),
     ('límite', 'm.', '界限，限度', 'límites')]),
  ]},
 'b1_09': {
  'title_zh': '终身学习',
  'note': '特别判断：第 1 句 título 指学历证书，译作“学位”；第 3 句 lo hacen 的 lo 指“学习”这件事，词条写成 hacerlo；'
          '第 1 句较短，只给 3 个词条（terminar、obtener、título）。',
  'npc': {},
  's': [
   ('教育并不会在一个人拿到学位时就结束。', [
     ('terminar', 'intr.', '结束', 'termina'),
     ('obtener', 'tr.', '获得，取得', 'obtiene'),
     ('título', 'm.', '学位，文凭', 'título')]),
   ('科技和社会的变化，使人们有必要在一生中不断掌握新的技能。', [
     ('hacer necesario + inf.', 'loc.', '使……成为必要', 'hacen necesario'),
     ('adquirir', 'tr.', '获得，掌握', 'adquirir'),
     ('habilidad', 'f.', '技能，能力', 'habilidades'),
     ('a lo largo de', 'loc.', '在……整个过程中', 'a lo largo de')]),
   ('有些人学习是为了转行，而另一些人学习则是出于好奇或个人的满足感。', [
     ('cambiar de profesión', 'loc.', '转行，换职业', 'cambiar de profesión'),
     ('mientras que', 'loc.', '而（表对比）', 'mientras que'),
     ('hacerlo', 'loc.', '这样做（lo 指学习）', 'lo hacen'),
     ('por curiosidad', 'loc.', '出于好奇', 'por curiosidad')]),
   ('成年后再学习可能会比较困难，因为要承担家庭和工作上的责任，但也有灵活的课程和免费的资源可供选择。', [
     ('de adulto', 'loc.', '成年后', 'de adulto'),
     ('resultar', 'intr.', '显得，变得', 'resultar'),
     ('debido a', 'loc.', '由于，因为', 'debido a'),
     ('laboral', 'adj.', '工作的，劳动的', 'laborales'),
     ('gratuito', 'adj.', '免费的', 'gratuitos')]),
   ('关键在于设定切合实际的目标，并有规律地坚持练习。', [
     ('la clave está en', 'loc.', '关键在于', 'La clave está en'),
     ('fijar metas', 'loc.', '设定目标', 'fijar metas'),
     ('realista', 'adj.', '切合实际的', 'realistas'),
     ('con regularidad', 'loc.', '有规律地，经常', 'con regularidad')]),
   ('保持好奇心，有助于更好地理解世界，也有助于适应新的情况。', [
     ('mantener la curiosidad', 'loc.', '保持好奇心', 'Mantener la curiosidad'),
     ('ayudar a + inf.', 'loc.', '有助于', 'ayuda a'),
     ('mejor', 'adv.', '更好地（bien 的比较级）', 'mejor'),
     ('adaptarse a', 'loc.', '适应', 'adaptarse a')]),
  ]},
 'b1_10': {
  'title_zh': '城市与绿地',
  'note': '特别判断：第 5 句 autoridades 译作“有关部门”，deberían 是条件式，语气比 deben 委婉；'
          '第 6 句 Diseñarlos 的 los 指这些绿地；第 4 句 “…zonas verdes, y algunas…” 是两个分句之间的逗号，照常停顿。',
  'npc': {'2': [{'after': 'caminar,', 'why': '列举：para caminar, hacer ejercicio y reunirse…（A, B y C）'}]},
  's': [
   ('城市里的公园和花园能提高居民的生活质量。', [
     ('jardín', 'm.', '花园', 'jardines'),
     ('mejorar', 'tr.', '改善，提高', 'mejoran'),
     ('calidad de vida', 'f.', '生活质量', 'calidad de vida'),
     ('habitante', 'm.', '居民', 'habitantes')]),
   ('它们为人们提供了散步、锻炼以及与他人相聚的场所。', [
     ('proporcionar', 'tr.', '提供', 'Proporcionan'),
     ('caminar', 'intr.', '散步，步行', 'caminar'),
     ('hacer ejercicio', 'loc.', '锻炼，做运动', 'hacer ejercicio'),
     ('reunirse con', 'loc.', '与……相聚', 'reunirse con')]),
   ('此外，树木能提供树荫，还有助于在炎热的月份里降低气温。', [
     ('sombra', 'f.', '阴凉，树荫', 'sombra'),
     ('ayudar a + inf.', 'loc.', '有助于', 'ayudan a'),
     ('reducir', 'tr.', '降低，减少', 'reducir'),
     ('caluroso', 'adj.', '炎热的', 'calurosos')]),
   ('然而，并不是每个街区都有足够的绿地，而且有些绿地疏于管护。', [
     ('sin embargo', 'loc.', '然而，不过', 'Sin embargo'),
     ('contar con', 'loc.', '拥有，具备', 'cuentan con'),
     ('zona verde', 'f.', '绿地', 'zonas verdes'),
     ('mal cuidado', 'loc.', '疏于照料的', 'mal cuidadas')]),
   ('有关部门应当把这些空间视为城市规划中不可或缺的一部分。', [
     ('autoridad', 'f.', '（复）当局，有关部门', 'autoridades'),
     ('deber + inf.', 'loc.', '应该（条件式，较委婉）', 'deberían'),
     ('considerar A como B', 'loc.', '把A看作B', 'considerar'),
     ('planificación urbana', 'f.', '城市规划', 'planificación urbana')]),
   ('在居民的参与下设计这些绿地，能促使它们更好地满足社区的实际需求。', [
     ('diseñar', 'tr.', '设计（los 指绿地）', 'Diseñarlos'),
     ('vecino', 'm.', '居民，邻居', 'vecinos'),
     ('favorecer que', 'loc.', '促使（+虚拟式）', 'favorecer que'),
     ('responder a', 'loc.', '满足，回应（需求）', 'respondan a')]),
  ]},
}


def main():
    for pid, d in DATA.items():
        path = DIR / f'{pid}.json'
        p = json.loads(path.read_text('utf-8'))
        sents = [s for para in p['paras'] for s in para]
        assert len(sents) == len(d['s']), (pid, len(sents), len(d['s']))
        used = set()
        for s, (zh, ws) in zip(sents, d['s']):
            s['zh'] = zh
            items = []
            for h, pos, gloss, surf in ws:
                assert pos in POS, (pid, h, pos)
                used.add(pos)
                items.append({'h': h, 'pos': pos, 'zh': gloss, 'surface': surf, 'source': 'supplement'})
            items.sort(key=lambda w: s['es'].find(w['surface']))
            s['w'] = items
        p['title_zh'] = d['title_zh']
        p['pos_legend'] = {k: v for k, v in POS.items() if k in used}
        p['no_pause_commas'] = d['npc']
        n = int(pid.split('_')[1])
        p['_说明'] = (f'西班牙语分级阅读文章集（用户 2026-10-18 发来的 Word 文档《西班牙语A1-C1分级阅读文章集》）B1 第 {n} 篇。'
                     'es：原文（原样，按句号切句）；zh：逐句中文翻译；w：生词栏（全部为补充词条，source=supplement），'
                     'h 词头（词典原形）、pos 词性、zh 释义（按本句语境）、surface 句中原形（在句中恰好出现一次）；'
                     'B1 选词侧重连接词、带虚拟式的结构、动词搭配和社会生活类词汇，少选一眼就懂的同源词；'
                     '同一词头只在首次出现的句子里列。no_pause_commas：只登记列举中不停顿的逗号，其余逗号照常停顿。'
                     + d['note'])
        path.write_text(json.dumps(p, ensure_ascii=False, indent=1) + '\n', 'utf-8')
        print('wrote', pid)


if __name__ == '__main__':
    main()
