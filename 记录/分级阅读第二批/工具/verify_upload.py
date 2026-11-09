"""上传后核对：python verify_upload.py <release.json> <tree.json> <仓库目录> <本机 release 目录> <仓库文件…>
release.json 是 api.github.com 的 releases/tags/<标签>，tree.json 是 git/trees/main?recursive=1。
Release 的每个文件：大小和 sha256（GitHub 给出的 digest）要和本机 release 目录里的一致，一个不多一个不少；
列出的仓库文件：blob sha 要和本机 git hash-object 算出的一致。"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

rel, tree = (json.loads(Path(p).read_text('utf-8')) for p in sys.argv[1:3])
kit, rdir, paths = Path(sys.argv[3]), Path(sys.argv[4]), sys.argv[5:]
G = str(Path(sys.executable).parent / 'git')
bad = []
local = {p.name: p for p in rdir.iterdir() if p.is_file()}
remote = {a['name']: a for a in rel['assets']}
if set(local) != set(remote):
    bad.append(f'Release 文件不一致：本机多 {sorted(set(local) - set(remote))}，GitHub 多 {sorted(set(remote) - set(local))}')
for name in sorted(set(local) & set(remote)):
    a, f = remote[name], local[name]
    h = hashlib.sha256(f.read_bytes()).hexdigest()
    ok = a.get('state') == 'uploaded' and a['size'] == f.stat().st_size and a.get('digest') == f'sha256:{h}'
    print(f"  {'✓' if ok else '✗'} {name} {a['size']} {a.get('digest')}")
    if not ok:
        bad.append(f"{name}：GitHub {a.get('state')} {a['size']} {a.get('digest')}，本机 {f.stat().st_size} sha256:{h}")
print(f"Release {rel['tag_name']}：{len(remote)} 个文件，draft={rel['draft']}")
if rel['draft']:
    bad.append('Release 是草稿')
blobs = {t['path']: t['sha'] for t in tree['tree'] if t['type'] == 'blob'}
if tree.get('truncated'):
    bad.append('tree 被截断')
for rp in paths:
    h = subprocess.run([G, '-C', str(kit), 'hash-object', rp], capture_output=True, text=True, check=True).stdout.strip()
    ok = blobs.get(rp) == h
    print(f"  {'✓' if ok else '✗'} {rp}")
    if not ok:
        bad.append(f'{rp}：GitHub {blobs.get(rp)}，本机 {h}')
print(f'仓库：核对 {len(paths)} 个文件')
for b in bad:
    print('  ✗', b)
print('VERIFY_OK' if not bad else 'VERIFY_FAILED')
sys.exit(1 if bad else 0)
