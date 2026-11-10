# 每日一读（单页朗读视频）

一种新的视频形式：竖版的一页“阅读卡”，整段配西语朗读。2026-11-11 按用户给的参考视频的**形式**试做了第 01 篇样片；文章、插图、版面细节都是原创，没有用参考视频里的任何内容。

## 形式

- 画面 1080×1512（5:7 竖版），24 帧/秒。一页上依次是：
  - 标题栏：西语标题 | 中文标题，右边是栏目语“每日一读 积少成多”，下面一条粗线；
  - 水彩风插图，左上角写着西语标题；
  - 右栏“重点词汇”15 条（西语原形＋中文）；
  - 西语短文两段（两端对齐、首行缩进）；
  - 中文译文两段。
- 朗读：西语，先读标题，再逐句读，句间停顿 1.0 秒，全长约 1 分钟。
- 样片出了两个版本，**用户 2026-11-11 选定逐句高亮版**，以后的篇目以它为成品：
  - **逐句高亮版**（选定）：正在读的那句西语和它的译文标浅黄，读标题时标题栏标黄；
  - 静态版：整段一张图，和参考形式一样。程序仍会顺带生成，留作备用，不作为成品。

## 第 01 篇样片：Mi pequeño huerto（我的小菜园）

- 级别 A2—B1，10 句、146 词（不含标题），62.8 秒。
- 语法：现在时、简单过去时、过去未完成时、现在完成时。
- 朗读音色 `qwen3_M1F5_25`（原速）。
- 视频在 Release `daily-reading`：
  - `daily_01_Mi_pequeno_huerto_highlight.mp4`（逐句高亮版，选定的成品）
  - `daily_01_Mi_pequeno_huerto.mp4`（静态版，备用）

| 文件 | 内容 |
|---|---|
| `article_01.json` | 文章：标题、栏目语、15 个重点词汇、两段原文和逐句译文、不停顿的逗号（列举） |
| `illust_01.svg` | 插图（阳台小菜园，手写 SVG，水彩纸纹用 SVG 滤镜做，没有外部素材） |
| `tools/make_daily_audio.py` | 朗读：调用 `西班牙语/tools/make_audio.py` 的整条处理链，不改工具包里的文件 |
| `tools/render_page.py` | 排版：用 Playwright 截出静态页和逐句高亮页，写出 `layout.json` |
| `tools/make_daily_video.py` | 合成两个 MP4：高亮版按每句的起止时间换图，每段的帧数按累计时间取整 |
| `tools/qa_daily.py` | 成品核查，见下 |
| `out/daily_01.mp3`、`out/daily_01_timings.json` | 朗读和每句的起止时间、响度报告 |
| `out/page_01/page.html`、`page_static.png`、`layout.json` | 排好的页面、静态页截图、各区块位置和词间距测量 |
| `out/daily_01_Mi_pequeno_huerto_highlight.plan.json` | 高亮版每段显示哪张图、从第几帧到第几帧 |
| `核查/qa_01.txt` | 成品核查的完整输出（47 项全部通过） |

## 怎么做一篇

在工具包根目录运行（环境同 `setup_mac.sh`；Playwright 要设 `PLAYWRIGHT_BROWSERS_PATH`）：

```bash
python 每日一读/tools/make_daily_audio.py 每日一读/article_01.json 每日一读/out
python 每日一读/tools/render_page.py 每日一读/article_01.json 每日一读/illust_01.svg 每日一读/out/page_01 每日一读/out/daily_01_timings.json
python 每日一读/tools/make_daily_video.py 每日一读/out/page_01 每日一读/out/daily_01_timings.json 每日一读/out/daily_01.mp3 每日一读/out/daily_01_Mi_pequeno_huerto.mp4 每日一读/out/daily_01_Mi_pequeno_huerto_highlight.mp4
python 每日一读/tools/qa_daily.py 每日一读/article_01.json 每日一读/out 每日一读/out/daily_01_Mi_pequeno_huerto.mp4 每日一读/out/daily_01_Mi_pequeno_huerto_highlight.mp4 <Parakeet 模型目录>
```

- 第一步：合成结果按句子文字缓存，改了哪句只重新合成哪句。
- 第二步：只截静态页的话，省掉最后的时间表参数。

## 核查（`tools/qa_daily.py`）

1. **规格**：H.264 1080×1512、24 帧/秒、yuv420p，AAC 48 kHz；视频和音频时长相差不超过 1 帧。
2. **声音**：
   - 两个版本的音轨逐样本相同；
   - 整体响度 −16±0.7 LUFS，峰值 ≤ −1 dBFS；
   - 合成时工具包的响度四项、电磁音两项全部通过；
   - 逐句切出用 Parakeet 识别，和朗读原文逐词比对，11 句（含标题）都必须 0 处出入。
3. **画面**：
   - 高亮版每一段取中间一帧，和全部 12 张源图逐对比较：只看应显示的那张和另一张不同的像素，这一帧必须明显更接近应显示的那张；
   - 每句从开口到读完都高亮这一句；
   - 静态版取 6 个时间点比对。
4. **版面**：页面不滚动、没有文字被截断，底部留白 ≥ 40 px，各区块互不重叠，西语两端对齐的最大词间空白 ≤ 8 px。
5. **内容**：
   - 15 个词汇都能在正文里找到（原形或变位）；
   - 中文没有半角标点；
   - 朗读文字＝标题＋正文，逐句一致。

## 做的过程中改过的地方

- **句间停顿**：参考视频约 1.3 秒。试了 1.3、1.2、1.1 秒，工具包的 3 秒短时响度波动分别是 1.34、1.24、1.13 LU，超过上限 1.0 LU。原因是窗口里静音占比变大，朗读本身句间偏差只有 0.44 LU。不改核查标准，取能通过的 1.0 秒（0.95 LU）。
- **第 6 句**：原来是 Cuidar el huerto me enseña…，识别核对时 huerto me 四种切法都认成 huerme。固定种子重合成结果不变，所以改成 Cuidar el huerto también me enseña…，译文同步改为“也教会我”。
- **西语排版**：13 px 时第二段有两行词间空白 11–12 px。试了 7 种字号 × 7 种字距，改为 13.1 px、字距 −0.05 px，最大 7 px。
- **独立审校**：西语没有发现错误。译文按审校意见改了两处，更贴近原文：
  - “让我学会了耐心”→“教会我要有耐心”（原文 me enseña）；
  - “从不用化学药剂”→“不用化学药剂”（原文 no uso）。
