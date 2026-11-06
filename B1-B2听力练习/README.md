# 西班牙语 B1—B2 听力练习（学生版＋教师版＋录音）

10 套西班牙语听力练习，是《西班牙语 A0—A1 听力练习》《西班牙语 A1—A2 听力练习》（`../A0-A1听力练习/`、`../A1-A2听力练习/`）的续篇：第 1—6 套 B1、第 7—10 套 B2，题型参照 DELE B1、B2 听力的五个任务，面向准备 DELE 或学完 B1 教程的中国学习者。每套 30 题、5 个部分；学生版（55 页）只有题目和答题处，可以直接打印，教师版（186 页）有逐题答案和原文依据、全部录音原文和中文译文、每套的使用建议；每套每个部分一段录音，共 50 段（约 369 分钟）。Word、PDF 和录音在 Release [`b1b2-listening`](../../../releases/tag/b1b2-listening)。

## 内容

| 套 | 级别 | 内容 | 题型 |
| --- | --- | --- | --- |
| 1 | B1 | 经历、趣事和意外（Historias y anécdotas） | DELE B1 的五个任务：短讯息、独白、新闻、配对、谁说的 |
| 2 | B1 | 计划、梦想和将来（Planes y proyectos） | DELE B1 的五个任务：短讯息、独白、新闻、配对、谁说的 |
| 3 | B1 | 合住、邻居和规矩（Vivir con otros） | DELE B1 的五个任务：短讯息、独白、新闻、配对、谁说的 |
| 4 | B1 | 观点、愿望和感受（Opiniones y sentimientos） | DELE B1 的五个任务：短讯息、独白、新闻、配对、谁说的 |
| 5 | B1 | 留言、转述和投诉（Mensajes, quejas y servicios） | DELE B1 的五个任务：短讯息、独白、新闻、配对、谁说的 |
| 6 | B1 | 旅行、地方和传说（Viajes, lugares y misterios） | DELE B1 的五个任务：短讯息、独白、新闻、配对、谁说的 |
| 7 | B2 | 工作和职业（El mundo del trabajo） | DELE B2 的五个任务：短对话、谁的观点、采访、配对、讲座 |
| 8 | B2 | 城市和环境（Ciudades y medio ambiente） | DELE B2 的五个任务：短对话、谁的观点、采访、配对、讲座 |
| 9 | B2 | 科学、健康和技术（Ciencia, salud y tecnología） | DELE B2 的五个任务：短对话、谁的观点、采访、配对、讲座 |
| 10 | B2 | 文化、语言和社会（Cultura, lenguas y sociedad） | DELE B2 的五个任务：短对话、谁的观点、采访、配对、讲座 |

- B1 各套（约 40 分钟）的五个部分：短讯息和短对话（6 题，各自录音）、一个人讲一段经历（6 题）、电台新闻（6 条）、六个人谈同一话题（配对，9 个选项，2 个用不上）、两人对话里“谁说的”（说的是男方、女方，还是两个人都不是）。B2 各套（约 45 分钟）：短对话（问意图、态度、决定）、两人对话里“谁的观点”、电台或播客采访、六段独白配对、讲座或专题报道。全部原创；DELE 只借用题型格式，没有使用官方样题。
- 题目指令用中文，后面附西语课堂指令；题干和选项全部用西语。B1 各套的语法和话题与《西班牙语 B1 教程》（`../B1教程/`）大体对应：经历和趣事、计划和将来、合住和规矩、观点和感受、留言和投诉、旅行和传说；B2 各套是工作、城市和环境、科学和技术、文化和社会，用到过去虚拟式、条件句、被动、复合时态、让步和转述观点。B2 的几套各有一位拉美说话人（哥伦比亚、墨西哥），使用建议里注明了用词差别。
- 录音结构：播音员读“Parte uno”和西语指令；每题前报题号，每题（整段录音的部分是整段）读两遍，读完留作答时间；整段录音的部分和配对题先留看题的时间；最后读“Fin de la parte uno”。一般每个部分整段放一遍即可。
- 录音用本仓库的 Qwen3-TTS 合成，播音员是男1，对话用和 A1、A2、B1 教程相同的另外五个声音；B1 各套 0.98 倍、B2 各套正常语速（有三段为通过电磁音核查微调了 0.01—0.02）。每一句都用语音识别（Parakeet）逐词核对；再查整体响度（−16 LUFS）、短时响度波动和电磁音；最后在成品 MP3 里把每一句切出来再识别一遍（`qa/check_final.py`，4434 句），全部通过。
- 题目写完后先后经过三轮独立审校（西语和答案、印出来的两本书）；录音时有几句因为合成总是吞字而换了说法，题目考的内容不变；版面检查了多轮（`qa/check_layout.py`）。

## 文件

| 文件 | 作用 |
| --- | --- |
| `sets/01.md` … `sets/10.md` | 每套的原文：题目、选项、答案、依据、录音稿和译文、使用建议（格式见 `编写要求.md`），学生版、教师版和录音都由它生成 |
| `编写要求.md` | 编写规则：各套的话题、语法和五个部分的题型，原文格式，录音稿的要求 |
| `build_listening.js` | 排版程序：`node build_listening.js student` / `teacher` 生成 Word（先运行 `tools/export_json.py`） |
| `tools/sets.py` | 读原文的程序（下面几个程序共用） |
| `tools/check_sets.py` | 格式和内容检查：题数、题号、例题、选项、答案分布、“谁说的”题的答案、配对选项、录音行、声音 |
| `tools/export_json.py` | 原文转成 `out/sets.json`（排版用） |
| `tools/make_tracks.py` | 录音：合成、逐句识别核对、响度和电磁音核查，输出 `B1B2_套号-部分号.mp3` 和核对记录 |
| `tools/split_sets.py` | 把学生版 PDF 按套拆开 |
| `qa/check_layout.py` | 版面检查 |
| `qa/check_final.py` | 成品录音逐句复核：按核对记录从合成缓存排出时间表，在成品 MP3 里切出每一句再识别 |

## 重新生成

Word：需要 Node.js 和 `npm install docx@9.5.1 jszip`。PDF 用 LibreOffice 26.8 转（用 FONTCONFIG_FILE 指向能找到苹方的字体配置）。录音在 `setup_mac.sh` 装好的环境里运行（另需 Parakeet 识别模型；男2、女2、女3 的参考录音用 `../A2教程/voices/`，女4 用 `../B1教程/voices/`）：

```bash
python B1-B2听力练习/tools/check_sets.py
python B1-B2听力练习/tools/export_json.py
node B1-B2听力练习/build_listening.js student B1-B2听力练习/out/西班牙语B1-B2听力练习_学生版.docx
node B1-B2听力练习/build_listening.js teacher B1-B2听力练习/out/西班牙语B1-B2听力练习_教师版.docx
soffice --headless --convert-to pdf --outdir B1-B2听力练习/out B1-B2听力练习/out/*.docx
python B1-B2听力练习/tools/make_tracks.py . B1-B2听力练习/audio_out 识别模型目录 1 2 3 4 5 6 7 8 9 10
```
