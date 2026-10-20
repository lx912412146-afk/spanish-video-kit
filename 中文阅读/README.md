# HSK1 中文阅读视频

把《HSK 1级中文阅读教材 · 第一册：我的中文生活》（面向西班牙语母语的中文初学者，50 篇）做成逐句精读视频，版式和时间轴沿用西班牙语分级阅读：逐句朗读、汉字上方逐字注拼音、重点词汇加粗编号并在右侧词汇栏给出拼音和西语释义、原文下面是西语翻译。成品视频在 Release [`hsk1-reading`](../../../releases/tag/hsk1-reading)。

目前做了第 01 篇（试做，等确认版式和语速后再做其余各篇）。

## 文件

| 文件 | 作用 |
| --- | --- |
| `原始资料/HSK1_中文阅读教材_第01-50篇.docx` | 用户发来的 Word 原件 |
| `文章/hsk1_XX.json` | 每篇的数据：zh 课文、py 拼音（照原件）、ruby 逐字注音、w 重点词汇（照原件词汇表）、es 逐句西语翻译（补写）、title_ruby 标题注音 |
| `tools/prep.py` | 从 Word 原件生成文章 JSON 骨架（逐字注音按原件拼音对齐；西语翻译和补充词条要人工补） |
| `tools/make_audio.py` | 合成朗读：Qwen3-TTS 克隆 `教学视频/第一册第1课/build/ref_zh.wav`（中文女声），0.85 倍速；每段用 SenseVoice 识别核对（比带声调拼音），有出入换种子重合成；响度、电磁音核查同西语 |
| `tools/make_video.py` | 生成 4K 视频（Chromium 截图，ruby 注音），核查分辨率、帧率、声画等长、停顿、响度 |
| `audio/` | 朗读 MP3、字幕 SRT、时间轴和识别核对结果 |

## 重新生成

在 `setup_mac.sh` 装好的环境里（另外要 `pip install pypinyin`，以及 [SenseVoice](https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-2024-07-17.tar.bz2) 识别模型），在仓库根目录：

```bash
D=中文阅读
python $D/tools/prep.py $D/原始资料/HSK1_中文阅读教材_第01-50篇.docx $D/文章 1      # 只在新做一篇时运行，会覆盖这一篇的 JSON
python $D/tools/make_audio.py . $D/文章/hsk1_01.json $D/audio SenseVoice模型目录
python $D/tools/make_video.py . $D/文章/hsk1_01.json $D/audio $D/最终视频
```

`make_video.py` 用 Chromium（Playwright），要在普通终端里运行。

## 原件里要注意的地方

- 第 41 篇的词汇表里有“家人”，课文里没有这个词，做到那一篇时要先确认。
- 原件拼音里“明天”“汉字”在句中也有大写的地方，生成逐字注音时会被当作专有名词保留大写，做到相关篇目时要检查。
