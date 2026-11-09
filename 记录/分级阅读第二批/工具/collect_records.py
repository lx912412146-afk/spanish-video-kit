"""把分级阅读第二批的工作文件收进工具包 记录/分级阅读第二批/（本机路径换成占位符）：
python collect_records.py <工作区 S> <KIT>
- 说明（README.md）、编写要求、审读要求、选题表、第二轮审读后的改动
- 写作区的小工具（est.py、diff.py、fix.py、build_release.py、collect_records.py、readme_edit.py、drop_sentence.py、gen_files.py、desk_copy.py）和生产脚本（gr2/*.sh、frames.py、verify_upload.py）
- 日志：gr2/logs/ 全部（每篇的音频、视频、识别核对日志和各条链的日志），折行检查前后的结果
写完再查一遍，不能留下本机路径。"""
import re
import shutil
import sys
from pathlib import Path

S, KIT = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
ART = Path('<写作区>')
GR2 = S / 'gr2'
DST = KIT / '记录' / '分级阅读第二批'
REPL = [(str(KIT), '<KIT>'), (str(S), '<工作区>'), ('<写作区>', '<写作区>'), ('<工作区>/gr2', '<工作区>/gr2'),
        ('<临时目录>', '<临时目录>'), ('<临时目录>', '<临时目录>'), (str(Path.home()), '~')]
BAD = re.compile(r'claude' r'-501|liu' r'xuanxuan|Application' r' Support|scratch' r'-workspaces')  # 分开写，这一行自己不会被查出来


def put(src, rel):
    t = Path(src).read_text('utf-8', errors='replace')
    for a, b in REPL:
        t = t.replace(a, b)
    out = DST / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(t, 'utf-8')


for f in ('编写要求.md', '审读要求.md', '选题表.md'):
    put(ART / f, f)
put(ART / '记录说明.md', 'README.md')
for f in ('round2_b1.txt', 'round2_b2.txt', 'round2_c1.txt'):
    put(ART / f, f'审读后的改动/{f}')
for f in ('est.py', 'diff.py', 'fix.py', 'build_release.py', 'collect_records.py', 'readme_edit.py', 'drop_sentence.py', 'gen_files.py', 'desk_copy.py'):
    put(ART / f, f'工具/{f}')
for f in sorted(GR2.glob('*.sh')) + [GR2 / 'frames.py', GR2 / 'verify_upload.py', GR2 / 'queue.txt']:
    put(f, f'工具/{f.name}')
for f in sorted((GR2 / 'logs').glob('*.log')):
    put(f, f'日志/{f.name}')
for f in ('wraps_all.txt', 'wraps_new.txt', 'wraps_final.txt'):
    put(ART / f, f'日志/{f}')
left = [str(p.relative_to(KIT)) for p in DST.rglob('*') if p.is_file() and BAD.search(p.read_text('utf-8', errors='replace'))]
if left:
    sys.exit('还有本机路径：' + ', '.join(left))
n = sum(1 for p in DST.rglob('*') if p.is_file())
print(f'OK：{n} 个文件在 {DST.relative_to(KIT)}')
