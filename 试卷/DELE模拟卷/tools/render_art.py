# -*- coding: utf-8 -*-
"""插图：art/svg/<id>.svg → art/png/<id>.png（Chromium 渲染，2 倍分辨率），并拼一张核对用的总览图。

    python tools/render_art.py [级别 …]            # 渲染这些级别插图清单里的全部 SVG，再出总览图
    python tools/render_art.py --only A1_CA1_1A …   # 只渲染这几张

总览图：art/核对/<级别>_总览_<n>.png（每张 12 幅，图下印 id 和中文说明，供肉眼核对图和说明是否一致）。
Chromium 要在命令沙盒外运行。
"""
import base64
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SVG, PNG, CHK = ROOT / 'art' / 'svg', ROOT / 'art' / 'png', ROOT / 'art' / '核对'
args = sys.argv[1:]
only = args[args.index('--only') + 1:] if '--only' in args else None
levels = [a.upper() for a in args if not a.startswith('--') and (only is None or args.index(a) < args.index('--only'))]


def arts_of(lv):
    out = []
    for p in sorted((ROOT / 'content' / lv).glob('art_*.json')):
        out += json.loads(p.read_text('utf-8'))
    return out


def size_of(svg_text):
    m = re.search(r'viewBox="\s*[-\d.]+\s+[-\d.]+\s+([\d.]+)\s+([\d.]+)', svg_text)
    if m:
        return float(m.group(1)), float(m.group(2))
    w = re.search(r'width="([\d.]+)', svg_text)
    h = re.search(r'height="([\d.]+)', svg_text)
    return (float(w.group(1)), float(h.group(1))) if w and h else (800, 600)


def main():
    PNG.mkdir(parents=True, exist_ok=True)
    CHK.mkdir(parents=True, exist_ok=True)
    todo = []
    if only:
        todo = [(i, {}) for i in only]
    for lv in levels:
        todo += [(a['id'], a) for a in arts_of(lv)]
    from playwright.sync_api import sync_playwright
    missing, done = [], 0
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        for aid, _ in todo:
            f = SVG / f'{aid}.svg'
            if not f.exists():
                missing.append(aid)
                continue
            t = f.read_text('utf-8')
            w, h = size_of(t)
            scale = 1000 / max(w, h)          # 长边 1000 CSS px，再 ×2 设备像素 → 长边 2000 px
            W, H = round(w * scale), round(h * scale)
            pg = br.new_page(viewport={'width': W, 'height': H}, device_scale_factor=2)
            pg.set_content(f'<!doctype html><html><body style="margin:0;background:#fff">'
                           f'<img src="data:image/svg+xml;base64,{base64.b64encode(t.encode()).decode()}" '
                           f'style="display:block;width:{W}px;height:{H}px"></body></html>')
            pg.wait_for_load_state('networkidle')
            pg.screenshot(path=str(PNG / f'{aid}.png'), clip={'x': 0, 'y': 0, 'width': W, 'height': H})
            pg.close()
            done += 1
        # 总览图
        for lv in levels:
            arts = [a for a in arts_of(lv) if (PNG / f'{a["id"]}.png').exists()]
            for k in range(0, len(arts), 12):
                part = arts[k:k + 12]
                cells = ''.join(
                    # about:blank 页面不能引用 file:// 图片，所以内嵌成 data URI
                    f'<div style="border:1px solid #999;padding:6px"><img src="data:image/png;base64,{base64.b64encode((PNG / (a["id"] + ".png")).read_bytes()).decode()}" style="width:100%;height:230px;object-fit:contain;display:block">'
                    f'<div style="font:600 13px Helvetica">{html.escape(a["id"])} · {html.escape(a.get("estilo", ""))}</div>'
                    f'<div style="font:12px PingFang SC">{html.escape(a.get("zh", ""))}</div>'
                    f'<div style="font:italic 12px Times">{html.escape(a.get("es", ""))}{" ｜ 图中文字：" + html.escape(a["texto_en_imagen"]) if a.get("texto_en_imagen") else ""}</div></div>'
                    for a in part)
                pg = br.new_page(viewport={'width': 1500, 'height': 1000})
                pg.set_content(f'<!doctype html><html><body style="margin:10px;background:#fff"><div style="display:grid;grid-template-columns:repeat(4,1fr);gap:8px">{cells}</div></body></html>')
                pg.wait_for_load_state('networkidle')
                pg.screenshot(path=str(CHK / f'{lv}_总览_{k // 12 + 1}.png'), full_page=True)
                pg.close()
        br.close()
    print(f'渲染 {done} 张', f'；缺 SVG {len(missing)} 张：{" ".join(missing)}' if missing else '')


if __name__ == '__main__':
    main()
