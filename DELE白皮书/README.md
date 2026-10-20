# DELE 考试白皮书（A1–C2）

为准备 DELE（Diplomas de Español como Lengua Extranjera）A1–C2 各级考试的中国考生和老师整理的一本备考书：各级考试结构、每个任务的题型模板和原创样题、易错点、考试常用词汇和表达。Word 和 PDF 在 Release [`dele-whitepaper`](../../../releases/tag/dele-whitepaper)。

## 内容

| 部分 | 章 |
| --- | --- |
| 第一部分 总览 | 第 1 章 DELE 考试概况：级别、报名和成绩、各级结构总表、评分和及格规则、版本变化 |
| 第二部分 各级考试结构和题型模板 | 第 2–7 章 DELE A1、A2、B1、B2、C1、C2：每一级的部分、任务、题量、时长和字数，每个任务的做题方法、原创样题和答案解析，写作范文和口语示范 |
| 第三部分 易错点和应试技巧 | 第 8 章 语法和用词易错点；第 9 章 各项技能的易错点和应试技巧 |
| 第四部分 考试常用词汇和表达 | 第 10–12 章 A1–A2、B1–B2、C1–C2 常用词汇和搭配；第 13 章 写作和口语常用表达 |
| 附录 | A 备考计划；B DELE 常用术语对照 |

- 本书是独立编写的备考资料，不是塞万提斯学院（Instituto Cervantes）的官方出版物。
- 考试结构依据 2026 年 10 月能查到的塞万提斯学院官方考试网站和官方考试指南整理（整理过程和来源可信度见 `资料/`）；来源不一致或没能核实的地方，书中已注明。报名和考前请以 examenes.cervantes.es 的最新说明为准。
- 样题、阅读篇章、听力原文、写作和口语范文全部是按现行考试格式新写的模拟材料，不是真题，也不是官方样卷。官方样卷（modelos de examen）可以在考试网站“Preparar la prueba”栏目免费下载。
- 拼写按现行 RAE 规范（solo、este 等不加重音），和《现代西班牙语》老版课本不同。
- 每章由一人编写、另一人独立审校，再做第二轮校对和全书一致性检查；范文字数用脚本数过。

## 文件

| 文件 | 作用 |
| --- | --- |
| `chapters/*.md` | 各章正文（约定的简化 Markdown，标记见 `DELE白皮书编写要求.md`） |
| `front_matter.md` | 编写说明 |
| `资料/` | 各级考试结构的事实文件（编写时的依据） |
| `build_dele.js` | 用 docx（npm）把各章排成 Word：封面、编写说明、目录（带页码）、各部分和附录 |
| `lint.py` | 检查章节文件的标记 |
| `DELE白皮书编写要求.md` | 编写规则和标记说明 |

## 重新生成

需要 Node.js 和 `npm install docx@9.5.1`。在仓库根目录：

```bash
python DELE白皮书/lint.py DELE白皮书/chapters/*.md DELE白皮书/front_matter.md
node DELE白皮书/build_dele.js DELE白皮书/out/DELE考试白皮书.docx
```

PDF 是用 LibreOffice 转的（`soffice --headless --convert-to pdf`），目录页码由转换时计算；在 Word 里打开时如提示更新域，选“是”即可更新目录页码。字体用苹方（PingFang SC），Windows 上会换成默认中文字体。
