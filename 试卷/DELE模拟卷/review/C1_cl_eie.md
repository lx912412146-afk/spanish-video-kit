# C1 阅读与语言运用（cl.json）、书面表达、中介与互动（eie.json）审校记录

审校方式：五个阅读 tarea 先不看答案自己做一遍，再对答案；逐句查西语（拼写、重音、¿¡、性数、变位、搭配、RAE 正字法、拉美用词）、逐段对中文译文、逐条核对解析里引用的原句是否和原文一字不差；写作 T1 的录音逐句数词（4—25 词），范文里每一句转述都回录音原文里找依据；T2 选项 1 的范文数字逐个对图表。art_lectura.json 是空数组，C1 阅读、写作不用插图。改完 `check_content.py C1 cl eie`：0 个错误、0 个提醒，PASS。

## 改动（共 17 处，表中每行一处）

| 位置 | 原来的问题 | 怎么改的 |
|---|---|---|
| cl.T1.1 题干 | “una traductora que todavía no ha publicado ningún libro traducido”：例外条款说的是“personas sin traducciones publicadas”。只在杂志上发过译文、没出过书的人既不满足一般条件，字面上也不属于“没有发表过译文”的例外，较真的考生会质疑 b | 改为“…que todavía no ha publicado ninguna traducción…”，和例外条款一一对应 |
| cl.T1.2 选项 b | T1 六题里有四题正确项是最长的（2、3、4、6），会被考生利用 | 加长干扰项：“incluye una cantidad adicional para cubrir los gastos de viaje de quienes acompañen al residente.”（借用原文 gastos de viaje，仍然明确错） |
| cl.T1.4 选项 b | 同上 | 改为“tendrá que recuperar esos cuatro días quedándose en la sede después de que termine la estancia.”（借用原文 recuperarse，原文说获准离开的天数 no tienen que recuperarse）。T1 正确项最长降到 2/6，整个 cl 为 4/26 |
| cl.T2 片段 F | “la experiencia de quien vive en la calle”：vivir en la calle 是“无家可归、露宿街头”的固定说法，会误读 | 改为“la experiencia cotidiana de los vecinos”（后面接“para el vecino al que despierta”），中文改为“抹去了居民的日常感受”。F 是片段，不计入 T2 正文词数 |
| cl.T3 第 1 段 | “al bajar de un auto… el conductor se dio vuelta antes de que yo abriera la puerta”：已经下车又“还没开门”，时间矛盾；al bajar 的主语也和主句不一致 | 改为“cuando estaba por bajarme de un auto de aplicación en Palermo”（estar por + 不定式，阿根廷常用）；中文改为“我坐网约车到了巴勒莫区，正要下车，还没开门……”；词数 598 → 600 |
| cl.T3 第 6 段、第 18 题解析 | “jamás nos pidió un comprobante”：comprobante 是卖方开给买方的凭证，赊账的店主向欠账的邻居“要凭证”不合逻辑 | 改为“jamás nos hizo firmar nada”（从没让我们签过任何字据），中文、第 18 题解析的引文同步改，词数不变 |
| cl.T3.17 解析 | “而是回家打分”原文没有“回家” | 改为引原文“esperamos a estar solos frente a la pantalla”，再用分数惩罚或原谅对方 |
| cl.T4.20 解析 | “A 和 B 恰恰肯定所谈传统有几百年的历史”：B 没说米尔帕有几百年历史 | 改为：A 说冻干土豆“durante siglos”帮助高原社区储存食物，B 把米尔帕称为“el sistema tradicional”，都没有质疑其历史；D 讲广告形象的变化 |
| cl.T4.24 解析 | 引文“hace dos años”和原文“Hace dos años”大小写不一致 | 改为“Hace dos años” |
| cl.T5 第 5 段 | 哥伦比亚作者写“la pluma y al sello”：邮票在哥伦比亚通常叫 estampilla，sello 是半岛用法 | 改为“volvamos a la pluma y a la estampilla”；词数 412 → 413 |
| cl.T5.30 解析（编写者疑问） | 原解析只说 a menos que、siempre que“意思完全不通”，没有说明怎么排除 | 核对结论：语义排除明确（见下文“编写者的疑问”），干扰项保留；解析改为说明两者表示条件、放进句中成了“除非／只要路上的时间是对话的一部分，才请对方尽快回信”，并指出下文“esa espera … parecía alimentarla”印证 como si 的“仿佛”义 |
| cl.T5 译文第 1、4 段 | prima suya 译成“表妹”，原文没有长幼、父系母系之分 | 改为“表姐妹”（两处） |
| eie.T1 录音第 6 段 | 墨西哥讲话人用了半岛色彩的“los alquileres”“tuvieron que marcharse”；“El resultado arquitectónico es impecable, ganó varios premios”主语错位（“结果”得了奖） | 改为“las rentas de la zona se duplicaron”“tuvieron que irse”“El resultado arquitectónico es impecable: el proyecto ganó varios premios…”；中文同步；录音 694 → 696 词，句长仍在 4—25 词 |
| eie.T1 范文 | ① 要点 1 要求概括“ejemplos”，范文只说“como ocurrió en uno de sus ejemplos”，普埃布拉的成功案例完全没有交代，没听讲座的读者不知道是什么；② 评价说“缺少关于如何融资的建议”，但讲座明确说过项目离不开“apoyo público”，批评不够准确；③ 个人观点只有一句“Comparto su idea central”，论证偏薄 | 重写第 2—4 段：补上普埃布拉纺纱厂（一年居民咨询 → 图书馆和作坊）和附近改成豪华住宅的反例；评价改为“propuestas de financiación más concretas que un genérico «apoyo público», ya que la propia ponente admite que rehabilitar puede costar más que construir de cero”；观点加上理由“de lo contrario, la memoria se convierte en decorado”。逐句核对过，转述内容录音里都有。245 词（220—250）；译文、点评同步重写 |
| eie.T2 选项 1 图表标题 | “(porcentaje de jóvenes, último año)”：四个年份的折线图配“último año”，容易读成“只是去年的数据” | 改为“(porcentaje de jóvenes; datos referidos a los doce meses anteriores a cada encuesta)” |
| eie.T2 选项 1 范文译文 | “se ha multiplicado por once”译成“翻了十一倍”（“翻”在中文里会被理解成 2 的 11 次方或增加 11 倍） | 改为“增长到原来的十一倍” |
| eie.T2 选项 2 新闻（按要求） | 标题写在 cuerpo 第一段 | 移到 estimulo 的 "titulo"（排版程序加粗印在框顶），cuerpo 只剩两段正文，zh 去掉标题的译文（和 B2 的 sinopsis 写法一致）。正文 125 → 113 词；estimulo 本身没有 palabras 字段（数据格式里没有，B2 也没有），所以没有别的数字要改。教师用书的 par_text 给 titulo 那一行留空的中文格，标题译文因此改写进 instruccion_zh：“阅读一则地方报纸的新闻（标题：《瓦尔德奥利瓦大学将取消面向老年人的面授语言课程》）” |

## 逐部分核对结论

- **cl.T1**（墨西哥基金会翻译驻留项目章程，737 词）：答案 B C A C A B，按条款顺序出题，每题唯一；干扰项都有条款依据（两次付款、随行人员自费、个人生活资助不兼容、未经批准才可能失去第二笔钱、补交期不能换样章、开始后空位不递补）。行政语域地道（convoca、bases、dotación、acrediten、días hábiles、se tendrá por retirada、debidamente acreditada）；墨西哥用词 boleto、lenguas originarias、aval。除上面三处外已逐题核对，无问题。
- **cl.T2**（城市噪音传感器报道，593 词）：答案 C F A G D B，多余片段 E。逐个核对过唯一性：C 只能放 [7]（下一段 Allí ＝ junta de distrito）；F 只能放 [8]（Ese promedio 承接 media anual）；A 只能放 [9]（下一段 Los vecinos replican 要求前面有市政技术人员的质疑）；G 只能放 [10]（Su razonamiento 指 algunos investigadores，下一段 Esa idea 指“数量胜过精度”）；D 只能放 [11]（ellos ＝ once locales）；B 只能放 [12]（Aun así 让步于“设备不录音”）。六处都被唯一占满后，E 没有位置；而且 E 说多数人出于技术好奇、并非因为噪音问题，和“El caso de Amparo no es excepcional”以及结尾“Quienes lo escuchamos cada noche”相矛盾。解析引文全部和原文一致。除片段 F 一处外无问题。
- **cl.T3**（阿根廷评论专栏，600 词）：答案 B A C C A B，每题唯一，13、14、16、18 题需要读出隐含意思（互相考核、表面为顾客实为省钱、平均分反映的是怯懦、信任来自长期交往），依据都能在文中找到，干扰项各有明确反证。阿根廷用词一致（auto、plomero、cuadras、ponés、a la noche、almacén、alcanzaba con、enojo、4,8）。除上面三处外无问题。
- **cl.T4**（六篇报告摘要，121—140 词）：答案 A C E D B F A E（A、E 各两次，六篇都用到）。逐条核对过八个陈述都只对得上一篇：19 只有 A 是被研究者自己记录数据；20 只有 C 质疑“自古就有”；21 只有 E 以作者本人经历为起点；22 只有 D 拿广告和问卷对比；23 只有 B 提出减税；24 只有 F 评估已实施的举措；25 只有 A 是适应气候变化；26 只有 E 警告保护措施适得其反（B 正相反，是“没有措施”才会消失）。秘鲁（papa、altiplano）、墨西哥（alcaldías、impuesto predial、frijol）、哥伦比亚（plaza de mercado）、智利（choclo、costo）用词地道。除两处解析外无问题。
- **cl.T5**（哥伦比亚随笔完形填空，413 词）：答案 C A A B C B A C B A B A C B（A 5、B 5、C 4），14 空各只有一个选项成立：介词短语 a lo largo de；固定说法 de un tirón、a vuelta de correo、tomarse la molestia、leer entre líneas、caer en la cuenta、de su puño y letra；连接词 lejos de、Sin embargo、aunque（a pesar de 缺 que、puesto que 要接陈述式）、además；语法 como si + 虚拟式、cuando + 虚拟式现在时（将来指向）、me gustaría que + 虚拟式过去未完成时。darse el lujo、finca、guayabos、extrañar 是拉美用法，和作者背景一致。除上面三处外无问题。
- **eie.T1**（中介）：说明语交代了写作目的、文体（artículo de opinión）、读者（Contraluz 杂志没到场的读者），四条要点和真考写法一致，没有写“Número de palabras”。录音 696 词（650—750），只用 女2，没有缩写、符号、拟声词，每句 4—25 词，墨西哥用词（platicarles、colonia、departamentos、vidrios、rentas）。范文改后见上表。
- **eie.T2**：选项 1 的范文和图表一一对上：有声书 2 → 22（multiplicado por once）；电子 12 → 31，2022—2026 年 30 → 31（estancado）；纸质 61 → 54 → 47（2022 年最低）→ 49（repunta）；没读书的 31、33、30、26，26 是整个序列最低值。213 词，四个要点都完成。选项 2 的信 204 词，五个要点都完成（身份、反对并论证、评价在线平台并引用«llegará a más gente»、三条降成本建议、请求接见），语域正式；新闻改动见上表。评分项和权重与规格一致。

## 编写者的疑问：T5 第 30 题的 a menos que、siempre que

结论：语义排除是明确的，干扰项保留，只把解析写清楚。

句子是“Cada carta… terminaba pidiendo noticias a vuelta de correo, ___ el tiempo que tardaban en cruzar la frontera formara parte de la conversación.”三个选项都能接 formara，语法上不能区分，所以要看意思：

- a menos que 要求前面的动作有一个例外条件——“除非路上的时间是对话的一部分，否则都请对方尽快回信”，前文后文都没有任何“例外”的意思，说不通；
- siempre que 接虚拟式只能是“只要／前提是”——“只要路上的时间是对话的一部分，才请对方尽快回信”，同样说不通（这里没有习惯性“每当”的读法，那要接陈述式 formaba）；
- como si 是“仿佛”：开头为迟复道歉、结尾催回信，好像信在路上的时间也成了对话的一部分；下一句“esa espera, lejos de enfriar la relación, parecía alimentarla”正好印证。C1 考生按上下文可以确定。

我考虑过换成要求陈述式的连接词（如 ya que、tal como），让语法也能排除，但书面语里 -ra 形式可以当陈述式过去完成时用（“tal como anunciara el ministro”），反而会引出争议，所以不换。唯一的小缺点是两个干扰项同属条件连接词，应试经验强的考生可能用“挑不一样的那个”猜对；影响不大，没有改。

## 还拿不准、没有改的地方

1. eie.T2 选项 2 标题的中文：排版程序（par_text）在教师用书里给 titulo 留一个空的中文格，标题译文无处可放。我把它写进了 instruccion_zh；如果希望标题译文印在原文对照表里，需要改 build_pdf.py（不归我改）。
2. cl.T1 第 3、5、8 条用“memoria final / memoria de actividades”：墨西哥公文更常说“informe final”，但 memoria 在拉美也通用，而且第 2、6 题的选项特意用了 informe 来避免和原文同词，所以保留。
3. cl.T2 片段 D“Ninguno de ellos aparecía en el mapa oficial”：严格说噪音地图标的是街道的声级，不是具体场所；这里可以理解成呼应前文“los modelos ignoran fuentes como las terrazas”，保留未改。

## 统稿补改

- cl.json 译文：人名 Amparo 的译名前后不一（“阿帕罗”“安帕罗”），全部统一为“安帕罗”。
