"""README 里分级阅读第二批的说明（表格以外的部分）：python readme_edit.py <KIT>/README.md"""
import sys
from pathlib import Path
p = Path(sys.argv[1]); t = p.read_text('utf-8')
R = [
 ("| a1_11 | Mi mascota 我的宠物（分级阅读第二批的试看版，原创短文，12 句 129 词，60 秒，0.8 倍速） | 视频在 Release `graded-reading-2`；音频、字幕在 `西班牙语/audio/qwen3_M1F5_25_slow/` |",
  "| a1_11–c1_20 | 西班牙语分级阅读第二批 A1–C1，每级 10 篇（原创短文，每篇约 1 分钟；A1—A2 0.8 倍速，B1—C1 原速） | 视频在 Release `graded-reading-2`；音频、字幕在 `西班牙语/audio/qwen3_M1F5_25_slow/`（A1—A2）和 `西班牙语/audio/qwen3_M1F5_25/`（B1—C1） |"),
 ("编号接着第一批（`a1_11` 起），版式和第一批相同。0.8 倍速下 A1 约 125 词、12 句正好 1 分钟。每篇除了工具包的 15 项核查，还用 `asr_check_reading.py` 逐句识别核对。先做了 A1-11 给用户试看，其余的等用户看过再做。",
  "编号接着第一批（`a1_11`—`c1_20`），版式和第一批相同。A1—C1 每级 10 篇，共 50 篇，每篇 55–65 秒。先做了 A1-11 给用户试看，用户认可后做了其余 49 篇。"
  "每篇除了工具包的 15 项核查，还用 `asr_check_reading.py` 逐句识别核对（识别和原文对不上的句子改写措辞重新合成，直到逐词一致），用 `check_wraps.py` 检查画面折行。"
  "编写要求、审读意见、生产脚本和日志在 `记录/分级阅读第二批/`。"),
 ("6. 逐句识别核对（可选，需要 Parakeet 识别模型 `sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8`）：`python 西班牙语/tools/asr_check_reading.py . <识别模型目录> <音色> <编号>`。从成品 MP3 按 `timings.json` 切出每句识别，和朗读文本逐词比，比对规则和 `B1-B2听力练习/tools/make_tracks.py` 相同。\n",
  "6. 逐句识别核对（可选，需要 Parakeet 识别模型 `sherpa-onnx-nemo-parakeet-tdt-0.6b-v3-int8`）：`python 西班牙语/tools/asr_check_reading.py . <识别模型目录> <音色> <编号>`。从成品 MP3 按 `timings.json` 切出每句识别，和朗读文本逐词比，比对规则和 `B1-B2听力练习/tools/make_tracks.py` 相同。\n"
  "7. 检查画面折行（可选）：`python 西班牙语/tools/check_wraps.py <编号>…`。用生成视频的同一套版式在浏览器里排出每一句，量出每行的字：生词释义在词中间断开、译文最后一行只剩一个字、一页放不下，都会列出来，要改文章或措辞；原文最后一行只有一个词、译文最后一行两个字只是提示。有要处理的地方时退出码是 1。\n"),
 ("| `prep_release.py 输出文件夹 [说明文件]` | 把 50 个视频复制成英文文件名，合并核查报告，写好 Release 说明 |\n",
  "| `prep_release.py 输出文件夹 [说明文件]` | 把 50 个视频复制成英文文件名，合并核查报告，写好 Release 说明 |\n"
  "| `check_wraps.py 编号…` | 检查画面折行：生词释义在词中间断开、译文最后一行只剩一个字、一页放不下 |\n"),
 ("  - `日志/`：合成缓存填充、截图排版检查、批量生成的日志，本机路径已替换成 `<KIT>` 等占位符。\n",
  "  - `日志/`：合成缓存填充、截图排版检查、批量生成的日志，本机路径已替换成 `<KIT>` 等占位符。\n"
  "  - `分级阅读第二批/`：第二批 50 篇的编写要求、审读要求、选题表、审读意见，写作和生产用的小工具和脚本，每篇的音频、视频、识别核对日志和折行检查结果（本机路径已替换成占位符），说明见其中的 `README.md`。\n"),
 ("| `graded-reading-2` | 分级阅读第二批的 4K 视频（目前是试看版 `A1-11_Mi_mascota.mp4`）、核查报告 `graded-reading-2_checks.json`、`graded-reading-2-SHA256SUMS.txt` |",
  "| `graded-reading-2` | 分级阅读第二批 50 篇的 4K 视频（`A1-11_Mi_mascota.mp4` … `C1-20_….mp4`）、核查报告 `graded-reading-2_checks.json`、`graded-reading-2-SHA256SUMS.txt` |"),
]
for a, b in R:
    n = t.count(a)
    if n != 1:
        sys.exit(f'出现 {n} 次：{a[:60]}')
    t = t.replace(a, b)
tail = "    - 新增 `B1-B2听力练习/`（10 套 B1—B2 听力练习的原文、排版和录音程序）和 Release `b1b2-listening`。\n"
assert t.endswith(tail), repr(t[-200:])
t += ("  - 2026-11-10：\n"
      "    - 分级阅读第二批 50 篇（`a1_11`—`c1_20`，原创短文，每篇约 1 分钟；A1—A2 0.8 倍速，B1—C1 原速）和 Release `graded-reading-2`；新增 `记录/分级阅读第二批/`。\n"
      "    - `make_video.py` 的折行：生词释义一行放不下时整段换到下一行（不在词中间断开），译文最后一行不只剩一个字；字号和行数不变。第一批的视频是改之前做的，没有重新生成。\n"
      "    - 新增 `check_wraps.py`（画面折行检查）；`voices.json` 里 `qwen3_M1F5_25_slow` 的 `leveler_ladder` 末尾加了两档（0.4 秒 ±10 dB、0.3 秒 ±12 dB），只有前面各档都不过才会用到，已经通过的篇目结果不变。\n")
p.write_text(t, 'utf-8')
print('README OK')
