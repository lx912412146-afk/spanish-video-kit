# 西班牙语 A1—A2 听力练习（学生版＋教师版＋录音）

10 套西班牙语听力练习，是《西班牙语 A0—A1 听力练习》（`../A0-A1听力练习/`）的续篇，从 A1 巩固逐套过渡到 A2，面向学完 A1 的中国学习者。每套 25 题、4 个部分，约 35 分钟；学生版（34 页）只有题目和答题处，可以直接打印，教师版（112 页）有逐题答案和原文依据、全部录音原文和中文译文、每套的使用建议；每套每个部分一段录音，共 40 段（约 203 分钟）。Word、PDF 和录音在 Release [`a1a2-listening`](../../../releases/tag/a1a2-listening)。

## 内容

| 套 | 级别 | 内容 | 题型 |
| --- | --- | --- | --- |
| 1 | A1 | 日常生活和业余时间（Un día normal） | 选择、判断对错、配对 |
| 2 | A1 | 住房和街区（Casas y barrios） | 选择、填空、配对 |
| 3 | A1—A2 | 饭馆、点菜和订餐（Comer fuera） | 选择、听写、判断对错 |
| 4 | A2 | 周末和假期（Fines de semana y vacaciones） | 选择、判断对错、配对 |
| 5 | A2 | 人生故事和经历（Vidas y experiencias） | 选择、填空、配对 |
| 6 | A2 | 小时候和以前（Antes y ahora） | 选择、判断对错、填空 |
| 7 | A2 | 健康和看病（La salud） | 选择、判断对错、配对 |
| 8 | A2 | 旅行（De viaje） | 选择、听写、配对 |
| 9 | A2 | 购物和服务（Compras y servicios） | 选择、判断对错、填空 |
| 10 | A2 | 学习和工作（Estudios y trabajo） | 选择、配对 |

- 题型：第一部分都是 7 段短对话三选一；其余三个部分有广播通知和广告（各题单独录音的三选一）、整段对话或采访（三选一或判断对错）、配对（9 个选项，2 个用不上）、留言和讲座填空、听写信息。全部原创；DELE A2 只借用题型格式（例题、每段读两遍、配对选项比题目多），没有使用官方样题。
- 题目指令用中文，后面附西语课堂指令；题干和选项全部用西语。语法从 A1 的现在时逐套加到 A2：第 3 套现在完成时，第 4—5 套简单过去时，第 6 套过去未完成时，第 7 套肯定命令式，第 9 套宾语代词，第 10 套几种过去时的配合；不用虚拟式、条件式（固定说法除外），将来时只在第 8—10 套的天气预报、广播里少量出现。说法参考《西班牙语 A2 教程》（`../A2教程/`）。
- 录音结构：播音员读“Parte uno”和西语指令；每题前报题号（Ejemplo、Número uno…），每题读两遍，读完留作答时间；整段录音的部分和配对题先留看题、看选项的时间，整段读两遍；最后读“Fin de la parte uno”。一般每个部分整段放一遍即可。
- 录音用本仓库的 Qwen3-TTS 合成，播音员是男1，对话用和 A1、A2、B1 教程相同的另外五个声音；语速第 1—3 套 0.92 倍、第 4—7 套 0.94 倍、第 8—10 套 0.95 倍（听写部分再慢一点）。每一句都用语音识别（Parakeet）逐词核对（拼读的字母逐个核对）；再查整体响度（−16 LUFS）、短时响度波动和电磁音；最后在成品 MP3（变速、母带处理之后）里把每一句切出来再识别一遍（`qa/check_final.py`，2969 句），全部通过。
- 题目写完后先后由两人独立审校（西语和答案、印出来的两本书）；版面检查了多轮（空白页、题目和选项分页、单词和数字断行等，`qa/check_layout.py`）。

## 文件

| 文件 | 作用 |
| --- | --- |
| `sets/01.md` … `sets/10.md` | 每套的原文：题目、选项、答案、依据、录音稿和译文、使用建议（格式见 `编写要求.md`），学生版、教师版和录音都由它生成 |
| `编写要求.md` | 编写规则：各套的话题、语法和题型，原文格式，录音稿的要求 |
| `build_listening.js` | 排版程序：`node build_listening.js student` / `teacher` 生成 Word（先运行 `tools/export_json.py`） |
| `tools/sets.py` | 读原文的程序（下面几个程序共用） |
| `tools/check_sets.py` | 格式和内容检查：题数、题号、例题、选项、答案分布、配对选项、填空的空、录音行、声音 |
| `tools/export_json.py` | 原文转成 `out/sets.json`（排版用） |
| `tools/make_tracks.py` | 录音：合成、逐句识别核对、响度和电磁音核查，输出 `A1A2_套号-部分号.mp3` 和核对记录 |
| `tools/split_sets.py` | 把学生版 PDF 按套拆开 |
| `qa/check_layout.py` | 版面检查 |
| `qa/check_final.py` | 成品录音逐句复核：按核对记录从合成缓存排出时间表，在成品 MP3 里切出每一句再识别 |

## 重新生成

Word：需要 Node.js 和 `npm install docx@9.5.1 jszip`。PDF 用 LibreOffice 26.8 转（用 FONTCONFIG_FILE 指向能找到苹方的字体配置）。录音在 `setup_mac.sh` 装好的环境里运行（另需 Parakeet 识别模型；男2、女2、女3 的参考录音用 `../A2教程/voices/`，女4 用 `../B1教程/voices/`）：

```bash
python A1-A2听力练习/tools/check_sets.py
python A1-A2听力练习/tools/export_json.py
node A1-A2听力练习/build_listening.js student A1-A2听力练习/out/西班牙语A1-A2听力练习_学生版.docx
node A1-A2听力练习/build_listening.js teacher A1-A2听力练习/out/西班牙语A1-A2听力练习_教师版.docx
soffice --headless --convert-to pdf --outdir A1-A2听力练习/out A1-A2听力练习/out/*.docx
python A1-A2听力练习/tools/make_tracks.py . A1-A2听力练习/audio_out 识别模型目录 1 2 3 4 5 6 7 8 9 10
```
