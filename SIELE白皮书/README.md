# SIELE 考试白皮书（A1–C1）

为准备 SIELE（Servicio Internacional de Evaluación de la Lengua Española，国际西班牙语评估服务）的中国考生和老师整理的一本备考书：考试结构、每个任务的题型模板和原创样题、易错点和易错题、注意事项、常考词汇和表达。Word 和 PDF 在 Release [`siele-whitepaper`](../../../releases/tag/siele-whitepaper)。

## 内容

| 部分 | 章 |
| --- | --- |
| 第一部分 总览 | 第 1 章 SIELE 考试概况：考试类型（Global、S1–S5）、四项考试一览、评分和分数段、报名、成绩和有效期、和 DELE 的区别 |
| 第二部分 各项考试结构和题型模板 | 第 2–5 章 阅读理解、听力理解、书面表达与互动、口头表达与互动：每个任务的级别、题型、做题方法、原创样题和答案解析、写作范文和口语示范 |
| 第三部分 易错点、易错题和注意事项 | 第 6 章 语法和用词易错点；第 7 章 易错题精练（按级别、带答案和解析）；第 8 章 各项考试的注意事项和应试技巧（电脑界面、时间分配、多级考试的策略） |
| 第四部分 常考词汇和表达 | 第 9–11 章 A1–A2、B1–B2、C1 常考词汇、搭配、习语和辨析；第 12 章 写作和口语常用表达 |
| 附录 | A 备考计划；B SIELE 常用术语对照 |

- 本书是独立编写的备考资料，不是 SIELE 或塞万提斯学院（Instituto Cervantes）的官方出版物。
- 考试结构依据 2026 年 10 月的 siele.org 和 2021 年 4 月版官方考试指南整理（整理过程和来源可信度见 `资料/`）；来源不一致或没能核实的地方，书中已注明。报考前请以 siele.org 的最新说明为准。
- 样题、阅读篇章、听力原文、写作范文和口语示范全部是按现行考试格式新写的模拟材料，不是真题，也不是官方样题。官方的练习资源有 siele.org 上的模拟系统（Demo）、考试指南和讲解视频。
- 拼写按现行 RAE 规范（solo、este 等不加重音）。
- 第 6 章和第 9–12 章由《DELE 考试白皮书》的相应各章改编。每章由一人编写、另一人独立审校，再做第二轮校对和全书一致性检查。

## 文件

| 文件 | 作用 |
| --- | --- |
| `chapters/*.md` | 各章正文（约定的简化 Markdown，标记见 `SIELE白皮书编写要求.md`） |
| `front_matter.md` | 编写说明 |
| `资料/` | SIELE 考试结构的事实文件（编写时的依据） |
| `build_siele.js` | 用 docx（npm）把各章排成 Word：封面、编写说明、目录（带页码）、各部分和附录 |
| `lint.py` | 检查章节文件的标记 |
| `SIELE白皮书编写要求.md` | 编写规则和标记说明 |

## 重新生成

需要 Node.js 和 `npm install docx@9.5.1`。在仓库根目录：

```bash
python SIELE白皮书/lint.py SIELE白皮书/chapters/*.md SIELE白皮书/front_matter.md
node SIELE白皮书/build_siele.js SIELE白皮书/out/SIELE考试白皮书.docx
```

PDF 是用 LibreOffice 转的（`soffice --headless --convert-to pdf`），目录页码由转换时计算；在 Word 里打开时如提示更新域，选“是”即可更新目录页码。字体用苹方（PingFang SC），Windows 上会换成默认中文字体。
