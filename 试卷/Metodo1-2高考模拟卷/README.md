# 西班牙语高考模拟试卷（《Método de español》第 1–2 册）

按高考西班牙语新课标卷题型出的原创模拟卷：满分 150 分，考试时间 120 分钟，听力、阅读、语言运用、写作四部分，题型、题量和分值与教育部教育考试院公布的 2024 年适应性测试样卷一致；听力按 2026 年起的规定，第一节每段录音也播放两遍。范围是《Método de español》（Anaya ELE）第 1、2 册，按 Método 1 对应 A1、Método 2 对应 A2 理解。题目、短文、对话和范文全部为原创。

出版社没有公开这两册的完整单元目录（官网只有 Método 2 第 2 单元和第 7 单元的样章），所以考查范围按这套教材所依据的欧洲语言共同参考框架和塞万提斯学院《课程计划》（PCIC）的 A1、A2 级来定，并对照已经核实的 Método 2 第 2、7 单元；`试卷.md` 的“考试说明”和“知识点覆盖表”写明了每项内容对应的题目。

## 文件

| 文件 | 内容 |
|---|---|
| `试卷.md` | 全卷原文：考试说明、注意事项、四部分试题、参考答案与评分标准（每题的依据或考点、写作评分档次、两篇范文）、听力原文（含录音结构）、知识点覆盖表和来源 |
| Release [`exam-metodo12`](../../../../releases/tag/exam-metodo12) | 试卷 `exam-metodo12-paper.docx/.pdf`（8 页）、答题卡 `exam-metodo12-answer-sheet.docx/.pdf`（2 页）、答案与评分说明 `exam-metodo12-key.docx/.pdf`（9 页，含听力原文）；整套听力 `exam-metodo12-listening.mp3`（16 分 19 秒，按高考格式：试音、中文指令语、读题时间、每段播两遍、作答停顿，最后提示用两分钟转涂答题卡——这两分钟不在录音里）、每段只放一遍的 `exam-metodo12-texto_1.mp3` … `texto_9.mp3`（讲评用）；核对报告 `exam-metodo12-asr-check.json`、`exam-metodo12-final-check.json`；`exam-metodo12-SHA256SUMS.txt` |
| `tools/check_paper.py` | 格式自检：各部分顺序、题号和选项、完形空格和选项表、语法填空提示词的位置、答案表和依据表一致、答案分布、听力原文的格式、范文词数和标注一致 |
| `tools/make_listening.py` | 从“听力原文”生成整套听力：合成、逐句语音识别核对（西语 Parakeet-TDT 0.6B v3，中文指令语 SenseVoice）、拼接、响度和电磁音核查（`build`）；再从成品 MP3 里把每一句切出来重新识别（`final`） |
| `tools/export_json.py`、`tools/build_exam.js` | 把 `试卷.md` 排成 A4 的试卷、答题卡、答案与评分说明（docx），再用 LibreOffice 转 PDF |
| `tools/check_pdf_text.py` | 排版完整性：`试卷.md` 里的每一段文字（题干、选项、短文、表格、列表）都要在 PDF 里找得到 |
| `听力/` | `听力_时间轴.json`（每句、每段在整套录音里的起止时间）、`听力_识别核对.json`（每句的识别结果和比对）、`听力_录音核查.json`（响度、峰值、电磁音）、`听力_成品复核.json`（成品逐句复核） |

## 听力录音

- 西语对话用本仓库的六个 Qwen3 声音（男声两个、女声四个，和 A1、A2、B1 教程、B1—B2 听力练习相同），每段对话里男女声音不同，第 8 段是独白；语速 0.95 倍。
- 中文指令语是女声（Qwen3 克隆第一册第 1 课教学视频的中文讲解声音），0.92 倍。
- 每一句都用语音识别转回文字，和原文逐词（中文逐字）核对：西语 116 句、中文 25 句全部一致；成品 MP3 里的每一句（对话两遍都算，共 258 处）又切出来重新识别了一遍，也全部对上。中文核对只放过一处同音字：结束语里的“转涂”，SenseVoice 不认这个词，读对了（tú）会写成同音的“转图”，算作一致；读成“转读”（dú）仍算错（见 `make_listening.py` 的 `ZH_SAME`）。整套录音 −16 LUFS。

## 重新生成

在仓库根目录、`setup_mac.sh` 装好的环境里运行。`ASR` 是 [sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8](https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8.tar.bz2) 的解压目录，`ASR_ZH` 是 [sherpa-onnx-sense-voice-zh-en-ja-ko-yue-int8-2024-07-17](https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-int8-2024-07-17.tar.bz2) 的解压目录：

```bash
D=试卷/Metodo1-2高考模拟卷
.mac-env/bin/python $D/tools/check_paper.py $D/试卷.md
.mac-env/bin/python $D/tools/make_listening.py build . $D/试卷.md $D/听力 $ASR $ASR_ZH
.mac-env/bin/python $D/tools/make_listening.py final . $D/试卷.md $D/听力 $ASR $ASR_ZH
```

改了听力原文后重跑 `build`：没改的句子直接用合成缓存（`听力/_合成缓存/`，不在仓库里）。

排版要 Node.js 的 `docx`（9.5.1）和 `jszip`，PDF 用 LibreOffice（字体：Times New Roman、宋体 Songti SC、黑体 Heiti SC）：

```bash
python3 $D/tools/export_json.py $D/试卷.md out/paper.json $D/听力/听力_时间轴.json
node $D/tools/build_exam.js out/paper.json out
soffice --headless --convert-to pdf --outdir out out/试卷.docx out/答题卡.docx out/答案与评分说明.docx
```
