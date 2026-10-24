# 西班牙语 A0—A1 听力练习（学生版＋教师版＋录音）

10 套西班牙语听力练习，从 A0（零起点）逐套过渡到 A1，面向中国的零起点和初级学习者。每套 23—24 题、4 个部分，约 30 分钟；学生版（25 页）只有题目和答题处，可以直接打印，教师版（65 页）有逐题答案和原文依据、全部录音原文和中文译文、每套的使用建议；每套每个部分一段录音，共 40 段（约 89 分钟）。Word、PDF 和录音在 Release [`a0a1-listening`](../../../releases/tag/a0a1-listening)。

## 内容

| 套 | 级别 | 内容 | 题型 |
| --- | --- | --- | --- |
| 1 | A0 | 字母、拼读和问候（El alfabeto y los saludos） | 选择、听写、判断对错 |
| 2 | A0 | 数字 0—20 和电话号码（Los números del 0 al 20） | 选择、听写、判断对错 |
| 3 | A0 | 颜色、教室用品和数字 21—100（Colores, objetos y números hasta 100） | 选择、听写、配对 |
| 4 | A0 | 星期、月份和日期（Los días, los meses y las fechas） | 选择、听写、填空 |
| 5 | A0—A1 | 时间和日常作息（La hora y la rutina diaria） | 选择、听写、配对 |
| 6 | A1 | 家人和个人信息（La familia y los datos personales） | 选择、填空、配对 |
| 7 | A1 | 购物和价格（De compras） | 选择、配对、填空 |
| 8 | A1 | 城市里：地点和问路（En la ciudad） | 选择、判断对错、填空 |
| 9 | A1 | 天气和日程安排（El tiempo y los planes） | 选择、配对、判断对错 |
| 10 | A1 | 打电话、留言和通知（Al teléfono y avisos） | 选择、填空、配对 |

- 题型：听词或听句选择（文字选项，没有插图）、判断对错、配对、听写数字和时间、拼写、短对话三选一、填空。全部原创；DELE A1 只借用题型格式（例题、每段读两遍、配对选项比题目多两个），没有使用官方样题。
- 题目指令用中文，后面附简短的西语课堂指令；第 1—4 套的题干和判断句用中文，第 5 套起改用简单的西语。词汇和语法不超过 A1（现在时为主，第 9、10 套用到 ir a + 不定式），说法参考《西班牙语 A1 教程》（`../A1教程/`）。
- 录音结构：播音员读“Parte uno”和西语指令；每题前报题号（Ejemplo、Número uno…），每题读两遍，读完留作答时间；整段对话或短文的部分和配对题先留看题、看选项的时间，整段对话读两遍；最后读“Fin de la parte uno”。一般每个部分整段放一遍即可。
- 录音用本仓库的 Qwen3-TTS 合成，播音员是男1，对话用和 A1、A2 教程相同的另外四个声音；语速第 1—4 套 0.86 倍、第 5 套 0.88 倍、第 6—10 套 0.9 倍（听写部分再慢一点）。每一句都用语音识别（Parakeet）逐词核对，拼读的字母逐个核对（只有字母 i 被识别成同音的 Y 不算错）；再查整体响度（−16 LUFS）、短时响度波动和电磁音；最后在成品 MP3（变速、母带处理之后）里把每一句切出来再识别一遍（`qa/check_final.py`，1379 句），全部通过。
- 题目写完后先后由两人独立审校（西语和答案、印出来的两本书）；版面检查了多轮（空白页、题目和选项分页、单词和数字断行等，`qa/check_layout.py`）。

## 文件

| 文件 | 作用 |
| --- | --- |
| `sets/01.md` … `sets/10.md` | 每套的原文：题目、选项、答案、依据、录音稿和译文、使用建议（格式见 `编写要求.md`），学生版、教师版和录音都由它生成 |
| `编写要求.md` | 编写规则和原文格式 |
| `build_listening.js` | 排版程序：`node build_listening.js student` / `teacher` 生成 Word（先运行 `tools/export_json.py`） |
| `tools/sets.py` | 读原文的程序（下面几个程序共用） |
| `tools/check_sets.py` | 格式和内容检查：题数、题号、选项、答案分布、配对选项、填空的空、录音行 |
| `tools/export_json.py` | 原文转成 `out/sets.json`（排版用） |
| `tools/make_tracks.py` | 录音：合成、逐句识别核对、响度和电磁音核查，输出 `A0A1_套号-部分号.mp3` 和核对记录 |
| `tools/split_sets.py` | 把学生版 PDF 按套拆开 |
| `qa/check_layout.py` | 版面检查 |
| `qa/check_final.py` | 成品录音逐句复核：按核对记录从合成缓存排出时间表，在成品 MP3 里切出每一句再识别 |

## 重新生成

Word：需要 Node.js 和 `npm install docx@9.5.1`。PDF 用 LibreOffice 26.8 转（用 FONTCONFIG_FILE 指向能找到苹方的字体配置）。录音在 `setup_mac.sh` 装好的环境里运行（另需 Parakeet 识别模型；男2、女2、女3 的参考录音用 `../A2教程/voices/`）：

```bash
python A0-A1听力练习/tools/check_sets.py
python A0-A1听力练习/tools/export_json.py
node A0-A1听力练习/build_listening.js student A0-A1听力练习/out/西班牙语A0-A1听力练习_学生版.docx
node A0-A1听力练习/build_listening.js teacher A0-A1听力练习/out/西班牙语A0-A1听力练习_教师版.docx
soffice --headless --convert-to pdf --outdir A0-A1听力练习/out A0-A1听力练习/out/*.docx
python A0-A1听力练习/tools/make_tracks.py . A0-A1听力练习/audio_out 识别模型目录 1 2 3 4 5 6 7 8 9 10
```
