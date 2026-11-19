# 《现代西班牙语》第三册（老版）分课单词表

接着[第一册](../../第一册/单词表/)、[第二册单词表](../../第二册/单词表/)，按课整理第三册 18 课课件里新出现的西语词：单词、词性、中文释义，各课第一次出现的动词形式和原形，每个新动词的完整变位表。共 671 个词条（其中 43 条是前面学过的词在这一课有了新意思，单列一条），200 个新动词的变位表，580 个动词形式；书后另有前两册 268 个动词的虚拟式过去未完成时速查表。

Release [`book3-vocab`](https://github.com/lx912412146-afk/spanish-video-kit/releases/tag/book3-vocab)：`book3-vocab.docx`、`book3-vocab.pdf`（A4，204 页，可以直接打印）、`book3-vocab-words.csv`（单词表，每个词条一行）、`book3-vocab-verbs.csv`（动词变位表，每个动词 6 行，后面附前两册动词的虚拟式过去未完成时）；CSV 是 UTF-8 带 BOM，Excel 直接打开。

- 依据是本仓库 [`课件/第三册/content/`](../content/) 里 18 课的课件内容（生词、课文、语法要点和例句、常用表达、练习、小结、作业）。**不是课本书后词汇表或生词表的翻印**：词条和释义按课件里的用法重新整理，和课本生词表的选词、释义可能不完全一样。
- 接着前两册排：第一、二册课件里学过的词不再算新词，前两册见过的动词形式也不再列。第一册只在语音练习里出现过、第二册也没学的词（aire、éxito……），第三册用到时算新词并注明；前两册学过、第三册有了新意思的词（importar“进口”、despertar“引起（兴趣等）”）在出现新意思的课单列一条，备注写明前两册学过的意思；第三册前面学过、后面又有了新意思的也一样。
- 每课：生词（按字母顺序；课件生词表里的词加粗）→ 生词表里前面学过的词（附本课课件的释义和第一次出现的册、课）→ 生词表里的短语 → 本课第一次出现的动词形式（→ 原形和形式说明，如虚拟式过去未完成时的 -ra、-se 形式、否定命令式、助动词 haber、过去分词作形容词）→ 已学词的新形式 → 新动词变位表 → 常用表达。书后有词汇总索引、动词变位表索引（带页码）和前两册动词的虚拟式过去未完成时。
- 变位表每个动词两张：上表是陈述式现在时、简单过去时、过去未完成时、将来未完成时、简单条件式，下表是虚拟式现在时、虚拟式过去未完成时（-ra 形式、-se 形式）、肯定命令式、否定命令式；标题行右边是副动词和过去分词。和规则变位不一样的形式标红。第三册新学的复合时态（虚拟式过去完成时、复合条件式、将来完成时、虚拟式现在完成时、复合原形动词）都是 haber + 过去分词，使用说明里有一张 haber 的变位表，不再逐个动词列。
- 拼写按老版课本：sólo、éste / ése / aquél 带重音。变位表里 reír 的 rio、riais 按现行正字法不带重音（老版课本写 rió、riáis），表下有注。
- 整理完以后对着课件逐条审读了两轮，每轮由两人分课审读（第 1—9 课、第 10—18 课），变位表另由一人逐格核对；改的地方都写在 `tools/merge.py` 开头的几张表里（`FIX`、`PIN`、`EXTRA`、`KNOWN_FIX` 等，每条注明原因），改完重新复核、排版，又查了版面（没有伸出版心的行，变位表不跨页）。

## 文件

| 文件 | 作用 |
| --- | --- |
| `tools/prior.py` | 读第一、二册单词表的结果（`../../第一册/单词表/data/vocab.json`、`../../第二册/单词表/data/vocab.json`）：前两册学过哪些词、哪些意思，见过哪些词形，哪些动词出过变位表 |
| `tools/extract.py` | 从课件 JSON 抽出每课的西语句子（`data/sentences.json`）和每个词形第一次出现的课（`data/forms.json`）；前两册没见过的词形分三组写进 `data/forms_L01-06.json` 等，前两册见过的写进 `data/known_L01-06.json` 等，前两册词条清单写进 `data/prior_lemmas.tsv` |
| `data/归并规则.md` | 词形归到原形的规则，和查前两册见过的词形有没有新意思的规则 |
| `data/lex_L01-06.tsv` 等三份 | 新词形的归并结果（词形、原形、词性、释义、形式说明） |
| `data/known_L01-06.tsv` 等三份 | 前两册见过的词形里，第三册是同形词或有了新意思的 |
| `tools/conj.py` | 变位程序：陈述式现在时、简单过去时、过去未完成时、将来未完成时、简单条件式、虚拟式现在时、虚拟式过去未完成时（-ra、-se 形式）、命令式（肯定、否定）、副动词、过去分词，含词根变化、拼写变化、不规则动词、自复动词、无人称动词和助动词 haber |
| `tools/check_tables.py` | 把 `conj.py` 和仓库里审校过的变位表（第一、二、三册课件的语法表和各教程的 Markdown 表）逐格比对，结果写进 `data/check_stats.json` |
| `tools/analyze.py` | 分析一个动词形式是哪个时态、人称（复核归并结果用） |
| `tools/merge.py` | 合并归并结果，按课整理成 `data/vocab.json`；每个动词形式都用 `analyze.py` 复核，要人工看的写进 `data/review.txt` |
| `build_vocab.js` | 排版：`data/vocab.json` → Word |
| `tools/export_csv.py` | 导出 `单词表.csv`、`动词变位表.csv` |
| `tools/review_text.py` | 把 `data/vocab.json` 写成审读用的纯文本 |

## 重新生成

需要 Python 3 和 Node.js（`npm install` 装 `package.json` 里的 docx、jszip）；第一、二册单词表的 `data/` 要在仓库里原来的位置：

```bash
cd 课件/第三册/单词表
python3 tools/extract.py ../content          # 课件改了才需要重跑；词形有增减时归并结果要跟着补
python3 tools/check_tables.py ../../..       # 变位程序和仓库里的变位表比对，应该是 0 处出入
python3 tools/merge.py ../content
node build_vocab.js out/现代西班牙语第三册（老版）分课单词表.docx
python3 tools/export_csv.py out
```

PDF 用 LibreOffice 转：`soffice --headless --convert-to pdf --outdir out out/*.docx`。
