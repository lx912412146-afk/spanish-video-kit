# 《现代西班牙语》第一册 第一课 ¿Quién es él? 教学视频

1920×1080，约 13 分钟。中文讲解（女声）＋西语示范（男女声），每个示范词句后留跟读时间。视频文件在 Release [`lesson-videos`](../../../releases/tag/lesson-videos)。

| 部分 | 内容 |
| --- | --- |
| 语音 | 元音 a e i o u；辅音 p t（不送气）、m n、l、s（在浊辅音前读浊音）；音节划分三条基本规则；重音规则；连读 |
| 课文 | 仿照第一课课文编写的对话（Paco、Ana、Pepe、Li Xin 介绍国籍），先完整听一遍，再逐句讲解、跟读 |
| 语法 | 阴阳性（-o / -a）、复数（加 -s，男女在一起用阳性复数）、ser 的 es / son、疑问句和否定句、¿ ¡ 和大小写 |
| 单词 | él、ella、ellos、quién、sí、no、amigo、cubano、chileno、panameño、chino |
| 练习 | 4 道小题，留思考时间后给答案 |

课次内容依据仓库里的 [`试卷/第一册分阶段模拟卷/课程大纲.md`](../../试卷/第一册分阶段模拟卷/课程大纲.md)。对话不是课本原文。

## 文件

| 文件 | 作用 |
| --- | --- |
| `lesson1.py` | 视频脚本：每一屏的版式、卡片和步骤（中文讲解、西语示范、跟读、练习） |
| `build.py` | `synth` 合成并逐句语音识别核对（西语 Parakeet-TDT，中文 SenseVoice 比带声调拼音），读错的换种子重合成；`render` 截画面；`video` 拼 MP4 |
| `template.html` | 画面模板（字体用工具包 `背景样式（6种）/fonts`） |
| `make_zh_ref.py` | 做中文讲解音色：让工具包女声说一段中文，挑识别全对的一版（`build/ref_zh.wav`）当克隆参考 |
| `build/识别核对.json` | 每句的识别结果和出入；`build/seed_overrides.json` 是换过种子的句子 |

## 重新生成

在仓库根目录、`setup_mac.sh` 装好的环境里运行。识别模型：西语用 [Parakeet-TDT 0.6B v3](https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8.tar.bz2)，中文用 [SenseVoice](https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/sherpa-onnx-sense-voice-zh-en-ja-ko-yue-2024-07-17.tar.bz2)；中文核对还要 `pip install pypinyin`。

```bash
D=教学视频/第一册第1课
.mac-env/bin/python $D/build.py synth . 西语识别模型目录 中文识别模型目录
.mac-env/bin/python $D/build.py render .
.mac-env/bin/python $D/build.py video
```

`render` 要用 Chromium，需要在普通终端里运行。改了 `lesson1.py` 里的讲解或例句后重跑：没改的句子直接用合成缓存。
