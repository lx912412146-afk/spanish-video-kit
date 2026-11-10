"""“每日一读”视频合成：静态页＋朗读（和参考视频一样整段一张图），另出一个逐句高亮版。

    python make_daily_video.py <页面目录> <id>_timings.json <朗读.mp3> <输出.mp4> [<高亮版输出.mp4>]

24 帧/秒，1080×1512，H.264 CRF 18（静态画面），AAC 160k 48 kHz。高亮版：第 k 句从开口前 0.12 秒高亮到下一句开口前，
最后一句高亮到读完后 0.3 秒，其余时间（片头、片尾）显示不高亮的静态页；每段的帧数按累计时间取整，不累积误差。
"""
import json
import subprocess
import sys
from pathlib import Path

PAGE, TIM, MP3, OUT = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4])
OUT_HL = Path(sys.argv[5]) if len(sys.argv) > 5 else None
FPS = 24
T = json.loads(TIM.read_text('utf-8'))
dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(MP3)],
                           capture_output=True, text=True, check=True).stdout)
NF = round(dur * FPS)
VENC = ['-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-tune', 'stillimage', '-pix_fmt', 'yuv420p', '-r', str(FPS),
        '-c:a', 'aac', '-b:a', '160k', '-ar', '48000', '-movflags', '+faststart']


def run(cmd):
    subprocess.run(['ffmpeg', '-v', 'error', '-y'] + cmd, check=True)


run(['-loop', '1', '-framerate', str(FPS), '-i', str(PAGE / 'page_static.png'), '-i', str(MP3),
     '-map', '0:v', '-map', '1:a', '-frames:v', str(NF), '-t', f'{NF / FPS:.6f}'] + VENC + [str(OUT)])
print('静态版', OUT.name, f'{NF} 帧（{NF / FPS:.3f} 秒），音频 {dur:.3f} 秒')

if OUT_HL:
    S = T['sentences']
    segs = [('page_static.png', 0.0)]
    for i, s in enumerate(S):
        segs.append((f"page_hl_{s['k']:02d}.png", max(0.0, s['start'] - 0.12)))
    segs.append(('page_static.png', min(dur, S[-1]['end'] + 0.3)))
    bounds = [round(t * FPS) for _, t in segs] + [NF]
    plan = []
    for (img, _), a, b in zip(segs, bounds, bounds[1:]):
        if b > a:
            plan.append((img, a, b))
    ins, fc = [], []
    for j, (img, a, b) in enumerate(plan):
        ins += ['-loop', '1', '-framerate', str(FPS), '-i', str(PAGE / img)]
        fc.append(f'[{j}:v]trim=end_frame={b - a},setpts=PTS-STARTPTS[v{j}]')
    fc.append(''.join(f'[v{j}]' for j in range(len(plan))) + f'concat=n={len(plan)}:v=1:a=0[v]')
    n = len(plan)
    run(ins + ['-i', str(MP3), '-filter_complex', ';'.join(fc), '-map', '[v]', '-map', f'{n}:a',
               '-frames:v', str(NF), '-t', f'{NF / FPS:.6f}'] + VENC + [str(OUT_HL)])
    (OUT_HL.with_suffix('.plan.json')).write_text(json.dumps(
        [{'img': img, 'from_frame': a, 'to_frame': b, 'from_s': round(a / FPS, 3), 'to_s': round(b / FPS, 3)} for img, a, b in plan],
        ensure_ascii=False, indent=1), 'utf-8')
    print('高亮版', OUT_HL.name, f'{len(plan)} 段，{NF} 帧')
