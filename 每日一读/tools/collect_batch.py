"""“每日一读”批量成品归档：核对每篇都通过核查后，
1) 视频复制到 Release 目录（ASCII 文件名 daily_A1-01_Mi_abuela.mp4）并写 SHA256SUMS；
2) 视频复制到桌面目录（中文名“西班牙语每日一读 A1-01 Mi abuela 我的奶奶.mp4”）；
3) 文章、插图、选题表、编写/插图要求、审读记录、朗读 MP3、时间表、高亮计划、版面数据、核查报告、工具复制进工具包 每日一读/。
   说明文档（.md）里写的本机工作目录换成仓库里的相对路径，换完还有本机路径就停下。

    python collect_batch.py <批次目录> <工具目录> <工具包根目录> <Release 目录> <桌面目录> [<路径替换.json>]

任何一篇缺文件或核查没写“全部通过”就停下，什么都不复制。打印仓库里要提交的文件清单（相对工具包根目录）到 <批次目录>/files.txt。
"""
import hashlib
import json
import re
import shutil
import sys
import unicodedata
from pathlib import Path

B, TOOLS, KIT, REL, DESK = (Path(x) for x in sys.argv[1:6])
topics = json.loads((B / '选题表.json').read_text('utf-8'))


def ascii_name(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()
    return re.sub(r'[^A-Za-z0-9]+', '_', s).strip('_')


rows, problems = [], []
for t in topics:
    i = t['id']
    out = B / 'out' / i
    a = json.loads((B / 'articles' / f'{i}.json').read_text('utf-8'))
    need = [out / f'{i}.mp4', out / f'{i}.mp3', out / f'{i}_timings.json', out / f'{i}.plan.json',
            out / 'page' / 'layout.json', out / 'qa.txt', B / 'illust' / f'{i}.svg']
    miss = [p.name for p in need if not p.exists()]
    if miss:
        problems.append(f'{i} 缺 {miss}')
        continue
    if not (out / 'qa.txt').read_text('utf-8').rstrip().endswith('全部通过'):
        problems.append(f'{i} 核查未通过')
        continue
    for k in ('title_es', 'title_zh', 'level'):
        if a[k] != t[k]:
            problems.append(f'{i} {k} 和选题表不一致：{a[k]} ≠ {t[k]}')
    lv, no = t['level'].upper(), f"{t['no']:02d}"
    rows.append((i, t, out, f'daily_{lv}-{no}_{ascii_name(t["title_es"])}.mp4',
                 f'西班牙语每日一读 {lv}-{no} {t["title_es"]} {t["title_zh"]}.mp4'))
if problems:
    sys.exit('不归档：\n' + '\n'.join(problems))

REL.mkdir(parents=True, exist_ok=True)
DESK.mkdir(parents=True, exist_ok=True)
sums = []
for i, t, out, rel_name, desk_name in rows:
    shutil.copy2(out / f'{i}.mp4', REL / rel_name)
    shutil.copy2(out / f'{i}.mp4', DESK / desk_name)
    sums.append(f"{hashlib.sha256((REL / rel_name).read_bytes()).hexdigest()}  {rel_name}")
(REL / 'daily-reading-50-SHA256SUMS.txt').write_text('\n'.join(sums) + '\n', 'utf-8')

D = KIT / '每日一读'
files = []


# 说明文档里写的本机路径 → 仓库里的相对路径：批次目录、工具目录按命令行给的写法换；另有要换的写在可选的第 6 个参数（JSON：[[原文, 换成], …]）
LOCAL = (json.loads(Path(sys.argv[6]).read_text('utf-8')) if len(sys.argv) > 6 else []) + [
    (f'{B}/review/', '每日一读/批量/审读/'), (f'{B}/', '每日一读/批量/'), (f'{TOOLS}/', '每日一读/tools/')]
LEAK = re.compile(r'/tmp/|/private/|/Users/|/home/|Application\sSupport')


def put(src, rel):
    dst = D / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.suffix == '.md':                                  # 说明文档：本机路径换成仓库里的相对路径
        t = src.read_text('utf-8')
        for a, b in LOCAL:
            t = t.replace(a, b)
        if LEAK.search(t):
            sys.exit(f'{src.name} 里还有本机路径：{LEAK.search(t).group(0)}')
        dst.write_text(t, 'utf-8')
    else:
        shutil.copy2(src, dst)
    files.append(str(Path('每日一读') / rel))


for f in sorted(TOOLS.glob('*.py')):
    put(f, f'tools/{f.name}')
for f in ('选题表.json', '选题表.md', '编写要求.md', '插图要求.md', '样板.json', 'make_topics.py', 'style_ref.svg', 'style_ref.png', '成品一览.md'):
    put(B / f, f'批量/{f}')
for f in sorted((B / 'review').glob('*.md')):
    put(f, f'批量/审读/{f.name}')
for i, t, out, rel_name, desk_name in rows:
    put(B / 'articles' / f'{i}.json', f'批量/articles/{i}.json')
    put(B / 'illust' / f'{i}.svg', f'批量/illust/{i}.svg')
    put(out / f'{i}.mp3', f'批量/out/{i}/{i}.mp3')
    put(out / f'{i}_timings.json', f'批量/out/{i}/{i}_timings.json')
    put(out / f'{i}.plan.json', f'批量/out/{i}/{i}.plan.json')
    put(out / 'page' / 'layout.json', f'批量/out/{i}/layout.json')
    put(out / 'qa.txt', f'批量/核查/{i}.txt')
(B / 'files.txt').write_text('\n'.join(files) + '\n', 'utf-8')
print(f'归档 {len(rows)} 篇：Release 目录 {len(rows)} 个视频＋SHA256SUMS，桌面 {len(rows)} 个视频，工具包 {len(files)} 个文件')
