// 《西班牙语高考白皮书》生成：chapters/*.md（约定的简化 Markdown）→ 西班牙语高考白皮书.docx（排版程序沿用《SIELE 考试白皮书》）
// 用法：node build_gaokao.js [输出文件]
const fs = require('fs');
const path = require('path');
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, Bookmark, PageReference, InternalHyperlink, TabStopType,
  Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle, AlignmentType, Header, Footer, PageNumber,
  LevelFormat, TableLayoutType, VerticalAlign, Tab,
} = require('docx');

const HERE = __dirname;
const CH = process.env.CHAPTERS_DIR || path.join(HERE, 'chapters');
const OUT = process.argv[2] || path.join(HERE, 'out', '西班牙语高考白皮书.docx');
const F = { ascii: 'PingFang SC', hAnsi: 'PingFang SC', eastAsia: 'PingFang SC', cs: 'PingFang SC' };
const LANG = { value: 'es-ES', eastAsia: 'zh-CN' };
const COL = { wine: '7A1F2B', saffron: 'C98A2B', saffronSoft: 'FCEFD8', ink: '1F2933', body: '3E4C59', muted: '6B7785',
  teal: '2F6F73', tealSoft: 'E3F0EF', tint: 'F7F1EE', line: 'D9CEC9' };
const PAGE_W = 11906, PAGE_H = 16838, MARGIN = 1134, CONTENT_W = PAGE_W - 2 * MARGIN;
const CN = ['零', '一', '二', '三', '四', '五', '六', '七', '八', '九', '十'];

const PARTS = [
  { title: '总览', chapters: ['01_overview.md'] },
  { title: '各部分题型和考试模板', chapters: ['10_listening.md', '11_reading.md', '12_cloze.md', '13_grammar_fill.md', '14_writing.md'] },
  { title: '易错点、易错题和注意事项', chapters: ['20_errors_grammar.md', '21_errors_words.md', '22_error_items.md', '23_tips.md'] },
  { title: '常考词汇和表达', chapters: ['30_vocab_topics.md', '31_vocab_core.md', '32_expressions.md'] },
  { title: '附录', appendix: true, chapters: ['90_plan.md', '91_mock.md', '92_terms.md'] },
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
      out.push(new TextRun({ text: q, font: F, language: LANG, size: ref ? Math.round((o.size || 21) * 0.86) : o.size || 21,
        bold: o.bold || bold, color: ref ? COL.teal : o.color || COL.ink }));
    }
  }
  return out;
}
function textW(s) { let w = 0; for (const ch of String(s)) w += /[⺀-鿿＀-￯　-〿…—‘’“”←-⇿]/.test(ch) ? 1 : 0.55; return w; }

// ---------------------------------------------------------------- 排版
let bm = 0;
const toc = [];
const nb = (s) => String(s).replace(/(\d) (?=\d{3}(?!\d))/g, '$1\u00a0').replace(/(\d) (?=_{3,})/g, '$1\u00a0').replace(/(_{3,}) (?=\()/g, '$1\u00a0').replace(/(\d) (?=%)/g, '$1\u00a0').replace(/(\d)～(?=\d)/g, '$1\u2060～\u2060').replace(/([×√]) (?=\S)/g, '$1\u00a0').replace(/(\d)—(?=\d)/g, '$1\u2060—\u2060')
  .replace(/([–-])(?=[a-záéíóúñü])/g, '$1\u2060').replace(/… (o|ni|y)…/g, '…\u00a0$1…')
  .replace(/—(?=[¿¡A-Za-zÁÉÍÓÚÑáéíóúñ])/g, '—\u2060')
  .replace(/([0-9A-Za-z])–(?=[0-9A-Za-z])/g, '$1\u2060–\u2060').replace(/([)）]) (?=_)/g, '$1\u00a0')
  .replace(/, (?=[-–]\u2060?[a-z]{1,3}\b)/g, ',\u00a0').replace(/(\S)(?=……)/g, '$1\u2060')
  // 数字和后面汉字之间的空格不断行（30 分钟、2026 年 10 月）。数字前面的空格保留普通空格：
  // 汉字和数字之间用不换行空格时，LibreOffice 把数字当成中文排，会在数字中间断行（9 / 0 分）
  .replace(/(\d) (?=[\u4e00-\u9fff])/g, '$1\u00a0').replace(/\b(Tareas?|Opción|Situación) (?=\d|[A-Z]\b)/g, '$1\u00a0');
function heading(level, label, text, tocLevel, splitZh = false) {
  const id = `b${++bm}`;
  const full = label ? `${label}　${text}` : text;
  const k = full.lastIndexOf('（');
  const two = splitZh && k > 0 && textW(full) > 34;
  if (tocLevel !== null) toc.push({ id, text: full, level: tocLevel });
  const size = { 1: 56, 2: 40, 3: 28, 4: 24 }[level];
  const color = level === 4 ? COL.ink : COL.wine;
  return new Paragraph({
    heading: [null, HeadingLevel.HEADING_1, HeadingLevel.HEADING_2, HeadingLevel.HEADING_3, HeadingLevel.HEADING_4][level],
    pageBreakBefore: level <= 2 || (level === 3 && /^参考答案/.test(text)),
    keepNext: true, keepLines: true,
    spacing: { before: { 1: 2400, 2: 0, 3: 360, 4: 240 }[level], after: { 1: 240, 2: 320, 3: 160, 4: 120 }[level] },
    border: level === 2 ? { bottom: { style: BorderStyle.SINGLE, size: 12, color: COL.saffron, space: 6 } } : undefined,
    children: [new Bookmark({ id, children: two
      ? [new TextRun({ text: nb(full.slice(0, k)), font: F, language: LANG, size, bold: true, color }), new TextRun({ text: full.slice(k), font: F, size, bold: true, color, break: 1 })]
      : [new TextRun({ text: nb(full), font: F, language: LANG, size, bold: true, color })] })],
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
  const keepRow = (i) => rows.length <= 9 && !o.split && !tall ? i < rows.length - 1
    : rows.length <= 9 ? i <= 1 || (i >= rows.length - 2 && i < rows.length - 1) : i <= 2 || (i >= rows.length - 3 && i < rows.length - 1);
  return new Table({
    width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: ws, layout: TableLayoutType.FIXED, borders: borders(),
    rows: rows.map((r, i) => new TableRow({ tableHeader: i === 0, cantSplit: true, children: r.map((c, j) => new TableCell({
      width: { size: ws[j], type: WidthType.DXA }, verticalAlign: VerticalAlign.CENTER,
      shading: { type: ShadingType.CLEAR, color: 'auto', fill: i === 0 ? COL.teal : i % 2 ? 'FFFFFF' : COL.tint },
      margins: { top: 50, bottom: 50, left: 90, right: 90 },
      children: [new Paragraph({ spacing: { after: 0, line: 280 }, keepNext: keepRow(i),
        children: runs(nb(c), { size, bold: i === 0, color: i === 0 ? 'FFFFFF' : COL.ink }) })],
    })) })),
  });
}
function examples(ex, keepAfter = false) {
  // 每句一段。估算排出来的行数：整框 8 行以内不拆；更长的框可以在句间跨页，超过 6 行的长段落本身也可以跨页。
  // 短的首句（标题、称呼）和末句（署名）和相邻的一句放在同一格里，不会单独留在另一页
  const n = ex.length;
  const lines = ex.map(([es, zh]) => Math.ceil((textW(es) + (zh ? textW(zh) * 0.95 + 1 : 0)) / 44));
  const total = lines.reduce((a, b) => a + b, 0);
  const paras = ex.map(([es, zh], k) => new Paragraph({ spacing: { after: k < n - 1 ? 80 : 0, line: 300 },
    keepNext: (k < n - 1 && total <= 8) || (k === n - 1 && keepAfter), keepLines: lines[k] <= 6, widowControl: true,
    children: [...runs(nb(es), { size: 20, bold: true, color: COL.ink }), ...(zh ? [new TextRun({ text: '　', font: F, size: 20 }), ...runs(nb(zh), { size: 19, color: COL.muted })] : [])] }));
  const head = (k) => /^(Opción|Situación|Tema|Texto|Mensaje|Diálogo|Fragmento|Grabación)\b/.test(ex[k][0]) || /[:：]$/.test(ex[k][0].trim());
  const groups = [];
  ex.forEach((_, k) => {
    const joinPrev = total > 8 && k > 0 && ((k === 1 && lines[0] <= 3) || (k === n - 1 && lines[k] <= 3 && !(k === 1 && lines[0] <= 3 && groups.length === 1 && groups[0].length > 1))
      || (/^√/.test(ex[k][0]) && /^[×√]/.test(ex[k - 1][0])));  // × 句和后面的 √ 句不分页
    const last = groups[groups.length - 1];
    // 以 Opción、Situación 等开头的一组，在凑够 4 行以前继续把后面的句子并进来（标题、导语和要求不分页）
    const headJoin = total > 8 && last && head(last[0]) && last.reduce((a, j) => a + lines[j], 0) <= 4;
    if (joinPrev || headJoin) last.push(k); else groups.push([k]);
  });
  const glines = (g) => g.reduce((a, k) => a + lines[k], 0);
  while (total > 8 && groups.length > 1 && glines(groups[0]) <= 3) groups.splice(0, 2, groups[0].concat(groups[1]));
  while (total > 8 && groups.length > 1 && glines(groups[groups.length - 1]) <= 3) groups.splice(-2, 2, groups[groups.length - 2].concat(groups[groups.length - 1]));
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
    if (b.type === 'p' && nxt && (['table', 'ex', 'note'].includes(nxt.type) && (label.index || textW(b.text) < 80) || ['table', 'ex', 'note', 'ul'].includes(nxt.type) && /[：:]$/.test(b.text))) b.keep = true;
    if (b.type === 'ul' && nxt && ['table', 'ex', 'note'].includes(nxt.type)) b.keepLast = true;
    const isLab = (x) => x && x.type === 'p' && LABEL.test(x.text.replace(/\*\*/g, ''));
    if (b.type === 'p' && nxt && nxt.type === 'p' && /,$/.test(nxt.text) && textW(nxt.text) <= 12) b.keep = true;
    if (b.type === 'p' && isLab(prev) && nxt && !/^h[234]$/.test(nxt.type) && textW(b.text) <= 150) b.keep = true;
    if (b.type === 'ex' && isLab(prev) && nxt && ['ul', 'p'].includes(nxt.type) && b.ex.reduce((a, [es, zh]) => a + textW(es) + (zh ? textW(zh) : 0), 0) <= 3 * 44) b.keepAfter = true;
  });
  for (const b of blocks) {
    if (b.type === 'h2') out.push(heading(2, label.chapter, b.text, 1));
    else if (b.type === 'h3') { sec += 1; out.push(heading(3, label.section(sec), b.text, tocSections ? 2 : null, !!label.index)); }
    else if (b.type === 'h4') out.push(heading(4, '', b.text, null));
    else if (b.type === 'p') out.push(para(b.text, b.keep ? { p: { keepNext: true, keepLines: true } } : {}));
    // 题目列表（第一层全是“数字. ”或“例 N”开头）不用项目符号：题号、选项字母后面用制表符，悬挂缩进，转行和首行正文对齐
    else if (b.type === 'ul') b.items.forEach((it, k, all, q = all.filter((x) => x.level === 0).every((x) => QLAB.test(x.text)),
      m = q && (it.level === 0 ? QLAB : OLAB).exec(it.text)) => out.push(new Paragraph({
      ...(q ? { indent: it.level === 0 ? { left: 480, hanging: 480, right: 110 } : m ? { left: 900, hanging: 360, right: 110 } : { left: 540, right: 110 } }
        : { numbering: { reference: 'bullets', level: it.level }, indent: { right: 110 } }),
      keepLines: true,
      keepNext: (k < b.items.length - 1 && b.items.length <= 10 && b.items.every((x) => /^([A-Z]\.|[a-z]\)|\d+\.) /.test(x.text)) && b.items.reduce((a, x) => a + textW(x.text), 0) <= 250) || (!!b.keepLast && k === b.items.length - 1) || (k < b.items.length - 1 && ((b.items.length >= 4 && (k === 0 || (k === b.items.length - 2 && !b.keepLast))) || b.items[k + 1].level === 1)),
      spacing: { after: 50, line: 300 },
      children: m ? [...runs(m[1]), new TextRun({ children: [new Tab()], font: F, size: 21 }), ...runs(nb(it.text.slice(m[0].length)))] : runs(nb(it.text)) })));
    else if (b.type === 'table') { out.push(table(b.rows, label.index ? { size: 18, split: true } : {})); out.push(spacer()); }
    else if (b.type === 'ex') { out.push(examples(b.ex, b.keepAfter)); out.push(spacer(b.keepAfter)); }
    else if (b.type === 'note') { out.push(note(b.text)); out.push(spacer()); }
  }
  while (out.length && out[out.length - 1].__spacer) out.pop();
  return out;
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

const INTRO = fs.readFileSync(path.join(HERE, 'front_matter.md'), 'utf8');
function build() {
  const body = [];
  let ch = 0, app = 0, partNo = 0;
  const loaded = PARTS.map((p) => ({ ...p, items: p.chapters.map(load) }));
  for (const p of loaded) {
    const label = p.appendix ? '' : `第${CN[++partNo]}部分`;
    body.push(heading(1, label, p.title, 0));
    const names = p.items.map((it) => it.blocks[0].text);
    body.push(new Paragraph({ spacing: { before: 240, after: 0 }, children: [] }));
    names.forEach((nm, k) => body.push(new Paragraph({ spacing: { after: 100 }, indent: { left: 400 },
      children: [new TextRun({ text: `${p.appendix ? `附录 ${String.fromCharCode(65 + app + k)}` : `第 ${ch + k + 1} 章`}　${nm}`, font: F, size: 26, color: COL.body })] })));
    for (const it of p.items) {
      let lab;
      if (p.appendix) { const L = String.fromCharCode(65 + app++); lab = { chapter: `附录 ${L}`, section: (s) => `${L}.${s}` }; }
      else { const n = ++ch; lab = { chapter: `第 ${n} 章`, section: p.index ? () => '' : (s) => `${n}.${s}`, index: p.index }; }
      body.push(...renderChapter(it.blocks, lab, !p.index));
    }
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
    new Paragraph({ spacing: { before: 3600, after: 200 }, children: [new TextRun({ text: '普通高等学校招生全国统一考试 · 外语（西班牙语）', font: F, size: 30, color: COL.teal })] }),
    new Paragraph({ spacing: { after: 300 }, children: [new TextRun({ text: '西班牙语高考白皮书', font: F, size: 80, bold: true, color: COL.wine })] }),
    new Paragraph({ spacing: { after: 1200 }, border: { bottom: { style: BorderStyle.SINGLE, size: 18, color: COL.saffron, space: 10 } },
      children: [new TextRun({ text: '试卷结构 · 考试模板和原创样题 · 易错点和易错题 · 常考词汇 · 模拟卷', font: F, size: 28, color: COL.body })] }),
    new Paragraph({ spacing: { after: 120 }, children: [new TextRun({ text: '依据现行新课标卷题型和高中西班牙语课程标准整理；样题为原创模拟题', font: F, size: 24, color: COL.muted })] }),
    new Paragraph({ spacing: { after: 120 }, children: [new TextRun({ text: '2026 年 10 月', font: F, size: 24, color: COL.muted })] }),
  ];
  const header = new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: '西班牙语高考白皮书', font: F, size: 16, color: COL.muted })] })] });
  const footer = new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: [PageNumber.CURRENT], font: F, size: 18, color: COL.muted })] })] });
  const page = { size: { width: PAGE_W, height: PAGE_H }, margin: { top: MARGIN, bottom: MARGIN, left: MARGIN, right: MARGIN, header: 560, footer: 560 } };
  const doc = new Document({
    creator: 'spanish-video-kit', title: '西班牙语高考白皮书', description: '高考西班牙语（新课标卷）题型、考试模板、易错点、易错题和常考词汇',
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
