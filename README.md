# spanish-video-kit

西班牙语逐句精读视频：把一篇西班牙语短文做成 4K 视频。视频有逐句朗读、中文翻译和生词栏，朗读用 Qwen3-TTS 克隆音色或 Supertonic 3。
程序、文章、音色设置都在这个仓库里，模型和成品视频放在 [Releases](../../releases)。换一台 Mac 也能马上接着用。

## 快速开始（macOS）

```bash
git clone https://github.com/lx912412146-afk/spanish-video-kit.git
cd spanish-video-kit
./setup_mac.sh          # 装环境、下载并校验模型（约 10 GB 磁盘，不需要管理员密码）
./run_mac.sh es02       # 生成朗读音频 + 4K 视频
```

- 只看画面：`./run_mac.sh es02 --stills`（截图写到 `预览截图/es02/`）
- 换音色：`./run_mac.sh es02 supertonic3_M1F5_25`（音色名见 `西班牙语/tools/voices.json`）
- 音频已经有了，只重做视频：`./run_mac.sh es02 --video-only`

## 新文章怎么加

1. 照 `西班牙语/文章/es02.json` 的格式写 `西班牙语/文章/<编号>.json`。每句要有 `es` 原文、`zh` 翻译，以及 3–5 个生词 `w`。生词的 `surface` 必须在句子里恰好出现一次，生词之间不能重叠。
2. 句子里有列举的逗号（A, B y C）时，把“不停顿”的逗号登记到 `西班牙语/tools/逗号停顿.json` 的 `"<编号>"` 下。
3. 原文不能有阿拉伯数字，数字要写成单词（dieciocho、las diez y media）。
4. 运行 `./run_mac.sh <编号>`。生成后会自动核查：响度、电磁音、片头 1.5 秒、句间 0.8 秒、结尾 2 秒、4K、30 帧、声画一致。任何一项不通过就不输出。

## 已做的文章

| 编号 | 标题 | 成品 |
|---|---|---|
| es01 | Mi pasión por los viajes 我对旅行的热爱 | 示例文章（原作者） |
| es02 | Mi vida diaria 我的日常生活 | 视频在 Release `videos`；音频、字幕在 `西班牙语/audio/qwen3_M1F5_25/` |

## Releases

| 标签 | 内容 |
|---|---|
| `es-kit-preview` | 原始工具包 `SPANISH-video-kit-preview.zip`、Qwen3-TTS 1.7B 模型分卷 `.001–.003`、`join_qwen3_parts.py`、`SHA256SUMS.txt` |
| `videos` | 生成好的视频（MP4）和核查报告 |

## 来源与改动

- 原始工具包：[AlienCodes/university-entrance-examination · es-kit-preview](https://github.com/AlienCodes/university-entrance-examination/releases/tag/es-kit-preview)（2026-10-15）。原版说明见 `使用说明.md`，模型和程序的版权归原作者，请遵守各自的许可。
- 在原版基础上的改动（2026-10-17）：
  - `逗号停顿.json` 改为按文章编号登记（原版只适用于 es01，用在别的文章上会报错）。
  - `voices.json` 的路径改为相对工具包根目录，`"python": "self"` 表示用当前环境，换电脑不用改路径。
  - 新增 `setup_mac.sh`（一键安装）、`run_mac.sh`（一键生成）和文章 `es02`。
