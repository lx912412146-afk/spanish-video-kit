// 《现代西班牙语》第二册分阶段高考模拟卷排版（沿用 Método 1–2 高考模拟卷的 build_exam.js）：paper.json（export_json.py 由 试卷.md 生成）→ 试卷、答题卡、答案与评分说明三个 A4 的 docx
// 用法：node build_exam.js paper.json 输出目录
// 和 Método 卷的不同：答题卡上第二节作文的题目从卷面“请以 “…” 为题”那句取（Método 卷是写死的）；短段落只有称呼、结尾语、署名顶格，其余照常首行缩进（flushLeft）。
// 阅读部分不强制换页（标题、说明、“A”和广告框连在一起，放不下就一起挪到下一页）；答案与评分说明里“参考答案”接着考试说明排。
// 版式仿高考试卷：正文 Times New Roman＋宋体五号，标题黑体；页脚“西班牙语试题 第 X 页（共 Y 页）”。
// LibreOffice 的坑（见仓库别的排版程序）：汉字和数字之间用普通空格、数字和后面的单位用不换行空格；数字范围的连接号两边加 WJ；
// 表格里“与下段同页”不起作用，要整表不拆页就给除最后一行外每一行的段落都设 keepNext。
const fs = require('fs');
const path = require('path');
const {
  Document, Packer, Paragraph, TextRun, TabStopType, Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle,
  AlignmentType, Footer, PageNumber, TableLayoutType, VerticalAlign, Tab, HeightRule, ExternalHyperlink, LineRuleType,
} = require('docx');

const [, , SRC, OUTDIR] = process.argv;
if (!SRC || !OUTDIR) { console.error('用法：node build_exam.js paper.json 输出目录'); process.exit(1); }
const D = JSON.parse(fs.readFileSync(SRC, 'utf8'));
// 第二节作文题目（答题卡上要印）：取卷面上“请以 “…” 为题”那一句（后面括号里的补充说明不印，免得这一行折行把答题卡挤成 3 页）
const ESSAY = JSON.stringify(D).match(/以\s*“([^”]+)”\s*为题/);
if (!ESSAY) throw new Error('试卷里找不到第二节作文的题目（请以 “…” 为题）');

const LAT = 'Times New Roman';
const F = { ascii: LAT, hAnsi: LAT, eastAsia: 'Songti SC', cs: LAT };
const FH = { ascii: LAT, hAnsi: LAT, eastAsia: 'Heiti SC', cs: LAT };
const LANG = { value: 'es-ES', eastAsia: 'zh-CN' };
const PAGE_W = 11906, PAGE_H = 16838, MX = 1134, MY = 1077, CW = PAGE_W - 2 * MX;
const SZ = 21;            // 五号
const NUM_W = 420;        // 题号悬挂缩进
const IND = 420;          // 段首缩进两个汉字
const LINE = 312;          // 固定行距 15.6 磅：西语行里夹了汉字（注释）也不会把行撑高
const EXACT = LineRuleType.EXACT;
const CN = '零一二三四五六七八九十';

// ---------------------------------------------------------------- 文字
const nb = (s) => String(s)
  .replace(/(\d) (?=\d{3}(?!\d))/g, '$1\u00a0')            // 电话号码分组
  .replace(/(\d) (?=[%€])/g, '$1\u00a0')
  .replace(/(\d) (?=[一-鿿])/g, '$1\u00a0')        // 数字和后面的单位（5 段、10 秒钟）
  .replace(/(\d)([–～—])(?=\d)/g, '$1\u2060$2\u2060')       // 1–5、30～50、9:30–13:30
  .replace(/(\S) ([×=+]) (?=\S)/g, '$1\u00a0$2\u00a0')      // 2 × 2 + 3 = 7
  .replace(/([A-Za-z]) (?=\d)/g, '$1\u00a0')                // A1、Texto 1 之类不拆
  // 西语里的中文注释（学生证）整体不拆：字和字之间加 WJ
  .replace(/\(([\u4e00-\u9fff]{2,})\)/g, (m, x) => `(${[...x].join('\u2060')})`);
function textW(s) { let w = 0; for (const ch of String(s).replace(/\*\*/g, '')) w += /[⺀-鿿＀-￯　-〿…—“”]/.test(ch) ? 1 : /[A-ZÁÉÍÓÚÑ]/.test(ch) ? 0.68 : /[mw]/.test(ch) ? 0.75 : /[iljtf.,;:'!¡ ]/.test(ch) ? 0.3 : 0.5; return w; }
const twips = (s, size = SZ) => Math.ceil(textW(s) * size * 10 * 1.06);

// 行内：**加粗**、\_\_41\_\_（空格题号）、________（题干里的空）、`代码`、[文字](链接)
function runs(text, o = {}) {
  const size = o.size || SZ;
  const font = o.font || F;
  const base = { font, language: LANG, size, color: o.color || '000000', italics: o.italics };
  const out = [];
  const parts = String(text).split(/(\*\*[^*]+\*\*|\\_\\_\d+\\_\\_|_{4,}|`[^`]+`|\[[^\]]+\]\([^)]+\))/g);
  for (const p of parts) {
    if (!p) continue;
    let m;
    if ((m = p.match(/^\*\*([^*]+)\*\*$/))) out.push(new TextRun({ ...base, text: nb(unesc(m[1])), bold: true }));
    else if ((m = p.match(/^\\_\\_(\d+)\\_\\_$/))) out.push(new TextRun({ ...base, text: `\u00a0\u00a0\u00a0${m[1]}\u00a0\u00a0\u00a0`, bold: o.bold, underline: {} }));
    else if (/^_{4,}$/.test(p)) out.push(new TextRun({ ...base, text: '\u00a0'.repeat(16), underline: {} }));
    else if ((m = p.match(/^`([^`]+)`$/))) out.push(new TextRun({ ...base, text: m[1], bold: o.bold }));
    else if ((m = p.match(/^\[([^\]]+)\]\(([^)]+)\)$/))) {
      out.push(new ExternalHyperlink({ link: m[2], children: [new TextRun({ ...base, text: nb(m[1]), bold: o.bold })] }));
      out.push(new TextRun({ ...base, text: `（${m[2]}）`, size: size - 3, color: '444444' }));
    } else {
      // 中文引号“”‘’用中文字体（不然落在 Times 里，又窄又偏）
      const qf = font === FH ? 'Heiti SC' : 'Songti SC';
      for (const q of nb(unesc(p)).split(/([“”‘’])/)) {
        if (!q) continue;
        if (/^[“”‘’]$/.test(q)) out.push(new TextRun({ ...base, text: q, bold: o.bold, font: { ascii: qf, hAnsi: qf, eastAsia: qf, cs: qf } }));
        else out.push(new TextRun({ ...base, text: q, bold: o.bold }));
      }
    }
  }
  return out;
}
const unesc = (s) => s.replace(/\\([_*\\])/g, '$1');
const TAB = (size = SZ) => new TextRun({ children: [new Tab()], font: F, size });
const isHan = (s) => /^[一-鿿（“《「]/.test(s.replace(/^\*\*/, ''));
const boldOnly = (s) => /^\*\*[^*]+\*\*$/.test(s);
const P = (o) => new Paragraph(o);
function para(kids, o = {}) {
  return P({
    alignment: o.align || AlignmentType.JUSTIFIED, widowControl: true,
    spacing: { before: o.before || 0, after: o.after ?? 60, line: o.line || LINE, lineRule: o.auto ? LineRuleType.AUTO : EXACT },
    keepNext: !!o.keep, keepLines: !!o.keepLines, indent: o.indent, tabStops: o.tabs, border: o.border, shading: o.shading,
    pageBreakBefore: !!o.pageBreak,
    children: typeof kids === 'string' ? runs(kids, o) : kids,
  });
}

// ---------------------------------------------------------------- 题目
function optionLayout(opts) {
  const w = opts.map((o) => twips(`${o[0]}. ${o[1]}`) + 240);
  const avail = CW - NUM_W;
  for (const n of [opts.length, 2]) {
    const col = Math.floor(avail / n);
    if (w.every((x) => x <= col)) return { per: n, pos: Array.from({ length: n }, (_, k) => NUM_W + k * col) };
  }
  return { per: 1 };
}
function question(b, keepLast = false) {
  const out = [para([...runs(`${b.num}.`), TAB(), ...runs(b.stem)],
    { indent: { left: NUM_W, hanging: NUM_W }, tabs: [{ type: TabStopType.LEFT, position: NUM_W }], keep: true, keepLines: true, after: 30, align: AlignmentType.LEFT })];
  const lay = optionLayout(b.options);
  const optRuns = (o) => runs(`${o[0]}. ${o[1].replace(/ /g, '\u00a0')}`);
  const rows = [];
  for (let i = 0; i < b.options.length; i += lay.per) rows.push(b.options.slice(i, i + lay.per));
  rows.forEach((r, k) => {
    const last = k === rows.length - 1;
    if (lay.per === 1) out.push(para(runs(`${r[0][0]}. ${r[0][1]}`), { indent: { left: NUM_W + 360, hanging: 360 }, keep: !last || keepLast, keepLines: true, after: last ? 110 : 0, align: AlignmentType.LEFT }));
    else out.push(para(r.flatMap((o) => [TAB(), ...optRuns(o)]), { tabs: lay.pos.map((x) => ({ type: TabStopType.LEFT, position: x })), keep: !last || keepLast, keepLines: true, after: last ? 110 : 0, align: AlignmentType.LEFT }));
  });
  return out;
}
function clozeOptions(b) {
  const col = Math.floor((CW - NUM_W) / 4);
  const tabs = [0, 1, 2, 3].map((k) => ({ type: TabStopType.LEFT, position: NUM_W + k * col }));
  return b.rows.map((r, i) => para([...runs(`${r[0]}.`), ...['A', 'B', 'C', 'D'].flatMap((l, k) => [TAB(), ...runs(`${l}. ${r[k + 1]}`)])],
    { tabs, after: 40, keep: i < b.rows.length - 1, keepLines: true, align: AlignmentType.LEFT }));
}

// ---------------------------------------------------------------- 段落、列表、表格
// 顶格不缩进的短行：信的称呼（Querida…:、Hola, …:）、结尾语（Un abrazo,、¡Hasta pronto!）、署名和地点日期（没有句末标点）；
// 其余的短段落（叙述、对话行、带句号的短句）照常首行缩进
function flushLeft(s) {
  if (s.length >= 50 || /^—/.test(s)) return false;
  if (/^(Querid|Estimad|Hola|Buen)/.test(s) && /[:,]$/.test(s)) return true;
  if (/^¡Hasta /.test(s)) return true;
  return /,$/.test(s) || !/[.!?:;»…)]$/.test(s);
}
function textPara(s, o = {}) {
  if (boldOnly(s)) return para(runs(s, { font: FH }), { keep: true, keepLines: true, before: 120, after: 60, align: AlignmentType.LEFT });
  const han = isHan(s);
  const short = !han && flushLeft(s);                  // 信的称呼、结尾语、署名不缩进
  return para(s, { indent: short || o.noIndent ? undefined : { firstLine: IND }, keep: o.keep || (han && /录音，回答第/.test(s)) || /[:：]$/.test(s), after: o.after ?? 60 });
}
function subPara(s) {
  return para(runs(s, { font: FH }), { keep: true, keepLines: true, before: 120, after: 60, align: AlignmentType.LEFT });
}
function listItems(items, ordered, o = {}) {
  return items.map((it, i) => {
    const label = ordered ? `${i + 1}.` : '•';
    return para([...runs(label), TAB(), ...runs(it)], {
      indent: { left: (o.left || 0) + NUM_W, hanging: NUM_W }, tabs: [{ type: TabStopType.LEFT, position: (o.left || 0) + NUM_W }],
      after: o.after ?? 40, keep: o.keepAll || (o.keep && i < items.length - 1), align: AlignmentType.LEFT,
    });
  });
}
function transcriptLine(s) {
  const m = s.match(/^([男女])：(.*)$/);
  if (!m) return textPara(s);
  return para([new TextRun({ text: `${m[1]}：`, font: FH, size: SZ, bold: true }), TAB(), ...runs(m[2])],
    { indent: { left: 520, hanging: 520 }, tabs: [{ type: TabStopType.LEFT, position: 520 }], after: 40, align: AlignmentType.LEFT });
}
const B = (sz = 4, color = '000000') => ({ style: BorderStyle.SINGLE, size: sz, color });
const NONE = { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' };
// 列宽：短的列（自然宽度不超过 2600）按自然宽度，不折行；其余宽度按自然宽度比例分给长的列
function colWidths(rows, total = CW) {
  const n = rows[0].length;
  const nat = Array(n).fill(520);
  for (const r of rows) r.forEach((c, j) => { nat[j] = Math.max(nat[j], twips(c.replace(/\*\*/g, ''), 19) + 240); });
  const sn = nat.reduce((a, b) => a + b, 0);
  let ws;
  if (sn <= total) ws = nat.map((x) => Math.floor(x + (total - sn) * x / sn));
  else {
    const short = nat.map((x) => x <= 2600);
    const fixed = nat.reduce((a, x, j) => a + (short[j] ? x : 0), 0);
    // 长的列之间按自然宽度的平方根分（两列都很长时，短一些的那列不至于太窄、折行太多）
    const longSum = nat.reduce((a, x, j) => a + (short[j] ? 0 : Math.sqrt(x)), 0);
    if (!longSum || fixed > total * 0.75) ws = nat.map((x) => Math.floor(x * total / sn));
    else ws = nat.map((x, j) => (short[j] ? x : Math.floor(Math.sqrt(x) * (total - fixed) / longSum)));
  }
  ws[ws.indexOf(Math.max(...ws))] += total - ws.reduce((a, b) => a + b, 0);
  return ws;
}
function table(rows, o = {}) {
  const letter = rows.every((r) => r.length === 10) && /^\d+$/.test(rows[0][0]);
  // 知识点覆盖表：第一列（内容）宽一些，少折行
  const cover = rows[0].join('|') === '内容|级别|对应题号';
  const ws = o.widths || (letter ? Array(10).fill(Math.floor(CW / 10)) : cover ? [5100, 850, CW - 5950] : colWidths(rows));
  const keepAll = o.keepAll ?? rows.length <= 12;
  const num = (r) => r.every((c) => /^(\*\*)?\d+(\*\*)?$/.test(c));
  const centerCol = rows[0].map((_, j) => rows.slice(1).every((r) => r[j].replace(/\*\*/g, '').length <= 7));
  return new Table({
    width: { size: ws.reduce((a, b) => a + b, 0), type: WidthType.DXA }, columnWidths: ws, layout: TableLayoutType.FIXED,
    borders: { top: B(6), bottom: B(6), left: B(4), right: B(4), insideHorizontal: B(4, '666666'), insideVertical: B(4, '666666') },
    rows: rows.map((r, i) => {
      const head = letter ? num(r) : i === 0;
      return new TableRow({
        cantSplit: true, tableHeader: !letter && i === 0,
        children: r.map((c, j) => {
          const center = letter || head || centerCol[j];
          return new TableCell({
            width: { size: ws[j], type: WidthType.DXA }, verticalAlign: VerticalAlign.CENTER,
            shading: head ? { type: ShadingType.CLEAR, color: 'auto', fill: 'EDEDED' } : undefined,
            margins: { top: 20, bottom: 20, left: 80, right: 80 },
            children: [P({ alignment: center ? AlignmentType.CENTER : AlignmentType.LEFT, keepNext: keepAll && i < rows.length - 1, keepLines: true,
              spacing: { after: 0, line: 268, lineRule: EXACT }, children: runs(c.replace(/^\*\*(.+)\*\*$/, '$1'), { size: 19, bold: head, font: head ? FH : F }) })],
          });
        }),
      });
    }),
  });
}
function quoteBox(paras) {
  const kids = paras.map((s, i) => {
    if (boldOnly(s)) return para(runs(s), { align: AlignmentType.CENTER, after: 60, keep: true });
    return para(s, { indent: flushLeft(s) ? undefined : { firstLine: IND }, after: 50, keepLines: true, keep: i < paras.length - 1 && paras.length <= 7 });
  });
  return new Table({
    width: { size: CW, type: WidthType.DXA }, columnWidths: [CW], layout: TableLayoutType.FIXED,
    borders: { top: B(4, '888888'), bottom: B(4, '888888'), left: B(4, '888888'), right: B(4, '888888'), insideHorizontal: NONE, insideVertical: NONE },
    rows: [new TableRow({ cantSplit: true, children: [new TableCell({ width: { size: CW, type: WidthType.DXA }, margins: { top: 100, bottom: 60, left: 200, right: 200 },
      shading: { type: ShadingType.CLEAR, color: 'auto', fill: 'F5F5F5' }, children: kids })] })],
  });
}
// 表格、框后面的空段；一节末尾的空段要去掉（不然下一节标题“段前分页”时，它会单独占一页）
const GAPS = new WeakSet();
const gap = (after = 80) => { const g = P({ spacing: { after, line: 200 }, children: [] }); GAPS.add(g); return g; };
const trimGaps = (out) => { while (out.length && GAPS.has(out[out.length - 1])) out.pop(); return out; };

// ---------------------------------------------------------------- 试卷（学生用）
function noticeBox(blocks) {
  const kids = [];
  let k = 0;
  for (const b of blocks) {
    if (b.t === 'p' && boldOnly(b.text)) {
      const top = k++ < 2;
      kids.push(para(runs(b.text, { size: top ? 23 : SZ }), { align: top ? AlignmentType.CENTER : AlignmentType.LEFT, before: top ? 0 : 100, after: 40, keep: true }));
    } else if (b.t === 'p') kids.push(para(b.text, { before: 100, after: 40 }));
    else if (b.t === 'ul') kids.push(...listItems(b.items, false, { left: 120, after: 10 }));
  }
  return new Table({
    width: { size: CW, type: WidthType.DXA }, columnWidths: [CW], layout: TableLayoutType.FIXED,
    borders: { top: B(8), bottom: B(8), left: B(8), right: B(8), insideHorizontal: NONE, insideVertical: NONE },
    rows: [new TableRow({ cantSplit: true, children: [new TableCell({ width: { size: CW, type: WidthType.DXA }, margins: { top: 120, bottom: 120, left: 240, right: 240 }, children: kids })] })],
  });
}
function partHeading(title, pageBreak = false) {
  return para(runs(title, { font: FH, size: 24, bold: true }), { before: 200, after: 100, keep: true, keepLines: true, align: AlignmentType.LEFT, pageBreak, auto: true });
}
function renderStudentSection(sec) {
  const out = [];
  const bl = sec.blocks;
  if (sec.title === '注意事项') {
    out.push(para(runs('注意事项：', { font: FH, bold: true }), { keep: true, after: 40, align: AlignmentType.LEFT }));
    for (const b of bl) if (b.t === 'ol') out.push(...listItems(b.items, true, { after: 30 }));
    return out;
  }
  out.push(partHeading(sec.title));     // 阅读不强制换页：标题、说明、“A”都和后面的广告框连在一起（框不跨页），放不下就一起挪到下一页
  for (let i = 0; i < bl.length; i++) {
    const b = bl[i], next = bl[i + 1];
    if (b.t === 'h3') {
      out.push(para(runs(b.text, { font: FH, bold: true, size: 22 }), { align: AlignmentType.CENTER, before: 140, after: 80, keep: true }));
      if (b.text === 'A' && sec.title.startsWith('第二部分')) {          // A 篇是广告：整块放进框里
        const notice = [];
        while (bl[i + 1] && bl[i + 1].t !== 'q') notice.push(bl[++i]);
        out.push(noticeBox(notice), gap(100));
      }
    } else if (b.t === 'sub') out.push(subPara(b.text));
    else if (b.t === 'p') out.push(textPara(b.text, { keep: next && (next.t === 'q' || next.t === 'ol' || next.t === 'h3') && isHan(b.text) }));
    else if (b.t === 'q') out.push(...question(b));
    else if (b.t === 'cloze') out.push(gap(60), ...clozeOptions(b), gap(60));
    else if (b.t === 'ol') out.push(...listItems(b.items, true, { keep: true }));
    else if (b.t === 'ul') out.push(...listItems(b.items, false));
    else if (b.t === 'table') out.push(table(b.rows), gap());
    else if (b.t === 'quote') out.push(quoteBox(b.paras), gap());
  }
  return trimGaps(out);
}
function paperDoc() {
  const secs = D.sections.filter((s) => s.title === '注意事项' || /^第[一二三四]部分/.test(s.title));
  const m = D.title.match(/^(.+?)（(.+)）$/);
  const head = [
    para(runs(m[1], { font: FH, size: 36, bold: true }), { align: AlignmentType.CENTER, after: 60, auto: true }),
    para(runs(`（${m[2]}）`, { size: 24 }), { align: AlignmentType.CENTER, after: 120, auto: true }),
    para([new TextRun({ children: ['本试卷共 ', PageNumber.TOTAL_PAGES, ' 页，满分 150 分，考试时间 120 分钟。'], font: F, size: SZ })], { align: AlignmentType.CENTER, after: 200 }),
  ];
  const body = secs.flatMap(renderStudentSection);
  return { label: '西班牙语试题', children: [...head, ...body], file: '试卷' };
}

// ---------------------------------------------------------------- 答题卡
function bubbleCell(first, last, n, w) {
  const letters = 'ABCD'.slice(0, n).split('');
  const kids = [];
  for (let q = first; q <= last; q++) {
    kids.push(P({ spacing: { after: 0, line: 290, lineRule: EXACT }, tabStops: [{ type: TabStopType.RIGHT, position: 380 }, ...letters.map((_, k) => ({ type: TabStopType.LEFT, position: 560 + k * 470 }))],
      children: [TAB(19), new TextRun({ text: String(q), font: F, size: 19, bold: true }),
        ...letters.flatMap((l) => [TAB(19), new TextRun({ text: `[${l}]`, font: F, size: 18, color: '333333' })])] }));
  }
  return new TableCell({ width: { size: w, type: WidthType.DXA }, margins: { top: 50, bottom: 50, left: 60, right: 60 }, children: kids });
}
function bubbleTable(start, n, cols = 4) {
  const w = Math.floor(CW / cols);
  return new Table({
    width: { size: w * cols, type: WidthType.DXA }, columnWidths: Array(cols).fill(w), layout: TableLayoutType.FIXED,
    borders: { top: B(8), bottom: B(8), left: B(8), right: B(8), insideHorizontal: B(4, '999999'), insideVertical: B(4, '999999') },
    rows: [new TableRow({ cantSplit: true, children: Array.from({ length: cols }, (_, k) => bubbleCell(start + 5 * k, start + 5 * k + 4, n, w)) })],
  });
}
function cardTitle(s, o = {}) {
  return para(runs(s, { font: FH, bold: true, size: 21 }), { before: o.before ?? 70, after: 50, keep: true, align: AlignmentType.LEFT });
}
function lineBox(nRows, height = 520) {
  return new Table({
    width: { size: CW, type: WidthType.DXA }, columnWidths: [CW], layout: TableLayoutType.FIXED,
    borders: { top: B(8), bottom: B(8), left: B(8), right: B(8), insideHorizontal: { style: BorderStyle.SINGLE, size: 2, color: 'AAAAAA' }, insideVertical: NONE },
    rows: Array.from({ length: nRows }, () => new TableRow({ cantSplit: true, height: { value: height, rule: HeightRule.EXACT },
      children: [new TableCell({ width: { size: CW, type: WidthType.DXA }, children: [P({ spacing: { after: 0 }, children: [] })] })] })),
  });
}
function cardDoc() {
  const m = D.title.match(/^(.+?)（(.+)）$/);
  const out = [
    para(runs(`${m[1]}　答题卡`, { font: FH, size: 32, bold: true }), { align: AlignmentType.CENTER, after: 40, auto: true }),
    para(runs(`（${m[2]}）`, { size: 21 }), { align: AlignmentType.CENTER, after: 100 }),
  ];
  // 考生信息和注意事项
  const lw = 4300, rw = CW - lw;
  const info = (label, n) => P({ spacing: { before: 100, after: 100 }, children: [new TextRun({ text: `${label}`, font: F, size: SZ }),
    new TextRun({ text: '\u00a0'.repeat(n), font: F, size: SZ, underline: {} })] });
  const notes = ['答题前，考生先将自己的姓名、班级、考场号、座位号、准考证号填写清楚。',
    '选择题用 2B 铅笔把对应题目的答案标号涂黑；非选择题用黑色字迹的签字笔书写，字体工整、笔迹清楚。',
    '请按照题号顺序在各题的答题区域内作答，超出答题区域书写的答案无效；在草稿纸、试卷上答题无效。',
    '保持卡面清洁，不要折叠、不要弄破。'];
  out.push(new Table({
    width: { size: CW, type: WidthType.DXA }, columnWidths: [lw, rw], layout: TableLayoutType.FIXED,
    borders: { top: B(8), bottom: B(8), left: B(8), right: B(8), insideHorizontal: B(4), insideVertical: B(4) },
    rows: [new TableRow({ cantSplit: true, children: [
      new TableCell({ width: { size: lw, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 160, right: 120 }, verticalAlign: VerticalAlign.CENTER,
        children: [info('姓　名', 28), info('班　级', 28), P({ spacing: { before: 100, after: 100 }, children: [new TextRun({ text: '考场号', font: F, size: SZ }),
          new TextRun({ text: '\u00a0'.repeat(9), font: F, size: SZ, underline: {} }), new TextRun({ text: '　座位号', font: F, size: SZ }), new TextRun({ text: '\u00a0'.repeat(9), font: F, size: SZ, underline: {} })] })] }),
      new TableCell({ width: { size: rw, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 160, right: 160 },
        children: [P({ spacing: { after: 40 }, children: runs('注意事项', { font: FH, bold: true, size: 19 }) }),
          ...notes.map((t, i) => P({ alignment: AlignmentType.JUSTIFIED, indent: { left: 300, hanging: 300 }, tabStops: [{ type: TabStopType.LEFT, position: 300 }], spacing: { after: 20, line: 260 },
            children: [new TextRun({ text: `${i + 1}.`, font: F, size: 18 }), TAB(18), ...runs(t, { size: 18 })] }))] }),
    ] })],
  }));
  // 准考证号
  const nBox = 10, labW = 1800, boxW = Math.floor((CW - labW) / nBox);
  out.push(gap(60), new Table({
    width: { size: labW + boxW * nBox, type: WidthType.DXA }, columnWidths: [labW, ...Array(nBox).fill(boxW)], layout: TableLayoutType.FIXED,
    borders: { top: B(8), bottom: B(8), left: B(8), right: B(8), insideHorizontal: B(4), insideVertical: B(4) },
    rows: [new TableRow({ cantSplit: true, height: { value: 560, rule: HeightRule.EXACT }, children: [
      new TableCell({ width: { size: labW, type: WidthType.DXA }, verticalAlign: VerticalAlign.CENTER, children: [P({ alignment: AlignmentType.CENTER, spacing: { after: 0 }, children: runs('准考证号', { font: FH, bold: true }) })] }),
      ...Array.from({ length: nBox }, () => new TableCell({ width: { size: boxW, type: WidthType.DXA }, children: [P({ spacing: { after: 0 }, children: [] })] }))] })],
  }));
  out.push(cardTitle('第一部分　听力（第 1–20 题）'), bubbleTable(1, 3));
  out.push(cardTitle('第二部分　阅读（第 21–40 题）'), bubbleTable(21, 4));
  out.push(cardTitle('第三部分　语言运用　第一节（第 41–60 题）'), bubbleTable(41, 4));
  // 语法填空
  out.push(cardTitle('第三部分　语言运用　第二节（第 61–70 题）'));
  const nw = 560, fw = Math.floor(CW / 2) - nw;
  const cellN = (q) => new TableCell({ width: { size: nw, type: WidthType.DXA }, verticalAlign: VerticalAlign.BOTTOM, borders: { top: NONE, bottom: NONE, left: NONE, right: NONE },
    children: [P({ alignment: AlignmentType.RIGHT, spacing: { after: 20 }, children: [new TextRun({ text: `${q}.`, font: F, size: SZ, bold: true })] })] });
  const cellL = () => new TableCell({ width: { size: fw, type: WidthType.DXA }, borders: { top: NONE, left: NONE, right: NONE, bottom: B(4) }, margins: { left: 80, right: 200 },
    children: [P({ spacing: { after: 0 }, children: [] })] });
  out.push(new Table({
    width: { size: 2 * (nw + fw), type: WidthType.DXA }, columnWidths: [nw, fw, nw, fw], layout: TableLayoutType.FIXED,
    borders: { top: B(8), bottom: B(8), left: B(8), right: B(8), insideHorizontal: NONE, insideVertical: NONE },
    rows: [0, 1, 2, 3, 4].map((k) => new TableRow({ cantSplit: true, height: { value: 500, rule: HeightRule.EXACT },
      children: [cellN(61 + k), cellL(), cellN(66 + k), cellL()] })),
  }));
  // 写作：第二页
  const w1 = cardTitle('第四部分　写作　第一节（10 分）', { before: 0 });
  const p2 = [P({ pageBreakBefore: true, spacing: { after: 0 }, children: [] }), w1,
    para(runs('请在框内作答，词数 30～50 个。超出框线的部分无效。', { size: 18, color: '333333' }), { after: 60, keep: true, align: AlignmentType.LEFT }),
    lineBox(8),
    cardTitle('第四部分　写作　第二节（25 分）', { before: 200 }),
    para(runs(`请在框内作答，题目 “${ESSAY[1]}” 写在第一行，词数 90～110 个。超出框线的部分无效。`, { size: 18, color: '333333' }), { after: 60, keep: true, align: AlignmentType.LEFT }),
    lineBox(16)];
  return { label: '西班牙语答题卡', children: [...out, ...p2], file: '答题卡' };
}

// ---------------------------------------------------------------- 答案与评分说明（教师用）
const fmt = (s) => `${Math.floor(s / 60)}:${String(Math.round(s % 60)).padStart(2, '0')}`.replace(/:60$/, ':59');
function timingTable() {
  if (!D.timeline) return [];
  const qs = { 1: '1', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6–8', 7: '9–12', 8: '13–16', 9: '17–20' };
  const by = {};
  for (const mk of D.timeline.texts) (by[mk.texto] = by[mk.texto] || [])[mk.play - 1] = mk;
  const rows = [['录音', '题号', '第一遍', '第二遍', '单独文件']];
  for (let x = 1; x <= 9; x++) {
    const [a, b] = by[x] || [];
    if (!a || !b) throw new Error(`时间轴缺第 ${x} 段`);
    rows.push([`第 ${x} 段`, qs[x], `${fmt(a.start)}–${fmt(a.end)}`, `${fmt(b.start)}–${fmt(b.end)}`, `Texto_${x}.mp3`]);
  }
  return [para(`各段录音在整套听力录音（全长 ${fmt(D.timeline.total_s)}）里的起止时间（分:秒）；每段另有只放一遍的单独文件，供讲评时用。`, { keep: true, after: 60, before: 80 }),
    table(rows, { widths: [1500, 1300, 2300, 2300, CW - 7400], keepAll: true }), gap()];
}
function renderTeacherSection(sec, first) {
  const out = [];
  const title = sec.title.replace(/（教师用）$/, '');
  // 答案、听力原文各自另起一页（听力原文可以单独印给学生讲评用）；知识点覆盖表接着排
  out.push(para(runs(title, { font: FH, size: 28, bold: true }), { before: first || title !== '知识点覆盖表' ? 0 : 360, after: 160, keep: true, align: AlignmentType.LEFT, pageBreak: !first && title !== '知识点覆盖表' && !title.startsWith('参考答案'), auto: true }));   // 参考答案接着考试说明排（考试说明长的卷子不会只在第 2 页留几行）
  const bl = sec.blocks;
  const listening = title === '听力原文';
  let olSeen = false;
  for (let i = 0; i < bl.length; i++) {
    const b = bl[i], next = bl[i + 1];
    if (b.t === 'sub') out.push(subPara(b.text));
    else if (b.t === 'p') {
      if (boldOnly(b.text)) out.push(para(runs(b.text, { font: FH, size: 22 }), { keep: true, keepLines: true, before: listening ? 160 : 140, after: 60, align: AlignmentType.LEFT }));
      else if (listening && /^[男女]：/.test(b.text)) out.push(transcriptLine(b.text));
      else out.push(textPara(b.text, { keep: next && next.t === 'table' }));
    } else if (b.t === 'table') out.push(table(b.rows), gap(100));
    else if (b.t === 'ul') {
      if (listening) out.push(...b.items.map(transcriptLine));
      else out.push(...listItems(b.items, false));
    } else if (b.t === 'ol') {
      out.push(...listItems(b.items, true));
      if (listening && !olSeen) out.push(...timingTable());
      olSeen = true;
    } else if (b.t === 'quote') out.push(quoteBox(b.paras), gap(100));
    else if (b.t === 'h3') out.push(subPara(b.text));
    else throw new Error(`教师版不认识的块：${b.t}`);
  }
  return trimGaps(out);
}
function keyDoc() {
  const secs = D.sections.filter((s) => !(s.title === '注意事项' || /^第[一二三四]部分/.test(s.title)));
  const m = D.title.match(/^(.+?)（(.+)）$/);
  const head = [
    para(runs(m[1], { font: FH, size: 32, bold: true }), { align: AlignmentType.CENTER, after: 40, auto: true }),
    para(runs(`（${m[2]}）`, { size: 22 }), { align: AlignmentType.CENTER, after: 60 }),
    para(runs('答案与评分说明（教师用）', { font: FH, size: 26, bold: true }), { align: AlignmentType.CENTER, after: 280, auto: true }),
  ];
  const body = secs.flatMap((s, k) => renderTeacherSection(s, k === 0));
  return { label: '答案与评分说明', children: [...head, ...body], file: '答案与评分说明' };
}

// ---------------------------------------------------------------- 输出
async function write(spec) {
  const footer = new Footer({ children: [P({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: [`${spec.label} 第 `, PageNumber.CURRENT, ' 页（共 ', PageNumber.TOTAL_PAGES, ' 页）'], font: F, size: 18 })] })] });
  const doc = new Document({
    creator: 'spanish-video-kit', title: `${D.title} · ${spec.file}`, description: `${D.title}：${spec.file}`,
    styles: { default: { document: { run: { font: F, size: SZ, language: LANG }, paragraph: { spacing: { line: LINE } } } } },
    sections: [{ properties: { page: { size: { width: PAGE_W, height: PAGE_H }, margin: { top: MY, bottom: MY, left: MX, right: MX, header: 500, footer: 560 } } },
      footers: { default: footer }, children: spec.children }],
  });
  const buf = await Packer.toBuffer(doc);
  const JSZip = require('jszip');
  const zip = await JSZip.loadAsync(buf);
  let st = await zip.file('word/styles.xml').async('string');
  // 行末标点不伸出版心
  if (st.includes('<w:pPrDefault><w:pPr>')) st = st.replace('<w:pPrDefault><w:pPr>', '<w:pPrDefault><w:pPr><w:overflowPunct w:val="0"/>');
  else if (st.includes('<w:pPrDefault>')) st = st.replace(/<w:pPrDefault>(<w:pPr[^>]*\/>)?/, '<w:pPrDefault><w:pPr><w:overflowPunct w:val="0"/></w:pPr>');
  else st = st.replace('<w:docDefaults>', '<w:docDefaults><w:pPrDefault><w:pPr><w:overflowPunct w:val="0"/></w:pPr></w:pPrDefault>');
  if (!st.includes('overflowPunct')) throw new Error('styles.xml: overflowPunct 没加上');
  zip.file('word/styles.xml', st);
  const out = path.join(OUTDIR, `${spec.file}.docx`);
  fs.writeFileSync(out, await zip.generateAsync({ type: 'nodebuffer', compression: 'DEFLATE' }));
  console.log(out);
}
(async () => {
  fs.mkdirSync(OUTDIR, { recursive: true });
  for (const f of [paperDoc, cardDoc, keyDoc]) await write(f());
})().catch((e) => { console.error(e.stack || e.message); process.exit(1); });
