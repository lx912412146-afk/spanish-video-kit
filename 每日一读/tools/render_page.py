"""“每日一读”单页：按文章 JSON 和插图 SVG 排出一页（CSS 720×1008，输出 1.5 倍 = 1080×1512），
截出静态页 page_static.png；给了时间表时再截出逐句高亮页 page_hl_01.png…（第 1 句 = 标题）。

    python render_page.py <文章.json> <插图.svg> <输出目录> [<id>_timings.json]

同时写出 layout.json（各区块的位置，用来查是否超出页面、是否互相重叠、文字有没有被截断）。
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
W, H, SCALE = 720, 1008, 1.5

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:720px;height:1008px;background:#fffdf8}
body{font-family:"Helvetica Neue","PingFang SC",sans-serif;color:#222;-webkit-font-smoothing:antialiased}
.page{position:relative;width:720px;height:1008px;padding:44px 94px 0 96px;
  background:radial-gradient(ellipse at 50% 40%,#fffefa 0%,#fffcf5 70%,#fbf7ee 100%)}
header{display:flex;justify-content:space-between;align-items:flex-end;padding-bottom:7px;border-bottom:3px solid #474747;
  box-shadow:0 1px 0 #d9d6cf}
header .t{font-size:15px;font-weight:700;letter-spacing:.1px}
header .t .tzh{font-family:"PingFang SC",sans-serif;font-weight:600}
header .t .bar{font-weight:400;color:#555;margin:0 5px}
header .s{font-family:"PingFang SC",sans-serif;font-size:14px;color:#333;letter-spacing:1px}
.body{display:flex;gap:26px;margin-top:20px}
.left{width:384px;flex:none}
.ill{width:384px;height:249.6px}
.ill svg{width:384px;height:249.6px;display:block}
.es{margin-top:14px;font-size:13.1px;letter-spacing:-0.05px;line-height:1.62;text-align:justify;hyphens:none;text-wrap:pretty}
.es p{text-indent:2em;margin-bottom:8px}
aside{width:120px;flex:none;padding-top:6px}
aside .vh{font-family:"PingFang SC",sans-serif;font-size:12.5px;color:#222;margin-bottom:11px}
aside .v{font-size:12.5px;line-height:18px;margin-bottom:11px;white-space:nowrap}
aside .v .z{font-family:"PingFang SC",sans-serif;margin-left:6px}
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
vocab = ''.join(f'<div class="v"><span class="w">{html.escape(w)}</span><span class="z">{html.escape(z)}</span></div>'
                for w, z in a['vocab'])
page = f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><style>{CSS}</style></head><body>
<div class="page">
 <header><div class="t"><span class="sn" data-k="1"><span class="es-t">{html.escape(a['title_es'])}</span><span class="bar">|</span><span class="tzh">{html.escape(a['title_zh'])}</span></span></div>
 <div class="s">{html.escape(a['slogan'])}</div></header>
 <div class="body">
  <div class="left">
   <div class="ill">{svg}</div>
   <div class="es" lang="es">{es_html}</div>
  </div>
  <aside><div class="vh">重点词汇</div>{vocab}</aside>
 </div>
 <div class="zh" lang="zh">{zh_html}</div>
</div></body></html>"""
OUT.mkdir(parents=True, exist_ok=True)
(OUT / 'page.html').write_text(page, 'utf-8')

LAYOUT_JS = """() => {
  const r = e => { const b = e.getBoundingClientRect(); return [b.left, b.top, b.right, b.bottom]; };
  const q = s => document.querySelector(s);
  const out = {header: r(q('header')), ill: r(q('.ill')), es: r(q('.es')), aside: r(q('aside')), zh: r(q('.zh')),
               vocab: [...document.querySelectorAll('aside .v')].map(r),
               overflow: [...document.querySelectorAll('aside .v, header .t, header .s')].filter(e => e.scrollWidth > e.clientWidth + 0.5).length,
               fonts: [...new Set([...document.querySelectorAll('.es span, .zh span, aside span')].map(e => getComputedStyle(e).fontFamily))],
               es_lines: Math.round(q('.es').getBoundingClientRect().height / 21.06),
               sentences: [...document.querySelectorAll('.sn')].map(e => [e.dataset.k, e.getClientRects().length])};
  // 两端对齐后每行词间距：逐词取位置，按行分组，记每行最大词间空白（正常空格约 3.6 px）
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
  out.es_gaps = gaps;
  out.es_max_gap = Math.max(...gaps.filter(g => g[0] === 'mid').map(g => g[1]));
  return out;
}"""

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': W, 'height': H}, device_scale_factor=SCALE)
    pg.set_content(page)
    pg.evaluate('document.fonts.ready')
    pg.wait_for_timeout(400)
    lay = pg.evaluate(LAYOUT_JS)
    lay['scroll'] = pg.evaluate('[document.documentElement.scrollWidth, document.documentElement.scrollHeight]')
    (OUT / 'layout.json').write_text(json.dumps(lay, ensure_ascii=False, indent=1), 'utf-8')
    pg.screenshot(path=str(OUT / 'page_static.png'))
    if TIM:
        for kk in range(1, NS + 1):
            pg.evaluate(f"""() => {{ document.querySelectorAll('.sn').forEach(e => e.classList.toggle('cur', e.dataset.k === '{kk}')); }}""")
            pg.wait_for_timeout(60)
            pg.screenshot(path=str(OUT / f'page_hl_{kk:02d}.png'))
    b.close()
print('静态页', OUT / 'page_static.png', '；句数（含标题）', NS, '；版面', json.dumps({k: lay[k] for k in ('header', 'ill', 'es', 'aside', 'zh', 'overflow', 'scroll')}))
