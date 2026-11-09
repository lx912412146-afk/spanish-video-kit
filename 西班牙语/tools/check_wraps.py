"""画面折行检查：按 make_video.py 的版式（同样的 CSS、同样的自动字号）逐句排版，量出原文、译文、每条生词各占几行。

    python 西班牙语/tools/check_wraps.py <编号>…        （在工具包根目录运行，用 Playwright 的 Chromium）

报出（要处理）：
  - 生词释义从中间断开（如“第二天早 / 上”）。释义整段换到下一行不算问题（make_video 的版式就是这样排的）；
    很长的西语词头在两个词之间换行也只算提示。
  - 译文最后一行只剩 1 个字（孤字）。2 个字只提示。
  - 一屏放不下。
只提示：原文最后一行只剩一个词。
最后一行打印 WRAPS_DONE 和要处理的条数；有要处理的就以 1 退出。"""
import pathlib
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import make_video as M  # noqa: E402

JS = r"""() => {
  const lines = el => {
    const rows = [];
    const w = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    let n;
    while ((n = w.nextNode())) {
      for (let i = 0; i < n.data.length; i++) {
        const r = document.createRange(); r.setStart(n, i); r.setEnd(n, i + 1);
        const rc = r.getClientRects()[0]; if (!rc) continue;
        let row = rows.find(x => Math.abs(x.top - rc.top - rc.height / 2) < 12);
        if (!row) { row = {top: rc.top + rc.height / 2, s: ''}; rows.push(row); }
        row.s += n.data[i];
      }
    }
    rows.sort((a, b) => a.top - b.top);
    return rows.map(x => x.s.trim()).filter(x => x);
  };
  return {en: lines(document.querySelector('.en')), zh: lines(document.querySelector('.zh')),
          v: [...document.querySelectorAll('.v > div')].map(lines)};
}"""
PUNCT = set('，。、；：？！“”‘’（）…—· ,.;:?!¡¿')


def main(ids):
    from playwright.sync_api import sync_playwright
    bad = 0
    td = pathlib.Path(tempfile.mkdtemp(prefix='es_wraps_'))
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        pg = br.new_page(viewport={'width': M.W, 'height': M.H})
        for pid in ids:
            p = M.load(pid)
            sents = [s for para in p['paras'] for s in para]
            for k, s in enumerate(sents, 1):
                f = td / 'slide.html'
                f.write_text(M.sentence_slide(p, s, k, len(sents)), 'utf-8')
                pg.goto(f.as_uri())
                pg.evaluate('document.fonts.ready')
                pg.wait_for_timeout(100)
                fs, vs, fits = pg.evaluate(M.C4V.FIT)
                r = pg.evaluate(JS)
                msgs = [] if fits else ['一屏放不下']
                for w, ln in zip(s['w'], r['v']):
                    if len(ln) > 1 and not ln[-1].startswith(w['zh']):
                        hw = ' '.join(ln).startswith(w['h']) and w['zh'] in ln[-1] and w['h'] not in ln[-1]
                        msgs.append(('（提示）词头换行 ' if hw else '释义折行 ') + f'{w["h"]}：' + ' / '.join(ln))
                last = r['zh'][-1] if r['zh'] else ''
                core = ''.join(c for c in last if c not in PUNCT)
                if len(r['zh']) > 1 and len(core) <= 1:
                    msgs.append('译文孤字：' + ' / '.join(r['zh']))
                elif len(r['zh']) > 1 and len(core) == 2:
                    msgs.append('（提示）译文末行两个字：' + ' / '.join(r['zh']))
                if len(r['en']) > 1 and len(r['en'][-1].split()) == 1:
                    msgs.append('（提示）原文末行一个词：' + r['en'][-1])
                for m in msgs:
                    bad += not m.startswith('（提示）')
                    print(f'{pid} 第{k}句 {m}')
        br.close()
    print(f'WRAPS_DONE 需要处理 {bad} 处')
    return 1 if bad else 0


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    sys.exit(main(sys.argv[1:]))
