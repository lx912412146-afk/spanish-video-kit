"""准备分级阅读 Release（graded-reading）要上传的文件：

    python 西班牙语/tools/prep_release.py 输出文件夹 [说明文件]

- 50 个视频复制成英文文件名（GitHub 附件名不支持中文和空格）：A1-01_Mi_familia.mp4 …
- 50 份核查报告合并成 graded-reading_checks.json（键是文章编号，含附件名）
- 发布说明写到“说明文件”（默认：输出文件夹旁边的 graded-reading-notes.md），之后用 gh release create/upload 上传
任何一篇缺视频、缺报告或有核查项没通过，都直接报错，不生成不完整的文件。
"""
import json
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import c4  # noqa: E402

mv = c4.load('es_make_video', '西班牙语/tools/make_video.py')


def ascii_name(p):
    t = p['title_es'].translate(str.maketrans('áéíóúüñÁÉÍÓÚÜÑ¿¡', 'aeiouunAEIOUUN  '))
    return f"{p['level']}-{p['no']:02d}_{re.sub(r'[^A-Za-z0-9]+', '_', t).strip('_')}.mp4"


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    out = Path(sys.argv[1]).resolve()
    notes_path = Path(sys.argv[2]) if len(sys.argv) > 2 else out.parent / 'graded-reading-notes.md'
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    vids = HERE.parent / '最终视频'
    ids = sorted(f.stem for f in (HERE.parent / '文章').glob('*.json') if re.fullmatch(r'[abc][12]_\d\d', f.stem))
    checks, rows, total = {}, [], 0.0
    for pid in ids:
        p = mv.load(pid)
        name = mv.video_name(p)
        mp4, rep = vids / name, vids / (Path(name).stem + '_核查.json')
        if not mp4.exists() or not rep.exists():
            raise SystemExit(f'{pid}：缺视频或核查报告（{name}）')
        r = json.loads(rep.read_text('utf-8'))
        bad = [c['item'] for c in r['checks'] if not c['ok']]
        if bad:
            raise SystemExit(f'{pid}：核查未通过 {bad}')
        asset = ascii_name(p)
        shutil.copyfile(mp4, out / asset)
        checks[pid] = {'asset': asset, **r}
        total += r['duration']
        rows.append(f"| {p['level']}-{p['no']:02d} | {p['title_es']} | {p['title_zh']} | {r['duration']:.0f} 秒 | `{asset}` |")
    (out / 'graded-reading_checks.json').write_text(json.dumps(checks, ensure_ascii=False, indent=1), 'utf-8')
    notes = f"""西班牙语分级阅读 A1–C1 逐句精读视频，共 {len(ids)} 篇（每级 10 篇），原文来自《西班牙语A1-C1分级阅读文章集》。

- 4K（3840×2160）、30 帧；每句有西语原文、中文翻译和 3–5 个生词。
- 朗读用音色 `qwen3_M1F5_25_slow`：Qwen3-TTS 1.7B 克隆音色，0.8 倍速，音高 +1 半音。
- 每个视频 15 项核查全部通过，报告在 `graded-reading_checks.json`。短时响度波动只统计朗读范围，原测法的数值记在 `info` 里，说明见仓库 README。
- 总时长约 {total / 60:.0f} 分钟。音频（MP3）、字幕（SRT）在仓库 `西班牙语/audio/qwen3_M1F5_25_slow/`。

| 编号 | 标题 | 中文 | 时长 | 文件 |
|---|---|---|---|---|
""" + '\n'.join(rows) + '\n\n重新生成：`zsh setup_mac.sh`，然后运行 `./batch_mac.sh`。\n'
    notes_path.write_text(notes, 'utf-8')
    print(f'已准备 {len(ids)} 个视频，共 {total / 60:.1f} 分钟：{out}；说明：{notes_path}')


if __name__ == '__main__':
    main()
