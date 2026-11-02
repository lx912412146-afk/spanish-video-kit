// 《现代西班牙语》第一册（老版）分课单词表排版：data/vocab.json（tools/merge.py 生成）→ docx
// 用法：node build_vocab.js [输出文件]
// 排版函数沿用 listen2/build_listening.js（PingFang SC、A4、行末标点不伸出版心）。
const fs = require('fs');
const path = require('path');
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, Bookmark, PageReference, InternalHyperlink, TabStopType,
  Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle, AlignmentType, Header, Footer, PageNumber,
  LevelFormat, TableLayoutType, VerticalAlign,
} = require('docx');

const HERE = __dirname;
const TITLE = '现代西班牙语 第一册（老版）分课单词表';
const OUT = process.argv[2] || path.join(HERE, 'out', '现代西班牙语第一册（老版）分课单词表.docx');
const D = JSON.parse(fs.readFileSync(path.join(HERE, 'data', 'vocab.json'), 'utf8'));
const LESSONS = D.lessons, CONJ = D.conj;
const F = { ascii: 'PingFang SC', hAnsi: 'PingFang SC', eastAsia: 'PingFang SC', cs: 'PingFang SC' };
const LANG = { value: 'es-ES', eastAsia: 'zh-CN' };
const COL = { main: '7A2E3B', accent: 'C98A2B', ink: '1F2933', body: '3E4C59', muted: '6B7785',
  teal: '2F6F73', tealSoft: 'E3F0EF', tint: 'F3F5F8', line: 'C9D3DE', irr: 'C0392B' };
const PAGE_W = 11906, PAGE_H = 16838, MARGIN = 1134, CONTENT_W = PAGE_W - 2 * MARGIN;
const SZ = 21;
const TS = 19;                           // 表格字号（半磅）

// ---------------------------------------------------------------- 文字
function runs(text, o = {}) {
  const out = [];
  for (const p of String(text).split(/(\*\*[^*]+\*\*)/g)) {
    if (!p) continue;
    const bold = /^\*\*[^*]+\*\*$/.test(p);
    const s = bold ? p.slice(2, -2) : p;
    out.push(new TextRun({ text: s, font: F, language: LANG, size: o.size || SZ, bold: o.bold || bold, italics: o.italics,
      color: o.color || COL.ink }));
  }
  return out;
}
function textW(s) { let w = 0; for (const ch of String(s).replace(/\*\*/g, '')) w += /[⺀-鿿＀-￯　-〿…—‘’“”←-⇿]/.test(ch) ? 1 : 0.55; return w; }
const twips = (s, size) => Math.ceil(textW(s) * size * 10 * 1.05);
// 数字和后面的汉字之间不断行（第 8 课、10 课）
const nb = (s) => String(s).replace(/(\d) (?=[一-鿿])/g, '$1 ').replace(/([一-鿿]) (?=\d)/g, '$1 ');

let bm = 0;
const toc = [];
const P = (o) => new Paragraph(o);
function para(text, o = {}) {
  return P({ alignment: AlignmentType.LEFT, widowControl: true, spacing: { after: o.after ?? 100, before: o.before || 0, line: o.line || 300 },
    keepNext: !!o.keep, keepLines: true, indent: o.indent, pageBreakBefore: !!o.pageBreak,
    children: Array.isArray(text) ? text : runs(nb(text), o) });
}
function sub(t, o = {}) {
  return P({ keepNext: true, keepLines: true, spacing: { before: o.first ? 120 : 300, after: 100 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: COL.line, space: 3 } },
    children: [...runs(t, { size: 24, bold: true, color: COL.main }), ...(o.hint ? runs(`　${o.hint}`, { size: 18, color: COL.muted }) : [])] });
}

// ---------------------------------------------------------------- 表格
const BORDERS = { top: { style: BorderStyle.SINGLE, size: 4, color: COL.line }, bottom: { style: BorderStyle.SINGLE, size: 4, color: COL.line },
  left: { style: BorderStyle.SINGLE, size: 4, color: COL.line }, right: { style: BorderStyle.SINGLE, size: 4, color: COL.line },
  insideHorizontal: { style: BorderStyle.SINGLE, size: 4, color: COL.line }, insideVertical: { style: BorderStyle.SINGLE, size: 4, color: COL.line } };
const CM = 70;                            // 单元格左右边距
const overflow = [];
// cells：每格是字符串，或 { runs: [...], w: 估算用的文字 }；head：表头（第一行重复）
function table(ws, head, rows, o = {}) {
  const size = o.size || TS;
  const keep = o.keep ?? rows.length <= 10;     // 短表整张不拆页
  const mk = (c, j, i, isHead) => {
    const content = typeof c === 'string' ? runs(nb(c), { size, bold: isHead, color: isHead ? 'FFFFFF' : COL.ink }) : c.runs;
    if (o.noWrap && o.noWrap[j] && !isHead) {
      const w = twips(typeof c === 'string' ? c : c.w, size) + 2 * CM;
      if (w > ws[j]) overflow.push(`${typeof c === 'string' ? c : c.w}（${w} > ${ws[j]}）`);
    }
    return new TableCell({ width: { size: ws[j], type: WidthType.DXA }, verticalAlign: VerticalAlign.CENTER,
      shading: { type: ShadingType.CLEAR, color: 'auto', fill: isHead ? COL.teal : (o.fill && o.fill(i, j)) || (i % 2 ? COL.tint : 'FFFFFF') },
      margins: { top: 30, bottom: 30, left: CM, right: CM },
      children: [P({ keepNext: keep && (isHead || i < rows.length - 1), keepLines: true, spacing: { after: 0, line: 250 }, alignment: (o.center && o.center[j]) ? AlignmentType.CENTER : AlignmentType.LEFT, children: content })] });
  };
  const trs = [];
  if (head) trs.push(new TableRow({ cantSplit: true, tableHeader: true, children: head.map((c, j) => mk(c, j, 0, true)) }));
  rows.forEach((r, i) => trs.push(new TableRow({ cantSplit: true, children: r.map((c, j) => mk(c, j, i, false)) })));
  return new Table({ width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: ws, layout: TableLayoutType.FIXED, borders: BORDERS, rows: trs });
}

// ---------------------------------------------------------------- 每一课
const vtag = (e) => e.vtype.join('，');
function wordTable(L) {
  const rows = L.words.map((e) => [
    { runs: runs(e.lemma, { size: TS, bold: e.core, color: e.core ? COL.main : COL.ink }), w: e.lemma },
    e.pos, e.zh, [vtag(e), e.note].filter(Boolean).join('；'),
  ]);
  return table([2500, 950, 2750, 3438], ['西语', '词性', '中文释义', '备注'], rows);
}
function phonTable(L) {
  const es = L.phon, half = Math.ceil(es.length / 2), rows = [];
  for (let i = 0; i < half; i++) {
    const a = es[i], b = es[i + half];
    rows.push([a.lemma, a.pos, a.zh, b ? b.lemma : '', b ? b.pos : '', b ? b.zh : '']);
  }
  return table([1750, 750, 2319, 1750, 750, 2319], ['西语', '词性', '中文', '西语', '词性', '中文'], rows);
}
function formTable(list, head0, note) {
  return table([2100, 2000, 5538], [head0, '原形', '说明'], list.map((v) => [v.form, v.lemma, note(v)]));
}
const PERS = ['yo', 'tú', 'él/ella/Ud.', 'nosotros', 'vosotros', 'ellos/ellas/Uds.'];
const CW = [2000, 1910, 1910, 1909, 1909];
function conjBlock(v) {
  const c = CONJ[v];
  const e = LESSONS.flatMap((L) => L.words).find((w) => w.lemma === v && w.pos === 'v.');
  const id = `v${++bm}`;
  verbIndex.push({ id, verb: v, zh: e.zh, lesson: e.lesson });
  const cell = (x) => ({ runs: runs(x.f, { size: 18, bold: x.irr, color: x.irr ? COL.irr : COL.ink }), w: x.f });
  const ger = (x) => runs(x.f, { size: 18, bold: x.irr, color: x.irr ? COL.irr : COL.body });
  const headLine = P({ keepNext: true, keepLines: true, spacing: { before: 200, after: 60 }, tabStops: [{ type: TabStopType.RIGHT, position: CONTENT_W }],
    children: [new Bookmark({ id, children: runs(v, { size: 24, bold: true, color: COL.main }) }),
      ...runs(`　${e.zh}`, { size: 20, color: COL.ink }),
      ...(e.vtype.length ? runs(`　${vtag(e)}`, { size: 18, color: COL.teal }) : []),
      new TextRun({ text: '\t', font: F, size: 18 }),
      ...runs('副动词 ', { size: 17, color: COL.muted }), ...ger(c.ger), ...runs('　过去分词 ', { size: 17, color: COL.muted }), ...ger(c.part)] });
  const rows = c.rows.map((r, i) => [PERS[i], ...r.map(cell)]);
  const out = [headLine, table(CW, ['人称', '陈述式现在时', '简单过去时', '过去未完成时', '命令式'], rows,
    { size: 18, keep: true, noWrap: [true, true, true, true, true], fill: (i, j) => (j === 0 ? COL.tealSoft : null) })];
  if (c.notes.length) out.push(para(c.notes.join('；'), { size: 18, color: COL.muted, before: 40, after: 0 }));
  return out;
}
const verbIndex = [];
function lesson(L) {
  const id = `l${++bm}`;
  toc.push({ id, text: `第 ${L.lesson} 课　${L.title_zh}`, es: L.title_es });
  const out = [
    P({ pageBreakBefore: true, keepNext: true, keepLines: true, spacing: { after: 60 }, heading: HeadingLevel.HEADING_1,
      children: [new Bookmark({ id, children: [new TextRun({ text: `第 ${L.lesson} 课　${L.title_zh}`, font: F, size: 34, bold: true, color: COL.main })] })] }),
    P({ keepNext: true, spacing: { after: 100 }, border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: COL.accent, space: 6 } },
      children: runs(`Lección ${L.lesson}　${L.title_es}`, { size: 23, color: COL.teal, italics: true }) }),
  ];
  const core = L.words.filter((e) => e.core).length;
  const bits = [`新词 ${L.words.length} 个（加粗的 ${core} 个在本课课件生词表里）`];
  if (L.verbs.length) bits.push(`新动词 ${L.verbs.length} 个`);
  if (L.vforms.length) bits.push(`第一次出现的动词形式 ${L.vforms.length} 个`);
  if (L.phon.length) bits.push(`语音练习词 ${L.phon.length} 个`);
  out.push(para(bits.join('　·　'), { size: 19, color: COL.muted, after: 60 }));
  out.push(sub('生词', { first: true, hint: '本课第一次出现的词，按字母顺序' }), wordTable(L));
  if (L.seen.length) {
    out.push(para([...runs('本课课件生词表里另有几条，前面课里已经出现过：', { size: 19, color: COL.muted }),
      ...L.seen.flatMap((s, i) => [...(i ? runs('；', { size: 19, color: COL.muted }) : []), ...runs(s.item, { size: 19, bold: true, color: COL.main }),
        ...runs(`（${s.where}）`, { size: 19, color: COL.muted })])], { before: 80, after: 0 }));
  }
  if (L.phon.length) out.push(sub('语音练习词', { hint: '只在本课语音练习里出现、课文里还没用到的词' }), phonTable(L));
  if (L.vforms.length) {
    out.push(sub('本课出现的动词形式', { hint: '第一次出现的变位形式 → 原形' }),
      formTable(L.vforms, '动词形式', (v) => [v.analysis, v.usage].filter(Boolean).join('；')));
  }
  if (L.newforms.length) out.push(sub('已学词的新形式', { hint: '前面课里学过的词，本课第一次出现的形式和用法' }), formTable(L.newforms, '词形', (v) => v.note));
  if (L.verbs.length) {
    out.push(sub('新动词变位表', { hint: '红色加粗：和规则变位不一样的形式' }));
    for (const v of L.verbs) out.push(...conjBlock(v));
  }
  if (L.phrases.length) {
    out.push(sub('常用表达'), table([4900, 4738], ['西语', '中文'], L.phrases.map((p) => [p[0], p[1]])));
  }
  return out;
}

// ---------------------------------------------------------------- 前言
function frontMatter() {
  const out = [];
  const h = (t) => P({ keepNext: true, spacing: { before: 200, after: 80 }, children: runs(t, { size: 26, bold: true, color: COL.main }) });
  const li = (t) => P({ numbering: { reference: 'bullets', level: 0 }, spacing: { after: 40, line: 290 }, keepLines: true, children: runs(nb(t), { size: 20 }) });
  out.push(P({ spacing: { after: 200 }, border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: COL.accent, space: 6 } },
    children: runs('使用说明', { size: 36, bold: true, color: COL.main }) }));
  const nw = LESSONS.reduce((a, L) => a + L.words.length, 0), np = LESSONS.reduce((a, L) => a + L.phon.length, 0);
  const nv = LESSONS.reduce((a, L) => a + L.verbs.length, 0), nf = LESSONS.reduce((a, L) => a + L.vforms.length, 0);
  out.push(para(`本表按课整理《现代西班牙语》第一册（老版）24 课里出现的西语词：共 ${nw} 个词条，另有第 1—8 课语音练习里的 ${np} 个练习词；${nv} 个动词都附完整的变位表，各课课文、语法和练习里出现的 ${nf} 个动词变位形式都注明了原形和是什么形式。`, { size: 20 }));
  out.push(h('怎么整理的'));
  out.push(li('依据是本仓库里第一册（老版）24 课的课件：生词、语音练习、课文、语法要点和例句、常用表达、练习和小结。课件里出现的每个西语词形都归到词典原形（名词单数，形容词阳性单数，动词不定式），按第一次出现的课排。'));
  out.push(li('本表不是课本书后词汇表或各课生词表的翻印。词条、词性、释义是按课件里的用法重新整理的，和课本生词表的选词、释义可能不完全一样：课本有而课件没用到的词，这里没有；课件生词表以外、课文和练习里出现的词，这里也收了。'));
  out.push(li('课件每课生词表里的词（13—18 条）在本课新词表里加粗，是每课要重点掌握的词。生词表里有的词前面课里已经出现过（比如第 7 课的 el hospital 第 6 课已经出现），就在新词表下面单列一行，注明第一次出现在哪一课。'));
  out.push(li('课件按老版课本的拼写：sólo（副词“只”）、指示代词 éste、ése、aquél 带重音符号。现在的正字法这几个词一般不带重音（solo、este、ese、aquel），两种写法都算对。'));
  out.push(li('变位表由程序按规则生成，又和仓库里审校过的课件、教程变位表逐格核对过（55 个动词、1128 格），没有出入；各课动词形式的说明也逐条用程序复核过。'));
  out.push(h('每课的内容'));
  out.push(li('生词：本课第一次出现的词，按西语字母顺序（ñ 排在 n 后面），有词性、中文释义、备注（常用搭配、不规则的复数、动词的变位类型等）。'));
  out.push(li('语音练习词（第 1—8 课）：只在语音练习里出现、课文里还没用到的词。后面课文里用到时，在那一课的生词表里再列一次。'));
  out.push(li('本课出现的动词形式：课文、语法、练习里第一次出现的变位形式，注明原形和形式（如 hablo → hablar，陈述式现在时第一人称单数）。连写代词的写成“命令式 tú + me, lo”之类。'));
  out.push(li('已学词的新形式：前面学过的词本课第一次出现的特殊形式和用法，比如第 23 课的绝对最高级（riquísimo ← rico）。'));
  out.push(li('新动词变位表：本课第一次出现的动词，列出陈述式现在时、简单过去时、过去未完成时、命令式四个时态和副动词、过去分词。'));
  out.push(li('常用表达：课件每课的常用表达和中文。'));
  out.push(h('变位表怎么看'));
  out.push(li('红色加粗的是和规则变位不一样的形式：不规则变化、词根变化（e → ie、o → ue、e → i、u → ue）、重音变化（envío、continúo）、拼写变化（busqué、llegué、empecé、leyó）都标红。'));
  out.push(li('动词的类型标在变位表标题和生词备注里：e→ie、o→ue、e→i、u→ue 是词根变化；i→í、u→ú 是重音变化；“不规则”是有不规则形式的（conozco、tuve、fui 等），既有词根变化又有不规则形式的两样都标（poder：o→ue，不规则）；没有标的是规则动词。'));
  out.push(li('“人称”一栏 Ud. 是 usted（您），Uds. 是 ustedes（您们）。命令式一栏：第二行是 tú，第三行是 usted，第四行是 nosotros，第五行是 vosotros，第六行是 ustedes；yo 没有命令式。'));
  out.push(li('自复动词（levantarse 等）的变位带代词（me levanto），命令式把代词连写在后面（levántate、levantaos）。“—”表示这个人称或时态不用，比如 llover（下雨）只用第三人称单数。'));
  out.push(li('四个时态在第一册里学的顺序：'));
  out.push(table([3000, 6638], ['时态', '在第一册里学的课'], [
    ['陈述式现在时', '第 1—6 课 ser、estar、tener；第 7—9 课 -ar、-er、-ir 三种规则变位；第 13—14 课词根变化动词'],
    ['命令式', '第 15 课 tú、vosotros；第 16 课 usted、ustedes、nosotros；第 17 课不规则和词根变化动词'],
    ['简单过去时', '第 19 课规则变位和 ser、ir、hacer；第 20 课词根变化和不规则动词'],
    ['过去未完成时', '第 21 课；第 22、24 课和简单过去时对比'],
    ['副动词、过去分词', '第一册不专门讲，列出来供查阅'],
  ]));
  out.push(h('词性缩写'));
  out.push(table([1600, 3219, 1600, 3219], ['缩写', '意思', '缩写', '意思'], [
    ['m.', '阳性名词', 'adv.', '副词'], ['f.', '阴性名词', 'prep.', '前置词'], ['m., f.', '阴阳同形，或有阴阳两种词尾的名词', 'conj.', '连词'],
    ['m. pl.', '只用（常用）复数的阳性名词', 'art.', '冠词'], ['f. pl.', '只用复数的阴性名词', 'pron.', '代词'], ['adj.', '形容词', 'num.', '数词'],
    ['v.', '动词（包括自复动词）', 'interj.', '感叹词'], ['地名', '地名、国名、机构名', '', ''],
  ]));
  out.push(para('有阴阳两种形式的名词、形容词写成“amigo, amiga”“cubano, cubana”；表示国籍的词写作形容词，释义里同时给出“……人”和“……的”。人名没有收。', { size: 20, before: 100 }));
  return out;
}

// ---------------------------------------------------------------- 索引
const esKey = (s) => s.toLowerCase().replace(/ñ/g, 'n~').normalize('NFD').replace(/[̀-ͯ]/g, '');
function wordIndex() {
  const all = [];
  for (const L of LESSONS) {
    for (const e of L.words) all.push({ w: e.lemma, pos: e.pos, zh: e.zh, l: String(L.lesson) });
    for (const e of L.phon) if (!e.lesson) all.push({ w: e.lemma, pos: e.pos, zh: e.zh, l: `${L.lesson} 语` });
  }
  all.sort((a, b) => (esKey(a.w) < esKey(b.w) ? -1 : esKey(a.w) > esKey(b.w) ? 1 : 0));
  const rows = [];
  // 每行放两条，从左到右读（左右分栏、各放一半的话跨页以后对不上）
  for (let i = 0; i < all.length; i += 2) {
    const a = all[i], b = all[i + 1];
    rows.push([a.w, a.pos, a.zh, a.l, b ? b.w : '', b ? b.pos : '', b ? b.zh : '', b ? b.l : '']);
  }
  const id = `x${++bm}`;
  toc.push({ id, text: '词汇总索引', es: `${all.length} 个词条，按字母顺序，数字是课次（“语”是只在语音练习里出现）`, level: 1 });
  return [
    P({ pageBreakBefore: true, keepNext: true, spacing: { after: 120 }, heading: HeadingLevel.HEADING_1,
      border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: COL.accent, space: 6 } },
      children: [new Bookmark({ id, children: [new TextRun({ text: '词汇总索引', font: F, size: 34, bold: true, color: COL.main })] })] }),
    para('按西语字母顺序（不计重音，ñ 排在 n 后面），每行从左到右读两条；“课”一栏是第一次出现的课，“语”表示只在那一课的语音练习里出现。', { size: 19, color: COL.muted }),
    table([1450, 600, 2019, 750, 1450, 600, 2019, 750], ['西语', '词性', '中文', '课', '西语', '词性', '中文', '课'], rows,
      { size: 17, center: [false, false, false, true, false, false, false, true] }),
  ];
}
function verbIdx() {
  const vs = [...verbIndex].sort((a, b) => (esKey(a.verb) < esKey(b.verb) ? -1 : 1));
  const id = `x${++bm}`;
  toc.push({ id, text: '动词变位表索引', es: `${vs.length} 个动词，按字母顺序，附课次和页码`, level: 1 });
  const cellV = (v) => (v ? { runs: [new InternalHyperlink({ anchor: v.id, children: runs(v.verb, { size: 18, color: COL.ink }) })], w: v.verb } : '');
  const cellP = (v) => (v ? { runs: [new TextRun({ children: [new PageReference(v.id)], font: F, size: 18 })], w: '000' } : '');
  const rows = [];
  for (let i = 0; i < vs.length; i += 2) {
    const a = vs[i], b = vs[i + 1];
    rows.push([cellV(a), a.zh, String(a.lesson), cellP(a), cellV(b), b ? b.zh : '', b ? String(b.lesson) : '', cellP(b)]);
  }
  return [
    P({ pageBreakBefore: true, keepNext: true, spacing: { after: 120 }, heading: HeadingLevel.HEADING_1,
      border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: COL.accent, space: 6 } },
      children: [new Bookmark({ id, children: [new TextRun({ text: '动词变位表索引', font: F, size: 34, bold: true, color: COL.main })] })] }),
    para('每行从左到右读两个动词；“课”是第一次出现的课，“页”是变位表所在的页。', { size: 19, color: COL.muted }),
    table([1500, 1769, 750, 800, 1500, 1769, 750, 800], ['动词', '中文', '课', '页', '动词', '中文', '课', '页'], rows,
      { size: 18, center: [false, false, true, true, false, false, true, true] }),
  ];
}

// ---------------------------------------------------------------- 组装
function build() {
  const body = [];
  for (const L of LESSONS) body.push(...lesson(L));
  body.push(...wordIndex(), ...verbIdx());
  const tocParas = [P({ pageBreakBefore: true, spacing: { after: 320 }, border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: COL.accent, space: 6 } },
    children: [new TextRun({ text: '目　录', font: F, size: 36, bold: true, color: COL.main })] })];
  for (const t of toc) {
    tocParas.push(P({ tabStops: [...(t.level ? [] : [{ type: TabStopType.LEFT, position: 1300 }]), { type: TabStopType.RIGHT, position: CONTENT_W, leader: 'dot' }],
      spacing: { before: t.level ? 160 : 80, after: 0 }, keepNext: true,
      children: [new InternalHyperlink({ anchor: t.id, children: [new TextRun({ text: t.text.replace('　', '\t'), font: F, size: 22, bold: true, color: COL.ink })] }),
        new TextRun({ text: '\t', font: F, size: 22 }), new PageReference(t.id, { font: F })] }));
    tocParas.push(P({ indent: { left: 1300 }, spacing: { after: 30 }, children: runs(t.es, { size: 18, color: COL.teal, italics: !t.level }) }));
  }
  const nw = LESSONS.reduce((a, L) => a + L.words.length, 0), nv = LESSONS.reduce((a, L) => a + L.verbs.length, 0);
  const cover = [
    P({ spacing: { before: 3000, after: 200 }, children: [new TextRun({ text: 'Español moderno 1 (edición antigua) · Vocabulario por lecciones', font: F, size: 26, color: COL.teal })] }),
    P({ spacing: { after: 200 }, children: [new TextRun({ text: '现代西班牙语 第一册（老版）', font: F, size: 60, bold: true, color: COL.main })] }),
    P({ spacing: { after: 1200 }, border: { bottom: { style: BorderStyle.SINGLE, size: 18, color: COL.accent, space: 10 } },
      children: [new TextRun({ text: '分课单词表', font: F, size: 48, bold: true, color: COL.body })] }),
    P({ spacing: { after: 120 }, children: runs(`24 课 · ${nw} 个词条 · ${nv} 个动词的完整变位表`, { size: 24, color: COL.muted }) }),
    P({ spacing: { after: 120 }, children: runs('单词、词性、中文释义 · 动词原形和各课出现的变位形式 · 动词变位表', { size: 24, color: COL.muted }) }),
    P({ spacing: { after: 120 }, children: runs('按课件内容整理的学习用表，不是课本词汇表的翻印', { size: 24, color: COL.muted }) }),
    P({ spacing: { after: 120 }, children: runs('2026 年 11 月', { size: 24, color: COL.muted }) }),
  ];
  const header = new Header({ children: [P({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: TITLE, font: F, size: 16, color: COL.muted })] })] });
  const footer = new Footer({ children: [P({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: [PageNumber.CURRENT], font: F, size: 18, color: COL.muted })] })] });
  const page = { size: { width: PAGE_W, height: PAGE_H }, margin: { top: MARGIN, bottom: MARGIN, left: MARGIN, right: MARGIN, header: 560, footer: 560 } };
  const doc = new Document({
    creator: 'spanish-video-kit', title: TITLE, description: '《现代西班牙语》第一册（老版）24 课分课单词表，含动词变位表',
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
  if (overflow.length) console.log(`变位表里可能换行的格子 ${overflow.length} 个：`, overflow.slice(0, 20).join('；'));
  fs.mkdirSync(path.dirname(OUT), { recursive: true });
  return Packer.toBuffer(doc).then(async (buf) => {
    const JSZip = require('jszip');
    const zip = await JSZip.loadAsync(buf);
    let st = await zip.file('word/styles.xml').async('string');
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
    console.log(OUT, `${toc.length} 条目录，${verbIndex.length} 张变位表`);
  });
}
build().catch((e) => { console.error(e.stack || e.message); process.exit(1); });
