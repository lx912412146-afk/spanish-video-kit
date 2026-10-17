# spanish-video-kit

西班牙语逐句精读视频：模型与生成程序的存档仓库，用来存放和管理这套工具包的各个版本，以及后续相关操作。

## 来源

- 原始发布：[AlienCodes/university-entrance-examination · es-kit-preview](https://github.com/AlienCodes/university-entrance-examination/releases/tag/es-kit-preview)（2026-10-15）
- 本仓库的 [Releases](../../releases) 页面原样转存了全部文件，并用原始 `SHA256SUMS.txt` 核对过。
- 模型和程序的版权归原作者所有，使用前请遵守各自的许可条款。

## 版本

| 标签 | 说明 |
|---|---|
| `es-kit-preview` | 先行版：生成程序 + Supertonic 3 模型 + Qwen3-TTS 1.7B 模型分卷 |
| `es-kit` | 完整工具包（原作者测试通过后另发，待转存） |

## es-kit-preview 文件

| 文件 | 大小 | 内容 |
|---|---|---|
| `SPANISH-video-kit-preview.zip` | 181 MB | 生成程序（朗读音频、4K 视频、自动核查）、音色设置、Supertonic 3 模型、示例文章、Qwen3 克隆参考声音、6 种背景样式。解压后先看 `使用说明.md`。 |
| `qwen3-tts-1.7b-base.zip.001` / `.002` / `.003` | 1.99 GB / 1.99 GB / 560 MB | Qwen3-TTS 1.7B 模型分卷，合并后约 4.5 GB |
| `join_qwen3_parts.py` | 1 KB | 合并分卷的脚本 |
| `SHA256SUMS.txt` | 1 KB | 所有文件以及合并后 `qwen3-tts-1.7b-base.zip` 的 SHA256 |

## 使用方法

1. 从 Releases 下载全部文件，放到同一个文件夹。
2. 合并模型分卷，任选一种：
   - `python join_qwen3_parts.py`
   - macOS / Linux：`cat qwen3-tts-1.7b-base.zip.0* > qwen3-tts-1.7b-base.zip`
   - Windows：`copy /b qwen3-tts-1.7b-base.zip.001+qwen3-tts-1.7b-base.zip.002+qwen3-tts-1.7b-base.zip.003 qwen3-tts-1.7b-base.zip`
3. 核对校验值：macOS / Linux 用 `shasum -a 256 -c SHA256SUMS.txt`。
4. 解压 `SPANISH-video-kit-preview.zip`，再把 `qwen3-tts-1.7b-base.zip` 解压到 `西班牙语/models/`。
