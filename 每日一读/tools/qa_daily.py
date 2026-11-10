"""“每日一读”成品核查（静态版、逐句高亮版两个 MP4 都查）：

1. 规格：H.264 1080×1512、24 帧/秒、yuv420p，AAC 48 kHz；视频和音频时长相差不超过 1 帧。
2. 声音：两个 MP4 的音轨解码后逐样本相同；整体响度 −16±0.7 LUFS、峰值 ≤ −1 dBFS；逐句切出用 Parakeet 识别，
   和朗读原文逐词比对（同 西班牙语/tools/asr_check_reading.py：换四种切点取最好的，必须 0 处出入）。
3. 画面：高亮版每一段取中间一帧，和 12 张源图（静态页＋11 张高亮页）在高亮区域里逐像素比，最像的必须是该段应显示的那张，
   逐对比：只看应显示的图和另一张不同的像素，帧到应显示图的差 < 0.35 × 到另一张的差；整页平均差 < 2.5（压缩噪声）；静态版取 6 个时间点，都必须和静态页一致。
4. 版面（layout.json）：页面不滚动、没有文字被截断、底部留白 ≥ 40 px、西语两端对齐的词间空白 ≤ 8 px。
5. 内容：词汇表 15 条，每条都能在正文里找到（原形或变位）；中文没有半角标点；每句西语和译文一一对应。

    cd <工具包根目录> && python qa_daily.py <文章.json> <输出目录> <静态版.mp4> <高亮版.mp4> <ASR 模型目录>
"""
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

ART, OUT, MP4S, MP4H, ASRD = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), Path(sys.argv[4]), sys.argv[5]
a = json.loads(ART.read_text('utf-8'))
T = json.loads((OUT / f"{a['id']}_timings.json").read_text('utf-8'))
PAGE = OUT / ('page_' + a['id'].split('_')[-1])          # daily_01 → page_01
FPS, W, H = 24, 1080, 1512
errs, notes = [], []


def ok(cond, msg):
    (notes if cond else errs).append(('✓ ' if cond else '✗ ') + msg)


def probe(f):
    r = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(f)],
                                  capture_output=True, text=True, check=True).stdout)
    v = next(s for s in r['streams'] if s['codec_type'] == 'video')
    au = next(s for s in r['streams'] if s['codec_type'] == 'audio')
    return v, au


for f in (MP4S, MP4H):
    v, au = probe(f)
    vd, ad = float(v['duration']), float(au['duration'])
    ok(v['codec_name'] == 'h264' and (v['width'], v['height']) == (W, H) and v['r_frame_rate'] == '24/1'
       and v['pix_fmt'] == 'yuv420p' and au['codec_name'] == 'aac' and au['sample_rate'] == '48000',
       f"{f.name}：{v['codec_name']} {v['width']}×{v['height']} {v['r_frame_rate']} {v['pix_fmt']}，{au['codec_name']} {au['sample_rate']} Hz")
    ok(abs(vd - ad) <= 1 / FPS + 0.03, f'{f.name}：视频 {vd:.3f} 秒，音频 {ad:.3f} 秒，帧数 {v.get("nb_frames")}')


def pcm(f, sr=48000):
    return np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', str(f), '-vn', '-f', 'f32le', '-ac', '1', '-ar', str(sr), '-'],
                                        capture_output=True, check=True).stdout, np.float32)


xs, xh = pcm(MP4S), pcm(MP4H)
ok(len(xs) == len(xh) and np.array_equal(xs, xh), f'两个版本音轨相同（{len(xs) / 48000:.3f} 秒）')

import pyloudnorm as pyln  # noqa: E402
il = pyln.Meter(48000).integrated_loudness(xs.astype(np.float64))
pk = 20 * np.log10(np.abs(xs).max())
ok(abs(il + 16) <= 0.7 and pk <= -1.0, f'MP4 音轨整体响度 {il:.2f} LUFS，峰值 {pk:.2f} dBFS')

# ---- 逐句识别
sys.argv = ['make_tracks.py', '.', tempfile.gettempdir(), ASRD, '1']
sys.path.insert(0, str(Path('B1-B2听力练习/tools').resolve()))
import make_tracks as M  # noqa: E402
rec = M.Recognizer()
SR = 48000
asr_bad = 0
for s in T['sentences']:
    best = None
    for pre, post in ((0.15, 0.25), (0.3, 0.4), (0.05, 0.15), (0.4, 0.6)):
        x = xs[max(0, int((s['start'] - pre) * SR)):int((s['end'] + post) * SR)]
        hyp = rec(x, SR)
        e, ops = M.compare(s['read'], hyp)
        if best is None or e < best[0]:
            best = (e, ops, hyp)
        if e == 0:
            break
    asr_bad += best[0] != 0
    print(f"{'✓' if best[0] == 0 else '✗'} {s['k']:2d} {s['read']}\n     识别：{best[2]}" + (f'  {best[1]}' if best[1] else ''))
ok(asr_bad == 0, f"逐句识别：{len(T['sentences'])} 句，{asr_bad} 句有出入")


# ---- 画面
def frame_at(f, t):
    return np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-ss', f'{t:.3f}', '-i', str(f), '-frames:v', '1',
                                         '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True, check=True).stdout,
                         np.uint8).reshape(H, W, 3).astype(np.int16)


def img(p):
    return np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', str(p), '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                                        capture_output=True, check=True).stdout, np.uint8).reshape(H, W, 3).astype(np.int16)


srcs = {p.name: img(p) for p in sorted(PAGE.glob('page_*.png'))}
static = srcs['page_static.png']
plan = json.loads(MP4H.with_suffix('.plan.json').read_text('utf-8'))
DIFF = {}


def pair_ok(fr, exp):
    """对每一张别的源图 C：只看 exp 和 C 不同的像素（各自的高亮处），帧必须明显更接近 exp。返回 (是否通过, 最差的比值, 是哪张)。"""
    worst = (0.0, '')
    for n, im in srcs.items():
        if n == exp:
            continue
        key = (exp, n)
        if key not in DIFF:
            DIFF[key] = np.abs(srcs[exp] - im).max(axis=2) > 12
        r = DIFF[key]
        de, dc = float(np.abs(fr - srcs[exp])[r].mean()), float(np.abs(fr - im)[r].mean())
        worst = max(worst, (de / dc, n))
    return worst[0] < 0.35, worst


fr_bad = 0
for seg in plan:
    t = (seg['from_frame'] + seg['to_frame']) / 2 / FPS
    fr = frame_at(MP4H, t)
    good, (ratio, who) = pair_ok(fr, seg['img'])
    whole = float(np.abs(fr - srcs[seg['img']]).mean())
    good = good and whole < 2.5
    fr_bad += not good
    print(f"{'✓' if good else '✗'} 高亮版 {t:6.2f} 秒 应为 {seg['img']}：和其余 11 张逐对比，最接近混淆的是 {who}（差值比 {ratio:.2f}，要求 < 0.35）；整页差 {whole:.2f}")
for t in (0.5, 10, 25, 40, 55, 62):
    fr = frame_at(MP4S, t)
    good, (ratio, who) = pair_ok(fr, 'page_static.png')
    dd = float(np.abs(fr - static).mean())
    good = good and dd < 2.5
    fr_bad += not good
    print(f"{'✓' if good else '✗'} 静态版 {t:5.1f} 秒 应为静态页：最接近混淆的是 {who}（差值比 {ratio:.2f}）；整页差 {dd:.2f}")
ok(fr_bad == 0, f'画面：高亮版 {len(plan)} 段、静态版 6 个时间点，{fr_bad} 处不对')

# 每句开口时高亮已经到位：逐句检查开口时刻所在的段
miss = []
for s in T['sentences']:
    f0 = int(s['start'] * FPS) + 1
    seg = next(g for g in plan if g['from_frame'] <= f0 < g['to_frame'])
    if seg['img'] != f"page_hl_{s['k']:02d}.png":
        miss.append(s['k'])
    f1 = int(s['end'] * FPS) - 1
    seg = next(g for g in plan if g['from_frame'] <= f1 < g['to_frame'])
    if seg['img'] != f"page_hl_{s['k']:02d}.png":
        miss.append(s['k'])
ok(not miss, f'每句从开口到读完都高亮这一句（{len(T["sentences"])} 句）' + (f'：不对的 {miss}' if miss else ''))

# ---- 版面
L = json.loads((PAGE / 'layout.json').read_text('utf-8'))
ok(L['scroll'] == [720, 1008] and L['overflow'] == 0, f"页面不滚动、没有截断（scroll {L['scroll']}，overflow {L['overflow']}）")
bottom = 1008 - max(L['zh'][3], L['aside'][3])
ok(bottom >= 40, f'底部留白 {bottom:.0f} px')
ok(L['es_max_gap'] <= 8, f"西语两端对齐最大词间空白 {L['es_max_gap']} px")
ok(L['ill'][3] < L['es'][1] and L['es'][3] < L['zh'][1] and L['aside'][0] > L['es'][2],
   '插图、西语、译文、词汇栏互不重叠')
ok(all(len(x['es'].split()) and x['zh'] for para in a['paras'] for x in para), '每句都有译文')

# ---- 内容
text = ' '.join(x['es'] for para in a['paras'] for x in para).lower()
FORMS = {'regar': 'riego'}
miss = [w for w, _ in a['vocab'] if not re.search(r'\b' + re.escape(FORMS.get(w, w)), text)]
ok(len(a['vocab']) == 15 and not miss, f"词汇表 {len(a['vocab'])} 条，正文里找不到的：{miss or '无'}")
zh_all = ''.join(x['zh'] for para in a['paras'] for x in para) + a['title_zh']
half = re.findall(r'[,.;:!?()"\']', zh_all)
ok(not half, f'中文半角标点：{half or "无"}')
es_sents = [x['es'] for para in a['paras'] for x in para]
read = [s['read'] for s in T['sentences']]
ok(read == [a['title_es'] + '.'] + es_sents, '朗读文字＝标题＋正文（逐句一致）')

print('\n'.join(notes + errs))
print('全部通过' if not errs else f'{len(errs)} 项不通过')
sys.exit(1 if errs else 0)
