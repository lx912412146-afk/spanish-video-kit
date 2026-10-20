// 《现代西班牙语》（老版）分课课件生成：content/Lxx.json → out/第xx课_….pptx（JSON 里的 book 字段决定第几册，默认第一册）
// 用法：node build_decks.js [01 02 …]（不给就生成全部）
const fs = require('fs');
const path = require('path');
const pptxgen = require('pptxgenjs');

const HERE = __dirname;
const OUT = process.env.OUT_DIR || path.join(HERE, 'out');
const CONTENT = process.env.CONTENT_DIR || path.join(HERE, 'content');
const FONT = 'PingFang SC';
const COL = {
  wine: '7A1F2B', wineDark: '5C1620', saffron: 'E8A33D', saffronSoft: 'FCEFD8', ink: '1F2933', body: '3E4C59',
  muted: '7B8794', line: 'E4D7D1', tint: 'F7F1EE', teal: '2F6F73', tealSoft: 'E3F0EF', white: 'FFFFFF',
};
const BOOKS = { 1: '第一册', 2: '第二册', 3: '第三册', 4: '第四册' };
const bookName = (d) => BOOKS[d.book || 1];
const W = 13.333, H = 7.5, MX = 0.6, TOP = 1.45, BOTTOM = 6.75;

// ---- 文字量估算（磅 → 英寸；中文每字约 1 个字号宽，西文约 0.55）
function textWidth(s, pt) {
  let w = 0;
  for (const ch of s) w += /[⺀-鿿＀-￯　-〿…—‘’“”←-⇿]/.test(ch) ? 1.0 : 0.56;
  return (w * pt) / 72;
}
function lines(s, pt, boxW) {
  return String(s).split('\n').reduce((n, part) => n + Math.max(1, Math.ceil(textWidth(part, pt) / (boxW * 0.94))), 0);
}
function height(s, pt, boxW, ls = 1.25) { return (lines(s, pt, boxW) * pt * ls) / 72; }
// 实测校准版（西文每字约 0.52 字宽），只用在卡片高度上
function heightCal(s, pt, boxW) {
  const n = String(s).split('\n').reduce((k, part) => {
    let w = 0; for (const ch of part) w += /[⺀-鿿＀-￯　-〿…—‘’“”←-⇿]/.test(ch) ? 1.0 : 0.52;
    return k + Math.max(1, Math.ceil((w * pt) / 72 / (boxW * 0.95)));
  }, 0);
  return (n * pt * 1.25) / 72;
}

function newDeck(d) {
  const pres = new pptxgen();
  pres.layout = 'LAYOUT_WIDE';
  pres.theme = { headFontFace: FONT, bodyFontFace: FONT };
  pres.title = `第${d.lesson}课 ${d.title_es}`;
  pres.subject = `《现代西班牙语》${bookName(d)}（老版）分课课件`;
  pres.author = 'spanish-video-kit';
  const footer = `《现代西班牙语》${bookName(d)} · 第 ${d.lesson} 课  ${d.title_es}`;
  pres.defineSlideMaster({
    title: 'CONTENT', background: { color: COL.white },
    objects: [
      { placeholder: { options: { name: 'title', type: 'title', x: MX, y: 0.42, w: W - 2 * MX, h: 0.85, fontFace: FONT,
        fontSize: 32, bold: true, color: COL.wine, valign: 'middle', align: 'left', margin: 0 }, text: '' } },
      { text: { text: footer, options: { x: MX, y: 7.0, w: 9, h: 0.3, fontFace: FONT, fontSize: 10, color: COL.muted, margin: 0 } } },
    ],
    slideNumber: { x: W - MX - 0.8, y: 7.0, w: 0.8, h: 0.3, fontFace: FONT, fontSize: 10, color: COL.muted, align: 'right' },
  });
  pres.defineSlideMaster({ title: 'DARK', background: { color: COL.wine }, objects: [] });
  return pres;
}

function add(pres, section, master = 'CONTENT') {
  pres._secs = pres._secs || new Set();
  if (!pres._secs.has(section)) { pres.addSection({ title: section }); pres._secs.add(section); }
  return pres.addSlide({ masterName: master, sectionTitle: section });
}
const fixTitle = (t) => nb(t).replace(/([A-Za-zÁÉÍÓÚáéíóúñü!?])、(?=[A-Za-z¿¡ÁÉÍÓÚáéíóúñ])/g, '$1, ');
const fit = (x, max, min) => { let pt = max; while (pt > min && textWidth(x, pt) > (W - 2 * MX) * 0.9) pt -= 1; return pt; };
const tooLong = (t) => fit(fixTitle(t), 32, 20) < 30;
function title(slide, t, split = false) {
  t = fixTitle(t);
  // 只在冒号处拆；没有冒号时只有课文标题可以在“ · ”处拆（语法标题的“ · ”在编号后面，不能拆）
  const pt = fit(t, 32, 20), sep = t.includes('：') ? '：' : (t.startsWith('语法') ? null : ' · '), k = sep ? t.indexOf(sep) : -1;
  // 占位符上设的字号会被版式覆盖，所以字号写在文字本身上
  if ((pt < 30 || split) && k > 0) {
    // 标题太长：冒号（或“ · ”）前作主标题（字号和别的页一样），后面的细目另起一行用小字；（表）和分页号留在主标题
    const tail = (t.match(/(（表）|（\d+\/\d+）)$/) || [''])[0], main = t.slice(0, k) + tail, sub = t.slice(k + sep.length, t.length - tail.length);
    slide.addText([{ text: main, options: { fontSize: fit(main, 32, 24), breakLine: true } },
      { text: sub, options: { fontSize: fit(sub, 20, 16), bold: false, color: COL.teal } }], { placeholder: 'title' });
    return;
  }
  slide.addText(pt < 32 ? [{ text: t, options: { fontSize: pt } }] : t, { placeholder: 'title' });
}
// 不让括号里的内容、箭头和填空线跟前后拆开换行；词尾写法（-ra、–se）前面的短横不和后面的字母拆开
function glue(t) {
  return String(t).replace(/(^|[\s（(、/])([-–])(?=[a-záéíóúñ])/g, '$1$2\u2060').replace(/[（(][^（）()]{1,24}[）)]/g, (m) => m.replace(/ /g, '\u00a0'))
    .replace(/ (→|—) /g, '\u00a0$1\u00a0').replace(/(_{2,}) /g, '$1\u00a0');
}
// 数字的分节空格（2 300 000）换成不换行空格，免得一个数拆到两行
const nb = (t) => String(t).replace(/(\d) (?=\d{3}(?!\d))/g, '$1\u00a0');
function tb(slide, text, o) {
  const t = Array.isArray(text) ? text.map((r) => Object.assign({}, r, { text: nb(r.text) })) : nb(text);
  slide.addText(t, Object.assign({ isTextBox: true, fontFace: FONT, margin: 0, valign: 'top' }, o));
}
function chunk(xs, n) { const out = []; for (let i = 0; i < xs.length; i += n) out.push(xs.slice(i, i + n)); return out; }
function circle(slide, pres, x, y, d, label, fill, color = COL.white, pt = 16) {
  slide.addShape(pres.shapes.OVAL, { x, y, w: d, h: d, fill: { color: fill }, line: { color: fill } });
  tb(slide, label, { x, y, w: d, h: d, fontSize: pt, bold: true, color, align: 'center', valign: 'middle' });
}

// ---------------------------------------------------------------- 各种页
function cover(pres, d) {
  const s = add(pres, '封面', 'DARK');
  tb(s, `《现代西班牙语》${bookName(d)}`, { x: MX + 0.2, y: 1.0, w: 8, h: 0.5, fontSize: 20, color: 'F3D9C9' });
  tb(s, `第 ${d.lesson} 课`, { x: MX + 0.2, y: 1.75, w: 8, h: 0.9, fontSize: 40, bold: true, color: COL.saffron });
  let pt = 60; while (textWidth(d.title_es, pt) > W - 2 * MX - 0.6 && pt > 36) pt -= 4;
  tb(s, d.title_es, { x: MX + 0.2, y: 2.9, w: W - 2 * MX - 0.4, h: 1.6, fontSize: pt, bold: true, color: COL.white, valign: 'middle' });
  tb(s, d.title_zh, { x: MX + 0.2, y: 4.6, w: W - 2 * MX - 0.4, h: 0.7, fontSize: 28, color: 'F3D9C9' });
  const parts = ['目标', d.pronunciation && d.pronunciation.length ? '语音' : null, '词汇', '课文', '语法', '练习'].filter(Boolean);
  tb(s, parts.join('  ·  '), { x: MX + 0.2, y: 6.2, w: 10, h: 0.5, fontSize: 18, color: COL.saffron });
  s.addNotes(`第 ${d.lesson} 课 ${d.title_es}（${d.title_zh}）。本课件按《现代西班牙语》${bookName(d)}（老版）各课的语音、语法和话题整理，课文部分是仿照本课编写的原创材料。`);
}

function goals(pres, d) {
  const s = add(pres, '本课目标'); title(s, '本课目标');
  const n = d.goals.length, gap = 0.25, rowH = Math.min(1.1, (BOTTOM - TOP - 0.3 - gap * (n - 1)) / n);
  d.goals.forEach((g, i) => {
    const y = TOP + 0.15 + i * (rowH + gap);
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: MX, y, w: W - 2 * MX, h: rowH, fill: { color: COL.tint }, line: { color: COL.tint }, rectRadius: 0.12 });
    circle(s, pres, MX + 0.25, y + (rowH - 0.6) / 2, 0.6, String(i + 1), COL.wine);
    tb(s, g, { x: MX + 1.1, y, w: W - 2 * MX - 1.4, h: rowH, fontSize: 26, color: COL.ink, valign: 'middle' });
  });
  if (d.notes && d.notes.goals) s.addNotes(d.notes.goals);
}

function pronunciation(pres, d) {
  (d.pronunciation || []).forEach((g) => {
    // 每页最多 3 张卡片：4 → 2+2，5 → 3+2，6 → 3+3
    const n = g.items.length, nPages = Math.ceil(n / 3), per = Math.ceil(n / nPages);
    chunk(g.items, per).forEach((items, pi) => {
      const s = add(pres, '语音'); title(s, `语音 · ${g.title}${nPages > 1 ? `（${pi + 1}/${nPages}）` : ''}`);
      let y = TOP;
      if (g.intro) {
        const ih = height(g.intro, 20, W - 2 * MX) * 1.12;
        tb(s, glue(g.intro), { x: MX, y, w: W - 2 * MX, h: ih, fontSize: 20, color: COL.teal }); y += ih + 0.15;
      }
      const cols = 3, gap = 0.3, cw = (W - 2 * MX - gap * (cols - 1)) / cols, ch = BOTTOM - y, iw = cw - 0.5;
      // 同一页的卡片用同一套字号
      let sp = 56; while (items.some((it) => textWidth(it.sound, sp) * 1.08 > iw) && sp > 26) sp -= 2;
      const lineOf = (w) => `${w[0]}  ${w[1].replace(/ /g, ' ')}`;
      let tipPt = 20, wPt = 24;
      const fitsLine = (w, pt) => textWidth(lineOf(w), pt) <= iw * 0.9;
      // 先把词和释义都排成一行（字号最多缩到 19）；整张卡片有一对排不下，这张卡片就一律“词一行、释义一行”
      while (wPt > 19 && items.some((it) => it.words.some((w) => !fitsLine(w, wPt)))) wPt -= 1;
      const twoLine = (it) => it.words.some((w) => !fitsLine(w, wPt));
      const cardH = (it) => sp / 72 * 1.3 + height(glue(it.tip), tipPt, iw) * 1.12 + 0.2 +
        it.words.length * (twoLine(it) ? 2 : 1) * wPt / 72 * 1.35 + 0.4;
      while (items.some((it) => cardH(it) > ch) && wPt > 16) { wPt -= 1; tipPt = Math.max(15, tipPt - 1); }
      items.forEach((it, i) => {
        const x = MX + (cols === items.length ? i : i + (cols - items.length) / 2) * (cw + gap);
        s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w: cw, h: ch, fill: { color: COL.tint }, line: { color: COL.line, width: 1 }, rectRadius: 0.12 });
        const sh = sp / 72 * 1.3, th = height(glue(it.tip), tipPt, iw) * 1.12;
        tb(s, it.sound, { x: x + 0.25, y: y + 0.2, w: iw, h: sh, fontSize: sp, bold: true, color: COL.wine });
        tb(s, glue(it.tip), { x: x + 0.25, y: y + 0.2 + sh, w: iw, h: th, fontSize: tipPt, color: COL.body });
        const runs = [];
        const two = twoLine(it);
        it.words.forEach((w, k) => {
          const oneLine = !two, last = k === it.words.length - 1;
          runs.push({ text: w[0], options: { bold: true, color: COL.ink, breakLine: !oneLine } });
          runs.push({ text: oneLine ? `  ${w[1].replace(/ /g, ' ')}` : w[1], options: { color: COL.muted, breakLine: !last } });
        });
        tb(s, runs, { x: x + 0.25, y: y + 0.4 + sh + th, w: iw, h: Math.max(0.4, ch - sh - th - 0.55), fontSize: wPt, paraSpaceAfter: 6 });
      });
      if (d.notes && d.notes.pronunciation && pi === 0) s.addNotes(d.notes.pronunciation);
    });
  });
}

function table2(slide, rows, x, y, w, pt, head, split = 0.55) {
  const data = [head.map((h) => ({ text: h, options: { bold: true, color: COL.white, fill: { color: COL.wine } } }))]
    .concat(rows.map((r, i) => r.map((c, j) => ({ text: c, options: { bold: j === 0, color: j === 0 ? COL.ink : COL.body,
      fill: { color: i % 2 ? COL.tint : COL.white } } }))));
  data.forEach((r) => r.forEach((c) => { c.text = nb(c.text); }));
  slide.addTable(data, { x, y, w, colW: [w * split, w * (1 - split)], fontFace: FONT, fontSize: pt, valign: 'middle',
    border: { type: 'solid', pt: 0.75, color: COL.line }, rowH: Math.min(pt / 72 * 2.2, (BOTTOM - TOP - 0.1) / (rows.length + 1)), margin: [0.04, 0.12, 0.04, 0.12] });
}

function vocab(pres, d) {
  const v = d.vocab, per = v.length > 9 ? Math.ceil(v.length / 2) : v.length;
  const s = add(pres, '词汇'); title(s, '本课词汇');
  const parts = chunk(v, per), gap = 0.4, w = parts.length === 1 ? 8.5 : (W - 2 * MX - gap) / 2;
  // 字号：最长的一格也要排在一行里
  let pt = Math.min(26, Math.floor((BOTTOM - TOP - 0.2) / ((per + 1) * 2.2 / 72)));
  const esW = (p) => Math.max(...v.map((r) => textWidth(r[0], p) * 1.06)) + 0.36, zhW = (p) => Math.max(...v.map((r) => textWidth(r[1], p))) + 0.36;
  while (pt > 14 && esW(pt) + zhW(pt) > w) pt -= 1;
  // 多出来的宽度两列平分；不够时先保证中文栏（中文宽度估得准，西语估得偏宽，实际还有富余）
  const extra = w - esW(pt) - zhW(pt), split = Math.min(0.7, Math.max(0.35, extra >= 0 ? (esW(pt) + extra / 2) / w : 1 - zhW(pt) / w));
  parts.forEach((p, i) => table2(s, p, MX + i * (w + gap), TOP + 0.05, w, pt, ['西班牙语', '中文'], split));
  if (d.notes && d.notes.vocab) s.addNotes(d.notes.vocab);
}

function textSlides(pres, d) {
  const t = d.text, per = 8, pages = chunk(t.lines, t.lines.length > per ? Math.ceil(t.lines.length / 2) : per);
  pages.forEach((ls, pi) => {
    const s = add(pres, '课文');
    title(s, `课文 · ${t.title}${pages.length > 1 ? `（${pi + 1}/${pages.length}）` : ''}`);
    tb(s, t.note || '仿照本课课文编写', { x: MX, y: TOP - 0.05, w: 8, h: 0.4, fontSize: 14, color: COL.teal, italic: true });
    const maxN = Math.max(...pages.map((x) => x.length)), y0 = TOP + 0.5, avail = BOTTOM - y0, base = Math.min(0.9, avail / maxN);
    const bw = (ln) => W - MX - (ln.who ? MX + 0.7 : MX);
    const nat = (ln, big, small) => height(ln.es, big, bw(ln)) * 1.08 + height(ln.zh, small, bw(ln)) + 0.12;
    const fitAll = (big, small) => pages.every((pg) => pg.reduce((h, ln) => h + nat(ln, big, small), 0) <= avail);
    let big = maxN > 6 ? 21 : 24, small = maxN > 6 ? 15 : 17;
    while (big > 16 && !fitAll(big, small)) { big -= 1; small = Math.max(13, small - 1); }
    const hs = ls.map((ln) => Math.max(nat(ln, big, small), base));
    const over = hs.reduce((a, b) => a + b, 0) - avail;
    if (over > 0) { const nh = ls.map((ln) => nat(ln, big, small)), spare = (avail - nh.reduce((a, b) => a + b, 0)) / ls.length; nh.forEach((h, i) => { hs[i] = h + spare; }); }
    let y = y0;
    ls.forEach((ln, i) => {
      const x0 = ln.who ? MX + 0.7 : MX;
      if (ln.who) circle(s, pres, MX, y + 0.06, 0.5, ln.who, ln.who === 'A' ? COL.wine : COL.teal, COL.white, 16);
      tb(s, [{ text: ln.es, options: { bold: true, color: COL.ink, fontSize: big, breakLine: true } },
             { text: ln.zh, options: { color: COL.muted, fontSize: small } }], { x: x0, y, w: W - MX - x0, h: hs[i] });
      y += hs[i];
    });
    if (d.notes && d.notes.text) s.addNotes(d.notes.text);
  });
}

function grammar(pres, d) {
  const split = d.grammar.some((g, gi) => tooLong(`语法 ${gi + 1} · ${g.title}`) || (g.table && tooLong(`语法 ${gi + 1} · ${g.title}（表）`)));
  // 标题拆成两行时，正文整体下移一点，和青色细目拉开距离
  const T0 = TOP + (split ? 0.15 : 0);
  const one = (g, gi, cap, tcap, draw) => {
    const hasT = !!(g.table && g.table.rows && g.table.rows.length);
    const cells = hasT ? [g.table.head].concat(g.table.rows) : [];
    const need = (pt) => hasT ? g.table.head.map((_, j) => Math.max(...cells.map((r) => textWidth(r[j], pt) * 1.08)) + 0.4) : [];
    const widths = (ws, tw) => ws.map((c) => c + (tw - sum(ws)) / ws.length);
    const sum = (xs) => xs.reduce((a, b) => a + b, 0);
    const sideW = W - 2 * MX - 6.6 - 0.4, fullW = W - 2 * MX, avail = BOTTOM - T0, exW = fullW - 0.6, ex = g.examples;
    const tabH = (pt) => hasT ? (g.table.rows.length + 1) * pt / 72 * 1.95 : 0;
    const exH = (pt, zh) => ex.reduce((h, e) => h + height(e[0], pt, exW) * 1.05 + height(e[1], zh, exW) + 0.14, 0) + 0.4;
    const ptsH = (pt, w) => g.points.reduce((h, p) => h + height(p, pt, w - 0.4) * 1.08 + 0.1, 0) + 0.15;
    const bullets = (pts) => pts.map((p, k) => ({ text: glue(p), options: { bullet: { code: '25CF', indent: 26 }, breakLine: k < pts.length - 1 } }));
    const tableData = () => [g.table.head.map((h) => ({ text: nb(h), options: { bold: true, color: COL.white, fill: { color: COL.teal } } }))]
      .concat(g.table.rows.map((r, i) => r.map((c, j) => ({ text: nb(c), options: { color: j === 0 ? COL.muted : COL.ink, bold: j > 0,
        fill: { color: i % 2 ? COL.tealSoft : COL.white } } }))));
    const drawEx = (sl, y0, pt, zh) => {
      const nd = exH(pt, zh), boxY = Math.min(y0, BOTTOM - nd), boxH = Math.min(nd, BOTTOM - boxY);
      sl.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: MX, y: boxY, w: fullW, h: boxH, fill: { color: COL.saffronSoft }, line: { color: COL.saffronSoft }, rectRadius: 0.1 });
      const runs = ex.map((e, k) => [{ text: e[0], options: { bold: true, color: COL.ink, fontSize: pt, breakLine: true } },
        { text: e[1], options: { color: COL.body, fontSize: zh, breakLine: k < ex.length - 1 } }]).flat();
      tb(sl, runs, { x: MX + 0.3, y: boxY + 0.18, w: exW, h: boxH - 0.25, paraSpaceAfter: 6 });
    };
    // 方案一：表格放在要点右边，例句在下面（表格每格都排得下一行、整页放得下）
    let tpt = 22; while (hasT && tpt > 17 && sum(need(tpt)) > sideW) tpt--;
    const sideOK = hasT && sum(need(tpt)) <= sideW;
    for (let pPt = Math.min(24, cap); pPt >= 20; pPt--) {
      const ex1 = pPt, zh1 = Math.max(16, pPt - 6);
      const leftW = sideOK ? 6.6 : fullW;
      const topH = sideOK ? Math.max(ptsH(pPt, leftW), tabH(tpt)) : ptsH(pPt, leftW);
      if ((sideOK || !hasT) && topH + 0.3 + exH(ex1, zh1) <= avail) {
        if (!draw) return { pPt };
        const s = add(pres, '语法'); title(s, `语法 ${gi + 1} · ${g.title}`, split);
        tb(s, bullets(g.points), { x: MX, y: T0, w: leftW, h: ptsH(pPt, leftW), fontSize: pPt, color: COL.ink, paraSpaceAfter: 6 });
        if (sideOK) {
          const colW = widths(need(tpt), sideW);
          s.addTable(tableData(), { x: MX + leftW + 0.4, y: T0, w: sideW, colW, fontFace: FONT, fontSize: tpt, valign: 'middle', align: 'left',
            border: { type: 'solid', pt: 0.75, color: 'C9DDDB' }, rowH: tpt / 72 * 1.95, margin: [0.03, 0.12, 0.03, 0.12] });
        }
        drawEx(s, T0 + topH + 0.3, ex1, zh1);
        if (d.notes && d.notes.grammar && gi === 0) s.addNotes(d.notes.grammar);
        return { pPt };
      }
    }
    // 方案二：要点 + 例句一页，变位表单独一页（大字）
    let pPt = Math.min(24, cap), ex1 = pPt, zh1 = Math.max(15, pPt - 6);
    while (ptsH(pPt, fullW) + 0.3 + exH(ex1, zh1) > avail && pPt > 18) { pPt--; ex1--; zh1 = Math.max(15, zh1 - 1); }
    let t2 = Math.min(30, tcap); while (hasT && t2 > 16 && (tabH(t2) > avail - 0.1 || sum(need(t2)) > fullW)) t2--;
    if (!draw) return { pPt, t2: hasT ? t2 : null };
    const s = add(pres, '语法'); title(s, `语法 ${gi + 1} · ${g.title}`, split);
    tb(s, bullets(g.points), { x: MX, y: T0, w: fullW, h: ptsH(pPt, fullW), fontSize: pPt, color: COL.ink, paraSpaceAfter: 6 });
    drawEx(s, T0 + ptsH(pPt, fullW) + 0.3, ex1, zh1);
    if (d.notes && d.notes.grammar && gi === 0) s.addNotes(d.notes.grammar);
    if (hasT) {
      const tw = fullW, colW = widths(need(t2), tw);
      const s2 = add(pres, '语法'); title(s2, `语法 ${gi + 1} · ${g.title}（表）`, split);
      s2.addTable(tableData(), { x: (W - tw) / 2, y: T0 + 0.1, w: tw, colW, fontFace: FONT, fontSize: t2,
        valign: 'middle', align: 'left', border: { type: 'solid', pt: 0.75, color: 'C9DDDB' }, rowH: t2 / 72 * 1.95, margin: [0.03, 0.15, 0.03, 0.15] });
    }
    return { pPt };
  };
  // 同一课：语法要点用同一个字号；单独成页的表格字号最多相差 4 磅，最大 26 磅
  const dry = d.grammar.map((g, gi) => one(g, gi, 24, 30, false)), t2s = dry.map((r) => r.t2).filter((x) => x);
  const cap = Math.min(...dry.map((r) => r.pPt)), tcap = Math.min(26, t2s.length ? Math.min(...t2s) + 4 : 26);
  d.grammar.forEach((g, gi) => one(g, gi, cap, tcap, true));
}

function phrases(pres, d) {
  if (!d.phrases || !d.phrases.length) return;
  const s = add(pres, '常用表达'); title(s, '常用表达');
  const per = Math.ceil(d.phrases.length / 2), parts = d.phrases.length > 4 ? chunk(d.phrases, per) : [d.phrases];
  const gap = 0.4, w = (W - 2 * MX - gap * (parts.length - 1)) / parts.length, iw = w - 0.5;
  // 左右两栏按行对齐：每一行的高度取这一行里最高的那张卡片
  const nRows = Math.max(...parts.map((p) => p.length)), total = (xs) => xs.reduce((a, b) => a + b, 0) + 0.2 * (xs.length - 1);
  let ep = 22, zp = 16, rows;
  for (;;) {
    rows = [...Array(nRows)].map((_, k) => Math.max(...parts.filter((p) => p[k]).map((p) =>
      heightCal(glue(p[k][0]), ep, iw) * 1.1 + heightCal(p[k][1], zp, iw) * 1.1 + 0.3)));
    if (total(rows) <= BOTTOM - TOP || ep <= 17) break;
    ep -= 1; zp = Math.max(14, zp - 1);
  }
  const slack = Math.min(0.25, Math.max(0, (BOTTOM - TOP - total(rows)) / nRows));
  parts.forEach((p, i) => {
    const x = MX + i * (w + gap);
    let y = TOP;
    p.forEach((ph, k) => {
      const ch = rows[k] + slack;
      s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h: ch, fill: { color: COL.tint }, line: { color: COL.line, width: 1 }, rectRadius: 0.1 });
      tb(s, [{ text: glue(ph[0]), options: { bold: true, color: COL.wine, fontSize: ep, breakLine: true } }, { text: ph[1], options: { color: COL.body, fontSize: zp } }],
        { x: x + 0.25, y: y + 0.08, w: iw, h: ch - 0.16, valign: 'middle' });
      y += ch + 0.2;
    });
  });
}

function numbered(pres, section, ttl, items, notes, key) {
  const blocks = (it) => key === 'ex'
    ? [{ text: `【${it.type}】`, pt: 15, color: COL.teal, bold: false }, { text: glue(it.q), pt: 21, color: COL.ink, bold: false }]
    : [{ text: glue(it.q), pt: 15, color: COL.muted, bold: false }, { text: glue(it.a), pt: 21, color: COL.ink, bold: true }];
  const itemH = (it, w, scale) => blocks(it).reduce((h, b) => h + height(b.text, Math.round(b.pt * scale), w - 0.7, 1.22) * 1.08, 0) + 0.05;
  const avail = BOTTOM - TOP, gap = 0.28;
  // 方案：两栏一页（字号最多缩到 0.86 倍）→ 单栏、每页最多 4 题
  const layouts = [];
  if (items.length > 4) {
    const per = Math.ceil(items.length / 2), cw = (W - 2 * MX - 0.45) / 2;
    for (const sc of [1, 0.93, 0.86]) {
      const cols = chunk(items, per);
      if (cols.every((c) => c.reduce((h, it) => h + itemH(it, cw, sc) + gap, -gap) <= avail)) { layouts.push({ pages: [cols], cw, sc }); break; }
    }
  } else {
    const cw = W - 2 * MX;
    if (items.reduce((h, it) => h + itemH(it, cw, 1) + gap, -gap) <= avail) layouts.push({ pages: [[items]], cw, sc: 1 });
  }
  if (!layouts.length) {
    const cw = W - 2 * MX, pages = [];
    let cur = [], h = -gap;
    items.forEach((it) => { const ih = itemH(it, cw, 1) + gap; if (cur.length && (h + ih > avail || cur.length >= 4)) { pages.push([cur]); cur = []; h = -gap; } cur.push(it); h += ih; });
    if (cur.length) pages.push([cur]);
    layouts.push({ pages, cw, sc: 1 });
  }
  const { pages, cw, sc } = layouts[0];
  let n = 0;
  pages.forEach((cols, pi) => {
    const s = add(pres, section); title(s, pages.length > 1 ? `${ttl}（${pi + 1}/${pages.length}）` : ttl);
    cols.forEach((col, ci) => {
      const x = MX + ci * (cw + 0.45);
      const used = col.reduce((h, it) => h + itemH(it, cw, sc), 0);
      const g = Math.min(0.55, Math.max(gap, (avail - used) / Math.max(1, col.length)));
      let y = TOP;
      col.forEach((it) => {
        n += 1;
        circle(s, pres, x, y + 0.05, 0.5, String(n), key === 'ans' ? COL.teal : COL.wine, COL.white, 16);
        const runs = blocks(it).map((b, k, arr) => ({ text: b.text, options: { fontSize: Math.round(b.pt * sc), color: b.color, bold: b.bold, breakLine: k < arr.length - 1 } }));
        const ih = itemH(it, cw, sc);
        tb(s, runs, { x: x + 0.7, y, w: cw - 0.7, h: ih, lineSpacingMultiple: 1.05 });
        y += ih + g;
      });
    });
    if (notes && pi === 0) s.addNotes(notes);
  });
}

function summary(pres, d) {
  const s = add(pres, '小结', 'DARK');
  tb(s, '本课小结', { x: MX, y: 0.42, w: 8, h: 0.85, fontSize: 32, bold: true, color: COL.saffron, valign: 'middle' });
  const items = d.summary.map((t, k) => ({ text: t, options: { bullet: { code: '25CF', indent: 30 }, breakLine: k < d.summary.length - 1 } }));
  tb(s, items, { x: MX, y: TOP + 0.1, w: W - 2 * MX - 0.4, h: BOTTOM - TOP - 0.1, fontSize: 28, color: COL.white, paraSpaceAfter: 18 });
  s.addNotes('用这一页带学生口头回顾本课要点，可以让学生用西语各说一个例句。');
}

function homework(pres, d) {
  const s = add(pres, '作业'); title(s, '课后作业');
  const n = d.homework.length, rowH = Math.min(1.3, (BOTTOM - TOP - 0.6) / n);
  d.homework.forEach((h, i) => {
    const y = TOP + i * rowH;
    s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: MX, y, w: W - 2 * MX, h: rowH - 0.2, fill: { color: COL.tint }, line: { color: COL.tint }, rectRadius: 0.1 });
    circle(s, pres, MX + 0.25, y + (rowH - 0.2 - 0.5) / 2, 0.5, String(i + 1), COL.saffron, COL.ink, 16);
    tb(s, h, { x: MX + 1.0, y, w: W - 2 * MX - 1.3, h: rowH - 0.2, fontSize: 24, color: COL.ink, valign: 'middle' });
  });
  tb(s, '¡Hasta la próxima clase!', { x: MX, y: BOTTOM - 0.2, w: W - 2 * MX, h: 0.5, fontSize: 20, bold: true, color: COL.wine, align: 'right' });
}

async function build(file) {
  const d = JSON.parse(fs.readFileSync(file, 'utf8'));
  const pres = newDeck(d);
  cover(pres, d); goals(pres, d); pronunciation(pres, d); vocab(pres, d); textSlides(pres, d); grammar(pres, d); phrases(pres, d);
  numbered(pres, '练习', '课堂练习', d.exercises, d.notes && d.notes.exercises, 'ex');
  numbered(pres, '练习', '练习答案', d.exercises, null, 'ans');
  summary(pres, d); homework(pres, d);
  const safe = d.title_es.replace(/[¿?¡!.,]/g, '').trim().replace(/\s+/g, '_');
  const name = `第${String(d.lesson).padStart(2, '0')}课_${safe}.pptx`;
  fs.mkdirSync(OUT, { recursive: true });
  await pres.writeFile({ fileName: path.join(OUT, name) });
  return name;
}

(async () => {
  const want = process.argv.slice(2);
  const files = fs.readdirSync(CONTENT).filter((f) => /^L\d\d\.json$/.test(f)).sort()
    .filter((f) => !want.length || want.includes(f.slice(1, 3)));
  for (const f of files) console.log(await build(path.join(CONTENT, f)));
})();
