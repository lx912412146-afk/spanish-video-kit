# 《现代西班牙语》第一册（老版）分课单词表

按课整理第一册 24 课课件里出现的西语词：单词、词性、中文释义，动词原形和各课出现的变位形式，每个动词的完整变位表。共 682 个词条（另有只在语音练习里出现的 136 个词）、127 个动词的变位表、657 个动词形式。

Release [`book1-vocab`](https://github.com/lx912412146-afk/spanish-video-kit/releases/tag/book1-vocab)：`book1-vocab.docx`、`book1-vocab.pdf`（A4，128 页，可以直接打印）、`book1-vocab-words.csv`（单词表，每个词条一行）、`book1-vocab-verbs.csv`（动词变位表，每个动词 6 行）；CSV 是 UTF-8 带 BOM，Excel 直接打开。

- 依据是本仓库 [`课件/第一册/content/`](../content/) 里 24 课的课件内容（生词、语音练习、课文、语法要点和例句、常用表达、练习、小结、作业）。**不是课本书后词汇表或生词表的翻印**：词条和释义按课件里的用法重新整理，和课本生词表的选词、释义可能不完全一样。
- 每课：生词（本课第一次出现的词，按字母顺序；课件生词表里的词加粗）→ 语音练习词（第 1—8 课）→ 本课第一次出现的动词形式（→ 原形和形式说明）→ 已学词的新形式（如第 23 课的绝对最高级）→ 新动词变位表（陈述式现在时、简单过去时、过去未完成时、命令式，副动词、过去分词；和规则变位不一样的形式标红）→ 常用表达。书后有词汇总索引和动词变位表索引（带页码）。
- 拼写按老版课本：sólo、éste / ése / aquél 带重音。
- 动词的类型标在生词备注和变位表标题上：e→ie、o→ue、e→i、u→ue 是词根变化，i→í、u→ú 是重音变化（envío、efectúo），“不规则”是有不规则形式的（conozco、tuve）。
- 整理完以后由两人分别对着课件逐条审读（第 1—12 课、第 13—24 课）；改的地方都写在 `tools/merge.py` 开头的几张表里（`FIX`、`PIN`、`EXTRA` 等，每条注明原因），改完重新复核、排版，又查了版面（没有伸出版心的行）。

## 文件

| 文件 | 作用 |
| --- | --- |
| `tools/extract.py` | 从课件 JSON 抽出每课的西语句子（`data/sentences.json`）和每个词形第一次出现的课（`data/forms.json`） |
| `data/forms_L01-08.json` 等三份、`data/归并规则.md` | 词形分三组按规则归到原形；结果是 `data/lex_L01-08.tsv`、`lex_L09-16.tsv`、`lex_L17-24.tsv`（词形、原形、词性、释义、形式说明） |
| `tools/conj.py` | 变位程序：现在时、简单过去时、过去未完成时、虚拟式现在时、命令式、副动词、过去分词，含词根变化、拼写变化、不规则动词、自复动词和命令式连写代词 |
| `tools/check_tables.py` | 把 `conj.py` 和仓库里审校过的变位表（课件语法表和各教程的 Markdown 表）逐格比对 |
| `tools/analyze.py` | 分析一个动词形式是哪个时态、人称（复核归并结果用） |
| `tools/merge.py` | 合并三份归并结果，按课整理成 `data/vocab.json`；每个动词形式都用 `analyze.py` 复核，对不上的写进 `data/review.txt` |
| `build_vocab.js` | 排版：`data/vocab.json` → Word |
| `tools/export_csv.py` | 导出 `单词表.csv`、`动词变位表.csv` |

## 重新生成

需要 Python 3 和 Node.js（`npm install` 装 `package.json` 里的 docx、jszip）：

```bash
cd 课件/第一册/单词表
python3 tools/extract.py ../content          # 课件改了才需要重跑；词形有增减时三份归并结果要跟着补
python3 tools/check_tables.py ../../..       # 变位程序和仓库里的变位表比对，应该是 0 处出入
python3 tools/merge.py ../content
node build_vocab.js out/现代西班牙语第一册（老版）分课单词表.docx
python3 tools/export_csv.py out
```

PDF 用 LibreOffice 转：`soffice --headless --convert-to pdf --outdir out out/*.docx`。
