# A1 阅读（cl.json）、写作（eie.json）、阅读写作插图（art_lectura.json）审校记录

审校方式：每题先不看答案自己做一遍，再对答案；逐句查西语（拼写、重音、¿¡、性数、变位、搭配、RAE 正字法）、逐段对中文译文、逐条核对解析里引用的原句是否和原文一字不差、核对规格里的数字。改完 `check_content.py A1 cl eie`：0 个错误、0 个提醒，PASS。

## 改动（共 13 处，表中每行一处）

| 位置 | 原来的问题 | 怎么改的 |
|---|---|---|
| cl.T1 文本第 4 段 | “Todos los días me levanto a las siete y media y voy a la universidad”和后面“Los domingos descanso: duermo mucho”、星期六上午打工自相矛盾 | 改成“De lunes a viernes me levanto…”；中文改为“星期一到星期五，我七点半起床……” |
| cl.T1 文本第 4 段、第 3 题解析 | “como en casa con mis compañeras”：A1 学生常把 compañeras 理解成同学，第 3 题正确项“come con Irene y Paula”的依据不够直接 | 改成“con mis compañeras de piso”；第 3 题解析的引文同步改，并说明 compañeras de piso 就是 Irene 和 Paula |
| cl.T1 palabras | 上面两处改动后正文 172 词 | 169 → 172（仍在 150—175 之内） |
| cl.T2 文本 F 译文 | “Mañana no puedo ir a clase”译成“明天我去不了学校”，不准确 | 改为“明天我不能去上课” |
| cl.T2.11 解析 | 把便条 C 说成“超市 C” | 改为“便条 C（让儿子去超市买面包和牛奶）” |
| cl.T3 广告 B（编写者疑问 1） | 第 15、17 题都没有同类干扰广告；第 15 题“gafas”一个词就能配上 C，题干里“Solo tengo tiempo libre los domingos”这个条件没有起作用 | 把没用的花店广告 B 换成第二家眼镜店“Óptica Plaza”：“Gafas para ver bien en clase o en el trabajo. Sus gafas, listas en una hora. Abierto de lunes a sábado, de 9:30 a 20:30. Domingos, cerrado.”（27 词）。干扰项借用了题干的词（ver bien、clase），正确项 C 用的是另一套说法（Revisión de la vista、los domingos, de 10:00 a 14:00），要看“星期天开不开门”才能选对。核对过：新 B 配不上其他任何一个人，答案仍唯一；中文译文、词数同步写好 |
| cl.T3.15 解析 | 原来拿比萨店 I、自行车店 J 当干扰项，没有说服力 | 改为说明眼镜店 B 也配眼镜、也说“para ver bien en clase”，但“Domingos, cerrado” |
| cl.T3.0、cl.T3.12 解析 | 两题解析原来都拿花店 B 当干扰项，B 换掉后不对了 | 第 0 题改为书店 G（星期六儿童活动）、比萨店 I（儿童套餐）都不卖蛋糕；第 12 题改为素食餐厅 E 虽有 verduras，但它是餐厅、不卖水果蔬菜 |
| cl.T3 tema_zh | 列表里还写着“花店” | 改为“两家眼镜店……素食餐厅……” |
| art_lectura A1_CL2_J | 图标画“电梯门＋红叉”，等于把第 10 题的答案（电梯坏了、只能走楼梯）直接画出来；A1_CL2_E 已经特意不画泳帽，标准不一致 | 改为“一栋住宅楼，楼门上贴着一张告示”，注明不画电梯、不画红叉（和博物馆 D 的建筑图标也形成干扰，不会一眼配上） |
| art_lectura A1_CL2_I | “儿童鞋＋价签”同时提示了第 11 题的“para sus hijos”和“más barato” | 改为“一只普通的运动鞋”，注明不画价签、不画成童鞋 |
| eie.T1 instruccion_es / instruccion_zh | 说明语最后一句“Complete el formulario.”在广告前，排版程序又在广告后印“Complete el formulario en la Hoja de respuestas.”，同一句话印两遍 | 改为“Usted vive en Valencia y quiere apuntarse a una actividad del polideportivo de su barrio. Para inscribirse, tiene que completar un formulario.”“Lea primero el anuncio del polideportivo.”，程序在广告后补“Complete el formulario en la Hoja de respuestas.”，顺序是：情境 → 读广告 → 填表。中文同步改 |
| eie.T1 广告译文 | “Para inscribirse, complete el formulario”译成“填写下面的表格”，原文没有“下面的”（表格其实在答题纸上） | 改为“报名请填写报名表，交到前台。” |

（表中“cl.T3 广告 B”一行包含广告正文、标题、译文、词数四个字段的改动。）

## 逐部分核对结论

- **cl.T1**（邮件，172 词）：6 题（含例）按文本顺序出题，答案 B / B C A C B，每题唯一；第 5 题三张图（雨伞、泳衣、自行车）都是邮件里提到的东西，正确项是 bañador。其余部分已逐题核对，无问题。
- **cl.T2**（10 个短文本，23—30 词）：答案 B（例）/ E G C F J I，不用的 A、D、H 核对过配不上任何一句；所有引文和原文一致。除上面两处外无问题。
- **cl.T3**（10 则广告 24—30 词，陈述 16—20 词）：答案 D（例）/ F A I C G J，不用的 B、E、H 各自是某一题的同类干扰项（B → 15，E → 14，H → 13、16）。除上面的改动外无问题。
- **cl.T4**（学校活动海报，200 词）：8 题答案 A C C B A B C A，每题唯一，干扰项都有原文依据（价钱、楼层、钟点、出发地点、报名日期、不要打电话）。已逐题核对，无问题。
- **eie.T1**（填表）：三个简答栏范文 7、8、7 词，共 22 词，在 15—25 之内，西语无误（hacer natación、me gusta + 原形、jugar al bádminton）。个人信息栏写法对（china 小写、4.º B、日/月/年）。
- **eie.T2**（邮件）：说明语、五条要点（不定式）和真考写法一致；范文 37 词（含署名），五个要点都完成，tú 一致，只用现在时和 tener que，水平合适；点评说得对。评分说明和规格一致（少于 20 词不评分，20—29 词最高 1 分）。
- **art_lectura**：第 5 题三张图一眼能区分；T2 的 10 个图标只表示文本类型（书、手机、冰箱便条、博物馆、泳池、药店十字、黑板、鞋、住宅楼），两个手机图标靠练习本区分。

## 编写者的三个疑问

1. **T3 第 15、17 题没有同类干扰广告**：确实太容易，第 15 题只靠“gafas”一个词就能配上。已按上表把 B 换成星期天不开门的眼镜店。三则没用的广告里只有 B 可以换：E 是第 14 题唯一的另一家餐厅，H 是第 13 题唯一的另一家有瑜伽的地方，换掉都会让那两题变成只靠关键词。B 原来只给第 12 题当一个很弱的干扰项（“llevamos … a casa”），第 12 题本来就要两步推断（naranjas y tomates → fruta y verdura；85 岁出不了门 → personas mayores、送到家），去掉 B 影响不大。第 17 题仍然是“bici ↔ Bicicletas”，相对容易，但只能换一则广告，这题保留不动。
2. **写作 T1 范文写在 formulario[].modelo、modelo.texto 留空**：可以。build_pdf.py 的教师用书会把“栏目 / 参考答案”印成表，texto 为空时只印 comentario_zh。不过有两个后果（是程序的问题，不是内容的问题，本人没改 tools/）：① modelo.zh（表格答案的中文）不会印出；② 填表任务不调用 stim_teacher，所以 T1 广告的中文译文也不会进教师用书。
3. **说明语里不用写“Número de palabras…”**：对。程序对 T2 在题册和答题纸上都按 palabras 印“Número de palabras: entre 30 y 40.”；T1 填表不印总字数，各简答栏的建议字数写在栏目名里（“(5-8 palabras)”）。
