# HSK1 中文阅读视频

把《HSK 1级中文阅读教材 · 第一册：我的中文生活》（面向西班牙语母语的中文初学者，50 篇）做成逐句精读视频，版式和时间轴沿用西班牙语分级阅读：逐句朗读、汉字上方逐字注拼音、重点词汇加粗编号并在右侧词汇栏给出拼音和西语释义、原文下面是西语翻译。成品视频在 Release [`hsk1-reading`](../../../releases/tag/hsk1-reading)。

50 篇全部做完（2026-10-21）。用户看过第 01 篇试做后要求“速度稍微慢一些”，语速从 0.85 倍改为 0.75 倍。

## 文件

| 文件 | 作用 |
| --- | --- |
| `原始资料/HSK1_中文阅读教材_第01-50篇.docx` | 用户发来的 Word 原件 |
| `文章/hsk1_XX.json` | 每篇的数据：zh 课文、py 拼音（照原件）、ruby 逐字注音、w 重点词汇（照原件词汇表，没有词条的句子补了 1–2 个 HSK1 词，source=supplement）、es 逐句西语翻译（补写）、title_ruby 标题注音、_说明 这篇的特别处理 |
| `tools/prep.py` | 从 Word 原件生成文章 JSON 骨架（逐字注音按原件拼音对齐；西语翻译和补充词条要人工补） |
| `tools/make_audio.py` | 合成朗读：Qwen3-TTS 克隆 `教学视频/第一册第1课/build/ref_zh.wav`（中文女声），0.75 倍速（个别篇电磁音核查不过时用 0.73–0.76 倍，听不出差别）；每段用 SenseVoice 识别核对（比带声调拼音），有出入换种子重合成；成品音频每句再识别一遍；响度、电磁音核查同西语 |
| `tools/refresh_srt.py` | 合成之后改过西语翻译时，按文章 JSON 重写字幕 SRT（不重新合成），并核对时间轴里的原文和 JSON 一致 |
| `tools/make_video.py` | 生成 4K 视频（Chromium 截图，ruby 注音），核查分辨率、帧率、声画等长、停顿、响度 |
| `tools/check_json.py` | 检查文章 JSON（翻译、注音、词条位置、拼音大小写） |
| `补写规范.md`、`审校规范.md` | 补写西语翻译和补充词条、独立审校时的规则 |
| `audio/` | 朗读 MP3、字幕 SRT、时间轴和识别核对结果 |

## 重新生成

在 `setup_mac.sh` 装好的环境里（另外要 `pip install pypinyin`，以及 [SenseVoice](https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-2024-07-17.tar.bz2) 识别模型），在仓库根目录：

```bash
D=中文阅读
python $D/tools/prep.py $D/原始资料/HSK1_中文阅读教材_第01-50篇.docx $D/文章 1      # 只在新做一篇时运行，会覆盖这一篇的 JSON
python $D/tools/make_audio.py . $D/文章/hsk1_01.json $D/audio SenseVoice模型目录
python $D/tools/refresh_srt.py $D/文章 $D/audio          # 只在合成以后又改了西语翻译时需要
python $D/tools/make_video.py . $D/文章/hsk1_01.json $D/audio $D/最终视频
```

`make_video.py` 用 Chromium（Playwright），要在普通终端里运行。

## 对原件做的处理

- 第 32 篇第 4 句原件拼音 zai 漏标声调，改为 zài。
- 第 41 篇词汇表的「家人」只在标题“我的家人”里出现：列在第 1 句词汇栏的最后，标 T（título）。
- 第 45 篇词汇表的「听懂」在课文里写作「听得懂」：按课文写法标注，释义 poder entender (al escuchar)。
- 原件词汇表里互相重叠的词条（如 星期／星期一、钱／多少钱、瓶／两瓶）挪到别的句子或调整，见各篇 _说明。
- 原件拼音句中大写的普通词（引号里的“Míngtiān jiàn!”、Hànzì）在逐字注音里按普通词小写；专有名词（中国、中文、北京、人名、英语）保留大写。
- 西语翻译用西班牙的标准西语（对大家说话用 vosotros；中国的“二楼”对应西班牙的 primera planta）。
