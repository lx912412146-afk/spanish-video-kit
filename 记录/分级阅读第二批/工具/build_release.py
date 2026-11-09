"""分级阅读第二批：准备 Release graded-reading-2 的文件、发布说明和 README 表格。
python build_release.py <工具包目录> <状态目录> <输出文件夹> <说明.md> <README表格.md>
- 50 篇（a1_11 … c1_20）：视频复制成英文文件名（A1-12_Mi_escuela.mp4 …），核查报告合并成 graded-reading-2_checks.json，
  再写 graded-reading-2-SHA256SUMS.txt
- 任何一篇缺视频、缺核查报告、有核查项没通过、逐句识别核对没通过（状态目录里没有 <编号>.asr_ok），或者视频比文章或 make_video.py（版式）旧，都报错退出
"""
import hashlib
import json
import shutil
import sys
from pathlib import Path

kit, state, out, notes, table = (Path(x) for x in sys.argv[1:6])
sys.path.insert(0, str(kit / '西班牙语' / 'tools'))
import make_video as M  # noqa: E402
from prep_release import ascii_name  # noqa: E402

LEVELS = {'A1': 'A1 基础入门', 'A2': 'A2 初级进阶', 'B1': 'B1 中级', 'B2': 'B2 中高级', 'C1': 'C1 高级'}
ids = [f'{lv}_{n}' for lv in ('a1', 'a2', 'b1', 'b2', 'c1') for n in range(11, 21)]
vids = kit / '西班牙语' / '最终视频'
if out.exists():
    sys.exit(f'{out} 已经存在，换一个新文件夹')
out.mkdir(parents=True)
bad, checks, rows = [], [], []
for pid in ids:
    p = M.load(pid)
    name = M.video_name(p)
    mp4 = vids / name
    rep = vids / (Path(name).stem + '_核查.json')
    art = kit / '西班牙语' / '文章' / f'{pid}.json'
    if not mp4.exists() or not rep.exists():
        bad.append(f'{pid}：缺视频或核查报告'); continue
    r = json.loads(rep.read_text('utf-8'))
    if not all(c['ok'] for c in r['checks']):
        bad.append(f'{pid}：有核查项没通过')
    if not (state / f'{pid}.asr_ok').exists():
        bad.append(f'{pid}：逐句识别核对没有通过记录')
    if mp4.stat().st_mtime < art.stat().st_mtime:
        bad.append(f'{pid}：视频比文章旧，要重新生成')
    if mp4.stat().st_mtime < (kit / '西班牙语' / 'tools' / 'make_video.py').stat().st_mtime:
        bad.append(f'{pid}：视频比 make_video.py（版式）旧，要重新生成')
    f = ascii_name(p)
    shutil.copyfile(mp4, out / f)
    checks.append({'file': f, 'article': pid, **r})
    sents = [s for para in p['paras'] for s in para]
    rows.append({'id': pid, 'level': p['level'], 'no': p['no'], 'es': p['title_es'], 'zh': p['title_zh'], 'n': len(sents),
                 'words': M.words(p), 'gloss': sum(len(s['w']) for s in sents), 'dur': r['duration'], 'file': f,
                 'slow': r['voice'].endswith('_slow')})
if bad:
    sys.exit('不能发布：\n  ' + '\n  '.join(bad))
(out / 'graded-reading-2_checks.json').write_text(json.dumps(checks, ensure_ascii=False, indent=1), 'utf-8')
sums = []
for f in sorted(out.iterdir()):
    sums.append(f'{hashlib.sha256(f.read_bytes()).hexdigest()}  {f.name}')
(out / 'graded-reading-2-SHA256SUMS.txt').write_text('\n'.join(sums) + '\n', 'utf-8')

durs = [x['dur'] for x in rows]
head = (f"西班牙语分级阅读第二批逐句精读视频，A1—C1 每级 10 篇，共 50 篇（A1-11 … C1-20），每篇约 1 分钟"
        f"（{min(durs):.1f}–{max(durs):.1f} 秒，平均 {sum(durs) / len(durs):.1f} 秒）。A1—A2 用 0.8 倍速，B1—C1 用原速。\n\n"
        "- 文章全部原创（不是《西班牙语A1-C1分级阅读文章集》里的），编号接着第一批（Release `graded-reading`）。\n"
        "- 4K（3840×2160）、30 帧；每句有西语原文、中文翻译和 3–5 个生词，版式和第一批相同。"
        "生词释义一行放不下时整段换到下一行，译文最后一行不留孤字。\n"
        "- A1—A2 朗读用音色 `qwen3_M1F5_25_slow`（Qwen3-TTS 1.7B 克隆音色，0.8 倍速，音高 +1 半音）；B1—C1 用 `qwen3_M1F5_25`（原速）。\n"
        "- 每个视频的 15 项核查全部通过，报告在 `graded-reading-2_checks.json`。每句朗读还从成品 MP3 切出来用语音识别（Parakeet）"
        "核对过，和原文逐词一致（`西班牙语/tools/asr_check_reading.py`）；画面折行用 `西班牙语/tools/check_wraps.py` 检查过。\n"
        "- 文章 JSON 在仓库 `西班牙语/文章/`，音频（MP3）、字幕（SRT）在 `西班牙语/audio/<音色>/`。"
        "`graded-reading-2-SHA256SUMS.txt` 是各文件的 SHA-256。\n")
lines = [head]
tlines = []
for lv, lvname in LEVELS.items():
    rs = [x for x in rows if x['level'] == lv]
    lines.append(f'\n### {lvname}\n\n| 编号 | 标题 | 中文 | 句数 · 词数 · 生词 | 语速 | 时长 | 文件 |\n|---|---|---|---|---|---|---|')
    tlines.append(f'<details><summary>第二批 {lvname}（10 篇，{"0.8 倍速" if rs[0]["slow"] else "原速"}）</summary>\n\n'
                  '| 编号 | 标题 | 中文 | 句数 · 词数 · 生词 | 时长 |\n|---|---|---|---|---|')
    for x in rs:
        lines.append(f"| {lv}-{x['no']} | {x['es']} | {x['zh']} | {x['n']} 句 · {x['words']} 词 · {x['gloss']} 个 | "
                     f"{'0.8 倍' if x['slow'] else '原速'} | {x['dur']:.0f} 秒 | `{x['file']}` |")
        tlines.append(f"| {x['id']} | {x['es']} | {x['zh']} | {x['n']} 句 · {x['words']} 词 · {x['gloss']} 个 | {x['dur']:.0f} 秒 |")
    tlines.append('\n</details>\n')
notes.write_text('\n'.join(lines) + '\n', 'utf-8')
table.write_text('\n'.join(tlines), 'utf-8')
print(f'OK：{len(rows)} 个视频，{min(durs):.1f}–{max(durs):.1f} 秒；文件在 {out}')
