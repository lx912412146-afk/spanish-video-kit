# 《现代西班牙语》第一册（老版）分课课件

第 1–24 课，每课一个 PowerPoint 课件（16:9），另有同内容的 PDF。PPTX 和 PDF 在 Release [`courseware-book1`](../../../releases/tag/courseware-book1)。

每课的结构：封面 → 本课目标 → 语音（第 1–8 课）→ 本课词汇 → 课文（仿照本课编写的原创对话或短文，附中文）→ 语法（要点、例句；变位表较大时单独一页）→ 常用表达 → 课堂练习 → 练习答案 → 本课小结 → 课后作业。大部分页附有给老师的备注（演讲者备注）。

- 各课的语音、语法和话题按 [`试卷/第一册分阶段模拟卷/课程大纲.md`](../../试卷/第一册分阶段模拟卷/课程大纲.md)；第 N 课的例句、课文和练习只用到第 N 课为止学过的语法。
- 课文不是课本原文；大纲里没有单列语法的课（第 18、24 课）按复习课安排。
- 拼写按老版课本的习惯：副词 sólo、指示代词 éste / ése / aquél 带重音（RAE 2010 起不再要求，备注里有说明）。
- 字体用苹方（PingFang SC）。Windows 电脑上没有这个字体，PowerPoint 会换成默认中文字体，版式基本不变。

## 文件

| 文件 | 作用 |
| --- | --- |
| `content/L01.json` … `L24.json` | 每课的内容（目标、语音、词汇、课文、语法、练习、小结、作业、教学备注） |
| `build_decks.js` | 用 pptxgenjs 把内容排成 PPTX（统一版式，按文字量自动调字号、分页） |
| `check_content.py` | 内容格式和长度自检 |
| `课件内容要求.md`、`课件审校要求.md` | 编写和审校的规则 |

## 重新生成

需要 Node.js 和 `npm install pptxgenjs@3.12.0`：

```bash
node 课件/第一册/build_decks.js          # 全部 24 课，输出到 课件/第一册/out/
node 课件/第一册/build_decks.js 05 06    # 只生成第 5、6 课
```

改某一课的内容只要改对应的 `content/Lxx.json` 再重新生成，先跑 `python check_content.py content/Lxx.json` 检查长度。
