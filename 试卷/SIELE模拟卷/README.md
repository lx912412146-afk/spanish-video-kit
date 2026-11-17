# SIELE 模拟卷（第一套）

> **非官方模拟卷。** 本卷按 SIELE Global 公开的考试结构自编，与 SIELE、塞万提斯学院、墨西哥国立自治大学（UNAM）、萨拉曼卡大学、布宜诺斯艾利斯大学都没有关系。所有文章、对话、录音、插图和题目都是原创，没有使用官方样题。

一整套 SIELE Global 格式的模拟考试，四项齐全：阅读（CL）、听力（CA）、写作（EIE）、口语（EIO）。每一项的 tarea 数量、题型、题量、文本长度、作答时间和计分方法都按 SIELE 的公开规格（见 [`考试规格.md`](考试规格.md)），可以直接打印做整套模考。

成品在 Release [`siele-mock-1`](../../../releases/tag/siele-mock-1)：

| 文件 | 内容 |
| --- | --- |
| `siele-mock-1-candidate.pdf` | 考生试题册（21 页）：封面和考生须知；阅读 5 个 tarea、听力 6 个 tarea、写作 2 个 tarea、口语 5 个 tarea 的全部题目、文章、选项、插图和说明 |
| `siele-mock-1-answer-sheet.pdf` | 答题卡（4 页）：阅读和听力 76 题的涂卡区、评分栏，写作两个 tarea 的答题纸 |
| `siele-mock-1-teacher.pdf` | 教师用书（28 页）：使用说明和音轨清单、答案速查、阅读逐题解析、听力原文和中文译文及逐题解析、写作和口语的评分标准、范文和范例、成绩换算表、评分表 |
| `SIELE_CA_T1.mp3` … `SIELE_CA_T6.mp3` | 听力 6 个 tarea 各一条音轨（读题时间、两遍之间的停顿、作答和检查时间都已录进去），共约 45 分钟 |
| `SIELE_CA_completa.mp3` | 听力 6 段连播（中间各隔 3 秒），整场模考时直接放这一条 |
| `SIELE_EIO_T1.mp3` … `SIELE_EIO_T5.mp3` | 口语的录音提问和计时提示：T1、T2、T3、T4（话题 1、话题 2 各一条）、T5，共约 30 分钟 |
| `siele-mock-1-audio.zip` | 上面 13 条音轨打包 |
| `siele-mock-1-audio-checks.json` | 录音核对记录：每条音轨的语速、时长、响度，每一句的识别结果 |
| `siele-mock-1-SHA256SUMS.txt` | 校验和 |

## 试卷结构

| 考试 | 时间 | Tareas | 题数 / 任务 | 满分 |
| --- | --- | --- | --- | --- |
| 阅读 Comprensión de lectura | 60 分钟 | 5（A1、A2、B1、B2、C1） | 38 题：短文三选一、邮件三选一、三篇短文配对、两篇文章补段落、C1 完形三选一 | 250 |
| 听力 Comprensión auditiva | 约 45 分钟（按音轨） | 6（A1、A2、B1、B2、C1、C1） | 38 题：对话补词（15 选 5）、5 条新闻、8 段独白配对、访谈三选一、分段讲座三选一、讲座 12 选 6 | 250 |
| 休息 | 15 分钟 | | | |
| 写作 Expresión e interacción escritas | 50 分钟 | 2 | 回信 100–150 词；意见文章或读者来信二选一，250–300 词 | 250 |
| 口语 Expresión e interacción orales | 每人约 26 分钟（含准备） | 5 | 回答个人问题、看图描述、电话留言、读短文答问、就对立观点陈述立场 | 250 |

- 阅读、听力每题 1 分，本部分得分 = 答对题数 × 250 ÷ 38；写作每个 tarea 按衔接、准确、广度、完成任务 4 项打分，口语每个 tarea 按语言运用、完成任务 2 项打分。教师用书里有换算表和按等级的分界。
- 听力的读题时间、两遍之间的停顿等系统时间按 SIELE 白皮书汇总的设定录进音轨；真实考试的题号和提示显示在屏幕上，这里由男声旁白简短报出（如“Tarea uno.”“Noticia dos.”），不读题目。
- 口语音轨读出问题和指令，作答时间是静音；一声高音提示开始说，两声低音提示停止。真实考试用照片，本卷 Tarea 2 用两幅原创插图代替，作答要求不变。

## 怎么用

1. 打印考生试题册和答题卡。阅读 60 分钟；听力播放 `SIELE_CA_completa.mp3`（或按 tarea 播放分段音轨），中间不停；休息 15 分钟后写作 50 分钟。
2. 口语一对一进行：播放对应的 `SIELE_EIO_*.mp3`，考生按提示作答，最好同时录音，之后对照教师用书的评分标准和范例打分。
3. 用教师用书的答案速查批改阅读和听力（听力 Tarea 6 正好选六个；多选一个扣一分，本 tarea 最低 0 分），按换算表算出各部分得分和等级。

## 文件

| 文件 | 作用 |
| --- | --- |
| `考试规格.md` | 依据、各部分的结构和时间、每个 tarea 的文本长度和题型、本卷录音里的系统时间、评分方法、出题原则 |
| `审校记录.md` | 自查、独立审校、版面检查和录音核对的经过，以及每一轮改了什么 |
| `content/cl.json` | 阅读：5 个 tarea 的文章、题目、答案和中文解析 |
| `content/ca.json` | 听力：录音稿（说话人、声音、西语和中文译文）、题目、答案和解析、每个 tarea 的读题和停顿时间 |
| `content/eie.json` | 写作：题目、新闻材料、评分标准、范文和点评 |
| `content/eio.json` | 口语：问题、插图说明、留言情境、短文、观点、范例和点评 |
| `art/` | 口语 Tarea 2 的两幅插图（SVG 原稿和 PNG） |
| `tools/check_content.py` | 内容自查：每段文本的词数、题号、答案和选项、配对题、三选一答案的分布和长度偏向 |
| `tools/asrcheck.py` | 合成和语音识别核对的公用部分（合成缓存、逐句比对、响度和电磁音核查），和 `B1-B2听力练习/tools/make_tracks.py` 同一套规则 |
| `tools/make_audio.py` | 录音：按 `ca.json`、`eio.json` 排出每条音轨（旁白、停顿、提示音），合成、逐句识别核对、母带处理，输出 MP3 和 `核对/report.json` |
| `tools/check_final.py` | 成品录音复核：在成品 MP3 里把每一句切出来再识别一遍；核对连播版确实是六段按顺序接起来的 |
| `tools/build_pdf.py` | 排版：由四个 JSON 生成试题册、答题卡、教师用书的 HTML，再用 Chromium 打印成 A4 PDF |
| `tools/contact.py` | 把 PDF 每页拼成缩略图，检查版面用 |

## 重新生成

在 `setup_mac.sh` 装好的环境里运行（录音另需 Parakeet 识别模型，见 `B1-B2听力练习/README.md`；PDF 需要 `playwright` 和它的 Chromium）。在仓库根目录：

```bash
python 试卷/SIELE模拟卷/tools/check_content.py
export SIELE_KIT="$PWD" SIELE_ASR=识别模型目录 SIELE_ROOT="$PWD/试卷/SIELE模拟卷"
python 试卷/SIELE模拟卷/tools/make_audio.py 试卷/SIELE模拟卷/out/audio ca eio
python 试卷/SIELE模拟卷/tools/check_final.py 试卷/SIELE模拟卷/out/audio
python 试卷/SIELE模拟卷/tools/build_pdf.py 试卷/SIELE模拟卷/out/pdf
```

`make_audio.py` 可以加 `--only SIELE_CA_T3` 之类只重做某几条音轨（合成缓存里已有的句子不会重新合成）。`build_pdf.py` 从 `out/audio/核对/report.json` 读音轨时长写进教师用书。

## 录音

- 用本仓库的 Qwen3-TTS 合成。旁白是男1（工具包推荐的男声）；对话和独白的男2、女2、女3、女4 和 A2、B1 教程相同，女1 和第一册高考模拟卷的女声相同。听力 Tarea 1 语速 0.9 倍，Tarea 2 0.95 倍，Tarea 3 0.98 倍，其余正常语速。
- 每一句合成后都用语音识别（Parakeet）和录音稿逐词比对，有出入就换种子重新合成；整条音轨再查整体响度（−16 LUFS）、短时响度波动和电磁音。最后在成品 MP3 里把每一句切出来再识别一遍（`tools/check_final.py`，461 句），全部通过。
