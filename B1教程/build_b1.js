// 《西班牙语 B1 教程》生成：student/*.md、teacher/*.md、audio/*.md（约定的简化 Markdown）→ 学生用书、教师用书 docx
// （排版程序沿用《西班牙语高考白皮书》的 build_gaokao.js）
// 用法：node build_a1.js student|teacher [输出文件]
const fs = require('fs');
const path = require('path');
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, Bookmark, PageReference, InternalHyperlink, TabStopType,
  Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle, AlignmentType, Header, Footer, PageNumber,
  LevelFormat, TableLayoutType, VerticalAlign, Tab,
} = require('docx');

const HERE = __dirname;
const MODE = process.argv[2];
if (!['student', 'teacher'].includes(MODE)) { console.error('用法：node build_a1.js student|teacher [输出文件]'); process.exit(1); }
const BOOK = MODE === 'student' ? '学生用书' : '教师用书';
const CH = HERE;
const OUT = process.argv[3] || path.join(HERE, 'out', `西班牙语B1教程_${BOOK}.docx`);
const F = { ascii: 'PingFang SC', hAnsi: 'PingFang SC', eastAsia: 'PingFang SC', cs: 'PingFang SC' };
const LANG = { value: 'es-ES', eastAsia: 'zh-CN' };
const COL = { wine: '24583A', saffron: 'C98A2B', saffronSoft: 'FCEFD8', ink: '1F2933', body: '3E4C59', muted: '6B7785',
  teal: '2F6F73', tealSoft: 'E3F0EF', tint: 'EEF3F8', line: 'C9D3DE' };   // B1 用深绿做主色（A1 酒红、A2 深蓝），名字 wine 沿用
const PAGE_W = 11906, PAGE_H = 16838, MARGIN = 1134, CONTENT_W = PAGE_W - 2 * MARGIN;
const CN = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十'];

const U = (d, ids) => ids.map((u) => `${d}/u${u}.md`);
const PARTS = MODE === 'student' ? [
  { title: '第 1–5 单元', chapters: U('student', ['01', '02', '03', '04', '05', 'R1']) },
  { title: '第 6–10 单元', chapters: U('student', ['06', '07', '08', '09', '10', 'R2']) },
  { title: '附录', appendix: true, chapters: ['student/appA.md', 'student/appB.md', { gen: () => glossary(), compact: true }, { gen: () => transcripts() }] },
] : [
  { title: '第 1–5 单元', chapters: U('teacher', ['01', '02', '03', '04', '05', 'R1']) },
  { title: '第 6–10 单元', chapters: U('teacher', ['06', '07', '08', '09', '10', 'R2']) },
  { title: '阶段测试', chapters: U('teacher', ['T1', 'T2']) },
];

// ---------------------------------------------------------------- 简化 Markdown 解析
function parse(md, src) {
  const blocks = [];
  const lines = md.replace(/\r/g, '').split('\n');
  let i = 0;
  const err = (m) => { throw new Error(`${src}:${i + 1}: ${m}`); };
  while (i < lines.length) {
    const raw = lines[i], t = raw.trim();
    if (!t) { i++; continue; }
    let m;
    if ((m = /^(#{2,4}) (.+)$/.exec(t))) { blocks.push({ type: 'h' + m[1].length, text: m[2].trim() }); i++; continue; }
    if (/^#/.test(t)) err('标题只能用 ##、###、####');
    if (/^\|/.test(t)) {
      const rows = [];
      while (i < lines.length && /^\|/.test(lines[i].trim())) {
        const r = lines[i].trim();
        if (!/^\|[\s:|-]+\|$/.test(r)) rows.push(r.replace(/^\||\|$/g, '').split('|').map((c) => c.trim()));
        i++;
      }
      const n = rows[0].length;
      rows.forEach((r, k) => { if (r.length !== n) throw new Error(`${src}: 表格第 ${k + 1} 行有 ${r.length} 列，表头 ${n} 列：${r.join(' | ')}`); });
      blocks.push({ type: 'table', rows });
      continue;
    }
    if (/^> /.test(t)) {
      const ex = [];
      while (i < lines.length && /^> /.test(lines[i].trim())) {
        const s = lines[i].trim().slice(2), k = s.indexOf('｜');
        ex.push(k < 0 ? [s, ''] : [s.slice(0, k).trim(), s.slice(k + 1).trim()]);
        i++;
      }
      blocks.push({ type: 'ex', ex });
      continue;
    }
    if (/^! /.test(t)) { blocks.push({ type: 'note', text: t.slice(2) }); i++; continue; }
    // @换页：下一段另起一页（LibreOffice 不理会例句框后面的“与下段同页”，个别框和题目分页时用）
    if (t === '@换页') {
      i++; while (i < lines.length && !lines[i].trim()) i++;
      const nt = (lines[i] || '').trim();
      if (!nt || /^[-|>#!@]/.test(nt)) throw new Error(`${src}: @换页 后面必须是普通段落`);
      blocks.push({ type: 'p', text: nt, breakBefore: true }); i++; continue;
    }
    if (/^@音频 /.test(t)) { blocks.push({ type: 'audio', id: t.slice(4).trim() }); i++; continue; }
    if (/^- /.test(t)) {
      const items = [];
      while (i < lines.length && /^\s*- /.test(lines[i])) {
        const l = lines[i];
        items.push({ level: /^\s{2,}- /.test(l) ? 1 : 0, text: l.trim().slice(2) });
        i++;
      }
      blocks.push({ type: 'ul', items });
      continue;
    }
    blocks.push({ type: 'p', text: t }); i++;
  }
  if (!blocks.length || blocks[0].type !== 'h2') throw new Error(`${src}: 第一行必须是 ## 章标题`);
  if (blocks.filter((b) => b.type === 'h2').length !== 1) throw new Error(`${src}: 只能有一个 ## 章标题`);
  return blocks;
}

// 行内：**加粗**、〔出处〕
function runs(text, o = {}) {
  const out = [];
  const parts = String(text).split(/(\*\*[^*]+\*\*)/g);
  for (const p of parts) {
    if (!p) continue;
    const bold = /^\*\*[^*]+\*\*$/.test(p);
    const s = bold ? p.slice(2, -2) : p;
    for (const q of s.split(/(〔[^〕]*〕)/g)) {
      if (!q) continue;
      const ref = /^〔[^〕]*〕$/.test(q);
      // 连读符号 ‿ 苹方里没有：单独一段用 Hiragino Maru Gothic（不加粗；加粗时 LibreOffice 会换成 DejaVu Sans Bold）；
      // 数字空格 U+2007（词表短语、“A Fidel”里的不断行空格）单独一段、字号缩小到普通空格的宽度
      for (const r of q.split(/(‿|\u2007)/g)) {
        if (!r) continue;
        const sz = ref ? Math.round((o.size || 21) * 0.86) : o.size || 21;
        out.push(new TextRun({ text: r, font: r === '‿' ? 'Hiragino Maru Gothic ProN' : F, language: LANG, size: r === '\u2007' ? Math.round(sz * 0.52) : sz,
          bold: r === '‿' ? false : o.bold || bold, color: ref ? COL.teal : o.color || COL.ink }));
      }
    }
  }
  return out;
}
function textW(s) { let w = 0; for (const ch of String(s)) w += /[⺀-鿿＀-￯　-〿…—‘’“”←-⇿]/.test(ch) ? 1 : 0.55; return w; }
// 列表项估计排几行；subGroup：第 k 项所在的那一组子项（第二层）
const itemLines = (items) => items.reduce((a, x) => a + Math.max(1, Math.ceil(textW(x.text) / 40)), 0);
// 一块内容大约排几行（例句框按句、表格按行）
const blockLines = (b) => b.type === 'ex' ? b.ex.reduce((a, [es, zh]) => a + Math.ceil((textW(es) + (zh ? textW(zh) : 0)) / 44), 0)
  : b.type === 'table' ? b.rows.length : b.type === 'ul' ? itemLines(b.items) : Math.ceil(textW(b.text || '') / 44);
// 表格里“el asiento de ventanilla / de pasillo”这类：斜线后面两三个词的短说法内部不断行（数字空格，runs() 里缩小）
const altJoin = (c) => String(c).replace(/ \/ ((?:[A-Za-zÁÉÍÓÚáéíóúñÑü]+ ){1,2}[A-Za-zÁÉÍÓÚáéíóúñÑü]+)(?=$|[ ,，;；)）])/g, (m, w) => ' / ' + w.replace(/ /g, '\u2007'));
function subGroup(items, k) { let s = k, e = k; while (s > 0 && items[s - 1].level > 0) s--; while (e < items.length - 1 && items[e + 1].level > 0) e++; return items.slice(s, e + 1); }

// ---------------------------------------------------------------- 排版
let bm = 0;
const toc = [];
const nb = (s) => String(s)
  // 录音号整体不断行：【音频 6-3】（不换行空格＋连字符两边加 WJ，2026-10 测试过）；sa-/BA-do 这类斜线两边不断；
  // 西语词和后面的数字不断行（residencia 1、las 8）
  .replace(/(^|[^\w])((?:\d{1,2}|R\d|T\d))-(?=(?:Q?\d|V)\b)/g, '$1$2\u2060-\u2060')
  .replace(/【音频 ([^】]+)】/g, (m, id) => `【\u2060音\u2060频\u00a0${id.replace(/-/g, '\u2060-\u2060')}\u2060】`).replace(/%–/g, '%\u2060–\u2060')
  .replace(/([A-Za-zÁÉÍÓÚáéíóúñ–-])\/(?=[A-Za-zÁÉÍÓÚáéíóú])/g, '$1\u2060/\u2060')
  .replace(/([a-záéíóúñ]) (?=\d)/g, '$1\u00a0').replace(/(\d) (?=[€$]|euros?\b|yuan(es)?\b|pesos?\b)/g, '$1\u00a0').replace(/(\S)(?=…)/g, '$1\u2060').replace(/ (?=…)/g, '\u00a0')
  .replace(/([a-záéíóúA-ZÁÉÍÓÚ])-(?=[a-záéíóúA-ZÁÉÍÓÚ])/g, '$1\u2060-\u2060').replace(/(\d) (?=\d{3}(?!\d))/g, '$1\u00a0').replace(/(\d) (?=_{3,})/g, '$1\u00a0').replace(/(_{3,}) (?=\()/g, '$1\u00a0').replace(/(\d) (?=%)/g, '$1\u00a0').replace(/(\d)～(?=\d)/g, '$1\u2060～\u2060').replace(/([×√]) (?=\S)/g, '$1\u00a0').replace(/(\d)—(?=\d)/g, '$1\u2060—\u2060').replace(/(\d) (?=\d)/g, '$1\u00a0').replace(/([\u4e00-\u9fff])(?=）)/g, '$1\u2060').replace(/([（：，、；])(\d+)[ \u00a0](?=[\u4e00-\u9fff])/g, '$1$2\u2060')
  .replace(/([–-])(?=[a-záéíóúñü])/g, '$1\u2060').replace(/… (o|ni|y)…/g, '…\u00a0$1…')
  .replace(/—(?=[¿¡A-Za-zÁÉÍÓÚÑáéíóúñ])/g, '—\u2060').replace(/——/g, '—\u2060—')
  // “、-iste、-o”：连字符前面不能断行，整串词尾连成一块会把行尾空出一大截；顿号后面加零宽空格允许在这里转行
  .replace(/([、，；])(?=[-–]\u2060?[a-záéíóúñ])/g, '$1\u200b')
  // “说的是谁：A Fidel，B Carolina，C 两个人都不是”：选项字母和后面的人名不分开
  // 用数字空格（runs() 和 hr() 里缩小字号）：不换行空格会让 LibreOffice 在人名中间断行（A Man / uel）
  .replace(/([：:，、])([A-J]) (?=\S)/g, '$1$2\u2007')
  .replace(/([0-9A-Za-z])–(?=[0-9A-Za-z])/g, '$1\u2060–\u2060').replace(/([)）]) (?=_)/g, '$1\u00a0')
  .replace(/, (?=[-–]\u2060?[a-z]{1,3}\b)/g, ',\u00a0').replace(/(\S)(?=……)/g, '$1\u2060')
  // 数字和后面汉字之间的空格不断行（30 分钟、2026 年 10 月）。数字前面的空格保留普通空格：
  // 汉字和数字之间用不换行空格时，LibreOffice 把数字当成中文排，会在数字中间断行（9 / 0 分）
  .replace(/(\d) (?=[\u4e00-\u9fff])/g, '$1\u00a0').replace(/\b(Tareas?|Opción|Situación) (?=\d|[A-Z]\b)/g, '$1\u00a0');
// 标题里的数字空格（U+2007）和正文 runs() 一样缩小字号
function hr(text, o, brk = false) {
  return String(text).split(/(\u2007)/).filter(Boolean).map((t, i) => new TextRun({ ...o, text: t, ...(t === '\u2007' ? { size: Math.round(o.size * 0.52) } : {}), ...(brk && i === 0 ? { break: 1 } : {}) }));
}
function heading(level, label, text, tocLevel, splitZh = false, breakBefore = false, keep = true) {
  const id = `b${++bm}`;
  const full = label ? `${label}　${text}` : text;
  // 长标题在“（”前转行；单元标题没有“（”的，在西语和中文之间的全角空格处转行（不让“样？”单独成行）
  const kp = full.lastIndexOf('（'), ks = level === 2 && kp < 0 ? full.lastIndexOf('　') : -1;
  const k = kp > 0 ? kp : ks, skip = kp > 0 ? 0 : 1;
  const two = splitZh && k > 0 && textW(full) > (level === 2 ? 22 : 34);
  if (tocLevel !== null) toc.push({ id, text: full, level: tocLevel });
  const size = { 1: 56, 2: 40, 3: 28, 4: 24 }[level];
  const color = level === 4 ? COL.ink : COL.wine;
  return new Paragraph({
    heading: [null, HeadingLevel.HEADING_1, HeadingLevel.HEADING_2, HeadingLevel.HEADING_3, HeadingLevel.HEADING_4][level],
    pageBreakBefore: breakBefore || level <= 2 || (level === 3 && /^(参考答案|[一二三四五]　|本测试录音稿)/.test(text)),
    keepNext: keep, keepLines: true,
    spacing: { before: { 1: 2400, 2: 0, 3: 360, 4: 240 }[level], after: { 1: 240, 2: 320, 3: 160, 4: 120 }[level] },
    border: level === 2 ? { bottom: { style: BorderStyle.SINGLE, size: 12, color: COL.saffron, space: 6 } } : undefined,
    children: [new Bookmark({ id, children: two
      ? [...hr(nb(full.slice(0, k)), { font: F, language: LANG, size, bold: true, color }), ...hr(nb(full.slice(k + skip)), { font: F, size, bold: true, color }, true)]
      : hr(nb(full), { font: F, language: LANG, size, bold: true, color }) })],
  });
}
function para(text, o = {}) {
  return new Paragraph({ alignment: AlignmentType.LEFT, widowControl: true, indent: { right: 110 }, spacing: { after: 110, line: 320 }, children: runs(nb(text), o), ...o.p });
}
function borders(color = COL.line, size = 4) {
  const b = { style: BorderStyle.SINGLE, size, color };
  return { top: b, bottom: b, left: b, right: b, insideHorizontal: b, insideVertical: b };
}
const NONE = { style: BorderStyle.NONE, size: 0, color: 'FFFFFF' };
function boxTable(children, fill, leftColor) {
  return new Table({
    width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: [CONTENT_W], layout: TableLayoutType.FIXED,
    borders: { top: NONE, bottom: NONE, right: NONE, insideHorizontal: NONE, insideVertical: NONE,
      left: { style: BorderStyle.SINGLE, size: 18, color: leftColor } },
    rows: [new TableRow({ cantSplit: !(children.__long), children: [new TableCell({ width: { size: CONTENT_W, type: WidthType.DXA },
      shading: { type: ShadingType.CLEAR, color: 'auto', fill }, margins: { top: 100, bottom: 100, left: 180, right: 180 }, children })] })],
  });
}
function spacer(keep = false) { const sp = new Paragraph({ spacing: { after: 0, before: 0, line: 200, lineRule: 'exact' }, keepNext: keep, children: [] }); sp.__spacer = true; return sp; }
function table(rows, o = {}) {
  const n = rows[0].length;
  // 列宽：按每列最长内容估算（封顶），再按比例分满
  // 每列：最长内容（封顶 40）和平均长度各占一部分，长列不会被压得太窄
  let need = rows[0].map((_, j) => {
    const ls = rows.map((r) => textW(r[j]));
    return Math.min(Math.max(...ls), 45) * 0.7 + ls.reduce((a, b) => a + b, 0) / ls.length * 0.3 + 2;
  });
  if (n === 4 && rows[0][0] === rows[0][2] && rows[0][1] === rows[0][3]) need = [0, 1, 0, 1].map((_, j) => (need[j % 2] + need[j % 2 + 2]) / 2);
  if (o.widths) need = o.widths;
  else if (rows[0].join('|') === '课|课文|语法') need = [2.5, 18.5, 40];
  // 附录 C 词汇总表：西语栏放宽到长短语（medicina tradicional china）排一行，中文栏转行可以接受
  else if (rows[0].join('|') === '西语|词性|中文|单元') need = [2600, 1068, 5011, 955];
  const size = o.size || 19;
  const sum = need.reduce((a, b) => a + b, 0);
  let ws = need.map((x) => Math.max(Math.round(CONTENT_W * x / sum), Math.round(CONTENT_W * 0.08)));
  const k = CONTENT_W / ws.reduce((a, b) => a + b, 0); ws = ws.map((w) => Math.floor(w * k));
  // 每列一行排下最长内容需要的宽度（字宽 × 字号 + 左右边距）；总和放得下就先满足它，余下的按比例分
  const full = rows[0].map((_, j) => Math.ceil(Math.max(...rows.map((r) => textW(r[j]))) * size * 10 * 1.12) + 260);
  const fsum = full.reduce((a, b) => a + b, 0);
  if (fsum <= CONTENT_W) ws = full.map((f) => Math.floor(f + (CONTENT_W - fsum) * f / fsum));
  else {
    const tok = (c, i) => Math.max(textW(c) <= (i === 0 ? 6 : 5) ? textW(c) : 0, ...String(c).replace(/\*\*/g, '').split(/[\s⺀-鿿＀-￯　-〿]+/).map((t) => textW(t)), 2);
    const minW = rows[0].map((_, j) => Math.ceil(Math.max(...rows.map((r, i) => tok(r[j], i))) * size * 10 * 1.12) + 260);
    for (let pass = 0; pass < 3; pass++) {
      const lack = ws.reduce((a, w, j) => a + Math.max(0, minW[j] - w), 0);
      if (!lack) break;
      const slack = ws.reduce((a, w, j) => a + Math.max(0, w - minW[j]), 0);
      if (slack < lack) break;
      ws = ws.map((w, j) => w < minW[j] ? minW[j] : Math.floor(w - lack * (w - minW[j]) / slack));
    }
  }
  // 两组“西班牙语 | 中文”并排的词汇表：左右两组列宽相同
  if (n === 4 && rows[0][0] === rows[0][2] && rows[0][1] === rows[0][3]) {
    const es = Math.floor((ws[0] + ws[2]) / 2), zh = Math.floor(CONTENT_W / 2) - es;
    ws = [es, zh, es, CONTENT_W - 2 * es - zh];
  }
  // 9 行以内（含表头）整表不拆；更长的表可以跨页，但两边至少各留 3 行
  const tall = rows.reduce((a, r) => a + Math.max(...r.map((c, j) => Math.ceil(textW(c) * size * 10 * 1.04 / Math.max(ws[j] - 180, 200)))), 0) > 8;
  const keepRow = (i) => o.keepLast ? true : o.whole || (rows.length <= 8 && !o.split && !tall) ? i < rows.length - 1
    : rows.length <= 9 ? i <= 1 || (i >= rows.length - 2 && i < rows.length - 1) : i <= 2 || (i >= rows.length - 3 && i < rows.length - 1);
  return new Table({
    width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: ws, layout: TableLayoutType.FIXED, borders: borders(),
    rows: rows.map((r, i) => new TableRow({ tableHeader: i === 0, cantSplit: true, children: r.map((c, j) => new TableCell({
      width: { size: ws[j], type: WidthType.DXA }, verticalAlign: VerticalAlign.CENTER,
      shading: { type: ShadingType.CLEAR, color: 'auto', fill: i === 0 ? COL.teal : i % 2 ? 'FFFFFF' : COL.tint },
      margins: o.compact ? { top: 15, bottom: 15, left: 80, right: 80 } : { top: 50, bottom: 50, left: 90, right: 90 },
      children: [new Paragraph({ spacing: { after: 0, line: o.compact ? 240 : 280 }, keepNext: keepRow(i),
        children: runs(nb(altJoin(c)), { size, bold: i === 0, color: i === 0 ? 'FFFFFF' : COL.ink }) })],
    })) })),
  });
}
function examples(ex, keepAfter = false, whole = false) {
  // 每句一段。估算排出来的行数：整框 8 行以内不拆；更长的框可以在句间跨页，超过 6 行的长段落本身也可以跨页。
  // 短的首句（标题、称呼）和末句（署名）和相邻的一句放在同一格里，不会单独留在另一页
  const n = ex.length;
  const lines = ex.map(([es, zh]) => Math.ceil((textW(es) + (zh ? textW(zh) * 0.95 + 1 : 0)) / 44));
  const total = lines.reduce((a, b) => a + b, 0);
  const small = total <= 8 || (whole && total <= 40);
  const paras = ex.map(([es, zh], k) => new Paragraph({ spacing: { after: k < n - 1 ? 80 : 0, line: 300 },
    keepNext: (k < n - 1 && small) || (k === n - 1 && keepAfter), keepLines: lines[k] <= 6, widowControl: true,
    children: [...runs(nb(es), { size: 20, bold: true, color: COL.ink }), ...(zh ? [new TextRun({ text: '　', font: F, size: 20 }), ...runs(nb(zh), { size: 19, color: COL.muted })] : [])] }));
  const head = (k) => /^(Opción|Situación|Tema|Texto|Mensaje|Diálogo|Fragmento|Grabación)\b/.test(ex[k][0]) || /[:：]$/.test(ex[k][0].trim());
  const groups = [];
  ex.forEach((_, k) => {
    const joinPrev = !small && k > 0 && ((k === 1 && lines[0] <= 3) || (k === n - 1 && lines[k] <= 3 && !(k === 1 && lines[0] <= 3 && groups.length === 1 && groups[0].length > 1))
      || (/^√/.test(ex[k][0]) && /^[×√]/.test(ex[k - 1][0])) || /^播音[:：]/.test(ex[k - 1][0]));  // × 句和 √ 句、播音段号和后面的对话不分页
    const last = groups[groups.length - 1];
    // 以 Opción、Situación 等开头的一组，在凑够 4 行以前继续把后面的句子并进来（标题、导语和要求不分页）
    const headJoin = !small && last && head(last[0]) && last.reduce((a, j) => a + lines[j], 0) <= 4;
    if (joinPrev || headJoin) last.push(k); else groups.push([k]);
  });
  const glines = (g) => g.reduce((a, k) => a + lines[k], 0);
  while (!small && groups.length > 1 && glines(groups[0]) <= 3) groups.splice(0, 2, groups[0].concat(groups[1]));
  while (!small && groups.length > 1 && glines(groups[groups.length - 1]) <= 3) groups.splice(-2, 2, groups[groups.length - 2].concat(groups[groups.length - 1]));
  const G = groups.length;
  return new Table({
    width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: [CONTENT_W], layout: TableLayoutType.FIXED,
    borders: { top: NONE, bottom: NONE, right: NONE, insideVertical: NONE,
      insideHorizontal: { style: BorderStyle.SINGLE, size: 4, color: COL.saffronSoft },
      left: { style: BorderStyle.SINGLE, size: 18, color: COL.saffron } },
    rows: groups.map((g, gi) => new TableRow({ cantSplit: glines(g) <= 6 || (g.length > 1 && glines(g) <= 14), children: [new TableCell({
      width: { size: CONTENT_W, type: WidthType.DXA }, shading: { type: ShadingType.CLEAR, color: 'auto', fill: COL.saffronSoft },
      margins: { top: gi === 0 ? 100 : 0, bottom: gi === G - 1 ? 100 : 0, left: 180, right: 180 }, children: g.map((k) => paras[k]) })] })),
  });
}
function note(text) {
  const kids = [new Paragraph({ spacing: { after: 0, line: 300 }, children: [new TextRun({ text: '注意　', font: F, size: 20, bold: true, color: COL.teal }), ...runs(nb(text), { size: 20 })] })];
  kids.__long = textW(text) > 6 * 44;
  return boxTable(kids, COL.tealSoft, COL.teal);
}

const LABEL = /^(原创样题|样题|听力原文|录音原文|范文|示范回答|示范对话|示范|做题方法|题型说明|评分时看什么|讲解|准备提纲|任务卡)/;
function labelize(t) {
  if (t.includes('**')) return t;
  if (/：$/.test(t) && textW(t) <= 14) return `**${t}**`;
  const m = t.match(/^([^（：]{2,8})(：|（)/);
  if (m && LABEL.test(t)) return m[2] === '：' ? `**${m[1]}：**${t.slice(m[0].length)}` : `**${m[1]}**${t.slice(m[1].length)}`;
  if (LABEL.test(t) && textW(t) <= 8) return `**${t}**`;
  return t;
}
const QLAB = /^(\d{1,3}\.|\d{1,3}(?= \*\*)|例 \d+)[ 　]/, OLAB = /^([A-D]\.)[ 　](?!.* B\. )/;
function renderChapter(blocks, label, tocSections) {
  const out = [];
  let sec = 0;
  blocks.forEach((b, bi) => {
    const nxt = blocks[bi + 1], prev = blocks[bi - 1];
    if (b.type === 'p') b.text = labelize(b.text);
    if (b.type === 'p' && nxt && !/^h[234]$/.test(nxt.type)) { const t = b.text.replace(/\*\*/g, ''); if (textW(t) <= 30 || (textW(t) <= 50 && !/[。.!?！？…]$/.test(t))) b.keep = true; }
    if (b.type === 'p' && nxt && (label.index || (prev && /^h[34]$/.test(prev.type) && textW(b.text) < 60))) b.keep = true;
    if (b.type === 'p' && nxt && (['table', 'ex', 'note'].includes(nxt.type) && (label.index || textW(b.text) < 80) || ['table', 'ex', 'note', 'ul'].includes(nxt.type) && /[：:]$/.test(b.text) && (textW(b.text) <= 88 || blockLines(nxt) <= 8))) b.keep = true;   // 三行以上的引导段和八行以上的框不硬连（整块挪页会空出半页）
    // 题目说明（“三、语法和词汇（6 分）：……”“……（Escucha y relaciona.）【音频 2-Q1】”“选项：A. …”）和下面的列表不分页；
    // 两行以内的引导段和后面六行以内的短列表（“任务二　对话……”和话题 A、B）也不分页
    if (b.type === 'p' && nxt && nxt.type === 'ul') {
      const t = b.text.replace(/\*\*/g, '');
      if ((textW(t) <= 200 && (/^[一二三四五六七八九十]、/.test(t) || /【音频[^】]+】$/.test(t) || /（[¿¡A-Z][^（）]*[.?!]）$/.test(t) || /^(选项|选词)[：:]/.test(t)))
        || (textW(t) <= 88 && itemLines(nxt.items) <= 6)) b.keep = true;
    }
    // 列表最后一项和后面的框连在一起：框八行以内，或者列表本身八行以内（选项连同短文第一段整块挪页会空出半页）
    if (b.type === 'ul' && nxt && ['table', 'ex', 'note'].includes(nxt.type) && (nxt.type !== 'ex' || blockLines(nxt) <= 8 || itemLines(b.items) <= 8)) b.keepLast = true;
    // 只有标题的练习（“练习 22　听录音跟读……【音频 7-5】”）后面紧接着下一个标题时不硬连
    if (b.type === 'h4' && /^练习 /.test(b.text) && nxt && /^h[34]$/.test(nxt.type)) b.loose = true;
    if (b.type === 'ul' && nxt && nxt.type === 'p' && textW(nxt.text.replace(/\*\*/g, '')) <= 80 && (!blocks[bi + 2] || /^h[234]$/.test(blocks[bi + 2].type))) b.keepLast = true;   // 题目列表后面一两行的说明（“规律：……”）不单独落到下一页
    const isLab = (x) => x && x.type === 'p' && LABEL.test(x.text.replace(/\*\*/g, ''));
    if (b.type === 'p' && nxt && nxt.type === 'p' && /,$/.test(nxt.text) && textW(nxt.text) <= 12) b.keep = true;
    if (b.type === 'p' && isLab(prev) && nxt && !/^h[234]$/.test(nxt.type) && textW(b.text) <= 150) b.keep = true;
    if (b.type === 'ex' && isLab(prev) && nxt && ['ul', 'p'].includes(nxt.type) && b.ex.reduce((a, [es, zh]) => a + textW(es) + (zh ? textW(zh) : 0), 0) <= 3 * 44) b.keepAfter = true;
    // 阶段测试的阅读短文和后面的题目不分页（只连短文最后一段和第一题）
    if (b.type === 'ex' && label.keepTasks && nxt && nxt.type === 'ul') b.keepAfter = true;
    // 排序题：选项和下面的“顺序：___ → ___”整块不分页
    if (b.type === 'ul' && nxt && nxt.type === 'p' && /^顺序[：:]/.test(nxt.text) && b.items.length <= 10) b.orderList = b.keepLast = true;
  });
  // 阶段测试：每个任务（#### 到下一个标题之间）串成一组，尽量排在同一页，复印出来题和原文、选项在一张纸上
  // 阶段测试：每个部分的第一个任务紧跟部分标题，其余任务另起一页；任务估计排得下一页（约 42 行）才整块连在一起，
  // 否则正常排（LibreOffice 对超过一页的连锁会留大片空白）
  if (label.keepTasks) {
    const est = (b) => b.type === 'p' ? Math.ceil(textW(b.text) / 44) + 0.5
      : b.type === 'ul' ? b.items.reduce((a, x) => a + Math.ceil(textW(x.text) / 40), 0) + 0.5
      : b.type === 'ex' ? b.ex.reduce((a, [es, zh]) => a + Math.ceil((textW(es) + (zh ? textW(zh) : 0)) / 44), 0) + 1.5
      : b.type === 'table' ? b.rows.length * 1.4 + 1 : 1;
    // 只管试卷部分（从“一　听力”到“参考答案”之前）；短任务（约 30 行以内）整块连在一起，长任务正常排
    let start = -1, inPaper = false, reading = false, firstInPart = false;
    const close = (end) => {
      if (start < 0) return;
      const body = blocks.slice(start + 1, end);
      const fits = body.reduce((a, b) => a + est(b), 2) <= 30;
      body.forEach((b, k) => { b.inTask = fits; b.chain = fits && k < body.length - 1; });
      start = -1;
    };
    blocks.forEach((b, bi) => {
      if (b.type === 'h3') { close(bi); inPaper = /^[一二三四五]　/.test(b.text); reading = /^[一二三四五]　阅读/.test(b.text); firstInPart = true; }
      else if (b.type === 'h2') close(bi);
      else if (b.type === 'h4') { close(bi); if (inPaper) start = bi; if (reading && !firstInPart) b.taskBreak = true; firstInPart = false; }
    });
    close(blocks.length);
  }
  // 横排的选项（A. … B. … C. …）选项内部不断行，只在选项之间断
  const hz = (t) => (/[　 ][B-J]\. /.test(t) ? t.split('　').map((o) => (o.length <= 20 ? o.replace(/ (?![A-J]\. )/g, '\u00a0') : o.replace(/^([A-J]\.) /, '$1\u00a0'))).join('　') : t);
  blocks.forEach((b, bi) => {
    if (b.type !== 'table') return;
    const before = blocks.slice(Math.max(0, bi - 2), bi).map((x) => x.text || '').join(' ');
    if (/剪开|卡片|可复印/.test(before)) b.whole = true;
  });
  for (const b of blocks) {
    if (b.type === 'h2') out.push(heading(2, label.chapter, b.text, 1, true));
    else if (b.type === 'h3') { sec += 1; out.push(heading(3, label.section(sec), b.text, tocSections ? 2 : null, !!label.index)); }
    else if (b.type === 'h4') out.push(heading(4, '', b.text, null, false, !!b.taskBreak, !b.loose));
    // 词表（“选词：”开头，或六个以上用全角空格隔开的西语短语）：每个短语内部不断行
    else if (b.type === 'p') out.push(para(/^选词[：:]/.test(b.text) || (b.text.split('　').length >= 6 && b.text.split('　').every((w) => w.length <= 30 && !/[\u4e00-\u9fff]/.test(w)))
      // 短语内部用数字空格 U+2007（runs() 里缩小字号，宽度和普通空格差不多）。2026-10 在 LibreOffice 26.8 试过：
      // 不换行空格会在词中间断行（el ch / ubasco），“空格＋WJ”照样在空格处断开（las / prácticas），只有数字空格两样都不出
      ? b.text.split('　').map((w, i) => (i ? w.replace(/ /g, '\u2007') : w.replace(/^(选词[：:])?(.*)$/, (m, a, c) => (a || '') + c.replace(/ /g, '\u2007')))).join('　')
      // 段落里的选项（“选项：A. …　B. …”）：选项字母和后面第一个词不分开（同样用缩小的数字空格）
      : b.text.replace(/(^|[：:　])([A-J])\. (?=\S)/g, '$1$2.\u2007'), { p: { ...(b.keep || b.chain ? { keepNext: true, keepLines: true } : {}), ...(b.breakBefore ? { pageBreakBefore: true } : {}) } }));
    // 题目列表（第一层全是“数字. ”或“例 N”开头）不用项目符号：题号、选项字母后面用制表符，悬挂缩进，转行和首行正文对齐
    else if (b.type === 'ul') b.items.forEach((it, k, all, q = all.filter((x) => x.level === 0).every((x) => QLAB.test(x.text)),
      m = q && (it.level === 0 ? QLAB : OLAB).exec(it.text)) => out.push(new Paragraph({
      ...(q ? { indent: it.level === 0 ? { left: 480, hanging: 480, right: 110 } : m ? { left: 900, hanging: 360, right: 110 } : { left: 540, right: 110 } }
        : { numbering: { reference: 'bullets', level: it.level }, indent: { right: 110 } }),
      // 六行以内的项整段不拆；教师用书里大半页长的答案条目（参考范文）可以跨页，否则整条挪页会空出半页
      keepLines: Math.ceil(textW(it.text) / 40) <= 6, widowControl: true,
      keepNext: (!!b.inTask && (k < b.items.length - 1 || b.chain)) || (k < b.items.length - 1 && b.items.length <= 10 && b.items.every((x) => /^([A-Z]\.|[a-z]\)|\d+\.) /.test(x.text)) && b.items.reduce((a, x) => a + textW(x.text), 0) <= 160) || (k < b.items.length - 1 && b.items.length <= 4 && b.items.reduce((a, x) => a + textW(x.text), 0) <= 120) || (b.items.length >= 2 && k === b.items.length - 2 && textW(b.items[b.items.length - 1].text) <= 90) || (!!b.orderList && k < b.items.length - 1)
        // 字母选项（A. B. C. …）整组不超过 14 行就不分页
        || (k < b.items.length - 1 && b.items.length <= 12 && b.items.every((x) => /^[A-Za-z][.)] /.test(x.text)) && itemLines(b.items) <= 14)
        // 最后一题（连同选项）不超过 3 行才和前一项连；子项只在整组不超过 8 行时互相连（长的子列表照常跨页）
        || (k > 0 && k === all.map((x) => x.level).lastIndexOf(0) - 1 && itemLines(all.slice(k + 1)) <= 3) || (!!b.keepLast && k === b.items.length - 1)
        || (k < b.items.length - 1 && ((b.items.length >= 4 && k === 0) || (b.items[k + 1].level === 1 && (it.level === 0 || itemLines(subGroup(all, k + 1)) <= 8)))),
      spacing: { after: 50, line: 300 },
      children: m ? [...runs(m[1]), new TextRun({ children: [new Tab()], font: F, size: 21 }), ...runs(nb(hz(it.text.slice(m[0].length))))] : runs(nb(hz(it.text))) })));
    else if (b.type === 'table') { out.push(table(b.rows, label.compact ? { size: 17, split: true, compact: true } : label.index ? { size: 18, split: true } : b.chain ? { keepLast: true } : b.whole ? { whole: true } : {})); out.push(spacer(!!b.chain)); }
    else if (b.type === 'ex') { out.push(examples(b.ex, b.keepAfter || !!b.chain, !!b.inTask)); out.push(spacer(b.keepAfter || !!b.chain)); }
    else if (b.type === 'note') { out.push(note(b.text)); out.push(spacer()); }
    else if (b.type === 'audio') {
      const tr = AUDIO[b.id];
      if (!tr) throw new Error(`@音频 ${b.id}：录音稿里没有这一段`);
      out.push(new Paragraph({ keepNext: true, spacing: { before: 60, after: 60 },
        children: [new TextRun({ text: `音频 ${b.id}　${tr.title}`, font: F, size: 19, bold: true, color: COL.teal })] }));
      out.push(examples(trackLines(tr, MODE === 'teacher'))); out.push(spacer());
    }
  }
  while (out.length && out[out.length - 1].__spacer) out.pop();
  return out;
}

// ---------------------------------------------------------------- 录音稿、总词汇表、课文译文和听力原文
const UNITS = ['01', '02', '03', '04', '05', 'R1', '06', '07', '08', '09', '10', 'R2'];
const unitName = (u) => (u[0] === 'R' ? `复习 ${u[1]}` : u[0] === 'T' ? `阶段测试 ${u[1]}` : `第 ${Number(u)} 单元`);
// audio/uNN.md → { 录音号: { title, type, roles, lines: [[名字, 西语, 中文]] } }（格式见 编写要求.md，check_unit.py 先查过）
function loadAudio(u) {
  const f = path.join(HERE, 'audio', `u${u}.md`);
  const out = { unit: u, title: '', tracks: [] };
  if (!fs.existsSync(f)) return out;
  let cur = null;
  for (const raw of fs.readFileSync(f, 'utf8').split('\n')) {
    const t = raw.trim();
    let m;
    if ((m = /^## (.+)$/.exec(t))) out.title = m[1];
    else if ((m = /^### (\S+)　(.+)$/.exec(t))) { cur = { id: m[1], title: m[2], type: '', lines: [] }; out.tracks.push(cur); }
    else if (cur && (m = /^- 类型：(.+)$/.exec(t))) cur.type = m[1].trim();
    else if (cur && (m = /^> ([^:：｜]+): (.+?)｜(.*)$/.exec(t))) cur.lines.push([m[1].trim(), m[2].trim(), m[3].trim()]);
  }
  return out;
}
const AUDIO = {};
for (const u of [...UNITS, 'T1', 'T2']) for (const tr of loadAudio(u).tracks) AUDIO[tr.id] = tr;
const SPOKEN = new Set(['对话', '课文', '听力']);
// 一段录音的例句框：对话行前面加说话人；跟读、发音类不加
function trackLines(tr, withZh) {
  const named = ['对话', '听力'].includes(tr.type) || new Set(tr.lines.map((l) => l[0])).size > 1;
  return tr.lines.map(([who, es, zh]) => [named ? `${who}: ${es}` : es, withZh ? (named && zh ? zh : zh) : '']);
}
// 书后总词汇表：收各单元学生用书里表头为“西语｜词性｜中文”的表，同一词（西语＋词性）只收第一次出现的单元
function glossary() {
  const seen = new Map();
  for (const u of UNITS) {
    const f = path.join(HERE, 'student', `u${u}.md`);
    if (!fs.existsSync(f)) continue;
    let inside = false;
    for (const raw of fs.readFileSync(f, 'utf8').split('\n')) {
      const t = raw.trim();
      if (t.replace(/\s/g, '') === '|西语|词性|中文|') { inside = true; continue; }
      if (inside && /^\|/.test(t)) {
        if (/^\|[\s:|-]+\|$/.test(t)) continue;
        const c = t.replace(/^\||\|$/g, '').split('|').map((x) => x.trim());
        const key = `${c[0].replace(/\*\*/g, '').toLowerCase()}\t${c[1]}`;
        const un = u[0] === 'R' ? `复${u[1]}` : String(Number(u));
        if (!seen.has(key)) seen.set(key, [c[0].replace(/\*\*/g, ''), c[1], [c[2]], [un]]);
        else {                                   // 同一个词在后面单元有新义项：释义并列，单元号都列出
          const e = seen.get(key);
          if (!e[2].includes(c[2]) && !e[3].includes(un)) { e[2].push(c[2]); e[3].push(un); }
        }
      } else inside = false;
    }
  }
  const sortKey = (w) => w.replace(/\*\*/g, '').toLowerCase().normalize('NFD').replace(/ñ/g, 'n~').replace(/[̀-ͯ]/g, '').replace(/^[¡¿]/, '');
  const rows = [...seen.values()].map(([w, pos, zh, us]) => [w, pos, zh.join('；'), us.join('、')])
    .sort((a, b) => (sortKey(a[0]) < sortKey(b[0]) ? -1 : sortKey(a[0]) > sortKey(b[0]) ? 1 : 0));
  return ['## Vocabulario　西中词汇总表', '', `本表收全书各单元生词表里的 ${rows.length} 个词和短语，按西语字母顺序排列（ñ 排在 n 后面）；“单元”一栏是收这个词的单元；同一个词在后面单元学了新的意思，释义并列、单元号都列出。`, '',
    '| 西语 | 词性 | 中文 | 单元 |', '| --- | --- | --- | --- |', ...rows.map((r) => `| ${r.join(' | ')} |`)].join('\n');
}
// 书后附录：课文译文和听力原文（对话、课文、听力三类；跟读和发音不收）
function transcripts() {
  const out = ['## Transcripciones　课文译文和听力原文', '', '这里收全书课文和听力练习的录音原文和中文译文，按单元和录音号排列。语音跟读和生词跟读的录音不收。', ''];
  for (const u of UNITS) {
    const a = loadAudio(u);
    const tr = a.tracks.filter((t) => SPOKEN.has(t.type));
    if (!tr.length) continue;
    out.push(u[0] === 'R' ? `### ${a.title}` : `### ${unitName(u)}　${a.title}`, '');
    for (const t of tr) {
      out.push(`#### 音频 ${t.id}　${t.title}`);
      for (const [es, zh] of trackLines(t, true)) out.push(`> ${es}｜${zh}`);
      out.push('');
    }
  }
  return out.join('\n');
}
// 教师用书每单元后面附上本单元全部录音稿
function scriptBlocks(u) {
  const a = loadAudio(u);
  if (!a.tracks.length) return [];
  const md = ['## x', '', u[0] === 'T' ? '### 本测试录音稿' : '### 本单元录音稿', '', '录音文件名是“B1_录音号.mp3”（如 B1_3-1.mp3）；生词跟读录音是“B1_单元号-V.mp3”。', ''];
  for (const t of a.tracks) {
    md.push(`#### 音频 ${t.id}　${t.title}（${t.type}）`);
    for (const [es, zh] of trackLines(t, true)) md.push(`> ${es}｜${zh}`);
    md.push('');
  }
  return parse(md.join('\n'), `audio/u${u}.md`).slice(1);
}

// ---------------------------------------------------------------- 组装
function load(c) {
  if (typeof c === 'string') {
    const f = path.join(CH, c);
    if (!fs.existsSync(f) && process.env.ALLOW_MISSING) return { blocks: parse(`## （待写）${c}\n这一章还没写好。`, c) };
    return { blocks: parse(fs.readFileSync(f, 'utf8'), c) };
  }
  return { blocks: parse(c.gen(), 'generated') };
}

const INTRO = fs.readFileSync(path.join(HERE, MODE, 'front.md'), 'utf8');
function build() {
  const body = [];
  let app = 0;
  const loaded = PARTS.map((p) => ({ ...p, items: p.chapters.map(load) }));
  for (const p of loaded) {
    body.push(heading(1, '', p.title, 0));
    const labels = p.chapters.map((c) => {
      if (p.appendix) return `附录 ${String.fromCharCode(65 + app++)}`;
      const u = /u(\w+)\.md$/.exec(c)[1];
      return /^[RT]/.test(u) ? '' : unitName(u);
    });
    const names = p.items.map((it) => it.blocks[0].text);
    body.push(new Paragraph({ spacing: { before: 240, after: 0 }, children: [] }));
    names.forEach((nm, k) => body.push(new Paragraph({ spacing: { after: 100 }, indent: { left: 400 },
      children: [new TextRun({ text: labels[k] ? `${labels[k]}　${nm}` : nm, font: F, size: 26, color: COL.body })] })));
    p.items.forEach((it, k) => {
      const lab = { chapter: labels[k], section: () => '', compact: !!p.chapters[k].compact, keepTasks: /uT\d\.md$/.test(String(p.chapters[k])) };
      const extra = MODE === 'teacher' && !p.appendix ? scriptBlocks(/u(\w+)\.md$/.exec(p.chapters[k])[1]) : [];
      body.push(...renderChapter([...it.blocks, ...extra], lab, false));
    });
  }
  while (body.length && body[body.length - 1].__spacer) body.pop();
  // 编写说明（不编号）
  const fm = parse(INTRO, 'front_matter.md');
  const front = [];
  for (const b of fm) {
    if (b.type === 'h2') front.push(heading(2, '', b.text, null));
    else if (b.type === 'h3') front.push(heading(3, '', b.text, null));
    else if (b.type === 'p') front.push(para(b.text));
    else if (b.type === 'ul') b.items.forEach((it) => front.push(new Paragraph({ numbering: { reference: 'bullets', level: it.level }, spacing: { after: 60, line: 320 }, children: runs(nb(it.text)) })));
    else if (b.type === 'table') { front.push(table(b.rows)); front.push(spacer()); }
  }
  // 目录
  const tocParas = [new Paragraph({ pageBreakBefore: true, spacing: { after: 320 }, border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: COL.saffron, space: 6 } },
    children: [new TextRun({ text: '目　录', font: F, size: 40, bold: true, color: COL.wine })] })];
  for (const t of toc) {
    const size = [24, 21, 19][t.level], indent = [0, 360, 900][t.level];
    // 编号和标题之间换成制表符，标题统一对齐
    const k = t.text.indexOf('　'), txt = t.level > 0 && k > 0 ? t.text.slice(0, k) + '\t' + t.text.slice(k + 1) : t.text;
    const numTab = t.level === 1 ? [{ type: TabStopType.LEFT, position: indent + 1300 }] : t.level === 2 ? [{ type: TabStopType.LEFT, position: indent + 720 }] : [];
    tocParas.push(new Paragraph({ tabStops: [...numTab, { type: TabStopType.RIGHT, position: CONTENT_W, leader: 'dot' }], indent: { left: indent },
      spacing: { before: t.level === 0 ? 160 : 0, after: t.level === 0 ? 60 : t.level === 1 ? 30 : 10 }, keepNext: t.level <= 1,
      children: [new InternalHyperlink({ anchor: t.id, children: txt.split('\t').flatMap((part, i) => [...(i ? [new TextRun({ text: '\t', font: F, size })] : []), new TextRun({ text: nb(part), font: F, size, bold: t.level === 0, color: t.level === 0 ? COL.wine : COL.ink })]) }),
        new TextRun({ text: '\t', font: F, size }), new PageReference(t.id, { font: F })] }));
  }
  // 封面
  const cover = [
    new Paragraph({ spacing: { before: 3200, after: 200 }, children: [new TextRun({ text: 'Español B1 · ' + (MODE === 'student' ? 'Libro del alumno' : 'Libro del profesor'), font: F, size: 30, color: COL.teal })] }),
    new Paragraph({ spacing: { after: 200 }, children: [new TextRun({ text: '西班牙语 B1 教程', font: F, size: 80, bold: true, color: COL.wine })] }),
    new Paragraph({ spacing: { after: 1200 }, border: { bottom: { style: BorderStyle.SINGLE, size: 18, color: COL.saffron, space: 10 } },
      children: [new TextRun({ text: BOOK, font: F, size: 44, bold: true, color: COL.body })] }),
    new Paragraph({ spacing: { after: 120 }, children: [new TextRun({ text: '面向学完 A2 的中国大学生和成人学习者 · 10 个单元 · 配录音', font: F, size: 24, color: COL.muted })] }),
    new Paragraph({ spacing: { after: 120 }, children: [new TextRun({ text: '依据欧洲共同参考框架 B1 和塞万提斯学院《课程计划》B1 编写；课文和练习为原创', font: F, size: 24, color: COL.muted })] }),
    new Paragraph({ spacing: { after: 120 }, children: [new TextRun({ text: '2026 年 10 月', font: F, size: 24, color: COL.muted })] }),
  ];
  const header = new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: `西班牙语 B1 教程 · ${BOOK}`, font: F, size: 16, color: COL.muted })] })] });
  const footer = new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: [PageNumber.CURRENT], font: F, size: 18, color: COL.muted })] })] });
  const page = { size: { width: PAGE_W, height: PAGE_H }, margin: { top: MARGIN, bottom: MARGIN, left: MARGIN, right: MARGIN, header: 560, footer: 560 } };
  const doc = new Document({
    creator: 'spanish-video-kit', title: `西班牙语 B1 教程 · ${BOOK}`, description: '西班牙语 B1 教程（学完 A2 的中国大学生和成人学习者，10 个单元）',
    features: { updateFields: true },
    styles: {
      default: { document: { run: { font: F, size: 21, color: COL.ink }, paragraph: { spacing: { line: 320 } } } },
      paragraphStyles: [1, 2, 3, 4].map((l) => ({ id: `Heading${l}`, name: `Heading ${l}`, basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { font: F, bold: true, color: COL.wine, size: { 1: 56, 2: 40, 3: 28, 4: 24 }[l] }, paragraph: { outlineLevel: l - 1 } })),
    },
    numbering: { config: [{ reference: 'bullets', levels: [
      { level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 400, hanging: 260 } } } },
      { level: 1, format: LevelFormat.BULLET, text: '–', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 800, hanging: 260 } } } },
    ] }] },
    sections: [
      { properties: { page }, children: cover },
      { properties: { page: { ...page, pageNumbers: { start: 1 } } }, headers: { default: header }, footers: { default: footer }, children: [...front, ...tocParas, ...body] },
    ],
  });
  fs.mkdirSync(path.dirname(OUT), { recursive: true });
  return Packer.toBuffer(doc).then(async (buf) => {
    const JSZip = require('jszip');
    const zip = await JSZip.loadAsync(buf);
    let st = await zip.file('word/styles.xml').async('string');
    // 行末标点不伸出版心
    if (st.includes('<w:pPrDefault><w:pPr>')) st = st.replace('<w:pPrDefault><w:pPr>', '<w:pPrDefault><w:pPr><w:overflowPunct w:val="0"/>');
    else if (st.includes('<w:pPrDefault>')) st = st.replace(/<w:pPrDefault>(<w:pPr[^>]*\/>)?/, '<w:pPrDefault><w:pPr><w:overflowPunct w:val="0"/></w:pPr>');
    else st = st.replace('<w:docDefaults>', '<w:docDefaults><w:pPrDefault><w:pPr><w:overflowPunct w:val="0"/></w:pPr></w:pPrDefault>');
    if (!st.includes('overflowPunct')) throw new Error('styles.xml: overflowPunct 没加上');
    zip.file('word/styles.xml', st);
    let docx = await zip.file('word/document.xml').async('string');
    let bid = 0, open = [];
    docx = docx.replace(/<w:bookmark(Start|End)\b([^>]*?)w:id="\d+"/g, (m, kind, mid) => {
      if (kind === 'Start') { bid += 1; open.push(bid); return `<w:bookmarkStart${mid}w:id="${bid}"`; }
      return `<w:bookmarkEnd${mid}w:id="${open.shift()}"`;
    });
    if (open.length) throw new Error('书签开始和结束对不上');
    zip.file('word/document.xml', docx);
    fs.writeFileSync(OUT, await zip.generateAsync({ type: 'nodebuffer', compression: 'DEFLATE' }));
    console.log(OUT, `${toc.length} 条目录`);
  });
}
build().catch((e) => { console.error(e.message); process.exit(1); });
