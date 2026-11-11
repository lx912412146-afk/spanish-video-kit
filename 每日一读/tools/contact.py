"""插图缩略图总览：python contact.py <输出.png> <png…>（两列，每张缩到 480 宽，左上角标编号）"""
import sys
from PIL import Image, ImageDraw
out, files = sys.argv[1], sys.argv[2:]
W = 480
ims = []
for f in files:
    im = Image.open(f).convert('RGB')
    ims.append((f.split('/')[-1][6:-4], im.resize((W, round(im.height * W / im.width)))))
h = ims[0][1].height
rows = (len(ims) + 1) // 2
sheet = Image.new('RGB', (W * 2 + 10, rows * (h + 10)), 'white')
d = ImageDraw.Draw(sheet)
for k, (name, im) in enumerate(ims):
    x, y = (k % 2) * (W + 10), (k // 2) * (h + 10)
    sheet.paste(im, (x, y))
    d.rectangle([x, y + h - 22, x + 70, y + h], fill='black')
    d.text((x + 5, y + h - 18), name, fill='white')
sheet.save(out)
