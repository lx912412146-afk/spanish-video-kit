# A2 阅读（cl.json）、写作（eie.json）、插图清单（art_lectura.json）审校记录

审校方式：先不看答案把 25 题做了一遍，再对答案、解析、译文；逐句核对西语（拼写、重音、¿¡、性数、变位、搭配、RAE 正字法）、词数、答案分布、正确项长度（最长项 4/20＝20%）。

## 修改

| 位置 | 原来的问题 | 怎么改的 |
|---|---|---|
| cl.T1.3 选项 C | 正确项 A（47 字符）比 B、C（29、32）长很多，长度上容易露出答案 | C 改为 “organiza viajes para grupos por las mañanas.”（借原文词、仍明确错），解析里的“组织旅行”改为“组织团体旅行” |
| cl.T1.3 解析 | 编写者问推断是否太绕。判断：推断只有一步，A2 能做到，B、C 都被原文直接否定，没有第二个可辩护的选项，题不改 | 解析补上依据：“es”是现在时，现在仍是最难的事，“poco a poco lo hago mejor”只是在进步，所以还需要提高 |
| cl.T2.7 选项 A | “no hay que pagar aparte por internet” 里的 “pagar por internet” 一般理解为“网上付款”，有歧义 | 改为 “no hay que pagar internet aparte.” |
| cl.T2.9 选项 C | “con los 25 euros no pagan la comida” 不自然（意思是 25 欧元不含午饭，说法别扭） | 改为 “tienen que pagar la comida aparte.”；解析补一句“午饭要另外付钱” |
| cl.T2.10 解析 | 编写者问“楼里另有吃饭的地方”是否推断过度。判断：这是公司发给全体员工的内部通知，“la cafetería del segundo piso”就是指公司这栋楼的二楼，A2 能理解；A（微波炉照常用）、C（食堂关了）都被原文直接否定，答案唯一，题不改 | 解析补上：“del segundo piso”指公司这栋楼的二楼 |
| cl.T4 译文第 6 段 | “viajar despacio también es viajar”译成“慢慢地走也是旅行”，意思偏了 | 改为“慢慢地旅行也是旅行” |
| eie.T2 Opción 2 范文译文 | “比赛的钱是给她们街区图书馆的”，“她们”错（su barrio＝她的街区） | 改为“给她所在街区的图书馆的” |
| art_lectura A2_EIE2_2（es、zh） | 男子和女孩“都在鼓掌”，同时女孩又“举着标语”，画不出来；中文“她身后还有……选手跑来”紧接女孩那句，“她”指代不清 | 改为男子鼓掌、身旁的女孩双手举标语；中文“她身后”改为“女子身后” |

## 已逐题核对、没有改的部分

- cl.T1（邮件，274 词）：文本西语无误；第 1、2、4、5 题答案唯一，解析引文和原文一字不差，译文准确。
- cl.T2（9 篇短文，67—74 词）：第 0、6、8、11、12、13 题已逐题核对，无问题；答案分布 C A B C B A C B，无规律。
- cl.T3（3 篇，101—105 词，每篇对应 2 题，答案 B C A B A C）：已逐题核对，无问题；每题另外两篇都确实不符合。
- cl.T4（博客，400 词）：第 20—25 题已逐题核对，无问题（第 22 题 cuarto＝habitación，第 25 题“con más gente”指加上 Maite 和她的孙女）。
- eie.T1：刺激文本 43 词；说明语和要点写法同真考，没写 “Número de palabras”；范文 68 词，五个要点都写到，西语无误；点评正确。
- eie.T2 Opción 1：范文 77 词、Opción 2：范文 78 词，要点齐全、时态用法正确，和资料、图片对得上（46 岁、护士、9:30、800 人、38 分钟、举标语的女儿）。评分项说明正确。
- 文本总词数 1620（规格 1325—1725）；check_content.py A2 cl eie：0 错误 0 提醒，PASS。

## 拿不准、没有改的

- cl.T3 说明语最后一句 “Cada texto corresponde a dos preguntas.”：我记得真考 A2 Tarea 3 的说明语里好像没有这句，但官网打不开，没法核对。这句不算错，只是会让题目变简单一点；没删，请主编决定。
- 译文里 “cuarto piso”“segundo piso” 照字面译成“四楼”“二楼”（西班牙的楼层从 planta baja 往上数，按中国的叫法要多一层）。不影响答题，没改。
- cl.T3 说明语：删去“Cada texto corresponde a dos preguntas.”（官方 Modelo 的说明语没有这一句，主编核对后删除；中文说明同步删去）。

## 统稿：阅读 T4 结尾改写

- cl.T4 第 6 段第 2 句：“Por ejemplo, que viajar despacio también es viajar, que no hace falta ser joven para vivir aventuras y que mi abuela tiene más energía que yo.”和 B1 阅读 T4（慢旅行）撞题 → 改为 “Por ejemplo, que no hace falta ser joven para vivir aventuras, que mi abuela hace amigos en cualquier sitio y que tiene más energía que yo.”（新加的一条是从奶奶在火车上认识 Maite 得出的，句子仍是 26 词，全文仍是 400 词）。
- cl.T4 译文第 6 段：同步改为“比如，不年轻也照样可以去冒险；奶奶走到哪儿都能交上朋友；还有，她比我还有精力。”
- cl.T4 第 20—25 题：重新核对，这句话不是任何一题的依据，答案和解析不用改（第 23 题依据的是第 4 段 “paseábamos despacio”，没动）；解析引文已用程序核对，和原文一字不差。阅读总词数仍是 1620（1325—1725）；`/usr/bin/python3 tools/check_content.py A2 cl`：0 个错误、0 个提醒，PASS。
