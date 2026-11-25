"""把一组页面 png 拼成一张总览图：python sheet.py 输出.png 每行几页 页1.png 页2.png …"""
import sys
from PIL import Image
out, cols, files = sys.argv[1], int(sys.argv[2]), sys.argv[3:]
ims = [Image.open(f).convert('RGB') for f in files]
w, h = max(i.width for i in ims), max(i.height for i in ims)
rows = (len(ims) + cols - 1) // cols
S = Image.new('RGB', (cols * w + (cols - 1) * 8, rows * h + (rows - 1) * 8), (120, 120, 120))
for k, im in enumerate(ims):
    S.paste(im, ((k % cols) * (w + 8), (k // cols) * (h + 8)))
S.save(out)
