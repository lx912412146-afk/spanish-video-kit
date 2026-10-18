# spanish-video-kit

西班牙语逐句精读视频：把一篇西班牙语短文做成 4K 视频。视频有逐句朗读、中文翻译和生词栏，朗读用 Qwen3-TTS 克隆音色或 Supertonic 3。
程序、文章、音色设置都在这个仓库里，模型和成品视频放在 [Releases](../../releases)。换一台 Mac 也能马上接着用。

## 快速开始（macOS）

在“终端”里依次运行（不需要 git，也不需要管理员密码）：

```bash
curl -L https://github.com/lx912412146-afk/spanish-video-kit/archive/refs/heads/main.tar.gz | tar -xz
cd spanish-video-kit-main
zsh setup_mac.sh        # 装环境、下载并校验模型（约 10 GB 磁盘、20 分钟）
zsh run_mac.sh es02     # 生成朗读音频 + 4K 视频（Apple 芯片上约 5 分钟）
```

- 要用 `.tar.gz`：macOS 自带的 `unzip` 解压 GitHub 的 `.zip` 时，中文文件名会出错。
- 装了 git 也可以用 `git clone https://github.com/lx912412146-afk/spanish-video-kit.git`。

常用命令：

- 只看画面：`./run_mac.sh es02 --stills`（截图写到 `预览截图/es02/`）
- 换音色：`./run_mac.sh es02 qwen3_M1F5_25_slow`（音色名见 `西班牙语/tools/voices.json`）
- 音频已经有了，只重做视频：`./run_mac.sh es02 --video-only`
- 批量生成：`./batch_mac.sh`（分级阅读全部 50 篇，音色 `qwen3_M1F5_25_slow`）或 `./batch_mac.sh 音色名 a1_01 b2_03 …`
  - 已经核查通过的会跳过，中断后重新运行会接着做；结果记在 `西班牙语/最终视频/批量日志.txt`。

## 音色

| 名字 | 说明 |
|---|---|
| `qwen3_M1F5_25` | 推荐：Qwen3-TTS 1.7B 克隆音色，原速 |
| `qwen3_M1F5_25_slow` | 同一个音色，**0.8 倍速、音高 +1 半音**（分级阅读 50 篇用的）。语速和音高在合成之后处理：soxr 重采样升调，再用 ffmpeg `atempo` 放慢。句间停顿 0.8 秒、逗号停顿 0.28 秒不变 |
| `supertonic3_*` | Supertonic 3，快、轻量 |

Qwen3 每一段的原始合成都缓存在 `西班牙语/audio/_合成缓存/`（不进 git）。只改语速、音高、停顿、电平时，重跑不用重新合成，几秒钟就好。
要换速度或音高，复制一个音色，改 `tempo`（0.8 = 慢到 0.8 倍）和 `pitch_cents`（100 = 一个半音）就行。

## 新文章怎么加

1. 照 `西班牙语/文章/es02.json` 或分级阅读的 `a1_01.json` 写 `西班牙语/文章/<编号>.json`：
   - 每句要有 `es` 原文、`zh` 翻译，以及 3–5 个生词 `w`（`h` 词头、`pos` 词性、`zh` 释义、`surface` 句中写法）。
   - 生词的 `surface` 必须是句中的完整词，恰好出现一次，生词之间不能重叠。
2. 列举（A, B y C）里“不停顿”的逗号，写在文章自己的 `no_pause_commas` 里（也可以写在 `西班牙语/tools/逗号停顿.json`）。不停顿合并后超过 100 个字符的长段，照常停顿。
3. 原文不能有阿拉伯数字、引号和括号，数字要写成单词（dieciocho、las diez y media）。
4. 先检查：`python 西班牙语/tools/check_articles.py <编号> -v`（`-v` 会打印朗读分段，`|` 是停顿的地方）。
5. 生成：`./run_mac.sh <编号> [音色]`。生成后会自动核查 15 项：响度、电磁音、片头 1.5 秒、句间 0.8 秒、结尾 2 秒、4K、30 帧、声画一致等，任何一项不通过就不输出。

## 已做的文章

| 编号 | 标题 | 成品 |
|---|---|---|
| es01 | Mi pasión por los viajes 我对旅行的热爱 | 示例文章（原作者） |
| es02 | Mi vida diaria 我的日常生活 | Release `videos`；音频、字幕在 `西班牙语/audio/qwen3_M1F5_25/`，0.8 倍速版在 `qwen3_M1F5_25_slow/` |
| a1_01–c1_10 | 西班牙语分级阅读 A1–C1，每级 10 篇（来自《西班牙语A1-C1分级阅读文章集》） | 视频在 Release `graded-reading`；音频、字幕在 `西班牙语/audio/qwen3_M1F5_25_slow/` |

分级阅读 50 篇的中文翻译和生词栏是 2026-10-18 补写的。原文档只有西班牙语原文，每篇的特别判断写在各自 JSON 的 `_说明` 里。

<details><summary>A1 基础入门（10 篇）</summary>

| 编号 | 标题 | 中文 | 句数 · 生词 |
|---|---|---|---|
| a1_01 | Mi familia | 我的家庭 | 7 句 · 30 词 |
| a1_02 | Un día normal | 平常的一天 | 7 句 · 30 词 |
| a1_03 | Mi ciudad | 我的城市 | 7 句 · 32 词 |
| a1_04 | En el supermercado | 在超市 | 7 句 · 32 词 |
| a1_05 | Mi mejor amiga | 我最好的朋友 | 8 句 · 33 词 |
| a1_06 | Un fin de semana | 一个周末 | 7 句 · 31 词 |
| a1_07 | Mi habitación | 我的房间 | 7 句 · 32 词 |
| a1_08 | En el restaurante | 在餐厅 | 8 句 · 31 词 |
| a1_09 | El tiempo | 天气 | 6 句 · 29 词 |
| a1_10 | Aprender español | 学习西班牙语 | 7 句 · 32 词 |

</details>

<details><summary>A2 初级进阶（10 篇）</summary>

| 编号 | 标题 | 中文 | 句数 · 生词 |
|---|---|---|---|
| a2_01 | Mi primer trabajo | 我的第一份工作 | 6 句 · 29 词 |
| a2_02 | Una visita a Salamanca | 萨拉曼卡之行 | 7 句 · 31 词 |
| a2_03 | Una vida más saludable | 更健康的生活 | 7 句 · 32 词 |
| a2_04 | La compra por internet | 网上购物 | 7 句 · 31 词 |
| a2_05 | Una nueva compañera de piso | 新室友 | 7 句 · 32 词 |
| a2_06 | El transporte público | 公共交通 | 6 句 · 28 词 |
| a2_07 | Una celebración familiar | 一次家庭庆祝会 | 7 句 · 33 词 |
| a2_08 | Aprender de los errores | 从错误中学习 | 6 句 · 29 词 |
| a2_09 | Un día sin móvil | 没有手机的一天 | 7 句 · 34 词 |
| a2_10 | Una excursión a la montaña | 一次山间远足 | 8 句 · 35 词 |

</details>

<details><summary>B1 中级（10 篇）</summary>

| 编号 | 标题 | 中文 | 句数 · 生词 |
|---|---|---|---|
| b1_01 | La importancia de organizar el tiempo | 合理安排时间的重要性 | 5 句 · 21 词 |
| b1_02 | Vivir en otro país | 在国外生活 | 6 句 · 24 词 |
| b1_03 | El valor de las bibliotecas | 图书馆的价值 | 6 句 · 25 词 |
| b1_04 | Turismo responsable | 负责任的旅游 | 5 句 · 23 词 |
| b1_05 | La comida y la memoria | 食物与记忆 | 6 句 · 28 词 |
| b1_06 | Estudiar en grupo | 小组学习 | 5 句 · 22 词 |
| b1_07 | El comercio de barrio | 社区小商店 | 5 句 · 22 词 |
| b1_08 | La influencia de las redes sociales | 社交网络的影响 | 6 句 · 25 词 |
| b1_09 | Aprender durante toda la vida | 终身学习 | 6 句 · 24 词 |
| b1_10 | La ciudad y los espacios verdes | 城市与绿地 | 6 句 · 24 词 |

</details>

<details><summary>B2 中高级（10 篇）</summary>

| 编号 | 标题 | 中文 | 句数 · 生词 |
|---|---|---|---|
| b2_01 | La flexibilidad laboral: oportunidad y desafío | 弹性工作：机遇与挑战 | 5 句 · 22 词 |
| b2_02 | ¿Es suficiente con reciclar? | 只靠回收就够了吗？ | 6 句 · 25 词 |
| b2_03 | La vivienda en las ciudades | 城市住房 | 5 句 · 24 词 |
| b2_04 | La inteligencia artificial en la educación | 教育中的人工智能 | 5 句 · 24 词 |
| b2_05 | La cultura de la inmediatez | 即时文化 | 5 句 · 22 词 |
| b2_06 | La preservación del patrimonio | 文化遗产的保护 | 5 句 · 23 词 |
| b2_07 | La brecha digital | 数字鸿沟 | 5 句 · 23 词 |
| b2_08 | La importancia de escuchar | 倾听的重要性 | 5 句 · 23 词 |
| b2_09 | Consumir menos, elegir mejor | 少消费，选得更好 | 6 句 · 27 词 |
| b2_10 | El valor de los errores | 错误的价值 | 6 句 · 26 词 |

</details>

<details><summary>C1 高级（10 篇）</summary>

| 编号 | 标题 | 中文 | 句数 · 生词 |
|---|---|---|---|
| c1_01 | La atención como recurso escaso | 作为稀缺资源的注意力 | 6 句 · 27 词 |
| c1_02 | La paradoja de la conectividad | 互联互通的悖论 | 5 句 · 23 词 |
| c1_03 | La ciudad como espacio de negociación | 作为协商空间的城市 | 5 句 · 23 词 |
| c1_04 | El idioma y la identidad | 语言与身份认同 | 5 句 · 24 词 |
| c1_05 | El trabajo y el sentido de la vida | 工作与人生意义 | 5 句 · 23 词 |
| c1_06 | La memoria colectiva y sus silencios | 集体记忆及其沉默 | 5 句 · 22 词 |
| c1_07 | La sostenibilidad más allá del individuo | 超越个人层面的可持续性 | 5 句 · 24 词 |
| c1_08 | La confianza en la información | 对信息的信任 | 6 句 · 27 词 |
| c1_09 | La innovación y sus consecuencias imprevistas | 创新及其意外后果 | 5 句 · 23 词 |
| c1_10 | La paciencia como forma de resistencia | 作为抵抗方式的耐心 | 6 句 · 27 词 |

</details>

## Releases

| 标签 | 内容 |
|---|---|
| `es-kit-preview` | 原始工具包 `SPANISH-video-kit-preview.zip`、Qwen3-TTS 1.7B 模型分卷 `.001–.003`、`join_qwen3_parts.py`、`SHA256SUMS.txt` |
| `videos` | es02 的视频（MP4）、朗读、字幕和核查报告 |
| `graded-reading` | 分级阅读 50 篇的 4K 视频（`A1-01_….mp4` …）和全部核查报告 |

## 来源与改动

- 原始工具包：[AlienCodes/university-entrance-examination · es-kit-preview](https://github.com/AlienCodes/university-entrance-examination/releases/tag/es-kit-preview)（2026-10-15）。原版说明见 `使用说明.md`，模型和程序的版权归原作者，请遵守各自的许可。
- 在原版基础上的改动：
  - 2026-10-17：
    - `逗号停顿.json` 改为按文章编号登记（原版只适用于 es01，用在别的文章上会报错）。
    - `voices.json` 的路径改为相对工具包根目录，`"python": "self"` 表示用当前环境，换电脑不用改路径。
    - 新增 `setup_mac.sh`（一键安装）、`run_mac.sh`（一键生成）和文章 `es02`。
  - 2026-10-18：
    - `make_audio.py`：
      - 新增合成缓存。
      - 新增合成后的变速变调（`tempo`、`pitch_cents`）。
      - 慢速电平参数可按音色设置（`leveler_win`、`leveler_rng`）。
      - 文章 JSON 里可以写 `no_pause_commas`。
    - `make_video.py`：页眉可按文章设置（`header`）；分级阅读按“等级-篇号”命名；新增 `--print-name`。
    - 新增 `batch_mac.sh`（批量生成）、`check_articles.py`（文章检查）、音色 `qwen3_M1F5_25_slow`、分级阅读 50 篇。
