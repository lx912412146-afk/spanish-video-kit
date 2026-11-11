"""“每日一读”单页：按文章 JSON 和插图 SVG 排出一页（CSS 720×1008，输出 1.5 倍 = 1080×1512），
截出静态页 page_static.png；给了时间表时再截出逐句高亮页 page_hl_01.png…（第 1 句 = 标题）。

    python render_page.py <文章.json> <插图.svg> <输出目录> [<id>_timings.json]

- 插图里没有 <text> 时，按样片的位置把“西语标题.”叠在插图左上角（Georgia，#55524c）。
- 西语正文自动选字号和字距：从 13.1 px、−0.05 px 起，在 12.6—13.4 px、−0.15—+0.1 px 里找两端对齐的最大词间空白
  ≤ 7.5 px、底部留白 ≥ 44 px、离 13.1 px 最近的一组；都达不到时取词间空白最小的一组；字最小也放不下就报错退出。
- 重点词汇一条放不下时释义整体换到下一行（词和释义都不在中间断开）。
- 写出 layout.json：各区块位置、两端对齐每行的词间空白、标题栏左右留空、词汇换行和越界数、选定的字号字距。
"""
import html
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ART, SVG, OUT = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
TIM = Path(sys.argv[4]) if len(sys.argv) > 4 else None
a = json.loads(ART.read_text('utf-8'))
svg = SVG.read_text('utf-8')
OVERLAY = '<text' not in svg
W, H, SCALE = 720, 1008, 1.5

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:720px;height:1008px;background:#fffdf8}
body{font-family:"Helvetica Neue","PingFang SC",sans-serif;color:#222;-webkit-font-smoothing:antialiased}
.page{position:relative;width:720px;height:1008px;padding:44px 94px 0 96px;
  background:radial-gradient(ellipse at 50% 40%,#fffefa 0%,#fffcf5 70%,#fbf7ee 100%)}
header{display:flex;justify-content:space-between;align-items:flex-end;padding-bottom:7px;border-bottom:3px solid #474747;
  box-shadow:0 1px 0 #d9d6cf}
header .t{font-size:15px;font-weight:700;letter-spacing:.1px;white-space:nowrap}
header .t .tzh{font-family:"PingFang SC",sans-serif;font-weight:600}
header .t .bar{font-weight:400;color:#555;margin:0 5px}
header .s{font-family:"PingFang SC",sans-serif;font-size:14px;color:#333;letter-spacing:1px;white-space:nowrap}
.body{display:flex;gap:26px;margin-top:20px}
.left{width:384px;flex:none}
.ill{position:relative;width:384px;height:249.6px}
.ill svg{width:384px;height:249.6px;display:block}
.ill .it{position:absolute;left:19.2px;top:20.64px;font:13.92px Georgia,"Times New Roman",serif;color:#55524c;white-space:nowrap}
.es{margin-top:14px;font-size:13.1px;letter-spacing:-0.05px;line-height:1.62;text-align:justify;hyphens:none;text-wrap:pretty}
.es p{text-indent:2em;margin-bottom:8px}
aside{width:120px;flex:none;padding-top:6px}
aside .vh{font-family:"PingFang SC",sans-serif;font-size:12.5px;color:#222;margin-bottom:11px}
aside .v{font-size:12.5px;line-height:18px;margin-bottom:11px}
aside .v .w,aside .v .z{white-space:nowrap}
aside .v .z{font-family:"PingFang SC",sans-serif;margin-left:2.5px}
.zh{width:384px;margin-top:26px;font-family:"PingFang SC",sans-serif;font-size:13px;line-height:1.78;text-align:justify;text-wrap:pretty}
.zh p{text-indent:2em;margin-bottom:8px}
.sn{border-radius:2px;-webkit-box-decoration-break:clone;box-decoration-break:clone;transition:none}
.sn.cur{background:linear-gradient(to bottom,transparent 8%,#ffe7a3 8%,#ffe7a3 94%,transparent 94%)}
"""


def sent_spans(sents, key, k0):
    return ' '.join(f'<span class="sn" data-k="{k0 + i}">{html.escape(s[key])}</span>' for i, s in enumerate(sents))


k = 2
es_html, zh_html = '', ''
for para in a['paras']:
    es_html += f'<p>{sent_spans(para, "es", k)}</p>'
    zh_html += '<p>' + sent_spans(para, 'zh', k).replace('</span> <span', '</span><span') + '</p>'
    k += len(para)
NS = k - 1                                            # 句数（含标题）
vocab = ''.join(f'<div class="v"><span class="w">{html.escape(v[0])}</span> <span class="z">{html.escape(v[1])}</span></div>'
                for v in a['vocab'])
it = f'<div class="it">{html.escape(a["title_es"])}.</div>' if OVERLAY else ''
page = f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><style>{CSS}</style></head><body>
<div class="page">
 <header><div class="t"><span class="sn" data-k="1"><span class="es-t">{html.escape(a['title_es'])}</span><span class="bar">|</span><span class="tzh">{html.escape(a['title_zh'])}</span></span></div>
 <div class="s">{html.escape(a['slogan'])}</div></header>
 <div class="body">
  <div class="left">
   <div class="ill">{svg}{it}</div>
   <div class="es" lang="es">{es_html}</div>
  </div>
  <aside><div class="vh">重点词汇</div>{vocab}</aside>
 </div>
 <div class="zh" lang="zh">{zh_html}</div>
</div></body></html>"""
OUT.mkdir(parents=True, exist_ok=True)

GAPS_JS = """() => {
  const gaps = [];
  for (const p of document.querySelectorAll('.es p')) {
    const words = [];
    const walker = document.createTreeWalker(p, NodeFilter.SHOW_TEXT);
    let n;
    while ((n = walker.nextNode())) {
      const re = /\\S+/g; let m;
      while ((m = re.exec(n.data))) {
        const rg = document.createRange(); rg.setStart(n, m.index); rg.setEnd(n, m.index + m[0].length);
        const b = rg.getBoundingClientRect(); words.push([Math.round(b.top), b.left, b.right, m[0]]);
      }
    }
    const lines = {};
    for (const w of words) (lines[w[0]] = lines[w[0]] || []).push(w);
    const keys = Object.keys(lines).map(Number).sort((x, y) => x - y);
    keys.forEach((k, i) => { const ws = lines[k].sort((x, y) => x[1] - y[1]); let g = 0;
      for (let j = 1; j < ws.length; j++) g = Math.max(g, ws[j][1] - ws[j - 1][2]);
      gaps.push([i === keys.length - 1 ? 'last' : 'mid', Math.round(g * 10) / 10, ws.map(w => w[3]).join(' ')]); });
  }
  const mid = gaps.filter(g => g[0] === 'mid').map(g => g[1]);
  const bottom = Math.max(document.querySelector('.zh').getBoundingClientRect().bottom,
                          document.querySelector('aside').getBoundingClientRect().bottom);
  return {gaps, max_gap: mid.length ? Math.max(...mid) : 0, bottom};
}"""

LAYOUT_JS = """() => {
  const r = e => { const b = e.getBoundingClientRect(); return [b.left, b.top, b.right, b.bottom]; };
  const q = s => document.querySelector(s);
  const aside = q('aside').getBoundingClientRect();
  const vs = [...document.querySelectorAll('aside .v')];
  return {header: r(q('header')), ill: r(q('.ill')), es: r(q('.es')), aside: r(q('aside')), zh: r(q('.zh')),
          ill_title: q('.ill .it') ? r(q('.ill .it')) : null,
          header_gap: q('header .s').getBoundingClientRect().left - q('header .t').getBoundingClientRect().right,
          vocab: vs.map(r),
          vocab_wrapped: vs.filter(e => e.getBoundingClientRect().height > 20).length,
          vocab_out: vs.filter(e => [...e.children].some(c => c.getBoundingClientRect().right > aside.right + 0.5)).length,
          overflow: [...document.querySelectorAll('header .t, header .s')].filter(e => e.scrollWidth > e.clientWidth + 0.5).length,
          fonts: [...new Set([...document.querySelectorAll('.es span, .zh span, aside span')].map(e => getComputedStyle(e).fontFamily))],
          sentences: [...document.querySelectorAll('.sn')].map(e => [e.dataset.k, e.getClientRects().length])};
}"""

FS = [13.1, 13.0, 13.2, 12.9, 13.3, 12.8, 13.4, 12.7, 12.6]
LS = [-0.05, 0.0, -0.1, 0.05, -0.15, 0.1]
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': W, 'height': H}, device_scale_factor=SCALE)
    pg.set_content(page)
    pg.evaluate('document.fonts.ready')
    pg.wait_for_timeout(400)
    tried = []
    for fs in FS:
        for ls in LS:
            pg.evaluate(f"() => {{ const e = document.querySelector('.es'); e.style.fontSize = '{fs}px'; e.style.letterSpacing = '{ls}px'; }}")
            m = pg.evaluate(GAPS_JS)
            tried.append((fs, ls, m['max_gap'], m['bottom']))
    fit = [t for t in tried if t[3] <= H - 44]
    good = [t for t in fit if t[2] <= 7.5]
    if good:
        pick = min(good, key=lambda t: abs(t[0] - 13.1) * 10 + abs(t[1] + 0.05) * 4)
    elif fit:
        pick = min(fit, key=lambda t: (t[2], abs(t[0] - 13.1)))
    else:
        b.close()
        sys.exit(f'放不下：字号 12.6 px 时底部仍到 {min(t[3] for t in tried):.0f} px（要 ≤ {H - 44}）')
    fs, ls = pick[0], pick[1]
    pg.evaluate(f"() => {{ const e = document.querySelector('.es'); e.style.fontSize = '{fs}px'; e.style.letterSpacing = '{ls}px'; }}")
    page_final = page.replace('.es{margin-top:14px;font-size:13.1px;letter-spacing:-0.05px;',
                              f'.es{{margin-top:14px;font-size:{fs}px;letter-spacing:{ls}px;')
    (OUT / 'page.html').write_text(page_final, 'utf-8')
    m = pg.evaluate(GAPS_JS)
    lay = pg.evaluate(LAYOUT_JS)
    lay.update(es_gaps=m['gaps'], es_max_gap=m['max_gap'], es_font=[fs, ls], scroll=pg.evaluate(
        '[document.documentElement.scrollWidth, document.documentElement.scrollHeight]'))
    (OUT / 'layout.json').write_text(json.dumps(lay, ensure_ascii=False, indent=1), 'utf-8')
    pg.screenshot(path=str(OUT / 'page_static.png'))
    if TIM:
        for kk in range(1, NS + 1):
            pg.evaluate(f"""() => {{ document.querySelectorAll('.sn').forEach(e => e.classList.toggle('cur', e.dataset.k === '{kk}')); }}""")
            pg.wait_for_timeout(60)
            pg.screenshot(path=str(OUT / f'page_hl_{kk:02d}.png'))
    b.close()
print(f"静态页 {OUT / 'page_static.png'}；句数（含标题）{NS}；西语 {fs} px 字距 {ls} px，最大词间空白 {lay['es_max_gap']} px，"
      f"底部 {max(lay['zh'][3], lay['aside'][3]):.0f} px，标题栏留空 {lay['header_gap']:.0f} px，词汇换行 {lay['vocab_wrapped']} 条、越界 {lay['vocab_out']} 条")
