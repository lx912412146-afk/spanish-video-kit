"""抽帧看版面：python frames.py <输出目录> <编号>…
每篇挑两句：西语最长的一句、生词栏文字最多的一句，在这句朗读中点截一帧（缩到 960 宽），两篇四帧拼成一张图。"""
import json, subprocess, sys
from pathlib import Path
from PIL import Image
S = Path(__file__).resolve().parents[1]
KIT = S / 'kit' / '西班牙语视频生成包（先行版）'
ES = KIT / '西班牙语'
out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
T = json.loads((ES / 'audio' / 'timings.json').read_text('utf-8'))
voice = lambda pid: 'qwen3_M1F5_25_slow' if pid[:2] in ('a1', 'a2') else 'qwen3_M1F5_25'
shots = []
for pid in sys.argv[2:]:
    p = json.loads((ES / '文章' / f'{pid}.json').read_text('utf-8'))
    S_ = [x for q in p['paras'] for x in q]
    k1 = max(range(len(S_)), key=lambda i: len(S_[i]['es']))
    k2 = max((i for i in range(len(S_)) if i != k1), key=lambda i: sum(len(w['h']) + len(w['zh']) for w in S_[i]['w']))
    name = subprocess.run([str(S / 'env/bin/python'), str(ES / 'tools/make_video.py'), pid, '--print-name'], capture_output=True, text=True, cwd=KIT).stdout.strip()
    mp4 = ES / '最终视频' / name
    sents = T[voice(pid)][pid]['sentences']
    for k in (k1, k2):
        t = (sents[k]['start'] + sents[k]['end']) / 2
        f = out / f'{pid}_{k + 1}.png'
        subprocess.run([str(S / 'env/bin/ffmpeg'), '-v', 'error', '-y', '-ss', f'{t:.2f}', '-i', str(mp4), '-frames:v', '1', '-vf', 'scale=960:-1', str(f)], check=True)
        shots.append(f)
for i in range(0, len(shots), 4):
    ims = [Image.open(f) for f in shots[i:i + 4]]
    sheet = Image.new('RGB', (1920, 1080), 'white')
    for j, im in enumerate(ims):
        sheet.paste(im, ((j % 2) * 960, (j // 2) * 540))
    sheet.save(out / f'sheet_{i // 4 + 1:02d}.png')
    print(out / f'sheet_{i // 4 + 1:02d}.png', [f.stem for f in shots[i:i + 4]])
