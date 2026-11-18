# C1 听力与语言运用（ca.json）、口头表达、中介与互动（eio.json）、口语插图（art_audio.json）审校记录

审校方式：听力四个 tarea 先不看答案自己做一遍（T1 选出 A C F H I L，T2 B C A C A B C A，T3 B C A C B A，T4 B A C C A B A C B C），再对答案，全部一致；逐句查西语（拼写、重音、¿¡、性数、变位、搭配、RAE 正字法、各地区用词是否和人物一致）和录音规则（缩写、符号、数字写法、拟声词、单独成句的 Sí/No、每句 4—25 词，另写脚本逐句数过，最长 25 词），逐段对中文译文，另写脚本把每条解析里“”中的西语引文回原文逐字比对；口语逐段读两篇文章、考官材料、三组参考回答，核对参考回答里的每一处转述在文章或任务卡上有依据；插图说明逐张对任务卡方案和参考回答。C1 听力没有“谁说的”题型（quien），这一项不适用。改完 `check_content.py C1 ca eio art`：0 个错误、0 个提醒，PASS。

## 改动（共 38 处，表中每行一处；同一片段的西语和译文算一处）

### 听力 ca.json

| 位置 | 原来的问题 | 怎么改的 |
|---|---|---|
| ca.T1 instruccion_es | “Usted va a escuchar un fragmento de una conferencia. La escuchará dos veces.”：听的是 fragmento（阳性），代词应为 lo（旧版 C1 真考也是“Lo escuchará dos veces”） | 改为“Lo escuchará dos veces.”（录音照读，题册同步） |
| ca.T1 第 3 片段译文 | “se bebía bastante más alcohol del que se reconocía”译成“多得多”，bastante más 没那么重，后面水果蔬菜的 mucha más 才是“多得多” | 改为“多出不少” |
| ca.T1.L 解析 | 连引文 152 字，超过 150 | 精简为“并说把数据当成“撒谎”的证据“me parece injusto””，引文不变 |
| ca.T2 Conversación 1，达妮埃拉第一句 | “Disculpe que le llame en domingo”：le 指人＋llamar 是西班牙的 leísmo 说法，墨西哥房客会说 lo 或 hablar | 改为“Disculpe que lo moleste en domingo”（词数不变），译文改为“不好意思星期天打扰您” |
| ca.T2 Conversación 1，房东第一句 | 开头“Ay,”是感叹声，编写要求不用拟声、感叹声，语音识别也不稳（常识别成 hay/ahí） | 改为“No me diga, Daniela, ¿otra vez la humedad?”（墨西哥口语自然）；译文“哎呀”改为“不会吧”；整段 284 词 |
| ca.T2 Conversación 1，达妮埃拉第四句 | “Yo le dejo entrar”同样是西班牙 leísmo，le 指水管工（男） | 改为“Yo lo dejo entrar” |
| ca.T2 Conversación 2，马丁第二句译文 | “no le gusta nada que le pongan peros”译成“最不喜欢别人跟他讲条件”，poner peros 是“挑毛病、提反对意见” | 改为“最受不了别人跟他提反对意见” |
| ca.T2 Conversación 4，安德烈斯第二句 | “la finca está a cuatro horas de los dos”：咖啡产区离麦德林四五个小时，离波哥大要六七个小时以上，“离两人都是四小时”地理上不对，哥伦比亚老师会挑 | 改为“y la finca nos queda lejísimos a los dos”（哥伦比亚常用 quedar）；译文改为“庄园离我们俩都远得很”；整段 267 词 |
| ca.T2.13 解析 | 引文是上面已改的原句 | 引文改为“nos queda lejísimos a los dos” |
| ca.T2 Conversación 4，安德烈斯第三句 | “que esto se alargue años”少介词，不自然 | 改为“que esto se alargue por años” |
| ca.T2 Conversación 4，巴伦蒂娜第四句译文 | “Me parece justo, la verdad.”只译了“我觉得公平”，漏了 la verdad | 改为“说真的，我觉得这样很公平。” |
| ca.T3 主持人各句译文（第 0、2、4、6、10、12、14 片段） | 主持人对嘉宾一直用 usted，译文却用“你”，语域不对；第 0 片段对听众的 ustedes 译成“您” | 嘉宾一律改为“您”；对听众改为“各位如果……” |
| ca.T3 第 3 片段（巴莱里娅） | “Estudié interpretación”“Lo hice fatal”都是典型的西班牙说法，和人物的阿根廷用词（vos、lindo、enojarte）不一致 | 改为“Estudié actuación”“Me salió horrible”（词数不变；译文不变） |
| ca.T3 第 5 片段（巴莱里娅） | “no es el español de ningún sitio”：sitio 是西班牙用法，阿根廷人说 lugar/lado；译文“现在我不用想就能说出来”和 me sale sin pensar 意思有偏差 | 改为“de ningún lugar”；译文改为“现在不用想就能做到” |
| ca.T3 第 13 片段译文 | “Que haga teatro”译成“去演戏”，含糊 | 改为“多演话剧” |
| ca.T3 第 15 片段（巴莱里娅） | “El placer ha sido mío”：阿根廷人几乎不用现在完成时，她别处都用简单过去时（me enteré、me costó、algo hice mal） | 改为“El placer fue mío.”；访谈共 805 词 |
| ca.T3.16 解析 | 引文要随原文改；连引文 160 字 | 引文改为“no es el español de ningún lugar”，B 的说明精简，150 字以内 |
| ca.T3.18、19、20 解析 | 连引文 152、154、152 字，超过 150 | 删去重复的说明词（“自己”“还”“并”等），引文不变，均在 150 字以内 |
| ca.T4 Diálogo 10，阿帕罗 | “después de la sequía… perdisteis casi media cosecha”之后接“el precio del aceite ha bajado a la mitad”：减产一半油价反而腰斩，不合常理（西班牙读者都知道旱灾年橄榄油大涨价） | 改为“y ahora el banco nos ha subido los intereses del préstamo”（词数不变，整段 40 词），第二件坏事和下雨无关，A 仍是字面干扰；译文改为“现在银行又提高了我们贷款的利息” |
| ca.T4.30 解析 | 说明的是已改的“油价又跌了一半”；原长 134 字，改后需控制 | 改为“旱灾损失近一半收成之后，银行又“nos ha subido los intereses””，其余不变，149 字 |
| ca.T4.25 解析 | 引文“terminé de pintarlo…”原文句首是大写 Terminé，不是一字不差 | 改为“Terminé de pintarlo yo solo el domingo pasado” |

### 口语 eio.json

| 位置 | 原来的问题 | 怎么改的 |
|---|---|---|
| eio.T1 Opción 1 文章第 6 段 | “un deporte en equipo enseña…, la música desarrolla… y, para muchas familias…, son además una solución práctica”：前面两个单数主语，son 的主语（las actividades organizadas）断开，读起来卡 | 改为“…, esas actividades son además una solución práctica”；文章 816 词 |
| eio.T1 Opción 1 文章译文第 5 段 | “muchas madres y muchos padres trabajamos”是作者把自己算进去，译成“很多父母工作时间极长”丢了这层 | 改为“我们很多做父母的工作时间极长” |
| eio.T1 Opción 2 文章译文第 8 段 | “se estarán ahorrando lo más caro y lo más necesario”译成“它们就省下了最昂贵也最必要的东西”，意思不清（原意是“等于在最该花钱的地方省钱”） | 改为“那就等于把最昂贵也最必要的投入省掉了” |
| eio.T1 Opción 1 参考回答第 1 段 | “Lo escribe una psicóloga mexicana”：考生材料只有标题和正文，没有作者国籍（只在考官提示里有），考生无从得知，范文不该示范臆测 | 删去 mexicana（“una psicóloga que además es madre”，正文有依据）；译文同步 |
| eio.T1 Opción 1 参考回答第 3 段 | “por qué a los padres nos cuesta”：考生不是父母（下文说“Yo misma, de pequeña…”）；“la más sincera”和原文“la más incómoda”意思不同，作为中介转述不准 | 改为“les cuesta”“la más incómoda de reconocer”；译文“最坦白的一点”改为“最难以承认的一点” |
| eio.T1 Opción 1 参考回答第 5 段 | “conozco muchas familias”：conocer 指具体的人要加 a | 改为“conozco a muchas familias” |
| eio.T1 Opción 1 参考回答第 6 段 | 说文章“没有”谈不平等，但原文提到“para muchas familias que trabajan hasta tarde, son además una solución práctica”，评价不准确（C1 的中介要求准确） | 改为“echo de menos una reflexión más profunda sobre la desigualdad: la autora solo la toca de pasada, cuando habla de las familias que trabajan hasta tarde.”；译文同步。参考回答 528 词（约 4.5—5 分钟） |
| eio.T1 Opción 2 参考回答第 5 段 | “Llamarlos turistas de larga duración”：作者并没有把新居民都叫作长住游客，只说不参与社区生活的人“es un vecino o un turista de larga duración”，转述走样 | 改为“Decir que quien no se implica enseguida es un turista de larga duración me parece algo duro”，后面“融入需要时间”的反驳正好接上；译文同步。参考回答 482 词 |
| eio.T2 examinador.notas_zh | 参考回答只按文本 1 写，原提示只有一句“文本 2 的考生可参照同样的结构作答”，考官拿到选文本 2 的考生不知道怎么用、怎么对照 | 补充：参考回答的考官话取自前 10 题；选文本 2 时用后 10 题，同样按经历—观点—假设进行；评分时参照参考回答的展开方式（亲身经历、先让步再坚持、条件式和虚拟式过去时、回扣文章论点），文本 2 的论点见 T1 文本 2 的参考回答 |
| eio.T3 Opción 1 texto_zh | 情境有译文，四个方案没有（教师用书“方案 A—D”处印的是插图说明，不是方案内容，考官提示里只有一句概括） | 加一段四个方案的完整译文 |
| eio.T3 Opción 2 texto_zh | 同上 | 加一段四个项目的完整译文 |

### 插图 art_audio.json（C1 的图还没画，art/svg 里没有 C1 文件，不用返工）

| 位置 | 原来的问题 | 怎么改的 |
|---|---|---|
| art C1_EIO3_1A | 西语说明把大巴写进“En primer plano”，中文是“远处土路边”，两版矛盾；西语漏了雾、人数、竹篮、拍照的人、咖啡壶 | 西语按中文重写（大巴“Más lejos, junto a un camino de tierra”）；中文不变 |
| art C1_EIO3_1B | texto_en_imagen“Un árbol por cada año”：十周年＝只种十棵树，和六十人的植树日、参考回答里“diez árboles por cada año”都对不上；“海报上方留一行短标题”没说写什么 | 标语改为“Sembremos juntos”（哥伦比亚用 sembrar，和方案标题一致）；中文写明“海报上方印着一行标题“Sembremos juntos””；西语补推车、相机、帐篷上的树叶图案 |
| art C1_EIO3_1C | “一块白板上写着时间（只画数字即可）”：清单外的文字，而且没说写什么数字 | 改为“一只只有指针、没有数字的圆形挂钟”；西语补每组人数、同色围裙、挂钟、人不多 |
| art C1_EIO3_1D | 有 texto_en_imagen 但说明里没说放在哪里；“问号形状的提示卡片”上写不写字没说清 | 写明“海报上方印着一行标题“¿Resolverás el enigma?””、卡片空白；西语同步（密码锁、举手出主意的远程同事） |
| art C1_EIO3_2A | “一块写着编号的小牌子（只画数字）”：清单外的文字 | 删去；西语补白发、背书包、火车站顶棚（la marquesina de la estación，对上情境“Junto a la estación”） |
| art C1_EIO3_2B、2C、2D | 西语说明比中文少关键细节：2B 没有年轻父亲；2C 写“otros escalan”（中文是一个女孩）、没有阳台上的老人（参考回答和考官问题用到的噪音线索）；2D 没有标题和音箱 | 三条西语按中文补齐；2D 中文写明“海报上方印着一行标题“Cine de verano”” |

## 已逐题核对、无问题的部分

- ca.T1：12 个陈述逐条回录音找依据。A（“La idea, desde luego, no es mía… Yo me formé en esa escuela”）、C（“no sabían en qué semanas íbamos a pasar por su casa”）、F（“aseguraban comer mucha más de la que en realidad compraban”）、H（“compraban grandes cantidades por miedo a nuevas subidas… una parte acababa en la basura”）、I（“En las capas profundas… la descomposición es lentísima”＋三十年前的报纸旁“restos de comida casi intactos”）、L（“A mí no me interesa señalar a nadie…”）六个正确项依据明确；B、D、E、G、J、K 六个干扰项都和原文相反（不是“没提到”），各有一句原文可以直接排除。录音 718 词，女2 一个声音，每句 ≤24 词，没有数字、符号。
- ca.T2：四段对话答案唯一；每题干扰项都借用了对话里的词或另一人说的话（如第 9 题 b 是马丁说的预算争吵），按对话确定是错的；第 7、8 题都在 Conversación 1 里按顺序出现，其余同。声音：女3/男2、女1/男2、女2/女4、女4/男2，人物和声音一一对应。各段 253—284 词。
- ca.T3：六题答案唯一，按访谈顺序出题；嘉宾的 voseo（Tenés、grabás、estás）照编写者意见保留，用法正确，和她说的“在家里还是一口布宜诺斯艾利斯腔”也呼应。
- ca.T4：十段习语题逐段核对，每段只有一个选项说得通，另两个分别是字面理解（brazo、agosto、llover、consultar）或和对话事实相反；习语都是西班牙常用的，释义和解析正确。各段 39—45 词。
- 三选一 24 题中正确项是最长选项的 4 题（第 8、11、12、13 题，17%）；T2—T4 答案分布无规律。
- 全部录音：没有缩写、% 和货币符号、阿拉伯数字（钟点、价钱、年份都写成词），没有单独的 Sí/No，没有省略号和舞台说明（“Ay”已改）；少于 4 词的短句（“Otra cosa es el público.”这类）按说明由合成程序并句，不改。
- eio.T1：两篇文章 816、788 词（规格 750—850）；文本 1 的墨西哥用词（junta de padres de familia、celular、hacer fila、hacer la tarea、tableta）、文本 2 的西班牙用词前后一致；两篇译文其余段落准确。说明语、考官开场话和三个备用问题可以直接照用。
- eio.T2：两组各 10 个考官问题，分经历、观点、假设三部分，观点题都带反驳角度（“¿No le parece…?”），假设题能引出条件式和虚拟式过去时；参考回答 595 词（4—6 分钟），语言无错误，有让步、反驳、举例，是 C1 的好答卷。
- eio.T3：两张任务卡的情境、四个方案和考官问题、考官提示里的方案概括互相一致（预算、十五个远程同事、两场烹饪、四十户菜地、调查最受欢迎、夜间噪音、音响贵）；两段参考回答（534、502 词）每一处论据都能在卡片上找到，最后都明确达成一致。考官提示“考生选了哪个就先支持另一个”和问题清单第 2、9 题对得上。中文 texto_zh 情境译文准确。
- art_audio.json 8 张图：每张都画得出来，和对应方案一一对上（1A 大巴＝路远，1B 灰云＝看天气、挖坑＝要体力，1C 人少＝容量有限，1D 屏幕上的远程同事＝办公室，2A 志愿者老人，2B 已有的常规乐园，2C 阳台老人＝噪音，2D 音箱＝设备贵），同一张卡的四张图内容完全不同，一眼能分清。

## 拿不准、没改的地方

1. ca.T3 嘉宾的 voseo（Tenés、grabás）用西班牙口音的声音合成：按编写者意见保留，合成后请在语音识别核对时留意这两个词是否被识别成 tienes、grabas。
2. ca.T3 第 0 片段主持人说“Si ustedes han visto dibujos animados en la última década, es muy probable que la hayan escuchado”：前提是听众看的是拉美配音的动画片；主持人说半岛西语，节目在哪个国家没交代。若设定是西班牙电台，这句就不成立（西班牙观众看的是西班牙配音）。没改，请编写者确认节目设定。
3. ca.T1 第 1 片段“A finales del siglo pasado, varios arqueólogos empezaron a aplicar a los vertederos modernos…”：现实中的“垃圾考古”始于二十世纪七十年代，说“上世纪末”略显不准，但讲座没有点名真实项目，不影响答题，没改。
4. eio.T3 的方案形式：规格写“4 个方案（海报、广告、照片、标语）”，本卷两张卡是四个活动／项目方案，各配一张照片、海报或效果图，插图里有三条短标语。我理解这符合 2024 版“以图文形式给出四个方案”的要求，但官方 Modelo 0 的具体呈现方式请总编再对一下。
5. eio.T1 考官开场话“Puede consultar sus notas, pero no leerlas.”和说明语“no podrá leer el texto, pero sí consultar sus notas”意思一致（可以看笔记，不能照念），沿用，没改。

## 统稿补改

| 位置 | 原来的问题 | 怎么改的 |
|---|---|---|
| ca.T1 第 2 段 | “A finales del siglo pasado”：用考古方法研究现代垃圾填埋场始于 20 世纪 70 年代，“上世纪末”不准 | 改为“En los años setenta del siglo pasado”，后半句“los mismos métodos que se usan en una excavación antigua”压成“los métodos de una excavación antigua”（全句 22 词）；译文和第 1 题相关解析的“上世纪末”同步改为“上世纪七十年代” |
| ca.T3 第 1 段 | 主持人“Si ustedes han visto dibujos animados en la última década…”默认听众看的是拉美配音，节目所在地没交代 | 改为“dibujos animados con doblaje latinoamericano”（22 词），不论节目设在哪里都成立；译文同步 |

## 统稿复核（口语 T3 卡片 1 插图）

- 四幅插图（1A 咖啡庄园、1B 植树海报、1C 烹饪比赛、1D 办公室寻宝海报）逐项对照画面说明核对：人物、动作、物品、海报标题都对得上，图中除两张海报的标题外没有文字，没有品牌标志。
- 1C：画面说明原写“画面里人数不多”，成图是三张操作台全部站满（12 名厨师＋3 位评委）。成图更能表现“每场只容 30 人、要分两场”，所以改说明不改图：es 改为“Todos los puestos de las mesas están ocupados; no queda sitio para nadie más.”，zh 改为“每个操作台都站满了人，没有空位，暗示场地容量有限。”

## 统稿复核（口语 T3 卡片 2 插图）

- 2A 社区菜园、2C 傍晚运动场、2D 露天广场海报逐项对照画面说明核对通过；2D 除标题“Cine de verano”外没有文字，三张都没有品牌标志。
- 2A：成图远处画的是铁路和一列开过的火车，看不出“车站顶棚”。改说明不改图：es 改为“…y, a la derecha, más lejos, las vías del tren con un tren de cercanías que pasa.”，zh 改为“右边远处是铁路线，一列市郊火车正开过。”（卡片里“solar junto a la estación”仍然成立。）
- 2B 公园效果图退回重画：秋千吊绳歪斜、像挂在滑梯塔上；滑梯末端顶到长椅和灯杆；长椅画成了单人椅；一根灯杆没有灯头。
- 2B 重画后复核通过：标准秋千（两端 A 字架、横梁、平行吊绳），滑梯背面有梯子、末端落在软垫上，两张三人长椅，删掉了没有灯头的灯杆。

## 统稿补改（录音复核）

成品逐句复核时，下面几句每种切法、每一遍都没认对（合成时吞音或念走样），改了说法后重新合成。这几处都不是考点，题目、选项、答案和解析都不变。

| 位置 | 原句 | 识别结果 | 改为 |
|---|---|---|---|
| ca.T1 第 5 段 | “Muchas se quedaban sorprendidas, y algunas…” | “quedabendidas”（吞掉一个音节） | “Muchas familias no se lo podían creer, y algunas…”；译文改为“很多家庭简直不敢相信” |
| ca.T2 对话 2（Valentina） | “Es muy juicioso, conoce la casa…” | “Es muy juicio” | “Es muy responsable, conoce la casa…”；译文“他很靠得住”不变；本段说明里列举的哥伦比亚说法把 juicioso 换成对话里有的 de chiquitos |
| ca.T4 对话 7（Laura） | “Qué va, dice que eso es para viejos…” | “Keba”（女声念不清；对话 1 男声的“Qué va”认对了） | “Para nada, dice que eso es para viejos…”；译文改为“根本没有，他说…”。本段考点 no dar su brazo a torcer 不变 |
| ca.T1 第 4 段 | “En cierto modo, la basura también es un archivo.” | 第一次复核换切法对上，重合成后五遍都认成“En cierto, …”（吞掉 modo） | “Podríamos decir que la basura también es un archivo.”；译文改为“可以说，垃圾也是一种档案。” |
