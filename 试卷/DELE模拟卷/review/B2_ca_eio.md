# B2 听力（ca.json）、口语（eio.json）、听力口语插图（art_audio.json）审校记录

审校方式：听力每题先不看答案自己做一遍，再对答案；逐句查西语（拼写、重音、¿¡、性数、变位、搭配、RAE 正字法）和录音规则（缩写、符号、拟声词、单独成句的 Sí/No、每句 4—25 词，另写脚本逐句数过），逐段对中文译文，逐条核对解析里引用的原句是否和原文一字不差；口语核对说明语、考官材料、参考回答和照片说明、调查数据是否互相一致。改完 `check_content.py B2 ca eio`：0 个错误、0 个提醒，PASS。

## 改动（共 24 处，表中每行一处；同一片段的西语和译文算一处）

| 位置 | 原来的问题 | 怎么改的 |
|---|---|---|
| ca.T1 Conversación 4，罗莎第一句 | 反话只靠语调：“Ya lo he visto, y ha quedado precioso, de verdad.”合成语音没有夸张语调，“de verdad”反而加强了字面意思，听者完全可以认为她真心觉得漂亮、只是嫌没地方坐，第 4 题 a（ha mejorado mucho el aspecto del barrio）就有了依据，答案不唯一。另外 T2 里露西娅真心说的也是“el edificio ha quedado precioso”，同一句话一处真一处反，容易混 | 改为“Ya lo he visto. Muy bonito, justo lo que nos faltaba. Ahora los mayores, que iban allí a sentarse, pueden admirar las flores de pie.”：用固定的反语说法 lo que nos faltaba，再把“原来来坐的老人现在站着赏花”的荒唐对比说明白，靠用词就能听出反讽；“Muy bonito”的字面意思仍是 a 的干扰点。译文改为“看到了。真“漂亮”啊，这下可好了。以前去那儿坐坐的老人们，现在可以站着赏花了。” |
| ca.T1 Conversación 4，卡门第二句 | 上一处改动后整段超过 60 词 | “Dicen que así nadie se quedará de noche haciendo ruido.”改为“Dicen que así nadie hará ruido por la noche.”（意思不变，第 4 题 b 的依据仍在）；整段 60 词；译文同步改 |
| ca.T1.4 解析 | 引的“ha quedado precioso”原文已改 | 改为说明“justo lo que nos faltaba”是表示不满的固定说法、“pueden admirar las flores de pie”是讽刺，a 只取了“Muy bonito”的字面意思 |
| ca.T1 Conversación 5 译文 | “no debería llevar más de cuarenta minutos”译成“应该用不了四十分钟”，意思偏了（原文是“不超过四十分钟”） | 改为“应该不会超过四十分钟” |
| ca.T1 Conversación 6，达尼埃尔最后一句 | “Precisamente por eso, que todo el mundo lo acepte no significa que esté bien.”逻辑上接不上（“正因为所有应用都这样，所以……”），口语也不顺 | 改为“Ese es el problema. Que todo el mundo lo acepte no significa que esté bien.”（整段 58 词）；译文改为“问题就在这儿。大家都接受，并不代表这就是对的。” |
| ca.T1.6 解析 | 引文要和原文一字不差 | 引文改为“Que todo el mundo lo acepte no significa que esté bien” |
| ca.T3 第 5 片段（拉米罗） | 阿根廷说话人用 acá、lugar、arrancar，同一段里又用西班牙说法 estanterías | “colgar unas estanterías”改为“colgar unos estantes”（阿根廷常用，西班牙也通用；词数不变） |
| ca.T3 第 15 片段（拉米罗） | “el portal de mi edificio”是典型的西班牙说法，和人物的阿根廷用词不一致 | 改为“la entrada de mi edificio”；译文“门厅里”改为“入口处”。（trasteros、ayuntamiento 是他在瓦伦西亚生活八年、说当地的事物，保留） |
| ca.T4 第 20 题录音译文 | “hago mis cuarenta largos”译成“游四十个来回”，largo 是单程，来回就成了八十个 | 改为“现在我每次都游四十趟” |
| eio.T1 Opción 1 texto_zh | 考生材料译文只有情境段，六条建议没有译文（只在考官提示里有概括） | 加一段六条建议的完整译文 ①—⑥ |
| eio.T1 Opción 2 texto_zh | 同上 | 加一段六条建议的完整译文 ①—⑥ |
| eio.T1 examinador.notas_zh | 六条建议的译文和考生材料译文重复；“独白约 370 词和 330 词”与实际（364、320）不符 | 删去重复的建议列表，改为“译文见下面各卡的考生材料译文”；词数改为约 360、320 |
| eio.T1 Opción 1 参考回答第 5 段 | “Si los descuentos los paga el ayuntamiento, puede salir muy caro, y si los pagaran los comerciantes, ganarían…”同一句里真实条件句和非真实条件句混用，作范文不好 | 统一为“Si los descuentos los pagara el ayuntamiento, saldría muy caro, y si los pagaran los comerciantes, ganarían…” |
| eio.T2 Opción 1 texto_zh | 卡上 6 个提示问题没有译文 | 加一段提示问题的译文 |
| eio.T2 Opción 1 参考回答第 2 段 | 照片说明写“一袋食物”，画不出来；参考回答说“seguramente con comida” | 插图改为“袋口露出锡纸包着的 bocadillo”，参考回答改为“Lleva en la mano una bolsa de papel con un bocadillo, seguro que para el viaje…”；译文同步 |
| eio.T2 Opción 2 texto_zh | 卡上 6 个提示问题没有译文 | 加一段提示问题的译文 |
| eio.T2 Opción 2 参考回答第 4 段 | 照片说明里“谁拿话筒”没写清（“habla ante un micrófono”），参考回答推测老太太是协会会长，但图上没有任何线索 | 插图改为：老太太穿着和志愿者一样的背心，对着三脚架上的摄像机讲话，旁边没穿背心的年轻女人把话筒递给她；参考回答改为“una mujer joven ha puesto una cámara sobre un trípode y le acerca un micrófono a una señora mayor, que lleva el mismo chaleco que los voluntarios”，推测“记者”“会长”就有了依据；译文同步 |
| eio.T3 Opción 1 encuesta | 问卷 5 个问题都和调查结果（“不常做饭的主要原因”）无关，说明语要求的“compare sus respuestas con los resultados”做不到 | 加第 6 题“Si no cocina más a menudo, ¿cuál es el principal motivo? (…)”，选项和结果的 5 类一一对应 |
| eio.T3 Opción 1 参考回答 | 配合第 6 题 | 考生回答问卷时加“En cuanto al motivo por el que no cocino más, es sobre todo el cansancio.”；后面的问答改为“E: ¿Es su caso?”“C: Sí, por eso he marcado el cansancio y no la falta de tiempo. …”；译文同步。引用的数字（38、22，合计过半，17、14、9）与 resultados 一致 |
| eio.T3 Opción 1 texto_zh | 问卷没有译文 | 加问卷 6 题及选项的译文，注明结果是第 6 题的答案分布 |
| eio.T3 Opción 2 encuesta | 同 Opción 1：结果“不多读书的主要原因”不在问卷里 | 加第 6 题“Si no lee más, ¿cuál es el principal motivo? (…)”，选项和结果的 5 类对应 |
| eio.T3 Opción 2 参考回答 | 配合第 6 题 | 回答问卷时加“Si no leo más, es porque me cuesta concentrarme en textos largos.”；后面改为“Sí, con el de la concentración, que es justo lo que he marcado yo.”；译文同步。引用的数字（41、27、5）与 resultados 一致 |
| eio.T3 Opción 2 texto_zh | 问卷没有译文 | 加问卷 6 题及选项的译文 |
| eio.T3 examinador.notas_zh | 配合第 6 题 | 加一句“问卷第 6 题就是调查结果对应的问题，考官引导考生先拿自己第 6 题的选择和结果比较” |

插图清单 art_audio.json 的两处改动（下面两行）与上表 eio.T2 的两行是同一件事的两半，单独列出便于插图组核对：

| 位置 | 原来的问题 | 怎么改的 |
|---|---|---|
| art B2_EIO2_1 | “一袋食物”画不出来；远处女孩“看表又挥手”两个动作没分清手；“眼眶湿润”画不出 | 改为袋口露出锡纸包着的长面包三明治；女孩一边看手表、一边用另一只手招呼男孩快点；母亲“眼含泪水，手里攥着纸巾”；加窗外晨光；其余不变（西语、中文两版同步） |
| art B2_EIO2_2 | “八个志愿者”是否包括前景的女孩和男人、远处两个女人穿不穿背心、话筒谁拿，都没写清，画出来人数和参考回答对不上 | 写明八个志愿者包括前景的女孩和男人，都穿同样的绿色背心；远处老太太也穿绿背心，对着三脚架上的摄像机讲话，没穿背心的年轻女人把话筒递给她（西语、中文两版同步）。B2 的插图还没画（art/svg 里没有 B2 文件），不用返工 |

（合计：上表 24 处＋插图 2 处＝26 处。）

## 逐部分核对结论

- **ca.T1**（6 段对话，54—60 词）：答案 B C A C A B；改后每题唯一。第 4 题的反讽现在靠 lo que nos faltaba 和“站着赏花”的对比就能听出，不依赖语调。第 6 段巴莱里娅（墨西哥）用 celular、bajar、¿ya bajaste?，自然、一致。声音：每段两人不同声，男女搭配合理。
- **ca.T2**（对话 266 词）：答案 A C B C B A；两道 C 的依据都是“两人说的正相反”（第 8 题铁架结构重新露出来、两人都认可修复；第 10 题两人都承认不再适合日常买菜），明确。已逐题核对，无问题。
- **ca.T3**（访谈 448 词）：答案 B C A B A C；每题干扰项都有原文依据（事后才知道别处有类似项目、场地由市政府提供、只接受会员需要的东西、只丢过两件、别人以为重要的是省钱、他没有建议先找市政支持）。除上面两处用词外无问题。
- **ca.T4**（7 段 58—64 词）：答案 B（例）/ C F E I G A。不用的三项逐段核对过：D（比预想的难）——只有华金提到预想，而且是相反的（比想的容易）；格洛丽亚只说看视频看不懂，没有和预期比较。H（后悔没早点开始）——安帕罗明确不同意别人“可惜没早学”的说法，其余人都没有惋惜。J（全靠自己）——每个人都有课程、老师、孙子或师傅。除第 20 题译文外无问题。
- **ca.T5**（讲座 432 词）：答案 C A B A C B；已逐题核对，无问题。
- 听力录音总词数 1921（规格 1590—1980）；所有句子 4—25 词，没有缩写、符号、拟声词、单独成句的 Sí/No；数字都写成词。
- **eio.T1**：两张卡的参考独白分别评价了 6 条建议（多于至少 4 条），有利弊、受益者、修改建议；独白 364、320 词，讨论 270、201 词，符合 3—4 分钟＋2—3 分钟。考官问题前缀“Opción 1:”“Opción 2:”保留。
- **eio.T2**：两张照片的说明、卡上的提示问题、考官问题、参考回答里提到的细节逐项对过（男孩的背包、箱子、护照登机牌，母亲拥抱，父亲搭肩和纸袋，妹妹拍照，远处催促的女孩；河岸、桥、垃圾袋、轮胎、推车、女孩和瓶子、蹲着拿文件夹的男人、远处的两个女人），改后一致。描述 330、320 词。
- **eio.T3**：两份调查都注明“Datos ficticios”，结果各项合计 100；参考回答引用的数字全部与 resultados 一致。

## 拿不准、没有改的

1. ca.T1 Conversación 5：老师说“En clase, cuando tiene el móvil cerca, le cuesta mucho concentrarse”。现在西班牙很多地区中小学课堂禁止带手机，这句话的情境略牵强；但题目本身成立（暗示孩子在家学习时分心），而要换成别的说法又会超过 60 词或让 c 项失去依据，所以没改，请主编定。
2. ca.T3 拉米罗仍用 trasteros、armario、recogen 这些西班牙通行说法；我按“他在瓦伦西亚住了八年、说的是当地的事”保留，只改了 portal 和 estanterías。如果希望他的阿根廷特色更浓，可以再改。
3. eio.T3 两份问卷各加了第 6 题（共 6 题）。数据格式和规格都没有规定题数；如果排版要求固定 5 题，可以删掉第 5 题来换。
4. eio.T2 Opción 1 参考回答里考生说“cuando vine a estudiar a España”，默认考生在西班牙留学；作为参考回答问题不大，国内使用时老师可以提醒学生按自己的情况说。
5. 两张照片说明的中文都在 190 字左右，超过数据格式建议的 80—150 字；为了画得出来、和参考回答对得上，没有压缩。

## 统稿补改（录音合成）

- 听力 T4 说明语“…que cuentan algo que aprendieron de adultas”：旁白合成 9 个种子都把“de”吞掉（识别成“aprendieron adultas”），改成“…que cuentan algo que aprendieron cuando ya eran adultas.”（题册里印的说明同步改，中文说明不变）。
- 听力 T4 Persona 1（托马斯）“Hace dos años decidieron que en cada oficina…”：9 个种子都把“que”吞掉，改成“Hace dos años se aprobó una norma: en cada oficina tenía que haber alguien que supiera lengua de signos.”，译文改为“两年前出台了一项规定：每个办事处都要有一个会手语的人。”。解析引用的“en cada oficina tenía que haber alguien que supiera lengua de signos”一字未变，答案不受影响。
