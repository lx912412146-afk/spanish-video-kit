// 《现代西班牙语》第二册（老版）分课单词表排版：data/vocab.json（tools/merge.py 生成）→ docx
// 用法：node build_vocab.js [输出文件]
// 版式沿用第一册单词表（PingFang SC、A4、行末标点不伸出版心）。
const fs = require('fs');
const path = require('path');
const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, Bookmark, PageReference, InternalHyperlink, TabStopType,
  Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle, AlignmentType, Header, Footer, PageNumber,
  LevelFormat, TableLayoutType, VerticalAlign,
} = require('docx');

const HERE = __dirname;
const TITLE = '现代西班牙语 第二册（老版）分课单词表';
const OUT = process.argv[2] || path.join(HERE, 'out', '现代西班牙语第二册（老版）分课单词表.docx');
const D = JSON.parse(fs.readFileSync(path.join(HERE, 'data', 'vocab.json'), 'utf8'));
const LESSONS = D.lessons, CONJ = D.conj, B1V = D.book1_verbs;
const STATS = fs.existsSync(path.join(HERE, 'data', 'check_stats.json')) ? JSON.parse(fs.readFileSync(path.join(HERE, 'data', 'check_stats.json'), 'utf8')) : null;
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
// 数字和后面的汉字之间不断行
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
const shrunk = [];
// 不换行的格子：字号从 base 往下减到放得下（最小 14，即 7 磅）
function fit(s, colW, base) {
  for (let z = base; z >= 14; z--) if (twips(s, z) + 2 * CM <= colW) { if (z < base) shrunk.push(`${s}（${z}）`); return z; }
  overflow.push(`${s}（${twips(s, 14) + 2 * CM} > ${colW}）`);
  return 14;
}
// cells：每格是字符串，或 { runs: [...], w: 估算用的文字 }；head：表头（第一行重复）
function table(ws, head, rows, o = {}) {
  const size = o.size || TS;
  const keep = o.keep ?? rows.length <= 10;     // 短表整张不拆页
  const mk = (c, j, i, isHead) => {
    const content = typeof c === 'string' ? runs(nb(c), { size: isHead && o.headSize ? o.headSize : size, bold: isHead, color: isHead ? 'FFFFFF' : COL.ink }) : c.runs;
    if (o.noWrap && o.noWrap[j] && !isHead && typeof c === 'string') {
      const w = twips(c, size) + 2 * CM;
      if (w > ws[j]) overflow.push(`${c}（${w} > ${ws[j]}）`);
    }
    return new TableCell({ width: { size: ws[j], type: WidthType.DXA }, verticalAlign: VerticalAlign.CENTER,
      shading: { type: ShadingType.CLEAR, color: 'auto', fill: isHead ? COL.teal : (o.fill && o.fill(i, j)) || (i % 2 ? COL.tint : 'FFFFFF') },
      margins: { top: 30, bottom: 30, left: CM, right: CM },
      children: [P({ keepNext: keep && (isHead || i < rows.length - 1 || o.keepAfter), keepLines: true, spacing: { after: 0, line: 250 }, alignment: (o.center && o.center[j]) ? AlignmentType.CENTER : AlignmentType.LEFT, children: content })] });
  };
  const trs = [];
  if (head) trs.push(new TableRow({ cantSplit: true, tableHeader: true, children: head.map((c, j) => mk(c, j, 0, true)) }));
  rows.forEach((r, i) => trs.push(new TableRow({ cantSplit: true, children: r.map((c, j) => mk(c, j, i, false)) })));
  return new Table({ width: { size: CONTENT_W, type: WidthType.DXA }, columnWidths: ws, layout: TableLayoutType.FIXED, borders: BORDERS, rows: trs });
}
// 变位形式的格子：不规则的红色加粗；放不下就缩小字号
const formCell = (x, colW, base, color = COL.ink) => {
  const z = fit(x.f, colW, base);
  return { runs: runs(x.f, { size: z, bold: x.irr, color: x.irr ? COL.irr : color }), w: x.f };
};

// ---------------------------------------------------------------- 每一课
const vtag = (e) => e.vtype.join('，');
function wordTable(L) {
  const rows = L.words.map((e) => [
    { runs: runs(e.lemma, { size: TS, bold: e.core, color: e.core ? COL.main : COL.ink }), w: e.lemma },
    e.pos, e.zh, [vtag(e), e.note].filter(Boolean).join('；'),
  ]);
  return table([2500, 950, 2750, 3438], ['西语', '词性', '中文释义', '备注'], rows);
}
function formTable(list, head0, note) {
  return table([2100, 2000, 5538], [head0, '原形', '说明'], list.map((v) => [v.form, v.lemma, note(v)]));
}
const PERS = ['yo', 'tú', 'él/ella/Ud.', 'nosotros', 'vosotros', 'ellos/ellas/Uds.'];
const CW_TOP = [1250, 1678, 1678, 1678, 1677, 1677];
const CW_BOT = [1250, 2796, 2796, 2796];
const verbIndex = [];
function conjBlock(v) {
  const c = CONJ[v];
  const e = LESSONS.flatMap((L) => L.words).find((w) => w.lemma === v && w.pos.split('；').includes('v.'));
  const id = `v${++bm}`;
  const title = c.aux ? `${v}（助动词）` : v;
  verbIndex.push({ id, verb: title, zh: c.aux ? '（助动词）' : e.zh, lesson: e.lesson });
  const ger = (x) => runs(x.f, { size: 18, bold: x.irr, color: x.irr ? COL.irr : COL.body });
  const headLine = P({ keepNext: true, keepLines: true, spacing: { before: 200, after: 60 }, tabStops: [{ type: TabStopType.RIGHT, position: CONTENT_W }],
    children: [new Bookmark({ id, children: runs(title, { size: 24, bold: true, color: COL.main }) }),
      ...runs(`　${c.aux ? '和过去分词构成复合时态' : e.zh}`, { size: 20, color: COL.ink }),
      ...(e.vtype.length && !c.aux ? runs(`　${vtag(e)}`, { size: 18, color: COL.teal }) : []),
      new TextRun({ text: '\t', font: F, size: 18 }),
      ...runs('副动词 ', { size: 17, color: COL.muted }), ...ger(c.ger), ...runs('　过去分词 ', { size: 17, color: COL.muted }), ...ger(c.part)] });
  const fill = (i, j) => (j === 0 ? COL.tealSoft : null);
  const top = c.top.map((r, i) => [PERS[i], ...r.map((x, j) => formCell(x, CW_TOP[j + 1], 17))]);
  const bot = c.bottom.map((r, i) => [PERS[i], ...r.map((x, j) => formCell(x, CW_BOT[j + 1], 17))]);
  const out = [headLine,
    table(CW_TOP, ['人称', '陈述式现在时', '简单过去时', '过去未完成时', '将来未完成时', '简单条件式'], top,
      { size: 17, headSize: 17, keep: true, keepAfter: true, fill }),
    P({ keepNext: true, keepLines: true, spacing: { before: 0, after: 0, line: 120 }, children: [] }),
    table(CW_BOT, ['人称', '虚拟式现在时', '肯定命令式', '否定命令式'], bot, { size: 17, headSize: 17, keep: true, fill })];
  if (c.notes.length) out.push(para(c.notes.join('；'), { size: 18, color: COL.muted, before: 40, after: 0 }));
  return out;
}
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
  out.push(para(bits.join('　·　'), { size: 19, color: COL.muted, after: 60 }));
  out.push(sub('生词', { first: true, hint: '本课第一次出现的词，按字母顺序；加粗的在本课课件生词表里' }), wordTable(L));
  if (L.seen.length) {
    out.push(sub('生词表里前面学过的词', { hint: '本课课件生词表里的这几条前面已经学过' }),
      table([2600, 4438, 2600], ['西语', '释义', '第一次出现'], L.seen.map((s) => [s.item, s.zh, s.where])));
  }
  if (L.vphrases.length) {
    out.push(sub('生词表里的短语', { hint: '课件生词表里的短语和固定搭配' }),
      table([4000, 5638], ['西语', '中文'], L.vphrases.map((p) => [p.es, p.zh])));
  }
  if (L.vforms.length) {
    out.push(sub('本课出现的动词形式', { hint: '第一次出现的变位形式 → 原形（第一册见过的不再列）' }),
      formTable(L.vforms, '动词形式', (v) => [v.analysis, v.usage].filter(Boolean).join('；')));
  }
  if (L.newforms.length) out.push(sub('已学词的新形式', { hint: '前面学过的词，本课第一次出现的形式和用法' }),
    formTable(L.newforms, '词形', (v) => `${v.note}（${v.lemma.split(',')[0]}：${v.where}）`));
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
  const nw = LESSONS.reduce((a, L) => a + L.words.length, 0);
  const nv = LESSONS.reduce((a, L) => a + L.verbs.length, 0), nf = LESSONS.reduce((a, L) => a + L.vforms.length, 0);
  out.push(para(`本表按课整理《现代西班牙语》第二册（老版）18 课里新出现的西语词：共 ${nw} 个词条；${nv} 个新动词都附完整的变位表，各课课文、语法和练习里第一次出现的 ${nf} 个动词变位形式都注明了原形和是什么形式。书后另有第一册 ${B1V.length} 个动词的新时态速查表。`, { size: 20 }));
  out.push(h('怎么整理的'));
  out.push(li('依据是本仓库里第二册（老版）18 课的课件：生词、课文、语法要点和例句、常用表达、练习、小结和作业。课件里出现的每个西语词形都归到词典原形（名词单数，形容词阳性单数，动词不定式），按第一次出现的课排。'));
  out.push(li('本表不是课本书后词汇表或各课生词表的翻印。词条、词性、释义是按课件里的用法重新整理的，和课本生词表的选词、释义可能不完全一样：课本有而课件没用到的词，这里没有；课件生词表以外、课文和练习里出现的词，这里也收了。'));
  out.push(li('接着第一册排：第一册 24 课课件里学过的词不再算新词，第一册见过的动词变位形式也不再列（第一册的单词表见 Release book1-vocab）。第一册只在语音练习里出现过的词，第二册用到时算新词，备注里注明。'));
  out.push(li('第一册学过、第二册有了新意思的词（比如 llevar“已有（多长时间）”、plato“（一道）菜”），在出现新意思的那一课单列一条，备注写明第一册的意思；第二册前面学过、后面有了新意思的（conseguir“做到”、acabar“完成”）也一样；同形的另一个词（Lima 利马、el sobre 信封这类）也单列。'));
  out.push(li('课件每课生词表里的词在本课新词表里加粗。生词表里前面已经学过的词（第一册或第二册前面的课），单列在“生词表里前面学过的词”，附本课课件的释义（常常带新的意思）和第一次出现的课；课件写成 poner(se) 这样的两个词分开对，本课新的那个列进生词，前面学过的那个列进这张表，释义只取课件释义里属于它的那部分；生词表里的短语（de pronto、acabar de + inf.）单列在“生词表里的短语”。'));
  out.push(li('课件按老版课本的拼写：sólo（副词“只”）、指示代词 éste、ése、aquél 带重音符号。现在的正字法这几个词一般不带重音（solo、este、ese、aquel），两种写法都算对。变位表里 reír 的 rio、riais 按现行正字法不写重音（老版课本写 rió、riáis）。'));
  const chk = STATS ? `（${STATS.verbs} 个动词、${STATS.cells} 格；第二册课件里每行列一个动词的表另核对了 ${STATS.rows} 个形式）` : '';
  out.push(li(`变位表由程序按规则生成，又和仓库里审校过的第一、二册课件和各教程里的变位表逐格核对过${chk}，没有出入；各课动词形式的说明也逐条用程序复核过。整理完以后对着课件逐条审读了两轮，每轮由两人分课审读（第 1—9 课、第 10—18 课），变位表另由一人逐格核对，改正后重新生成。`));
  out.push(h('每课的内容'));
  out.push(li('生词：本课第一次出现的词，按西语字母顺序（ñ 排在 n 后面），有词性、中文释义、备注（常用搭配、不规则的复数、动词的变位类型等）。'));
  out.push(li('生词表里前面学过的词、生词表里的短语：见上。'));
  out.push(li('本课出现的动词形式：课文、语法、练习里第一次出现的变位形式，注明原形和形式（如 tendré → tener，将来未完成时第一人称单数）。虚拟式现在时用在否定命令式里（no hagas）、haber 作助动词、过去分词作形容词或用于被动语态的，在说明里注出。'));
  out.push(li('已学词的新形式：前面学过的词本课第一次出现的特殊形式，比如指小词、绝对最高级、短尾形式。'));
  out.push(li('新动词变位表：本课第一次出现的动词的全部简单时态（见下）和副动词、过去分词。第一册学过的动词的新时态见书后速查表。'));
  out.push(li('常用表达：课件每课的常用表达和中文。'));
  out.push(h('变位表怎么看'));
  out.push(li('每个动词两张表：上表是陈述式现在时、简单过去时、过去未完成时、将来未完成时、简单条件式；下表是虚拟式现在时、肯定命令式、否定命令式（no + 虚拟式现在时）。标题行右边是副动词和过去分词。'));
  out.push(li('复合时态都是 haber + 过去分词：he hablado（现在完成时，第 13 课）、había hablado（过去完成时，第 15 课）。haber 作助动词的变位表在第 13 课。'));
  out.push(li('红色加粗的是和规则变位不一样的形式：不规则变化、词根变化（e → ie、o → ue、e → i、u → ue）、重音变化（envío、continúo）、拼写变化（busqué、llegué、empecé、leyó、no toques）、将来时和条件式的不规则词根（tendré、haría）都标红。'));
  out.push(li('动词的类型标在变位表标题和生词备注里：e→ie、o→ue、e→i、u→ue 是词根变化（-ir 动词的 e→ie、o→ue 另标 e→i、o→u：divirtió、durmió）；i→í、u→ú 是重音变化（envío、prohíbo、reúno）；“不规则”是有不规则形式的（conozco、tuve、tendré 等），既有词根变化又有不规则形式的两样都标；没有标的是规则动词。只有过去分词不规则的（describir → descrito、cubrir → cubierto）不标“不规则”，过去分词在变位表标题行标红。“相互动词”表示“互相……”，只用复数（nos abrazamos）；基本动词前面有变位表的不另出表，备注里注明。'));
  out.push(li('“人称”一栏 Ud. 是 usted（您），Uds. 是 ustedes（您们）。命令式两栏：第二行是 tú，第三行是 usted，第四行是 nosotros，第五行是 vosotros，第六行是 ustedes；yo 没有命令式。'));
  out.push(li('自复动词的变位带代词（me levanto）；肯定命令式把代词连写在后面（levántate），否定命令式代词放在动词前（no te levantes）。“—”表示这个人称或时态不用，比如 llover（下雨）只用第三人称单数。'));
  out.push(P({ numbering: { reference: 'bullets', level: 0 }, spacing: { after: 40, line: 290 }, keepLines: true, keepNext: true, children: runs('第二册新学的时态和动词形式：', { size: 20 }) }));
  out.push(table([3200, 6438], ['时态、形式', '在第二册里学的课'], [
    ['过去分词', '第 1 课构成和作形容词；第 13 课不规则分词；第 16 课 ser + 过去分词（被动语态）'],
    ['否定命令式（虚拟式现在时的变位）', '第 3 课；第 6 课复习'],
    ['副动词', '第 3 课构成和 estar + 副动词；第 4、5、16 课用法；第 8、10 课 ir / seguir / llevar + 副动词'],
    ['将来未完成时', '第 7 课变位和用法；第 8 课表示推测；第 12 课复习'],
    ['虚拟式现在时', '第 9、10 课用在名词性从句里；第 12 课复习'],
    ['现在完成时', '第 13 课；第 14 课和简单过去时对比；第 18 课复习'],
    ['过去完成时', '第 15 课；第 18 课复习'],
    ['简单条件式', '第 16 课；第 18 课复习'],
  ]));
  out.push(h('词性缩写'));
  out.push(table([1600, 3219, 1600, 3219], ['缩写', '意思', '缩写', '意思'], [
    ['m.', '阳性名词', 'adv.', '副词'], ['f.', '阴性名词', 'prep.', '前置词'], ['m., f.', '阴阳同形，或有阴阳两种词尾的名词', 'conj.', '连词'],
    ['m. pl.', '只用（常用）复数的阳性名词', 'art.', '冠词'], ['f. pl.', '只用复数的阴性名词', 'pron.', '代词'], ['adj.', '形容词', 'num.', '数词'],
    ['v.', '动词（包括自复动词）', 'interj.', '感叹词'], ['地名', '地名、国名、机构名', '', ''],
  ]));
  out.push(para('有阴阳两种形式的名词、形容词写成“vecino, vecina”“griego, griega”；表示国籍、民族的词写作形容词，释义里同时给出“……人”和“……的”。人名没有收。', { size: 20, before: 100 }));
  return out;
}

// ---------------------------------------------------------------- 书后
const esKey = (s) => s.toLowerCase().replace(/ñ/g, 'n~').normalize('NFD').replace(/[̀-ͯ]/g, '');
const h1 = (id, t) => P({ pageBreakBefore: true, keepNext: true, spacing: { after: 120 }, heading: HeadingLevel.HEADING_1,
  border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: COL.accent, space: 6 } },
  children: [new Bookmark({ id, children: [new TextRun({ text: t, font: F, size: 34, bold: true, color: COL.main })] })] });
function wordIndex() {
  const all = [];
  for (const L of LESSONS) for (const e of L.words) all.push({ w: e.lemma, pos: e.pos, zh: e.zh, l: String(L.lesson) });
  all.sort((a, b) => (esKey(a.w) < esKey(b.w) ? -1 : esKey(a.w) > esKey(b.w) ? 1 : Number(a.l) - Number(b.l)));
  const rows = [];
  // 每行放两条，从左到右读（左右分栏、各放一半的话跨页以后对不上）
  for (let i = 0; i < all.length; i += 2) {
    const a = all[i], b = all[i + 1];
    rows.push([a.w, a.pos, a.zh, a.l, b ? b.w : '', b ? b.pos : '', b ? b.zh : '', b ? b.l : '']);
  }
  const id = `x${++bm}`;
  toc.push({ id, text: '词汇总索引', es: `${all.length} 个词条，按字母顺序，数字是课次`, level: 1 });
  return [
    h1(id, '词汇总索引'),
    para('按西语字母顺序（不计重音，ñ 排在 n 后面），每行从左到右读两条；“课”一栏是第一次出现（或有新意思）的课。', { size: 19, color: COL.muted }),
    table([1450, 600, 2069, 700, 1450, 600, 2069, 700], ['西语', '词性', '中文', '课', '西语', '词性', '中文', '课'], rows,
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
    h1(id, '动词变位表索引'),
    para('每行从左到右读两个动词；“课”是第一次出现的课，“页”是变位表所在的页。', { size: 19, color: COL.muted }),
    table([1650, 1619, 650, 900, 1650, 1619, 650, 900], ['动词', '中文', '课', '页', '动词', '中文', '课', '页'], rows,
      { size: 18, center: [false, false, true, true, false, false, true, true] }),
  ];
}
function book1Verbs() {
  const id = `x${++bm}`;
  toc.push({ id, text: '第一册动词的新时态', es: `第一册 ${B1V.length} 个动词的将来未完成时、简单条件式、虚拟式现在时和过去分词`, level: 1 });
  const ws = [1250, 1350, 420, 1300, 1400, 1200, 1480, 0];
  ws[7] = CONTENT_W - ws.slice(0, 7).reduce((a, b) => a + b, 0);   // 1238
  const rows = B1V.map((r) => [
    { runs: runs(r.verb, { size: fit(r.verb, ws[0], 17), bold: true, color: COL.main }), w: r.verb },
    r.zh + (r.third ? '（只用第三人称单数）' : ''), String(r.lesson),
    formCell(r.fut, ws[3], 17), formCell(r.cond, ws[4], 17), formCell(r.subj1, ws[5], 17), formCell(r.subj4, ws[6], 17), formCell(r.part, ws[7], 17),
  ]);
  const notes = B1V.filter((r) => r.notes.length).map((r) => `${r.verb}：${r.notes.join('；')}`);
  return [
    h1(id, '第一册动词的新时态'),
    para('第一册学过的动词，第二册新学的几个时态：将来未完成时、简单条件式、虚拟式现在时（也是否定命令式的形式）列出 yo 的形式（只用第三人称单数的动词列第三人称单数），虚拟式另列 nosotros（-ir 词根变化动词这一人称要变：durmamos、pidamos），最后是过去分词（构成现在完成时、过去完成时）。红色加粗的是和规则变位不一样的形式。“课”是第一册里第一次出现的课；完整的现在时、简单过去时、过去未完成时和命令式见第一册单词表。', { size: 19, color: COL.muted }),
    ...(notes.length ? [para(notes.join('。') + '。', { size: 18, color: COL.muted })] : []),
    table(ws, ['动词', '中文', '课', '将来未完成时', '简单条件式', '虚拟式 yo', '虚拟式 nosotros', '过去分词'], rows,
      { size: 17, headSize: 16, center: [false, false, true, false, false, false, false, false] }),
  ];
}

// ---------------------------------------------------------------- 组装
function build() {
  const body = [];
  for (const L of LESSONS) body.push(...lesson(L));
  body.push(...wordIndex(), ...verbIdx(), ...book1Verbs());
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
    P({ spacing: { before: 3000, after: 200 }, children: [new TextRun({ text: 'Español moderno 2 (edición antigua) · Vocabulario por lecciones', font: F, size: 26, color: COL.teal })] }),
    P({ spacing: { after: 200 }, children: [new TextRun({ text: '现代西班牙语 第二册（老版）', font: F, size: 60, bold: true, color: COL.main })] }),
    P({ spacing: { after: 1200 }, border: { bottom: { style: BorderStyle.SINGLE, size: 18, color: COL.accent, space: 10 } },
      children: [new TextRun({ text: '分课单词表', font: F, size: 48, bold: true, color: COL.body })] }),
    P({ spacing: { after: 120 }, children: runs(`18 课 · ${nw} 个词条 · ${nv} 个新动词的完整变位表`, { size: 24, color: COL.muted }) }),
    P({ spacing: { after: 120 }, children: runs('单词、词性、中文释义 · 各课出现的动词新形式 · 动词变位表 · 第一册动词的新时态', { size: 24, color: COL.muted }) }),
    P({ spacing: { after: 120 }, children: runs('按课件内容整理的学习用表，不是课本词汇表的翻印', { size: 24, color: COL.muted }) }),
    P({ spacing: { after: 120 }, children: runs('2026 年 11 月', { size: 24, color: COL.muted }) }),
  ];
  const header = new Header({ children: [P({ alignment: AlignmentType.RIGHT, children: [new TextRun({ text: TITLE, font: F, size: 16, color: COL.muted })] })] });
  const footer = new Footer({ children: [P({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: [PageNumber.CURRENT], font: F, size: 18, color: COL.muted })] })] });
  const page = { size: { width: PAGE_W, height: PAGE_H }, margin: { top: MARGIN, bottom: MARGIN, left: MARGIN, right: MARGIN, header: 560, footer: 560 } };
  const doc = new Document({
    creator: 'spanish-video-kit', title: TITLE, description: '《现代西班牙语》第二册（老版）18 课分课单词表，含动词变位表',
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
  if (overflow.length) console.log(`放不下、可能换行的格子 ${overflow.length} 个：`, overflow.slice(0, 20).join('；'));
  if (shrunk.length) console.log(`缩小了字号的格子 ${shrunk.length} 个：`, shrunk.slice(0, 30).join('；'));
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
