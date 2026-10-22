# spanish-video-kit

西班牙语逐句精读视频：把一篇西班牙语短文做成 4K 视频。视频有逐句朗读、中文翻译和生词栏，朗读用 Qwen3-TTS 克隆音色或 Supertonic 3。
程序、文章、音色设置都在这个仓库里，模型和成品视频放在 [Releases](../../releases)。换一台 Mac 也能马上接着用。

## 快速开始（macOS）

在“终端”里依次运行（不需要 git，也不需要管理员密码）：

```bash
curl -L https://github.com/lx912412146-afk/spanish-video-kit/archive/refs/heads/main.tar.gz | tar -xz
cd spanish-video-kit-main
zsh setup_mac.sh        # 装环境、下载并校验模型（约 10 GB 磁盘、20 分钟）
zsh run_mac.sh es02     # 生成朗读音频 + 4K 视频（Apple 芯片上约 5 分钟）
```

- 要用 `.tar.gz`：macOS 自带的 `unzip` 解压 GitHub 的 `.zip` 时，中文文件名会出错。
- 装了 git 也可以用 `git clone https://github.com/lx912412146-afk/spanish-video-kit.git`。
- `zsh setup_mac.sh --cache`：另外下载 Qwen3 原始合成缓存（Release `work-files`，约 161 MB）。有了缓存，重做 es02 和分级阅读 50 篇不用重新合成，可以省约 2.5 小时。

常用命令：

- 只看画面：`./run_mac.sh es02 --stills`（截图写到 `预览截图/es02/`）
- 换音色：`./run_mac.sh es02 qwen3_M1F5_25_slow`（音色名见 `西班牙语/tools/voices.json`）
- 音频已经有了，只重做视频：`./run_mac.sh es02 --video-only`
- 批量生成：`./batch_mac.sh`（分级阅读全部 50 篇，音色 `qwen3_M1F5_25_slow`）或 `./batch_mac.sh 音色名 a1_01 b2_03 …`
  - 已经核查通过的会跳过，中断后重新运行会接着做；结果记在 `西班牙语/最终视频/批量日志.txt`。

## 音色

| 名字 | 说明 |
|---|---|
| `qwen3_M1F5_25` | 推荐：Qwen3-TTS 1.7B 克隆音色，原速 |
| `qwen3_M1F5_25_slow` | 同一个音色，**0.8 倍速、音高 +1 半音**（分级阅读 50 篇用的）。语速和音高在合成之后处理：soxr 重采样升调，再用 ffmpeg `atempo` 放慢。句间停顿 0.8 秒、逗号停顿 0.28 秒不变 |
| `supertonic3_*` | Supertonic 3，快、轻量 |

### 响度检查（2026-10-18 调整）

“短时响度波动 ≤ 1.0 LU”这一项，现在**只统计朗读范围内**（第一句开始到最后一句结束）的 3 秒窗口，上限不变。见 `西班牙语/tools/loudness.py`。
- 为什么改：原测法把模板规定的片头 1.5 秒、结尾 2 秒静音也算进了“朗读响度的起伏”，首尾窗口一半是静音。分级阅读的短文按原测法，原模板原速原调 50 篇里也有 16 篇过不了。
- 片头、结尾静音另有两项单独核查。原测法的数值照样算，写在核查报告的 `info` 里，只记录不判定。
- 视频核查会对视频里的音轨再测一次，所以 `qwen3_M1F5_25_slow` 在音频阶段先压到 0.97 以下（`safe_short_term`）。超过的那一篇，按 `leveler_ladder` 依次加强慢速电平再试（四级 c14 用过同样的做法）。50 篇里有 5 篇用到。

Qwen3 每一段的原始合成都缓存在 `西班牙语/audio/_合成缓存/`（不进 git）。只改语速、音高、停顿、电平时，重跑不用重新合成，几秒钟就好。
要换速度或音高，复制一个音色，改 `tempo`（0.8 = 慢到 0.8 倍）和 `pitch_cents`（100 = 一个半音）就行。
- 缓存的文件名由文字、合成设置和参考录音的内容算出来，不含本机路径，所以换电脑也能直接用。
- 2026-10-18 的缓存打包在 Release `work-files` 的 `qwen3-synthesis-cache.zip`：可以用 `setup_mac.sh --cache` 下载，也可以手动 `unzip qwen3-synthesis-cache.zip -d 西班牙语/audio/_合成缓存`。

## 辅助工具（`西班牙语/tools/`）

| 脚本 | 用途 |
|---|---|
| `check_articles.py 编号… [-v]` | 生成前检查文章 JSON：生词、词性图例、不停顿逗号；`-v` 打印朗读分段 |
| `fill_cache.py 音色 编号…` | 只做 Qwen3 合成、存进缓存，不做后期也不出视频。批量生成前先跑它，最慢的一步就和后期参数无关了 |
| `long_merge_rule.py 编号…` | 不停顿合并后超过 100 字符的长段恢复逗号停顿，并写进 `_说明` |
| `loudness_survey.py [--voices 音色,…] 编号…` | 只用缓存，比较“原测法”和“朗读范围”两种短时响度波动 |
| `prep_release.py 输出文件夹 [说明文件]` | 把 50 个视频复制成英文文件名，合并核查报告，写好 Release 说明 |

## 仓库里的其他资料

- `原始资料/`：用户发来的《西班牙语A1-C1分级阅读文章集》Word 原件、从中提取的文本 `articles.txt`、生成 50 篇骨架的 `make_skeletons.py`。
- `记录/`：
  - `文章补写/`：补写翻译和生词时给 5 个助手的统一规范 `补写规范.md`，以及他们的填写脚本和数据（结果以 `西班牙语/文章/*.json` 为准）。
  - `响度测法对比_50篇.txt`：两种测法在 50 篇上的对比数据。
  - `日志/`：合成缓存填充、截图排版检查、批量生成的日志，本机路径已替换成 `<KIT>` 等占位符。

## 新文章怎么加

1. 照 `西班牙语/文章/es02.json` 或分级阅读的 `a1_01.json` 写 `西班牙语/文章/<编号>.json`：
   - 每句要有 `es` 原文、`zh` 翻译，以及 3–5 个生词 `w`（`h` 词头、`pos` 词性、`zh` 释义、`surface` 句中写法）。
   - 生词的 `surface` 必须是句中的完整词，恰好出现一次，生词之间不能重叠。
2. 列举（A, B y C）里“不停顿”的逗号，写在文章自己的 `no_pause_commas` 里（也可以写在 `西班牙语/tools/逗号停顿.json`）。不停顿合并后超过 100 个字符的长段，照常停顿。
3. 原文不能有阿拉伯数字、引号和括号，数字要写成单词（dieciocho、las diez y media）。
4. 先检查：`python 西班牙语/tools/check_articles.py <编号> -v`（`-v` 会打印朗读分段，`|` 是停顿的地方）。
5. 生成：`./run_mac.sh <编号> [音色]`。生成后会自动核查 15 项：响度、电磁音、片头 1.5 秒、句间 0.8 秒、结尾 2 秒、4K、30 帧、声画一致等，任何一项不通过就不输出。

## 已做的文章

| 编号 | 标题 | 成品 |
|---|---|---|
| es01 | Mi pasión por los viajes 我对旅行的热爱 | 示例文章（原作者） |
| es02 | Mi vida diaria 我的日常生活 | Release `videos`；音频、字幕在 `西班牙语/audio/qwen3_M1F5_25/`，0.8 倍速版在 `qwen3_M1F5_25_slow/` |
| a1_01–c1_10 | 西班牙语分级阅读 A1–C1，每级 10 篇（来自《西班牙语A1-C1分级阅读文章集》） | 视频在 Release `graded-reading`；音频、字幕在 `西班牙语/audio/qwen3_M1F5_25_slow/` |

分级阅读 50 篇的中文翻译和生词栏是 2026-10-18 补写的。原文档只有西班牙语原文，每篇的特别判断写在各自 JSON 的 `_说明` 里。

<details><summary>A1 基础入门（10 篇）</summary>

| 编号 | 标题 | 中文 | 句数 · 生词 |
|---|---|---|---|
| a1_01 | Mi familia | 我的家庭 | 7 句 · 30 词 |
| a1_02 | Un día normal | 平常的一天 | 7 句 · 30 词 |
| a1_03 | Mi ciudad | 我的城市 | 7 句 · 32 词 |
| a1_04 | En el supermercado | 在超市 | 7 句 · 32 词 |
| a1_05 | Mi mejor amiga | 我最好的朋友 | 8 句 · 33 词 |
| a1_06 | Un fin de semana | 一个周末 | 7 句 · 31 词 |
| a1_07 | Mi habitación | 我的房间 | 7 句 · 32 词 |
| a1_08 | En el restaurante | 在餐厅 | 8 句 · 31 词 |
| a1_09 | El tiempo | 天气 | 6 句 · 29 词 |
| a1_10 | Aprender español | 学习西班牙语 | 7 句 · 32 词 |

</details>

<details><summary>A2 初级进阶（10 篇）</summary>

| 编号 | 标题 | 中文 | 句数 · 生词 |
|---|---|---|---|
| a2_01 | Mi primer trabajo | 我的第一份工作 | 6 句 · 29 词 |
| a2_02 | Una visita a Salamanca | 萨拉曼卡之行 | 7 句 · 31 词 |
| a2_03 | Una vida más saludable | 更健康的生活 | 7 句 · 32 词 |
| a2_04 | La compra por internet | 网上购物 | 7 句 · 31 词 |
| a2_05 | Una nueva compañera de piso | 新室友 | 7 句 · 32 词 |
| a2_06 | El transporte público | 公共交通 | 6 句 · 28 词 |
| a2_07 | Una celebración familiar | 一次家庭庆祝会 | 7 句 · 33 词 |
| a2_08 | Aprender de los errores | 从错误中学习 | 6 句 · 29 词 |
| a2_09 | Un día sin móvil | 没有手机的一天 | 7 句 · 34 词 |
| a2_10 | Una excursión a la montaña | 一次山间远足 | 8 句 · 35 词 |

</details>

<details><summary>B1 中级（10 篇）</summary>

| 编号 | 标题 | 中文 | 句数 · 生词 |
|---|---|---|---|
| b1_01 | La importancia de organizar el tiempo | 合理安排时间的重要性 | 5 句 · 21 词 |
| b1_02 | Vivir en otro país | 在国外生活 | 6 句 · 24 词 |
| b1_03 | El valor de las bibliotecas | 图书馆的价值 | 6 句 · 25 词 |
| b1_04 | Turismo responsable | 负责任的旅游 | 5 句 · 23 词 |
| b1_05 | La comida y la memoria | 食物与记忆 | 6 句 · 28 词 |
| b1_06 | Estudiar en grupo | 小组学习 | 5 句 · 22 词 |
| b1_07 | El comercio de barrio | 社区小商店 | 5 句 · 22 词 |
| b1_08 | La influencia de las redes sociales | 社交网络的影响 | 6 句 · 25 词 |
| b1_09 | Aprender durante toda la vida | 终身学习 | 6 句 · 24 词 |
| b1_10 | La ciudad y los espacios verdes | 城市与绿地 | 6 句 · 24 词 |

</details>

<details><summary>B2 中高级（10 篇）</summary>

| 编号 | 标题 | 中文 | 句数 · 生词 |
|---|---|---|---|
| b2_01 | La flexibilidad laboral: oportunidad y desafío | 弹性工作：机遇与挑战 | 5 句 · 22 词 |
| b2_02 | ¿Es suficiente con reciclar? | 只靠回收就够了吗？ | 6 句 · 25 词 |
| b2_03 | La vivienda en las ciudades | 城市住房 | 5 句 · 24 词 |
| b2_04 | La inteligencia artificial en la educación | 教育中的人工智能 | 5 句 · 24 词 |
| b2_05 | La cultura de la inmediatez | 即时文化 | 5 句 · 22 词 |
| b2_06 | La preservación del patrimonio | 文化遗产的保护 | 5 句 · 23 词 |
| b2_07 | La brecha digital | 数字鸿沟 | 5 句 · 23 词 |
| b2_08 | La importancia de escuchar | 倾听的重要性 | 5 句 · 23 词 |
| b2_09 | Consumir menos, elegir mejor | 少消费，选得更好 | 6 句 · 27 词 |
| b2_10 | El valor de los errores | 错误的价值 | 6 句 · 26 词 |

</details>

<details><summary>C1 高级（10 篇）</summary>

| 编号 | 标题 | 中文 | 句数 · 生词 |
|---|---|---|---|
| c1_01 | La atención como recurso escaso | 作为稀缺资源的注意力 | 6 句 · 27 词 |
| c1_02 | La paradoja de la conectividad | 互联互通的悖论 | 5 句 · 23 词 |
| c1_03 | La ciudad como espacio de negociación | 作为协商空间的城市 | 5 句 · 23 词 |
| c1_04 | El idioma y la identidad | 语言与身份认同 | 5 句 · 24 词 |
| c1_05 | El trabajo y el sentido de la vida | 工作与人生意义 | 5 句 · 23 词 |
| c1_06 | La memoria colectiva y sus silencios | 集体记忆及其沉默 | 5 句 · 22 词 |
| c1_07 | La sostenibilidad más allá del individuo | 超越个人层面的可持续性 | 5 句 · 24 词 |
| c1_08 | La confianza en la información | 对信息的信任 | 6 句 · 27 词 |
| c1_09 | La innovación y sus consecuencias imprevistas | 创新及其意外后果 | 5 句 · 23 词 |
| c1_10 | La paciencia como forma de resistencia | 作为抵抗方式的耐心 | 6 句 · 27 词 |

</details>

## 试卷

- [`试卷/第一册高考模拟卷/`](试卷/第一册高考模拟卷/)：按 2024 年起的高考西班牙语新课标卷题型出的原创模拟卷，范围是《现代西班牙语》第一册老版，满分 150 分。
  - 原文是 `试卷.md`。学生版、教师版 PDF 和约 10 分钟的听力音频在 Release `exam-book1`。
  - 听力用本仓库的 Qwen3 音色合成男女声对话，每句都用语音识别和录音稿逐词核对过。
- [`试卷/第一册分阶段模拟卷/`](试卷/第一册分阶段模拟卷/)：同样题型的 8 套分阶段卷，范围分别是第 1–4、1–8、1–12、1–14、1–16、1–18 课和第 1–20 课（A、B 两套）。
  - 每套一个文件夹，原文是 `试卷.md`；`课程大纲.md` 是各课语法和话题，`出题要求.md`、`审校要求.md` 是出题和审校的规则。
  - PDF 和听力音频在 Release `exam-book1-stages`。

## 课件

- [`课件/第一册/`](课件/第一册/)：《现代西班牙语》第一册（老版）第 1–24 课的分课课件（PowerPoint 16:9，另有 PDF）。每课：目标、语音（第 1–8 课）、词汇、课文、语法、常用表达、练习和答案、小结、作业，附教学备注。
  - 每课内容是一个 JSON（`content/Lxx.json`），`build_decks.js` 统一排版生成。PPTX 和 PDF 在 Release `courseware-book1`。
- [`课件/第二册/`](课件/第二册/)：第二册（老版）第 1–18 课的分课课件，版式同上（第二册没有语音部分；第 6、12、18 课是复习课）。PPTX 和 PDF 在 Release `courseware-book2`。
- [`课件/第三册/`](课件/第三册/)：第三册（老版）第 1–18 课的分课课件，版式同上（第 6、12、18 课按复习课处理）。PPTX 和 PDF 在 Release `courseware-book3`。
- [`课件/第四册/`](课件/第四册/)：第四册（老版）第 1–18 课的分课课件，版式同上。PPTX 和 PDF 在 Release `courseware-book4`。

## 学习白皮书

- [`白皮书/`](白皮书/)：《西班牙语学习白皮书》，把《现代西班牙语》（老版）第一至四册 78 课的知识点按专题整理成一本书（395 页）：四册学习路线和语法进度总表、语音与正字法、词法、动词、句法、分课索引和全部重点词汇、常见错误、术语对照。每个知识点标出处〔册·课〕。
  - 各章正文是 `chapters/*.md`，`build_whitepaper.js` 读各章和四册课件 JSON 排成 Word；PDF 由 LibreOffice 转出。Word 和 PDF 在 Release `whitepaper`。

## DELE 考试白皮书

- [`DELE白皮书/`](DELE白皮书/)：《DELE 考试白皮书》（A1–C2，436 页），面向准备 DELE 的中国考生和老师：各级考试结构（部分、任务、题量、时长、字数、及格规则），每个任务的题型模板、原创样题和答案解析，写作范文和口语示范；语法用词易错点和各项技能的应试技巧；A1–C2 常用词汇、搭配、习语和写作口语常用表达；备考计划和术语对照。
  - 考试结构依据 2026 年 10 月的塞万提斯学院官方考试网站和考试指南整理（`资料/`），样题和范文都是原创的，不是真题或官方样卷。拼写按现行 RAE 规范（solo、este 不加重音）。
  - 各章正文是 `chapters/*.md`，`build_dele.js` 排成 Word，PDF 由 LibreOffice 转出。Word 和 PDF 在 Release `dele-whitepaper`。

## SIELE 考试白皮书

- [`SIELE白皮书/`](SIELE白皮书/)：《SIELE 考试白皮书》（A1–C1，332 页），面向准备 SIELE 的中国考生和老师：考试类型（Global、S1–S5）和四项考试的每个任务（级别、题型、题量、时长、字数），各项分数段，原创样题和答案解析、写作范文和口语示范；语法用词易错点、按级别的易错题精练、电脑考试的注意事项和应试技巧；A1–C1 常考词汇、写作口语常用表达；备考计划和术语对照。
  - 考试结构依据 2026 年 10 月的 siele.org 和 2021 年 4 月版官方考试指南整理（`资料/`），样题和范文都是原创的。第 6 章和第 9–12 章由 DELE 白皮书的相应各章改编。
  - 各章正文是 `chapters/*.md`，`build_siele.js` 排成 Word，PDF 由 LibreOffice 转出。Word 和 PDF 在 Release `siele-whitepaper`。

## 中文阅读（HSK1）

- [`中文阅读/`](中文阅读/)：把《HSK 1级中文阅读教材 · 第一册：我的中文生活》（面向西班牙语母语的中文初学者，50 篇）做成逐句精读视频，版式沿用西班牙语分级阅读：汉字上方逐字注拼音、重点词汇编号并给出拼音和西语释义、原文下面是西语翻译。朗读用 Qwen3-TTS 克隆中文女声（0.75 倍速），每段用 SenseVoice 识别核对。
  - 50 篇全部做完（2026-10-21）。视频在 Release `hsk1-reading`（`hsk1_01.mp4` … `hsk1_50.mp4`）。

## 西班牙语高考白皮书

- [`高考白皮书/`](高考白皮书/)：《西班牙语高考白皮书》（415 页），面向参加普通高考、外语选考西班牙语的高中生和老师：新课标卷的试卷结构、考试时间和听力安排、各地差异和课标要点；听力、阅读、完形填空、语法填空、写作各一章（经典类型、做题方法、原创样题和解析、便签和短文范文）；语法易错点，用词、拼写和重音易错点，易错题精练，应试注意事项；按课标主题整理的常用词汇、高频动词和搭配、写作常用表达；备考计划、一套原创的全真格式模拟卷和语法术语一览。
  - 试卷结构依据教育部教育考试院 2024 年 1 月公布的适应性测试西班牙语新课标试卷和专家解读，语言范围依据普通高中西班牙语课程标准（`资料/` 里每条事实注明来源和可信度）；样题、范文和模拟卷都是原创的。
  - 各章正文是 `chapters/*.md`，`build_gaokao.js` 排成 Word，PDF 由 LibreOffice 转出。Word 和 PDF 在 Release `gaokao-whitepaper`。

## 西班牙语 A1 教程

- [`A1教程/`](A1教程/)：《西班牙语 A1 教程》，面向中国大学生和成人零起点学习者：12 个单元＋3 个复习单元，学生用书（547 页）和教师用书（349 页），配 115 段录音。讲解以中文为主，课文、例句和练习用西语；依据 CEFR A1 和塞万提斯学院《课程计划》A1，编排参考海外交际法教材（Método、Prisma、Aula 等）的通行做法，课文、对话、练习和人物全部原创。教师用书含逐单元教学建议、全部答案、录音稿和 3 套阶段测试。
  - 各单元是 `student/`、`teacher/`、`audio/`（录音稿）下的 Markdown，`build_a1.js` 排成 Word，PDF 由 LibreOffice 转出；录音由 `tools/make_tracks.py` 用本仓库的 Qwen3-TTS 合成（五个声音），逐句语音识别核对。Word、PDF 和录音在 Release `a1-textbook`。

## 教学视频

- [`教学视频/第一册第1课/`](教学视频/第一册第1课/)：《现代西班牙语》第一册第一课 ¿Quién es él? 的教学视频（约 13 分钟，1920×1080）。中文讲解＋西语示范和跟读：元音、辅音、音节划分、重音、连读，仿照课文的对话，语法、单词和小练习。
  - 讲解和每个示范词句都用语音识别核对过（中文比带声调拼音）。视频在 Release `lesson-videos`。

## Releases

| 标签 | 内容 |
|---|---|
| `es-kit-preview` | 原始工具包 `SPANISH-video-kit-preview.zip`、Qwen3-TTS 1.7B 模型分卷 `.001–.003`、`join_qwen3_parts.py`、`SHA256SUMS.txt` |
| `videos` | es02 的视频（MP4）、朗读、字幕和核查报告；0.8 倍速样片 `es02_Mi_vida_diaria_4K_slow.mp4` 和它的核查报告 |
| `graded-reading` | 分级阅读 50 篇的 4K 视频（`A1-01_….mp4` …）和全部核查报告 |
| `work-files` | 工作文件：Qwen3 原始合成缓存 `qwen3-synthesis-cache.zip`（505 段）、50 篇和 es02 的预览截图 `preview-stills.zip`、`work-files-SHA256SUMS.txt` |
| `exam-book1` | 第一册高考模拟卷：学生版 / 教师版 PDF、整套听力 `listening_full.mp3`、分段听力 `texto_1.mp3` … `texto_9.mp3` |
| `exam-book1-stages` | 8 套分阶段卷，文件名以卷号开头（`L01-04` … `L01-20B`）：`_student.pdf`、`_teacher.pdf`、`_listening.mp3`、`_texto_1.mp3` … `_texto_9.mp3` |
| `lesson-videos` | 教学视频：`book1_lesson01_quien_es_el.mp4`（第一册第一课）、`lesson-videos-SHA256SUMS.txt` |
| `courseware-book1` | 第一册分课课件：`book1_L01.pptx` … `book1_L24.pptx` 和同名 PDF、`courseware-book1-SHA256SUMS.txt` |
| `courseware-book2` | 第二册分课课件：`book2_L01.pptx` … `book2_L18.pptx` 和同名 PDF、`courseware-book2-SHA256SUMS.txt` |
| `courseware-book3` | 第三册分课课件：`book3_L01.pptx` … `book3_L18.pptx` 和同名 PDF、`courseware-book3-SHA256SUMS.txt` |
| `courseware-book4` | 第四册分课课件：`book4_L01.pptx` … `book4_L18.pptx` 和同名 PDF、`courseware-book4-SHA256SUMS.txt` |
| `whitepaper` | 西班牙语学习白皮书：`es-whitepaper.docx`、`es-whitepaper.pdf`、`whitepaper-SHA256SUMS.txt` |
| `dele-whitepaper` | DELE 考试白皮书（A1–C2）：`dele-whitepaper.docx`、`dele-whitepaper.pdf`、`dele-whitepaper-SHA256SUMS.txt` |
| `siele-whitepaper` | SIELE 考试白皮书（A1–C1）：`siele-whitepaper.docx`、`siele-whitepaper.pdf`、`siele-whitepaper-SHA256SUMS.txt` |
| `gaokao-whitepaper` | 西班牙语高考白皮书：`gaokao-whitepaper.docx`、`gaokao-whitepaper.pdf`、`gaokao-whitepaper-SHA256SUMS.txt` |
| `a1-textbook` | 西班牙语 A1 教程：`a1-student-book.docx/.pdf`、`a1-teacher-book.docx/.pdf`、全部录音 `A1_*.mp3` 和打包的 `a1-audio.zip`、`a1-audio-checks.json`、`a1-textbook-SHA256SUMS.txt` |
| `hsk1-reading` | HSK1 中文阅读视频：`hsk1_01.mp4` … `hsk1_50.mp4`（50 篇）、`hsk1-reading-checks.json`、`hsk1-reading-SHA256SUMS.txt` |

## 来源与改动

- 原始工具包：[AlienCodes/university-entrance-examination · es-kit-preview](https://github.com/AlienCodes/university-entrance-examination/releases/tag/es-kit-preview)（2026-10-15）。原版说明见 `使用说明.md`，模型和程序的版权归原作者，请遵守各自的许可。
- 在原版基础上的改动：
  - 2026-10-17：
    - `逗号停顿.json` 改为按文章编号登记（原版只适用于 es01，用在别的文章上会报错）。
    - `voices.json` 的路径改为相对工具包根目录，`"python": "self"` 表示用当前环境，换电脑不用改路径。
    - 新增 `setup_mac.sh`（一键安装）、`run_mac.sh`（一键生成）和文章 `es02`。
  - 2026-10-18：
    - `make_audio.py`：
      - 新增合成缓存。
      - 新增合成后的变速变调（`tempo`、`pitch_cents`）。
      - 慢速电平参数可按音色设置（`leveler_win`、`leveler_rng`）。
      - 文章 JSON 里可以写 `no_pause_commas`。
    - `make_video.py`：页眉可按文章设置（`header`）；分级阅读按“等级-篇号”命名；新增 `--print-name`。
    - 新增 `batch_mac.sh`（批量生成）、`check_articles.py`（文章检查）、音色 `qwen3_M1F5_25_slow`、分级阅读 50 篇。
    - 新增 `loudness.py`：短时响度波动只统计朗读范围，用户确认。`make_audio.py` 新增安全线和逐级加强电平；`make_video.py` 的核查改用 `loudness.verify`，原测法数值记在 `info`。
  - 2026-10-19：
    - 新增 `原始资料/`、`记录/`，以及 `fill_cache.py`、`long_merge_rule.py`、`loudness_survey.py`、`prep_release.py` 四个辅助工具。
    - `setup_mac.sh` 新增 `--cache`；新增 Release `work-files`。
    - 新增 `试卷/第一册高考模拟卷/`（试卷原文、听力生成、语音识别核对、PDF 排版）和 Release `exam-book1`。
    - 新增 `试卷/第一册分阶段模拟卷/`（8 套）和 Release `exam-book1-stages`；全册卷按查到的第 22–24 课内容改了完形 51、57 题和知识点覆盖表；新增 `check_paper.py`（格式自检）、`asr_retry.py`（读错的句子换种子重合成）。
    - 新增 `教学视频/第一册第1课/`（脚本、合成和核对、画面模板）和 Release `lesson-videos`。
    - 新增 `课件/第一册/`（24 课的课件内容和生成程序）和 Release `courseware-book1`。
  - 2026-10-20：
    - 新增 `课件/第二册/`（18 课的课件内容、第二册课程大纲和生成程序）和 Release `courseware-book2`；课件生成程序改成按 JSON 里的 `book` 字段区分第几册；修正长标题不缩小的问题，第一册课件重新导出（文字不变）。
    - 新增 `课件/第三册/`（18 课的课件内容、第三册课程大纲和生成程序）和 Release `courseware-book3`。
    - 新增 `课件/第四册/`（18 课的课件内容、第四册课程大纲和生成程序）和 Release `courseware-book4`。
    - 新增 `白皮书/`（西班牙语学习白皮书的各章正文和生成程序）和 Release `whitepaper`；修正课件里的几处：第三册第 1、5、8 课几页语法标题只显示“语法 N”，第三册第 17 课 in- 在 r 前应作 ir-，第三册第 7 课四位数 2850 不分节，第二册第 10 课第二个“虚拟式现在时（二）”改为“（二，续）”，第一册第 20 课“以 j 结尾的词根用 -eron”限于不规则词根。
    - 新增 `DELE白皮书/`（DELE 考试白皮书 A1–C2 的各章正文、考试结构资料和生成程序）和 Release `dele-whitepaper`；学习白皮书的页数改为实际的 395 页。
  - 2026-10-21：
    - 新增 `SIELE白皮书/`（SIELE 考试白皮书 A1–C1 的各章正文、考试结构资料和生成程序）和 Release `siele-whitepaper`。
    - 新增 `中文阅读/`（HSK1 中文阅读视频的文章数据、生成程序和 Word 原件）和 Release `hsk1-reading`（第 01 篇试做）。
    - `中文阅读/` 50 篇全部做完：补写并审校了逐句西语翻译和补充词条，语速改为 0.75 倍；Release `hsk1-reading` 换成 50 篇的视频。
    - 新增 `高考白皮书/`（西班牙语高考白皮书的各章正文、考试事实资料和生成程序）和 Release `gaokao-whitepaper`。
  - 2026-10-23：
    - 新增 `A1教程/`（西班牙语 A1 教程的学生用书、教师用书、录音稿、生成和录音程序）和 Release `a1-textbook`。
