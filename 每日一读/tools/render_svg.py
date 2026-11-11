"""插图自查：python render_svg.py <插图.svg> <预览.png> [标题]

1. 检查 SVG：viewBox 必须是 0 0 400 260；不能有 <text>、<image>、<script>、<foreignObject>、外部链接；文件 ≤ 60 KB；
   必须用到水彩滤镜（feTurbulence + feDisplacementMap）、纸纹和边缘渐隐遮罩（mask）。
2. 渲染成 1000×650 的 PNG（2.5 倍），左上角按成品页面的样子叠上标题（Georgia 14.5，#55524c，x=20，y=34），
   方便看标题区域是否干净、清楚。
3. 量一下标题区域（x 14–14+标题宽，y 18–40）背景的明暗和杂乱程度：太暗或太花会让标题看不清，打印提醒。
"""
import re
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

svg_path, png = Path(sys.argv[1]), Path(sys.argv[2])
title = (sys.argv[3] + '.') if len(sys.argv) > 3 else ''
s = svg_path.read_text('utf-8')
errs = []
if not re.search(r'<svg[^>]*viewBox="0 0 400 260"', s):
    errs.append('viewBox 必须是 "0 0 400 260"')
for tag in ('<text', '<image', '<script', '<foreignObject', '<style'):
    if tag in s:
        errs.append(f'不能有 {tag}>')
if re.search(r'(href|src)="(https?:|data:|file:)', s):
    errs.append('不能有外部链接或内嵌图片')
if len(s.encode('utf-8')) > 60_000:
    errs.append(f'文件 {len(s.encode()) // 1000} KB，超过 60 KB')
for need in ('feTurbulence', 'feDisplacementMap', '<mask'):
    if need not in s:
        errs.append(f'缺少 {need}（水彩滤镜、纸纹、边缘渐隐要和样板一致）')

page = f"""<!doctype html><html><head><meta charset="utf-8"><style>
html,body{{margin:0;background:#fffdf8}} .w{{position:relative;width:400px;height:260px}} .w svg{{display:block;width:400px;height:260px}}
.t{{position:absolute;left:20px;top:21.5px;font:14.5px Georgia,'Times New Roman',serif;color:#55524c;white-space:nowrap}}
</style></head><body><div class="w">{s}<div class="t">{title}</div></div></body></html>"""
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 400, 'height': 260}, device_scale_factor=2.5)
    pg.set_content(page)
    pg.wait_for_timeout(300)
    tw = pg.evaluate("document.querySelector('.t').getBoundingClientRect().width") if title else 0
    pg.evaluate("document.querySelector('.t').style.visibility='hidden'")
    raw = pg.screenshot(clip={'x': 14, 'y': 18, 'width': max(60, tw + 12), 'height': 22})
    pg.evaluate("document.querySelector('.t').style.visibility='visible'")
    pg.screenshot(path=str(png))
    b.close()

import io  # noqa: E402
try:
    from PIL import Image
    im = Image.open(io.BytesIO(raw)).convert('L')
    px = list(im.tobytes())
    mean = sum(px) / len(px)
    var = (sum((x - mean) ** 2 for x in px) / len(px)) ** 0.5
    print(f'标题区域背景：平均亮度 {mean:.0f}（越亮越好，建议 ≥ 200），起伏 {var:.0f}（越小越干净，建议 ≤ 25）')
    if mean < 200 or var > 25:
        print('   提醒：标题区域偏暗或偏花，标题可能看不清，最好把左上角留成浅色、少细节')
except ImportError:
    pass
print(('✗ ' + '；'.join(errs)) if errs else f'OK {svg_path.name}（{len(s.encode()) // 1000} KB）', '→', png)
sys.exit(1 if errs else 0)
