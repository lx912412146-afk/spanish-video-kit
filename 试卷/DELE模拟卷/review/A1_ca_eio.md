# A1 听力（ca.json）、口语（eio.json）、插图清单（art_audio.json）· 第二审校记录

审校方法：先不看答案把听力 25 题做了一遍，再对答案和解析；录音原文逐句数词（按 check_content.py 的分词和分句规则），查缩写、符号、拟声词、单独的 Sí/No/Vale；对照 build_pdf.py 看口语卡片和考官提示会怎样印出来。

## 改动

| 位置 | 原来的问题 | 怎么改的 |
|---|---|---|
| ca.T1.0 seg0 | “Buenos días, señor.” 一句只有 3 个词（规则 4—25 词） | 并成一句 “Buenos días, señor, ¿qué va a tomar?” |
| ca.T1.0 seg2 | “¿Quiere un té?” 3 个词 | 改为 “¿Quiere usted un té?” |
| ca.T1.1 seg1 | “Cuesta 80 euros.” 3 个词 | 改为 “Cuesta 80 euros, pero también tenemos cosas más baratas: corbatas y libros de cocina.”（词数不变），中文同步 |
| ca.T1.3 seg0 | “¿Puedo ir andando?” 3 个词；而且问句放在最后，女士接着答 “Sí, está bastante lejos”，“Sí” 听起来像在回答“能走着去吗” | 调换顺序：“Perdone, ¿puedo ir andando al museo de arte? ¿Está lejos de aquí?”，“Sí” 回答的是“远不远”；中文同步 |
| ca.T1.3 seg2 | “Muchas gracias, señora.” 3 个词 | 改为 “Vale, entonces voy en metro, muchas gracias.”；中文同步 |
| ca.T1.3 解析、ca.T1 tema_zh | 同一个 museo de arte，译文作“美术馆”，解析和话题说明作“博物馆” | 统一为“美术馆” |
| ca.T1.5 seg2 | “¿Y el domingo?” 3 个词 | 改为 “Bueno, ¿y el domingo? …” |
| ca.T1.5 seg1 | 上一处加了 1 个词，这段会到 41 词（规格 30—40） | “voy a la piscina a nadar” 改为 “nado en la piscina”（意思不变，答案仍是 C）；解析引文、中文同步。本段 39 词 |
| ca.T2.6 | “Atención, señores clientes.” 3 个词 | 用冒号并进下一句：“Atención, señores clientes: hoy, en la sección de pescado, …”（词数不变） |
| ca.T2.10 | “Atención, por favor.” 3 个词 | 同上：“Atención, por favor: la biblioteca cierra en quince minutos.”；解析引文改成小写 la，和原文一致 |
| ca.T3.0 解析 | 引文 “estudia Medicina …” 和原文大小写不一致（原文句首 Estudia） | 改为 “Estudia Medicina …” |
| ca.T3.13 解析 | 结尾 C 是从 “pueblo pequeño” 推出来的，解析没有点明 | 加一句“pueblo（村镇）和 ciudad（城市）相对”，同时压缩了后半句，字数不增加 |
| ca.T4 seg1 | “Muy bien, Inés.” 3 个词 | 改为 “Muy bien, gracias, Inés.”；中文同步 |
| ca.T4 seg7 | 上下两处一共加了 3 个词，T4 会到 186 词（规格 160—185）；“Hay de todo” 是 A2 的固定说法，答题用不到 | 删去 “Hay de todo:”，改为 “Al lado de mi casa hay una farmacia y el supermercado está muy cerca.”；中文同步。第 22 题的解析引文本来就是这一句，不用改 |
| ca.T4 seg8 | “¿Vas en coche?” 3 个词 | 改为 “¿Vas en tu coche?”；第 23 题解析的引文同步 |
| ca.T4 seg14 | “¡Hasta el sábado!” 是 3 个词的感叹句。make_audio.py 只把少于 3 个词的短句并进前后句，这一句会单独合成；而且这段对话里已经有 “¡Qué bonito!”“¡Qué suerte!” 两个短感叹句 | 改为 “¡Nos vemos el sábado!”（4 个词）。中文“星期六见！”不变 |
| ca.T4.20 解析 | “他妈妈只在后面说要做蛋糕”读起来像是妈妈自己说话（其实是 Raúl 说的） | 改为“后面提到的妈妈只是要给聚会做蛋糕，并不和他住在一起，而且 madre 也不在选项里” |
| eio.T2 notas_zh | 考官提示里写了“卡片下方的提示问题写在 texto 里，排版时放进卡片下方的框”。这是写给排版程序的话，会原样印进教师用书的“考官提示” | 换成给考官看的说明：卡片上每个方面旁边的提示问题只是帮考生组织内容，考生不用逐条回答，讲三个方面就行 |
| eio.T2 guion | “¿Qué tema prefiere…?” 听起来像是现在才选，可考生在准备室已经选好、也准备好了 | 改为 “¿Qué tema ha preparado: Mi tiempo libre o La comida?”（T3 的考官话里已经用了现在完成时 Hemos terminado） |
| eio.T3 modelo | 考官提示要求“不要问考生在 T2 已经讲清楚的内容”，可参考对话里问了三个 T2 范文已经讲过的问题：“¿Y qué deporte hace?”（已说打羽毛球）、“¿Qué series le gustan?”（已说中国爱情剧）、“¿Y qué hace en vacaciones?”（已说回成都） | 改成追问新信息：“Usted juega al bádminton. ¿Hace otros deportes?”“¿Y ve series en español?”“¿Y qué va a hacer en las vacaciones de invierno?”，考生的回答也改成接着往下说，不再重复 T2；modelo_zh 同步。对话现在 251 词，3—4 分钟 |
| art A1_CA1_5A—5C | A、B 是物品（一个足球；球拍和网球），C 是一个女人在游泳。构图不统一，C 是唯一画了人的图，有点显眼 | 三张图画同一个年轻女子，分别在踢足球、打网球、游泳，动作写清楚；和题目 “¿Qué hace Carmen…?” 问的“做什么”对得上 |
| art A1_CA1_3A—3C | A 画人在走路，B、C 只画车辆，构图不统一 | 三张图画同一个男孩：走路，在地下站台等地铁，上公交车；地铁要能看出在地下，公交车画出开着的门 |
| art A1_CA1_4A—4C | 三张天气图构图不统一（A 有树，B 有云和伞，C 只有太阳） | 三张图里是同一棵树、同一片地面：A 树被风吹弯、叶子飞；B 树直立、灰云和雨点、旁边一把撑开的伞；C 树直立、蓝天和大太阳。每张图都写明不画另外两种天气的标志 |
| art A1_CA1_0C、A1_CA2_A、A1_CA2_G | “几颗咖啡豆”“几支蜡烛”“几条沙丁鱼”，数量没写，画图时要靠猜 | 写成三颗、五支、四条，并补了一句“三张饮料图大小、角度相同” |

## 改动后的数字

- 录音词数：T1 共 234（例 37，第 1—5 段 40 / 39 / 40 / 39 / 39，规格 30—40），T2 共 144（每条 20—28，规格 15—30），T3 共 167（每句 16—23，规格 15—25），T4 共 183（规格 160—185）。**总词数 728**（规格 505—735）。
- 录音里还有两句不到 4 个词：T4 的 “¡Qué bonito!”“¡Qué suerte!”。都是两个词的感叹句，make_audio.py 会把它们并进后一句，按您说的保留。别的句子都在 4—25 个词之间。
- 没有缩写、符号、拟声词，也没有单独的 Sí / No / Vale。钟点、价钱用阿拉伯数字（80 euros、3 euros、300 euros），符合规则。
- 声音分配：同一段里人物和声音一一对应。男声角色都用男2，男1 只当播音员；男女声和人物性别相符。
- `check_content.py A1 ca eio art`：0 个错误，0 个提醒，PASS。

## 已逐题核对、没有改动的地方

- **听力 T1**：六段对话自己做了一遍，答案 B（例）、C、A、B、A、C，和 clave 一致，每题只有一个依据。每题的三张图都是录音里提到过的东西：饮料是 zumo / té / café con leche，礼物是 reloj / corbata / libro de cocina，钟点是 10:30 / 12:00 / 10:00，交通是 andando / metro / autobús，天气是 viento / lluvia（No llueve）/ sol（mañana），运动是 fútbol / tenis / piscina。tú 和 usted 用得前后一致。
- **听力 T2**：答案 C（例）、G、E、A、I、D，一张图只对应一条讯息。九张图各是不同的物品或地点，一眼能分开。
- **听力 T3**：九句开头各自只能配一个结尾。三个不用的结尾都有明确的诱因：F enseña música（钢琴老师是 Rosa 的丈夫，Hugo 只是自己弹）、H vive en Madrid（住在马德里的是表兄弟姐妹）、L vende pan（开面包店的是 Nerea 的妈妈）。它们按句首说的那个人去配，都配不上。
- **T3 结尾 C “no vive en una ciudad”（编写者提的问题）**：确认可以用。pueblo 和 ciudad 都是 A1 词汇，本来就是一对相对的词，“no + 动词”的否定也是 A1 语法，用不着超纲的推断。也没有别的开头配得上 C：Marta 在 Salamanca，Rosa 在 París，Nerea 在“市中心的书店”，Ramírez 住“隔壁的公寓”，都在城市里；Luis、Pilar、Hugo、Javier 没说住在哪里，没有依据。K “vive en otro país” 也套不到爷爷身上，因为录音没说那个村子在外国。
- **听力 T4**：答案 E（例）、C、H、G、A、F、I、D。只有 B domingo 一个选项不用，它是明确的干扰项（“El domingo no puedo”）。每个空在语法上能填的不止一个词（比如 22、25 两题都要阴性名词），但按录音只有一个对。
- **说明语**：四个 tarea 的 instruccion_es 和规格、题数一致（cinco / nueve imágenes, cinco / doce finales, ocho / nueve opciones, siete），中文译文准确。
- **中文译文**：逐句对过，意思一致，用的是全角标点。
- **口语 T1**：卡片上的七个方面和规格一致。参考回答 141 词，按 A1 的慢语速约 1.5 分钟，七个方面都讲到了，没有语言错误。
- **口语 T2（编写者提的问题）**：提示问题放在 opciones[].texto 里，每张卡 5 条，和 puntos 一一对应。build_pdf.py 在 texto 和 puntos 条数相同时会印成“方面＋提示问题”两栏表，这样放可以。两篇参考回答 232 / 226 词，各讲了三个方面，语言正确，水平是 A1 的好答卷。
- **口语 T3**：说明语和考生卡写清了“回答考官的问题＋向考官提两个问题”。考官问题每张卡 7 个，考官提示说清了挑 4—6 个问、不重复 T2 讲过的内容。
- **评分标准（criterios）**：两项的说明符合 A1。
- **插图清单的其余条目**：都画得出来，有字的图都写了 texto_en_imagen（10:30、12:00、10:00、2）。

## 拿不准、没有改的地方

1. **T2 不用的三张图（B 水果、F 出租车、H 篮球）录音里都没提到。**它们和讯息同属一类（超市、交通、体育中心），可以起干扰作用，但不是“录音里提到过的东西”。我没改，因为 T2 不提问，只要求“把讯息和图配起来”。如果哪条讯息里顺带提到了某张不用的图（比如超市广播说一句“今天没有水果”），考生就可以争辩那张图也和这条讯息有关，答案反而不唯一了。要不要按“干扰图也是录音里提到过的”来改 T2，请主编定。
2. **T1 例题和第 5 段各有 4 个话轮**，规格写的是“2—3 个话轮”。如果“话轮”指的是一问一答算一轮，就符合规格；如果指每个人说一次算一轮，就超了一轮。两段的词数（37、39）都在范围内，所以没有改。
3. **T3 第 18 题：E “habla cuatro lenguas” 和原文 “habla cuatro idiomas” 只差一个同义词**，比较容易。编写要求说正确项尽量不用原文的词。这道题在 A1 可以接受，我没改。
4. **T1 几条解析在 148—159 字之间**，略超“60—150 字”的上限，是因为引用的西语原句比较长，所以没有删。
