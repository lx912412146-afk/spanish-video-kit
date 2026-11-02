"""把 sets/*.md 解析成 out/sets.json，供 build_listening.js 排版用；有录音核对记录时一并写上每段录音的时长。
python export_json.py"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sets as S  # noqa: E402

data = []
for st in S.load_all():
    for p in st['parts']:
        p['intro'] = S.intro_lines(p)
        p['outro'] = S.outro_line(p)
        p['track'] = f"{st['num']:02d}-{p['idx']}"
        p['first'] = next((it['num'] for it in p['items'] if it['num'] != '例'), None)
        p['last'] = [it['num'] for it in p['items'] if it['num'] != '例'][-1]
    st['n_questions'] = len(S.questions(st))
    rep = S.ROOT / 'audio_out' / '核对' / f"set{st['num']:02d}.json"
    if rep.exists():
        r = json.loads(rep.read_text('utf-8'))
        dur = {t['id']: t['duration'] for t in r['tracks']}
        for p in st['parts']:
            p['duration'] = dur.get(p['track'])
    data.append(st)
out = S.ROOT / 'out' / 'sets.json'
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(data, ensure_ascii=False, indent=1), 'utf-8')
print(out, len(data), '套')
