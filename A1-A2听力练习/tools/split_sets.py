"""把学生版 PDF 按套拆开（方便单独打印一套）：python split_sets.py <学生版 PDF> <输出目录> <poppler 的 bin 目录>
输出 第01套_学生版.pdf …；每套从标题“第 N 套”所在的页到下一套之前一页。"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

pdf, out, bin_ = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
out.mkdir(parents=True, exist_ok=True)
txt = subprocess.run([str(bin_ / 'pdftotext'), '-layout', str(pdf), '-'], capture_output=True, text=True, check=True).stdout
pages = txt.split('\f')[:-1]
starts = {}
for i, pg in enumerate(pages, 1):
    head = '\n'.join(l for l in pg.split('\n')[:14])
    m = re.search(r'^\s*第\s*(\d+)\s*套', head, re.M)
    if m and i > 3:
        starts[int(m.group(1))] = i
nums = sorted(starts)
assert nums == list(range(1, len(nums) + 1)) and len(nums) == 10, starts
with tempfile.TemporaryDirectory() as td:
    subprocess.run([str(bin_ / 'pdfseparate'), str(pdf), f'{td}/p-%d.pdf'], check=True)
    for k, n in enumerate(nums):
        a, b = starts[n], (starts[nums[k + 1]] - 1 if k + 1 < len(nums) else len(pages))
        dst = out / f'第{n:02d}套_学生版.pdf'
        subprocess.run([str(bin_ / 'pdfunite'), *[f'{td}/p-{j}.pdf' for j in range(a, b + 1)], str(dst)], check=True)
        print(dst.name, f'第 {a}—{b} 页（{b - a + 1} 页）')
