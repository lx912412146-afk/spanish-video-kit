// 《西班牙语 A1—A2 听力练习》排版：out/sets.json（tools/export_json.py 由 sets/*.md 生成）→ 学生版、教师版 docx
// 用法：node build_listening.js student|teacher [输出文件]
// 沿用《西班牙语 A0—A1 听力练习》的 build_listening.js（排版函数又沿用《西班牙语 A2 教程》的 build_a2.js）。版面上不用表格做框（LibreOffice 里框后面的
// “与下段同页”不起作用），题目、选项、录音原文都是段落，框用段落底纹和左边线。
const fs = require('fs');
const path = require('path');
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, Bookmark, PageReference, InternalHyperlink, TabStopType,
  Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle, AlignmentType, Header, Footer, PageNumber,
  LevelFormat, TableLayoutType, VerticalAlign, Tab,
} = require('docx');

const HERE = __dirname;
const MODE = process.argv[2];
if (!['student', 'teacher'].includes(MODE)) { console.error('用法：node build_listening.js student|teacher [输出文件]'); process.exit(1); }
const T = MODE === 'teacher';
const BOOK = T ? '教师版' : '学生版';
const TITLE = '西班牙语 A1—A2 听力练习';
const OUT = process.argv[3] || path.join(HERE, 'out', `西班牙语A1-A2听力练习_${BOOK}.docx`);
const SETS = JSON.parse(fs.readFileSync(path.join(HERE, 'out', 'sets.json'), 'utf8'));
const F = { ascii: 'PingFang SC', hAnsi: 'PingFang SC', eastAsia: 'PingFang SC', cs: 'PingFang SC' };
const LANG = { value: 'es-ES', eastAsia: 'zh-CN' };
const COL = { main: '7A2E3B', accent: 'C98A2B', accentSoft: 'FCEFD8', ink: '1F2933', body: '3E4C59', muted: '6B7785',
  teal: '2F6F73', tealSoft: 'E3F0EF', tint: 'F3F5F8', line: 'C9D3DE' };
const PAGE_W = 11906, PAGE_H = 16838, MARGIN = 1134, CONTENT_W = PAGE_W - 2 * MARGIN;
const CN = '零一二三四五六七八九十';
const NUM_W = 520;                       // 题号占的宽度（悬挂缩进）
const SZ = 21;                           // 正文字号（半磅）

// ---------------------------------------------------------------- 文字
// 行内：**加粗**；数字空格 U+2007（电话号码分组、西语短语里不断行的空格）单独一段、字号缩小到普通空格的宽度
function runs(text, o = {}) {
  const out = [];
  for (const p of String(text).split(/(\*\*[^*]+\*\*)/g)) {
    if (!p) continue;
    const bold = /^\*\*[^*]+\*\*$/.test(p);
    const s = bold ? p.slice(2, -2) : p;
    for (const r of s.split(/( )/g)) {
      if (!r) continue;
      const sz = o.size || SZ;
      out.push(new TextRun({ text: r, font: F, language: LANG, size: r === ' ' ? Math.round(sz * 0.52) : sz,
        bold: o.bold || (bold && !o.plainBold), italics: o.italics, color: (bold && o.boldColor) || o.color || COL.ink, underline: o.underline }));
    }
  }
  return out;
}
function textW(s) { let w = 0; for (const ch of String(s).replace(/\*\*/g, '')) w += /[⺀-鿿＀-￯　-〿…—‘’“”←-⇿]/.test(ch) ? 1 : 0.55; return w; }
const twips = (s, size = SZ) => Math.ceil(textW(s) * size * 10 * 1.05);
// 不断行的地方（2026-10 在 LibreOffice 26.8 试过的写法，见 build_a2.js 的 nb()）：
// 数字和后面的汉字之间（15 岁、3 月 12 日）用不换行空格；电话号码各组之间、数字和 € 之间用数字空格；
// 空格后面接答题线时不断开
const nb = (s) => String(s)
  .replace(/(\d) (?=\d)/g, '$1 ')
  .replace(/(\d) (?=[€%])/g, '$1 ')
  .replace(/(\d) (?=[一-鿿])/g, '$1 ')
  .replace(/([)）:]) (?=_)/g, '$1 ')
  .replace(/(_{3,}) (?=[a-záéíóú])/g, '$1 ')
  // 文件名、拼读里的连字符两边不断（A1A2_03-2.mp3、H-I-D-A-L-G-O；2026-10 在 build_a2.js 里试过 WJ）
  .replace(/([\w一-鿿])-(?=[\w一-鿿])/g, '$1⁠-⁠')
  // 引号里的西语短语（“Parte uno”“Fin de la parte uno”）内部不断行：数字空格
  .replace(/“([A-Za-zÁÉÍÓÚÑáéíóúñü ]+)”/g, (m, x) => `“${x.replace(/ /g, ' ')}”`);

let bm = 0;
const toc = [];
const P = (o) => new Paragraph(o);
function para(text, o = {}) {
  return P({ alignment: AlignmentType.LEFT, widowControl: true, spacing: { after: o.after ?? 100, before: o.before || 0, line: o.line || 300 },
    keepNext: !!o.keep, keepLines: !o.split, indent: o.indent, tabStops: o.tabs, border: o.border, shading: o.shading,
    pageBreakBefore: !!o.pageBreak, children: Array.isArray(text) ? text : runs(nb(text), o) });
}
const BLANK = '______________';
const blank = (n = 14) => '_'.repeat(n);
const answerRun = (s, o = {}) => runs(nb(s), { color: COL.teal, bold: true, ...o });

// ---------------------------------------------------------------- 套的标题、部分标题
function setHeading(st) {
  const id = `b${++bm}`;
  toc.push({ id, text: `第 ${st.num} 套　${st.zh_title}`, es: st.es_title, level: 0 });
  return [
    P({ pageBreakBefore: true, keepNext: true, keepLines: true, spacing: { after: 60 }, heading: HeadingLevel.HEADING_1,
      children: [new Bookmark({ id, children: [new TextRun({ text: `第 ${st.num} 套　`, font: F, size: 34, bold: true, color: COL.main }),
        new TextRun({ text: st.zh_title, font: F, size: 34, bold: true, color: COL.main })] })] }),
    P({ keepNext: true, spacing: { after: 120 }, border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: COL.accent, space: 6 } },
      children: runs(st.es_title, { size: 23, color: COL.teal, italics: true }) }),
  ];
}
function setInfo(st) {
  const parts = st.parts.length, n = st.n_questions;
  const tracks = `A1A2_${String(st.num).padStart(2, '0')}-1 至 -${parts}`;
  const dur = st.parts.every((p) => p.duration) ? st.parts.reduce((a, p) => a + p.duration, 0) : null;
  const durTxt = dur ? `，录音共 ${Math.round(dur / 60)} 分钟` : '';
  const out = [para(`级别 ${st.level}　·　${parts} 个部分，共 ${n} 题　·　${st.time.replace(/^约/, '约 ').replace(/约  /, '约 ')}${T ? durTxt : ''}　·　录音 ${tracks}`, { size: 19, color: COL.muted, keep: true, after: 80 })];
  if (!T) out.push(para(`姓名 ${blank(10)}　　班级 ${blank(8)}　　日期 ${blank(8)}　　得分 ${blank(5)} / ${n}`, { size: 20, color: COL.body, after: 160, before: 60 }));
  return out;
}
const range = (p) => (p.first === p.last ? `第 ${p.first} 题` : `第 ${p.first}—${p.last} 题`);
function fmtDur(s) { const m = Math.floor(s / 60), r = Math.round(s - m * 60); return r === 60 ? `${m + 1} 分` : `${m} 分 ${r} 秒`; }
function partHeading(st, p) {
  const label = `录音 A1A2_${p.track}` + (T && p.duration ? `（${fmtDur(p.duration)}）` : '');
  return P({ keepNext: true, keepLines: true, spacing: { before: 280, after: 80 }, tabStops: [{ type: TabStopType.RIGHT, position: CONTENT_W }],
    border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: COL.line, space: 3 } },
    children: [new TextRun({ text: `第${CN[p.idx]}部分　${p.title}`, font: F, size: 24, bold: true, color: COL.main }),
      new TextRun({ text: `（${range(p)}）`, font: F, size: 20, color: COL.body }),
      new TextRun({ children: [new Tab()], font: F, size: 19 }), new TextRun({ text: label, font: F, size: 18, color: COL.teal })] });
}
function instruction(p) {
  return para([...runs(nb(p.instr_zh), {}), ...runs(`（${p.instr_es}）`, { color: COL.teal, italics: true })], { keep: true, after: 100 });
}

// ---------------------------------------------------------------- 题目
const numLabel = (it) => (it.num === '例' ? '例' : `${it.num}.`);
// 选项横排：一部分里能放进三等栏的题都用三等栏（各题对齐）；放不下的题按这一题的选项长度分栏，余下的宽度平分到栏间；
// 还放不下才每个选项一行
function optionLayout(it) {
  const w = it.options.map((o) => twips(`${o[0]}. ${o[1]}`));
  const avail = CONTENT_W - NUM_W, need = w.reduce((a, b) => a + b, 0);
  const eq = Math.floor(avail / 3);
  if (w.every((x) => x + 300 < eq)) return { horizontal: true, pos: [0, eq, 2 * eq].map((x) => NUM_W + x) };
  if (need + 3 * 300 > avail) {
    // 三栏放不下：两栏（A、B 一行，C 下一行）放得下就分两行，不然每个选项一行
    const half = Math.floor(avail / 2);
    return w.every((x) => x + 300 < half) ? { horizontal: false, two: true, pos: [NUM_W, NUM_W + half] } : { horizontal: false };
  }
  const gap = Math.floor((avail - need) / 3);
  return { horizontal: true, pos: [NUM_W, NUM_W + w[0] + gap, NUM_W + w[0] + w[1] + 2 * gap] };
}
function optionRuns(it, o, mark) {
  const isAns = mark && o[0] === it.answer;
  return [...runs(`${o[0]}.`, { bold: isAns, color: isAns ? COL.teal : COL.ink }), new TextRun({ text: ' ', font: F, size: SZ }),
    ...runs(nb(o[1].replace(/ /g, ' ')), { bold: isAns, color: isAns ? COL.teal : COL.ink, underline: isAns ? {} : undefined })];
}
function choiceItem(p, it, keepLast = false) {
  const lay = optionLayout(it);
  // 例题和教师版标出答案（加粗、绿色）；学生版的例题在后面写“（答案：B）”
  const mark = T || it.num === '例';
  const out = [];
  const tail = it.num === '例' ? [new TextRun({ text: '　', font: F, size: SZ }), ...runs(`（答案：${it.answer}）`, { size: 19, color: COL.teal })]
    // “答案 C”整体不断行：两个字之间用 WJ，字和字母之间用不换行空格
    : T ? [new TextRun({ text: '　', font: F, size: SZ }), new TextRun({ text: `答\u2060案\u00a0${it.answer}`, font: F, language: LANG, size: 19, color: COL.teal, bold: true })] : [];
  const tabs = lay.horizontal ? lay.pos.map((x) => ({ type: TabStopType.LEFT, position: x })) : [];
  const TAB = () => new TextRun({ children: [new Tab()], font: F, size: SZ });
  const exTail = !T && it.num === '例';      // 学生版例题都写“（答案：B）”（黑白打印时颜色看不出来）
  // 例题的“（答案：B）”接在选项后面；那一行放不下时 LibreOffice 自然转到下一行
  if (!it.stem && lay.horizontal) {
    out.push(para([...runs(numLabel(it)), ...it.options.flatMap((o, k) => [TAB(), ...optionRuns(it, o, mark)]), ...(exTail || T ? tail : [])],
      { indent: { left: NUM_W, hanging: NUM_W }, tabs, after: 90, keep: keepLast }));
    return out;
  }
  out.push(para([...runs(numLabel(it)), TAB(), ...runs(nb(it.stem || '')), ...(lay.horizontal && !exTail && !T ? [] : tail)],
    { indent: { left: NUM_W, hanging: NUM_W }, tabs: [{ type: TabStopType.LEFT, position: NUM_W }], keep: true, after: 40 }));
  if (lay.horizontal) out.push(para(it.options.flatMap((o) => [TAB(), ...optionRuns(it, o, mark)]), { tabs, after: 90, keep: keepLast }));
  else if (lay.two) {
    const tabs2 = lay.pos.map((x) => ({ type: TabStopType.LEFT, position: x }));
    out.push(para(it.options.slice(0, 2).flatMap((o) => [TAB(), ...optionRuns(it, o, mark)]), { tabs: tabs2, after: 20, keep: true }));
    out.push(para([TAB(), ...optionRuns(it, it.options[2], mark)], { tabs: tabs2, after: 90, keep: keepLast }));
  } else it.options.forEach((o, k) => { const last = k === it.options.length - 1;
    out.push(para(optionRuns(it, o, mark), { indent: { left: NUM_W }, keep: !last || keepLast, after: last ? 90 : 20 })); });
  return out;
}
function tfItem(p, it, keepLast = false) {
  const show = it.num === '例' || T;
  return [para([...runs(numLabel(it)), new TextRun({ children: [new Tab()], font: F, size: SZ }), ...runs(nb(it.stem)),
    new TextRun({ children: [new Tab()], font: F, size: SZ }), ...runs(show ? `（ ${it.answer} ）` : '（　　）', { color: show ? COL.teal : COL.ink, bold: show })],
  { indent: { left: NUM_W, hanging: NUM_W }, tabs: [{ type: TabStopType.LEFT, position: NUM_W }, { type: TabStopType.RIGHT, position: CONTENT_W }], after: 90, keep: keepLast })];
}
function fillStem(it, show) {
  const st = it.stem.includes('____') ? it.stem : `${it.stem} ____`;
  const [a, b] = st.split('____');
  const tailBlank = !b.trim();
  if (show) return [...runs(nb(a)), ...answerRun(` ${it.answer} `, { underline: {}, bold: T && it.num !== '例' }), ...runs(nb(b))];
  return [...runs(nb(a.replace(/ $/, ' '))), ...runs(tailBlank ? blank(22) : blank(12)), ...runs(nb(b))];
}
function fillItem(p, it, keepLast = false) {
  const show = T || it.num === '例';
  return [para([...runs(numLabel(it)), new TextRun({ children: [new Tab()], font: F, size: SZ }), ...fillStem(it, show)],
    { indent: { left: NUM_W, hanging: NUM_W }, tabs: [{ type: TabStopType.LEFT, position: NUM_W }], after: 110, line: 340, keep: keepLast })];
}
// 选项框、要点表的边线：左边一条色线；上下是和底色同色的线，只为留出 4 磅的上下空白（相同边线的段落合成一个框）
const BOX = () => ({ left: { style: BorderStyle.SINGLE, size: 12, color: COL.accent, space: 8 },
  top: { style: BorderStyle.SINGLE, size: 2, color: COL.accentSoft, space: 4 }, bottom: { style: BorderStyle.SINGLE, size: 2, color: COL.accentSoft, space: 4 },
  right: { style: BorderStyle.SINGLE, size: 2, color: COL.accentSoft, space: 8 } });     // 右边留白：行末悬挂的中文标点（LibreOffice 不认 overflowPunct）落在底纹里
// 配对：选项分两栏（短的分三栏，长的一行一个），题目每行两到三题
function matchOptions(p) {
  const opts = p.options.map((o) => `${o[0]}. ${o[1]}`);
  const w = Math.max(...opts.map((o) => twips(o)));
  // A2 的配对选项常是整句：两栏放不下就一行一个
  const ncol = w + 400 < (CONTENT_W - NUM_W) / 3 ? 3 : w + 400 < (CONTENT_W - NUM_W) / 2 ? 2 : 1;
  const col = Math.floor((CONTENT_W - NUM_W) / ncol);
  const rows = [];
  for (let i = 0; i < opts.length; i += ncol) rows.push(p.options.slice(i, i + ncol));
  const box = BOX();
  return rows.map((r, i) => para(r.flatMap((o, k) => [new TextRun({ children: [new Tab()], font: F, size: SZ }), ...runs(`${o[0]}.`, { bold: true }),
    new TextRun({ text: ' ', font: F, size: SZ }), ...runs(o[1].replace(/ /g, ' '))]),
  // 学生版选项框和下面的题目连在一起；教师版下面是每题的录音原文，框后面可以换页
  { tabs: Array.from({ length: ncol }, (_, k) => ({ type: TabStopType.LEFT, position: NUM_W + k * col })), keep: !T || i < rows.length - 1,
    shading: { type: ShadingType.CLEAR, color: 'auto', fill: COL.accentSoft }, border: box, indent: { left: 160, right: 160 },
    before: i === 0 ? 40 : 0, after: i === rows.length - 1 ? 120 : 0, line: 300 }));
}
function matchItems(p) {
  const items = p.items;
  const w = Math.max(...items.map((it) => twips(`${numLabel(it)} ${it.stem}`) + 1500));
  const ncol = w < (CONTENT_W - 0) / 3 ? 3 : 2;
  const col = Math.floor(CONTENT_W / ncol);
  const out = [];
  for (let i = 0; i < items.length; i += ncol) {
    const row = items.slice(i, i + ncol);
    out.push(para(row.flatMap((it, k) => {
      const show = T || it.num === '例';
      return [...(k ? [new TextRun({ children: [new Tab()], font: F, size: SZ })] : []), ...runs(`${numLabel(it)} `),
        ...runs(nb(it.stem.replace(/ /g, ' '))), new TextRun({ text: '  ', font: F, size: SZ }),
        ...(show ? answerRun(` ${it.answer} `, { underline: {} }) : runs(blank(6)))];
    }), { tabs: Array.from({ length: ncol }, (_, k) => ({ type: TabStopType.LEFT, position: k * col })), keep: i + ncol < items.length, after: 80, line: 330 }));
  }
  return out;
}
// 填空：短文放在底纹框里，空写成 (19) ______
function passage(p) {
  const ans = Object.fromEntries(p.items.map((it) => [String(it.num), it.answer]));
  const box = BOX();
  return p.passage.map((line, i) => {
    const kids = [];
    for (const seg of line.split(/(\{[^}]+\})/g)) {
      if (!seg) continue;
      const m = /^\{([^}]+)\}$/.exec(seg);
      if (!m) { kids.push(...runs(nb(seg).replace(/　/g, '\t'), { size: SZ })); continue; }
      const k = m[1];
      kids.push(...runs(`(${k}) `, { size: 19, color: COL.body }));
      kids.push(...(T || k === '例' ? answerRun(` ${ans[k]} `, { underline: {}, bold: T && k !== '例' }) : runs(blank(14))));
    }
    return para(kids, { keep: i < p.passage.length - 1, shading: { type: ShadingType.CLEAR, color: 'auto', fill: COL.accentSoft }, border: box,
      indent: { left: 160, right: 160 }, before: i === 0 ? 40 : 0, after: i === p.passage.length - 1 ? 160 : 0, line: 360,
      tabs: [{ type: TabStopType.LEFT, position: 4800 }] });
  });
}

// ---------------------------------------------------------------- 教师版：录音原文、依据
const stripWho = (zh) => zh.replace(/^[^：]{1,12}：/, '');
function transcript(lines, o = {}) {
  // lines: [[说话人, 西语, 中文]]（说话人为空的是播音员）
  // 右边和底色同色的边线留出 8 磅：行末悬挂的中文标点落在底纹里，不伸出框
  const box = { left: { style: BorderStyle.SINGLE, size: 12, color: COL.teal, space: 8 }, right: { style: BorderStyle.SINGLE, size: 2, color: COL.tealSoft, space: 8 } };
  // 原文很长（超过 5 句，或总字数超过 400）就可以跨页：只把前一行和后两行连住；o.keepEnd 时最后一行也和下面的依据连住
  const long = lines.length > 5 || lines.reduce((a, l) => a + l[1].length + l[2].length, 0) > 400;
  return lines.map(([who, es, zh], i) => para([...runs(nb(who ? `${who}${/[一-鿿]/.test(who) ? '：' : ': '}${es}` : `【播音】${es}`), { size: 20, bold: true, color: who ? COL.ink : COL.teal }),
    new TextRun({ text: '　', font: F, size: 19 }), ...runs(nb(who ? stripWho(zh) : zh), { size: 19, color: COL.muted })],
  { keep: (o.keepAll && !(o.release && i === lines.length - 1)) || (i < lines.length - 1 && (!long || i < 1 || i >= lines.length - 2)) || (o.keepEnd && i === lines.length - 1), shading: { type: ShadingType.CLEAR, color: 'auto', fill: COL.tealSoft }, border: box,
    indent: { left: o.indent ?? 160, right: 160 }, before: i === 0 ? 20 : 0, after: i === lines.length - 1 ? (o.after ?? 80) : 20, line: 280,
    split: es.length + zh.length > 250 }));     // 很长的一段（B 级的独白）可以在段内换页，孤行控制保证两边至少各两行
}
function basis(it, keep = false) {
  if (!it.basis) return [];
  return [para([...runs('依据：', { size: 19, bold: true, color: COL.teal }), ...runs(nb(it.basis), { size: 19, color: COL.body })],
    { indent: { left: NUM_W }, after: 120, keep, line: 280 })];
}
const narr = ([es, zh]) => ['', es, zh];

// ---------------------------------------------------------------- 一个部分
function renderPart(st, p, last = false) {
  // 教师版每套最后一部分的最后几题（连同“Fin de la parte”）连在一起，不让一套的最后一页只剩一两行
  const qs = p.items.filter((it) => it.num !== '例'), tailAt = (k) => (T && last ? qs.length - k : Infinity);
  const out = [partHeading(st, p), instruction(p)];
  const shared = p.audio.length > 0;
  // 教师版配对、填空的选项框或要点表较长：播音员的开场白后面可以换页（标题、指令、开场白仍在一起）
  if (T) out.push(...transcript([...p.intro.map(narr)], { keepAll: true, after: 60, release: p.type === '配对' || p.type === '填空' }));
  if (p.type === '配对') out.push(...matchOptions(p));
  if (p.type === '填空') out.push(...passage(p));
  if (T && shared) {
    out.push(para(runs('录音原文（读两遍）', { size: 19, bold: true, color: COL.teal }), { keep: true, after: 40 }));
    out.push(...transcript([...p.audio, narr(p.outro)], { after: 140 }));
  }
  const one = (it, keep = false) => (p.type === '选择' ? choiceItem(p, it, keep) : p.type === '判断' ? tfItem(p, it, keep) : p.type === '填写' ? fillItem(p, it, keep) : []);
  if (p.type === '配对' && !T) out.push(...matchItems(p));
  if (T && shared) {
    if (p.type === '配对') { /* 题目已排在上面 */ }
    for (const it of p.items) {
      const j = qs.indexOf(it);
      if (p.type === '填空' || p.type === '配对') out.push(para([...runs(numLabel(it), { bold: true }), new TextRun({ children: [new Tab()], font: F, size: SZ }),
        ...(it.stem ? runs(nb(it.stem.replace(/ /g, ' ')) + '　') : []), ...answerRun(it.answer), new TextRun({ text: '　', font: F, size: 19 }),
        ...(it.basis ? [...runs('依据：', { size: 19, bold: true, color: COL.teal }), ...runs(nb(it.basis), { size: 19, color: COL.body })] : [])],
      { indent: { left: NUM_W, hanging: NUM_W }, tabs: [{ type: TabStopType.LEFT, position: NUM_W }], after: 80, line: 290, keep: j >= tailAt(5) && j < qs.length - 1 }));
      else out.push(...one(it, !!it.basis), ...basis(it, j >= tailAt(2) && j < qs.length - 1));
    }
    return out;
  }
  if (!T && p.type !== '配对' && p.type !== '填空') { for (const it of p.items) out.push(...one(it)); return out; }
  if (!T) return out;
  // 教师版、每题单独录音：题目 → 录音原文 → 依据
  for (const it of p.items) {
    const tail = T && qs.indexOf(it) === qs.length - 1;     // 各题单独录音的部分：最后一题和“Fin de la parte”连住，不让它单独落到下一页开头（两题都连住常空出半页）
    if (p.type === '配对') out.push(para([...runs(it.num === '例' ? '例' : `${it.num}.`, { bold: true }), new TextRun({ children: [new Tab()], font: F, size: SZ }),
      ...runs(nb(it.stem.replace(/ /g, ' ')) + '　'), ...answerRun(it.answer)], { indent: { left: NUM_W, hanging: NUM_W }, tabs: [{ type: TabStopType.LEFT, position: NUM_W }], keep: true, after: 30 }));
    else out.push(...one(it, true));
    // 录音原文 4 行以内整段和依据连在一起；更长的（B2 的短对话）可以跨页，只连住开头一行和最后两行
    const short = it.audio.length <= 4 && it.audio.reduce((a, l) => a + l[1].length + l[2].length, 0) <= 400;
    out.push(...transcript(it.audio, { indent: NUM_W + 160, after: it.basis ? 40 : 140, keepAll: (!!it.basis || tail) && short, keepEnd: !!it.basis || tail }));
    out.push(...basis(it, tail));
  }
  out.push(...transcript([narr(p.outro)], { after: 140 }));
  return out;
}

// ---------------------------------------------------------------- 教师版：使用建议和答案一览
function teacherIntro(st) {
  const out = [para(runs('使用建议', { size: 22, bold: true, color: COL.main }), { keep: true, before: 120, after: 60 })];
  st.tips.forEach((t, i) => out.push(P({ numbering: { reference: 'bullets', level: 0 }, spacing: { after: 50, line: 300 }, keepNext: i < st.tips.length - 1, keepLines: true,
    children: runs(nb(t), { size: 20 }) })));
  out.push(para(runs('答案一览', { size: 22, bold: true, color: COL.main }), { keep: true, before: 160, after: 60 }));
  st.parts.forEach((p, k) => {
    const qs = p.items.filter((it) => it.num !== '例');
    out.push(para([...runs(`第${CN[p.idx]}部分　`, { size: 20, bold: true, color: COL.body }),
      ...qs.flatMap((it, j) => [...(j ? [new TextRun({ text: '　', font: F, size: 20 })] : []), ...runs(`${it.num}. `, { size: 20, color: COL.muted }),
        ...runs(nb(it.answer.replace(/（.*$/, '')).replace(/ /g, ' '), { size: 20, bold: true, color: COL.teal })])],
    { keep: k < st.parts.length - 1, after: 40, indent: { left: 1300, hanging: 1300 } }));
  });
  return out;
}

// ---------------------------------------------------------------- 前言（使用说明）
function frontMatter() {
  const out = [];
  const h = (t) => P({ keepNext: true, spacing: { before: 200, after: 100 }, children: runs(t, { size: 26, bold: true, color: COL.main }) });
  const li = (t) => P({ numbering: { reference: 'bullets', level: 0 }, spacing: { after: 60, line: 310 }, keepLines: true, children: runs(nb(t), { size: 20 }) });
  out.push(P({ spacing: { after: 240 }, border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: COL.accent, space: 6 } },
    children: runs('使用说明', { size: 36, bold: true, color: COL.main }) }));
  const total = SETS.reduce((a, s) => a + s.n_questions, 0);
  const per = [...new Set(SETS.map((s) => s.n_questions))].join('—');
  out.push(para(`本册共 ${SETS.length} 套听力练习、${total} 道题，是《西班牙语 A0—A1 听力练习》的续篇，从 A1 逐套过渡到 A2：第 1—2 套巩固 A1（日常生活和业余时间、住房和街区），第 3 套是 A1 到 A2 的过渡（饭馆和订餐），第 4—10 套是 A2（周末和假期、人生故事和经历、小时候和以前、健康和看病、旅行、购物和服务、学习和工作），过去时、命令式等 A2 语法逐套加进来。每套 ${per} 题，分 4 个部分，用时约 35 分钟。`, { size: 20 }));
  out.push(para('题型有短对话三选一、广播通知和广告、整段对话或采访选择、判断对错、配对、留言和讲座填空、听写数字和信息，题目和录音全部原创；题型参照 DELE A2 听力的格式（例题、每段读两遍、配对选项比题目多、短对话和广播），题干和选项都用西语。', { size: 20 }));
  out.push(h('录音'));
  out.push(li('每套的每个部分一段录音，文件名是“A1A2_套号-部分号.mp3”，如第 3 套第二部分是 A1A2_03-2.mp3。各部分标题右边注明了录音文件名。'));
  out.push(li('录音开头播音员读“Parte uno”（第一部分）和西语指令；每题前报题号（“Ejemplo”是例题，“Número uno”是第 1 题）；每题读两遍，读完留出作答时间；整段对话或短文的部分和配对题先留出看题、看选项的时间，整段对话读两遍；最后读“Fin de la parte uno”（第一部分结束）。'));
  out.push(li('录音由语音合成制作，声音有男有女，语速比正常稍慢，越往后越接近正常语速；每一句都经过语音识别逐词核对。'));
  out.push(h('作答'));
  out.push(li('选择题和配对题写选项字母（或圈出选项）；判断题在括号里写 V（verdadero，对）或 F（falso，错）。'));
  out.push(li('填空和听写：数字、时间、价格用阿拉伯数字，如 9:30、12,50 €、612 304 958；其他的空写西语单词，拼读的名字按听到的字母写出。'));
  out.push(li('每部分开头有一道例题，例题的答案已经给出。'));
  if (T) {
    out.push(h('教师版的内容'));
    out.push(li('每套前面是使用建议和答案一览；后面按部分排：题目（答案加粗、加下划线，标成绿色）、这一题的录音原文和中文译文、答案依据。整段录音的部分先排全文，再排各题的答案和依据。'));
    out.push(li('录音原文里“【播音】”是播音员读的话；题号（“Ejemplo”“Número uno”…）和第二遍录音不再重复排出。'));
    out.push(li('评分：每题 1 分，每套 25 分。填空和听写的词意思对、拼写对就给分；名字、地名的首字母写成小写也算对，漏写重音酌情给分；数字、时间写法不同但意思对（如 21:30 和 9:30）都算对。'));
    out.push(li('播放：录音里每题（整段录音的部分是整段）已经读两遍，一般每个部分整段放一遍即可；基础弱的班可以整段再放一遍，或在每题后暂停。'));
    out.push(h('各套一览'));
    const rows = [['套', '级别', '内容', '题数', '录音'], ...SETS.map((s) => [String(s.num), s.level, s.zh_title, String(s.n_questions),
      s.parts.every((p) => p.duration) ? `${Math.round(s.parts.reduce((a, p) => a + p.duration, 0) / 60)} 分钟` : '—'])];
    const ws = [700, 1300, 5038, 1000, 1600];
    out.push(new Table({ width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: ws, layout: TableLayoutType.FIXED,
      borders: { top: { style: BorderStyle.SINGLE, size: 4, color: COL.line }, bottom: { style: BorderStyle.SINGLE, size: 4, color: COL.line },
        left: { style: BorderStyle.SINGLE, size: 4, color: COL.line }, right: { style: BorderStyle.SINGLE, size: 4, color: COL.line },
        insideHorizontal: { style: BorderStyle.SINGLE, size: 4, color: COL.line }, insideVertical: { style: BorderStyle.SINGLE, size: 4, color: COL.line } },
      rows: rows.map((r, i) => new TableRow({ cantSplit: true, tableHeader: i === 0, children: r.map((c, j) => new TableCell({ width: { size: ws[j], type: WidthType.DXA },
        verticalAlign: VerticalAlign.CENTER, shading: { type: ShadingType.CLEAR, color: 'auto', fill: i === 0 ? COL.teal : i % 2 ? 'FFFFFF' : COL.tint },
        margins: { top: 40, bottom: 40, left: 90, right: 90 },
        children: [P({ spacing: { after: 0, line: 260 }, alignment: j === 2 ? AlignmentType.LEFT : AlignmentType.CENTER, children: runs(nb(c), { size: 19, bold: i === 0, color: i === 0 ? 'FFFFFF' : COL.ink }) })] })) })) }));
  }
  return out;
}

// ---------------------------------------------------------------- 组装
function build() {
  const body = [];
  for (const st of SETS) {
    body.push(...setHeading(st), ...setInfo(st));
    if (T) body.push(...teacherIntro(st));
    st.parts.forEach((p, k) => body.push(...renderPart(st, p, k === st.parts.length - 1)));
  }
  const tocParas = [P({ pageBreakBefore: true, spacing: { after: 320 }, border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: COL.accent, space: 6 } },
    children: [new TextRun({ text: '目　录', font: F, size: 36, bold: true, color: COL.main })] })];
  for (const t of toc) {
    tocParas.push(P({ tabStops: [{ type: TabStopType.LEFT, position: 1100 }, { type: TabStopType.RIGHT, position: CONTENT_W, leader: 'dot' }], spacing: { before: 120, after: 0 }, keepNext: true,
      children: [new InternalHyperlink({ anchor: t.id, children: [new TextRun({ text: t.text.replace('　', '\t'), font: F, size: 23, bold: true, color: COL.ink })] }),
        new TextRun({ text: '\t', font: F, size: 23 }), new PageReference(t.id, { font: F })] }));
    tocParas.push(P({ indent: { left: 1100 }, spacing: { after: 60 }, children: runs(t.es, { size: 19, color: COL.teal, italics: true }) }));
  }
  const cover = [
    P({ spacing: { before: 3000, after: 200 }, children: [new TextRun({ text: 'Español A1—A2 · Comprensión auditiva · ' + (T ? 'Libro del profesor' : 'Libro del alumno'), font: F, size: 28, color: COL.teal })] }),
    P({ spacing: { after: 200 }, children: [new TextRun({ text: TITLE, font: F, size: 72, bold: true, color: COL.main })] }),
    P({ spacing: { after: 1200 }, border: { bottom: { style: BorderStyle.SINGLE, size: 18, color: COL.accent, space: 10 } },
      children: [new TextRun({ text: BOOK, font: F, size: 44, bold: true, color: COL.body })] }),
    P({ spacing: { after: 120 }, children: runs(`${SETS.length} 套 · 每套 ${[...new Set(SETS.map((s) => s.n_questions))].join('—')} 题 · 配录音（${SETS.reduce((a, s) => a + s.parts.length, 0)} 段 MP3）`, { size: 24, color: COL.muted }) }),
    P({ spacing: { after: 120 }, children: runs('从 A1 巩固到 A2（假期、经历、健康、旅行、购物、学习和工作）', { size: 24, color: COL.muted }) }),
    P({ spacing: { after: 120 }, children: runs('题目和录音全部原创', { size: 24, color: COL.muted }) }),
    P({ spacing: { after: 120 }, children: runs(T ? '含答案和依据、全部录音原文和中文译文、使用建议' : '只有题目和答题处，可以直接打印', { size: 24, color: COL.muted }) }),
    P({ spacing: { after: 120 }, children: runs('2026 年 11 月', { size: 24, color: COL.muted }) }),
  ];
  const header = new Header({ children: [P({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: `${TITLE} · ${BOOK}`, font: F, size: 16, color: COL.muted })] })] });
  const footer = new Footer({ children: [P({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: [PageNumber.CURRENT], font: F, size: 18, color: COL.muted })] })] });
  const page = { size: { width: PAGE_W, height: PAGE_H }, margin: { top: MARGIN, bottom: MARGIN, left: MARGIN, right: MARGIN, header: 560, footer: 560 } };
  const doc = new Document({
    creator: 'spanish-video-kit', title: `${TITLE} · ${BOOK}`, description: '西班牙语 A1—A2 听力练习（10 套，配录音）',
    features: { updateFields: true },
    styles: {
      default: { document: { run: { font: F, size: SZ, color: COL.ink }, paragraph: { spacing: { line: 300 } } } },
      paragraphStyles: [{ id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { font: F, bold: true, color: COL.main, size: 34 }, paragraph: { outlineLevel: 0 } }],
    },
    numbering: { config: [{ reference: 'bullets', levels: [
      { level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 400, hanging: 260 } } } },
    ] }] },
    sections: [
      { properties: { page }, children: cover },
      { properties: { page: { ...page, pageNumbers: { start: 1 } } }, headers: { default: header }, footers: { default: footer }, children: [...frontMatter(), ...tocParas, ...body] },
    ],
  });
  fs.mkdirSync(path.dirname(OUT), { recursive: true });
  return Packer.toBuffer(doc).then(async (buf) => {
    const JSZip = require('jszip');
    const zip = await JSZip.loadAsync(buf);
    let st = await zip.file('word/styles.xml').async('string');
    // 行末标点不伸出版心（同 build_a2.js）
    if (st.includes('<w:pPrDefault><w:pPr>')) st = st.replace('<w:pPrDefault><w:pPr>', '<w:pPrDefault><w:pPr><w:overflowPunct w:val="0"/>');
    else if (st.includes('<w:pPrDefault>')) st = st.replace(/<w:pPrDefault>(<w:pPr[^>]*\/>)?/, '<w:pPrDefault><w:pPr><w:overflowPunct w:val="0"/></w:pPr>');
    else st = st.replace('<w:docDefaults>', '<w:docDefaults><w:pPrDefault><w:pPr><w:overflowPunct w:val="0"/></w:pPr></w:pPrDefault>');
    if (!st.includes('overflowPunct')) throw new Error('styles.xml: overflowPunct 没加上');
    zip.file('word/styles.xml', st);
    let docx = await zip.file('word/document.xml').async('string');
    let bid = 0; const open = [];
    docx = docx.replace(/<w:bookmark(Start|End)\b([^>]*?)w:id="\d+"/g, (m, kind, mid) => {
      if (kind === 'Start') { bid += 1; open.push(bid); return `<w:bookmarkStart${mid}w:id="${bid}"`; }
      return `<w:bookmarkEnd${mid}w:id="${open.shift()}"`;
    });
    if (open.length) throw new Error('书签开始和结束对不上');
    docx = docx.replace(/<w:pPr>([\s\S]*?)<\/w:pPr>/g, (m, inner) => (inner.includes('overflowPunct') ? m
      : `<w:pPr>${inner.replace(/(<w:(?:topLinePunct|autoSpaceDE|autoSpaceDN|bidi|adjustRightInd|snapToGrid|spacing|ind|contextualSpacing|mirrorIndents|suppressOverlap|jc|textDirection|textAlignment|outlineLvl|rPr)\b)|$/, '<w:overflowPunct w:val="0"/>$1')}</w:pPr>`));
    zip.file('word/document.xml', docx);
    fs.writeFileSync(OUT, await zip.generateAsync({ type: 'nodebuffer', compression: 'DEFLATE' }));
    console.log(OUT, `${toc.length} 条目录`);
  });
}
build().catch((e) => { console.error(e.stack || e.message); process.exit(1); });
