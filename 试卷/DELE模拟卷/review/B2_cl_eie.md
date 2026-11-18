# B2 阅读（cl.json）、写作（eie.json）审校记录

审校方式：先不看答案把 36 道题做了一遍，再对答案、解析、译文；逐句核对西语（拼写、重音、¿¡、性数、变位、搭配、RAE 正字法）、方言用法、词数、答案分布、正确项长度（最长项 4/20＝20%）；用脚本核对了解析里引用的西语原句（T1—T3 全部和原文一字不差；T4 的引文是填好空的句子，也对）。写作逐句核对了录音原文（3 个声音、19 句、每句 8—22 词、无缩写符号拟声词）和范文里的每一个数字、每一个要点。art_lectura.json 是空数组，本卷阅读和写作不用插图（图表由程序画），没有要审的。

## 修改

| 位置 | 原来的问题 | 怎么改的 |
|---|---|---|
| cl.T2 文本 D（安德烈斯，墨西哥） | “me advirtieron de que perdería clientes”：advertir de que 是西班牙偏好的写法，墨西哥人口语里一般说 advertir que（两种都合规范） | 改为 “me advirtieron que perdería clientes” |
| cl.T2 文本 D | 前面已有 “Lo curioso es que…”，最后一句又是 “y, curiosamente, gano casi lo mismo”，短文里重复；而且这里要表达的是让步（工时少了，收入却没少） | 改为 “Hoy trabajo menos horas y, aun así, gano casi lo mismo que antes.”；译文“奇怪的是，挣得和以前差不多”改为“可挣得还是和以前差不多”。词数仍是 135 |
| cl.T2.13 解析 | 只给 B（阿根廷 voseo）加了方言注释，D 的墨西哥用法没有说明 | 句末加注：“Ya pasó un año”用简单过去时表示到现在为止的事，是拉美常见用法（西班牙多说 ya ha pasado） |
| cl.T1 译文第 5 段 | “renunciar a la propiedad”译成“放弃私有财产”，带政治色彩，原文说的是“拥有物品” | 改为“放弃拥有自己的东西” |
| cl.T3 多余片段 F 的说明 | 只解释了为什么不能放第 19 空；F 以 “Por eso” 开头，学生也可能想放在第 18 空（“镇政府看到机会，所以村民卖房”），说明里没有排除 | 补一句：放在第 18 空也不行，“oportunidad”推不出“Por eso… vender sus casas”，而且和镇政府想“frenar la despoblación”相反（第 18 空只有 A 能放） |
| cl.T4.26 解析 | 说 constar “不能和 en 搭配”不准确：constar en（记载于）是存在的 | 改为：constar de 是“由……组成”，constar en 是“记载在……里”，都不能表示“工作的内容是……” |
| eie.T1 范文第 2 段 | 录音是 “al menos cuatro noches por semana”，范文写成“cuatro noches por semana”，条件转述不准 | 改为 “al menos cuatro noches por semana”；译文改为“每周至少要……吃四次晚饭” |
| eie.T1 范文第 4 段 | 要点 2 要求概括“条件”，要点 4 要求说明“怎么申请”，录音里明确说学生要“pasar una entrevista”，范文没提 | 末句加 “; además, tendrás que pasar una entrevista.”；译文、点评同步补上 |
| eie.T1 范文第 1 段 | 为了把新增内容放进字数上限 | “ahora que buscas piso para el próximo curso” 删去 “para el próximo curso”（任务说明里已交代）；译文同步。范文 173→177 词（150—180） |
| eie.T2 Opción 2 范文第 1 段 | “La segunda novela … pertenece, sin duda, al segundo grupo”，segunda / segundo 紧挨着重复，读起来别扭 | 改为 “pertenece, sin duda, a este último grupo” |
| eie.T2 Opción 2 范文末段 | 要点 4 是“推荐给哪类读者、为什么”，原句 “Se la recomiendo a quienes disfruten de las historias familiares y no tengan prisa.” 只说了哪类读者，“为什么”要读者自己推 | 改为 “Por eso se la recomiendo a lectores pacientes que disfruten de las historias familiares.”，用 Por eso 接上前一句（中段节奏慢，但结尾值得）；译文、点评同步。范文 176→177 词 |

## 已逐题核对、没有改的部分

- cl.T1（文章，446 词，答案 B C A C A B）：第 1—6 题答案唯一，每个干扰项都被原文明确否定（第 2 题借期是一周、年费不是按件收；第 4 题 A 是“en primer lugar”的意料之中的好处；第 5 题 B 是假设句、C 是“algunos”）。“no cree que vayamos a renunciar… ni que eso fuera deseable”里 fuera 表示假设，语法可以。
- cl.T2（4 篇，134—136 词，答案 C A D B A C D A B C，A、C 各 3 次，B、D 各 2 次）：10 题逐题核对，每题只有一篇对得上。B 的 voseo（vos aguantás）只出现在女儿的话里，和 celular、colectivo、“Ya volví”一致，没有西班牙专用词；D 没有西班牙专用词（没有 móvil、ordenador、vosotros 之类）。A、C 是西班牙人，用词相符（pan comido、tartas、encargos）。
- cl.T3（文章 438 词，片段 17—20 词）：答案 D A H E G C 唯一。B 只能试第 20 空，与 “No hay hoteles, no hay transporte…” 矛盾；F 第 18、19 空都放不进（见上）；其余空的语义、指代（el vídeo、Ese contraste、La reserva、resume 的主语）都只指向一个片段。
- cl.T4（传记 424 词，答案 A 4、B 5、C 5）：14 空逐空核对，每空另外两个选项都明确错（语式、搭配、前置词、关系词性数、laísmo、como si 后的时态），没有“也说得通”的。第 28 空 sin 要靠冒号后的 “firmados con las iniciales del director” 排除，B2 能做到。年代一致：1903 年生，19 岁到马德里，1939 年到墨西哥，1977 年后回加的斯，1987 年去世，84 岁。
- 阅读文本总词数 1849（规格 1750—1950）。
- eie.T1：录音 247 词（200—250），女1（播音员）、男2（协调人）、女3（78 岁的梅塞德斯）三个声音，人物和声音一一对应；无缩写、%、€、拟声词、单独的 “Sí.”；数字（60 euros、18 y 30 años、65 años、78 años、15 de julio）都可以朗读。说明语和要点写法同真考，没写 “Número de palabras”。改后的范文五个要点都完成，每条信息都能在录音里找到依据。
- eie.T2 Opción 1：图表数据 2016／2026——社交网络 48／71、电视 61／33、数字报纸 39／36、视频平台 22／47、广播 24／15、纸质报纸 17／5，可多选所以合计超过 100，说明语里写了。范文提到的数字和说法都对得上：电视 61 %→33 %、社交网络 71 % 成为第一（2016 年第一是电视 61 %）、视频平台 22→47“se ha duplicado con creces”（47 > 44，确实一倍多）、纸质报纸 17→5“casi ha desaparecido”。范文 173 词，要点齐全。
- eie.T2 Opción 2：简介 217 词（200—250）；范文和简介一致（1989 年 8 月、卢戈海边、四兄妹、母亲宣布卖房、托马斯去了布宜诺斯艾利斯、作者第二部小说），没有透露结局；用 vosotros 称呼博客读者，前后一致。
- 评分项说明和规格一致（分析量表 60%、整体 40%，0—3 分）。
- check_content.py B2 cl eie：0 个错误，0 个提醒，PASS。

## 拿不准、没有改的

- cl.T1.4 正确项 C “los lazos que acaban creándose entre los socios”：原文说的是使用者参加维修工作坊、“enseñando a otros vecinos”，严格说是“使用者和邻居之间”，不一定都是会员。题目只有 C 能选，A、B 都被原文否定，所以没改；如果主编想更严谨，可以改成 “entre los vecinos”（但 vecinos 是原文词）。
- eie.T2 Opción 1 范文第 3 段讲原因只有一句（手机让信息即时、免费、随手可得），对 B2 的好答卷来说略单薄；字数已到 173，要展开就得删别处，没动。
- eie.T1 范文里 “personas mayores que están solas”：录音是 “viven solas”。están solas 也说得通（独自一人），而改成 viven 会和前面的 vivan 重复，所以保留。
- cl.T1.4 正确项 C 由“los lazos que acaban creándose entre los socios.”改为“las relaciones que surgen entre quienes las usan.”（原文说的是使用者教“otros vecinos”、互相认识，不限于会员之间；主编按审校的疑问修改）。

## 统稿：阅读 T1 换题

原 T1“Bibliotecas de cosas: pedir prestado en lugar de comprar”和听力 T3（电台访谈，“物品图书馆”）同一话题，保留听力，阅读 T1 整篇换掉。新话题“公共饮水泉重新回到街头”换题前查过五套卷子所有 json 的 tema_zh、标题和正文（fuente、grifo、agua potable、sequía、饮水、水泉等），没有用过。上面“已逐题核对”和“拿不准”里关于 cl.T1 的几条说的是旧文本，已经不适用。

- cl.T1 instruccion_es：“un artículo sobre las llamadas bibliotecas de cosas”改为“un artículo sobre la recuperación de las fuentes públicas”，其余照旧；instruccion_zh 同步改为“阅读一篇关于公共水泉重新兴起的文章……”。
- cl.T1 tema_zh：改为“城市生活与环境：公共饮水泉重新回到街头（信息类文章）”。
- cl.T1 文本：标题改为“Beber en la calle: la segunda vida de las fuentes públicas”（titulo_zh“在街头喝水：公共水泉的第二次生命”），署名改为 Clara Montiel（虚构）；正文 6 段全部新写（水泉的旧日作用和衰落、复兴的两个原因、信任问题和工程师 Nieves Arrieta 的话、维护费和干旱时关停的争议、新一代水泉的设计、作者的看法），不提真实城市和真实数据。
- cl.T1 zh：6 段译文全部新写，和西语逐段对应。
- cl.T1 palabras：446→446（新文本按 check_content 的数法也是 446 词，规格 400—450）；阅读四篇总词数仍是 1849（1750—1950）。
- cl.T1.1—6：6 道题全部新出，按文本顺序一段一题，答案 C A C B A B（A、B、C 各 2 次，原来是 B C A C A B）；每题两个干扰项都被原文否定或没有依据（借用原文词：pueblos y barrios、miles de litros、dar ejemplo de ahorro、directamente del caño、número de grifos 等）；正确项都换了说法，没有和原文连续 4 个词相同。
- cl.T1 正确项最长：6 题里只有第 5 题正确项最长（54／52／53 个字符）；整个阅读部分 5/20＝25%（原来 4/20）。
- cl.T1.1—6 解析：全部新写，西语引文用脚本核对过和原文一字不差，每个干扰项都有一句说明。
- check_content.py B2 cl：0 个错误，0 个提醒，PASS。

## 统稿复核（阅读 T1 新文本）

- 主审逐句看过新文本、6 道题和解析：西语地道，难度符合 B2，每题只有一个答案有原文依据，中文译文对应。
- cl.T1.preguntas[1]（第 2 题）：干扰项 C 原为“ayudan a los vecinos a gastar menos dinero en agua embotellada”。省钱确实是原文里水泉复兴的理由之一，考生可能争辩，所以改为原文没有依据的“lo han reclamado durante años los trabajadores que pasan el día en la calle.”。正确项 A 的“a quien está muchas horas fuera de casa”对无家可归的人不贴切，改为“a quien pasa gran parte del día al aire libre.”。解析同步改写。答案仍是 A；正确项不是三项中最长的。
- 再跑 `/usr/bin/python3 tools/check_content.py B2 cl`：0 个错误，0 个提醒，PASS。
