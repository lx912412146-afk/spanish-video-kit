"""PDF → 每页 PNG（pdftoppm），再拼成每张 8 页的缩略图，方便检查版面。

    python tools/contact.py <pdf> <输出目录> [dpi]
"""
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

pdf, out = Path(sys.argv[1]), Path(sys.argv[2])
dpi = sys.argv[3] if len(sys.argv) > 3 else '60'
out.mkdir(parents=True, exist_ok=True)
bin_ = Path(sys.argv[4]) if len(sys.argv) > 4 else None
for p in out.glob(f'{pdf.stem}-*.png'):
    p.unlink()
subprocess.run([str(bin_ / 'pdftoppm') if bin_ else 'pdftoppm', '-r', dpi, '-png', str(pdf), str(out / pdf.stem)], check=True)
pages = sorted(out.glob(f'{pdf.stem}-*.png'))
for k in range(0, len(pages), 8):
    ims = [Image.open(p) for p in pages[k:k + 8]]
    w, h = ims[0].size
    sheet = Image.new('RGB', (4 * w + 50, 2 * h + 30), 'white')
    d = ImageDraw.Draw(sheet)
    for i, im in enumerate(ims):
        x, y = 10 + (i % 4) * (w + 10), 10 + (i // 4) * (h + 10)
        sheet.paste(im, (x, y))
        d.rectangle([x, y, x + w - 1, y + h - 1], outline='#888')
        d.text((x + 4, y + 2), str(k + i + 1), fill='red')
    sheet.save(out / f'sheet_{pdf.stem}_{k // 8 + 1}.png')
    print(out / f'sheet_{pdf.stem}_{k // 8 + 1}.png')
