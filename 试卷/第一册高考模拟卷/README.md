# 西班牙语高考模拟试卷（《现代西班牙语》第一册）

按 2024 年起的高考西班牙语新课标卷题型出的原创模拟卷，满分 150 分，考试时间 120 分钟。范围是《现代西班牙语》第一册老版（董燕生、刘建，共 24 课）。

| 文件 | 内容 |
|---|---|
| `试卷.md` | 全卷原文：命题说明、注意事项、四部分试题、答案与评分标准、听力原文、知识点覆盖表 |
| Release [`exam-book1`](../../releases/tag/exam-book1) | `exam_book1_student.pdf`（学生版，9 页）、`exam_book1_teacher.pdf`（教师版，含答案和听力原文）、`listening_full.mp3`（整套听力，约 10 分钟，按真题的读题、作答停顿）、`texto_1.mp3` … `texto_9.mp3`（每段只播一遍，供练习） |
| `make_listening.py` | 从 `试卷.md` 的“听力原文”生成听力音频。男声 `qwen3_M1F5_25`；女声用 Qwen3-TTS 克隆 Supertonic 3 F1（参考录音 `听力/ref_female_F1.wav`） |
| `asr_check.py` | 用语音识别（Parakeet-TDT 0.6B v3）把每句录音转回文字，和录音稿逐词比对，结果在 `听力/听力_识别核对.json` |
| `asr_retry.py` | 识别有错词的句子换随机种子重新合成，挑识别最准的一版；挑中的种子记在 `听力/seed_overrides.json`，`make_listening.py` 照着用 |
| `build_pdf.py` | 把 `试卷.md` 排成 A4 的学生版、教师版 PDF |

## 重新生成

在仓库根目录、`setup_mac.sh` 装好的环境里运行。PDF 要用 Chromium，需要在普通终端里运行：

```bash
D=试卷/第一册高考模拟卷
.mac-env/bin/python $D/make_listening.py . $D/试卷.md $D/听力
.mac-env/bin/python $D/build_pdf.py $D/试卷.md $D/pdf
```

核对听力（`ASR` 是识别模型目录）；有句子读错就换种子重合成，再生成一遍、复核：

```bash
.mac-env/bin/python $D/asr_check.py . $D/试卷.md $D/听力 $ASR
.mac-env/bin/python $D/asr_retry.py . $D/试卷.md $D/听力 $ASR
.mac-env/bin/python $D/make_listening.py . $D/试卷.md $D/听力
.mac-env/bin/python $D/asr_check.py . $D/试卷.md $D/听力 $ASR
```

`asr_check.py` 要先下载识别模型 [sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8](https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8.tar.bz2)（464 MB），解压到一个目录，作为第 4 个参数传入（`asr_retry.py` 同）。

改了 `试卷.md` 的听力原文后重跑 `make_listening.py`：没改的句子直接用合成缓存，只合成改动的句子。
