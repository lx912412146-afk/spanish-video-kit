"""“每日一读”批量成品一览：从各篇的时间表、版面数据、核查报告里取数，写成 Markdown 表格。

    python summary_batch.py <批次目录> <输出.md>

每篇一行：级别、标题、音色、句数、正文词数、时长、句间停顿、整体响度、短时响度波动、西语字号和字距、最大词间空白、底部留白、核查项数。
"""
import json
import re
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
B, OUT = Path(sys.argv[1]), Path(sys.argv[2])
sys.argv = sys.argv[:1]
import check_daily as CD  # noqa: E402

topics = json.loads((B / '选题表.json').read_text('utf-8'))
rows, durs = [], {}
for t in topics:
    i = t['id']
    a = json.loads((B / 'articles' / f'{i}.json').read_text('utf-8'))
    o = B / 'out' / i
    T = json.loads((o / f'{i}_timings.json').read_text('utf-8'))
    L = json.loads((o / 'page' / 'layout.json').read_text('utf-8'))
    qa = (o / 'qa.txt').read_text('utf-8').splitlines()
    sents = [s for p in a['paras'] for s in p]
    nw = sum(len(CD.words(s['es'])) for s in sents)
    checks = [x for x in qa if re.match(r'^[✓✗]', x)]
    n_ok = sum(x.startswith('✓') for x in checks)
    m = re.search(r'视频 ([\d.]+) 秒', '\n'.join(qa))
    dur = float(m.group(1)) if m else T['duration']
    bottom = max(L['zh'][3], L['aside'][3])
    durs.setdefault(t['level'], []).append(dur)
    rows.append(f"| {t['level']}-{t['no']:02d} | {a['title_es']} | {a['title_zh']} | {'0.8 倍速' if a['voice'].endswith('_slow') else '原速'} | "
                f"{len(sents)} | {nw} | {dur:.1f} 秒 | {T['sentence_pause']} 秒 | {T['loudness']['integrated_lufs']} | "
                f"{T['loudness']['short_term_std_lu']} | {L['es_font'][0]} / {L['es_font'][1]:+g} | {L['es_max_gap']} | "
                f"{1008 - bottom:.0f} | {n_ok}/{len(checks)} |")
alld = [d for v in durs.values() for d in v]
head = ['# 每日一读 50 篇成品一览', '',
        f"共 {len(rows)} 篇，每级 10 篇。时长 {min(alld):.1f}—{max(alld):.1f} 秒，平均 {statistics.mean(alld):.1f} 秒；"
        + '，'.join(f'{lv} 平均 {statistics.mean(v):.1f} 秒' for lv, v in durs.items()) + '。', '',
        '- 词数：正文（不含标题）；时长：MP4 视频时长；停顿：句间停顿（先试 1.0 秒，不过才用 0.9、0.8 秒）。',
        '- 响度：整体 LUFS、3 秒短时响度波动（LU，上限 1.0）。字号／字距：西语正文自动选的 px。',
        '- 词间空白：两端对齐各行最大词间空白（px，上限 8）；留白：页面底部留白（px，下限 40）；核查：通过项／总项。', '',
        '| 编号 | 西语标题 | 中文标题 | 朗读 | 句 | 词 | 时长 | 停顿 | 响度 | 波动 | 字号／字距 | 词间空白 | 留白 | 核查 |',
        '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|']
OUT.write_text('\n'.join(head + rows) + '\n', 'utf-8')
print(f'{OUT.name}：{len(rows)} 篇，时长 {min(alld):.1f}—{max(alld):.1f} 秒')
