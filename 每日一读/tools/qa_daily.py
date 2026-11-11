"""“每日一读”成品核查（逐句高亮版必查；给了静态版也一起查）：

1. 规格：H.264 1080×1512、24 帧/秒、yuv420p，AAC 48 kHz；视频和音频时长相差不超过 1 帧；总时长 53—67 秒。
2. 声音：整体响度 −16±0.7 LUFS、峰值 ≤ −1 dBFS（两个版本时，音轨还要逐样本相同）；逐句切出用 Parakeet 识别，
   和朗读原文逐词比对（同 西班牙语/tools/asr_check_reading.py：换四种切点取最好的，必须 0 处出入）。
3. 画面：高亮版每一段取中间一帧，和全部源图（静态页＋各句高亮页）逐对比较：只看应显示的图和另一张不同的像素，
   帧到应显示图的差 < 0.35 × 到另一张的差；整页平均差 < 2.5（压缩噪声）。每句从开口到读完都高亮这一句。
   静态版在全片均匀取 6 个时间点，都必须是静态页。
4. 版面（layout.json）：页面不滚动、没有文字被截断、底部留白 ≥ 40 px、各区块互不重叠、西语两端对齐的词间空白 ≤ 8 px、
   标题栏左右两块之间留空 ≥ 12 px、插图上的标题不超出插图、词汇栏每条都在栏内。
5. 内容：词汇 15 条，原文写法都在正文里（完整的词）；中文没有半角标点；朗读文字＝标题＋正文逐句一致。

    cd <工具包根目录> && python qa_daily.py <文章.json> <输出目录> <静态版.mp4 或 -> <高亮版.mp4> <ASR 模型目录> [页面目录]

输出目录里要有 <id>_timings.json；页面目录默认是 <输出目录>/page（没有就用 <输出目录>/page_<编号末两位>，第 01 篇样片用这个）。
"""
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

ART, OUT = Path(sys.argv[1]), Path(sys.argv[2])
MP4S = None if sys.argv[3] == '-' else Path(sys.argv[3])
MP4H, ASRD = Path(sys.argv[4]), sys.argv[5]
a = json.loads(ART.read_text('utf-8'))
T = json.loads((OUT / f"{a['id']}_timings.json").read_text('utf-8'))
if len(sys.argv) > 6:
    PAGE = Path(sys.argv[6])
elif (OUT / 'page').is_dir():
    PAGE = OUT / 'page'
else:
    PAGE = OUT / ('page_' + a['id'].split('_')[-1])          # 样片 daily_01 → page_01
FPS, W, H = 24, 1080, 1512
LETTER = 'A-Za-zÁÉÍÓÚÜÑáéíóúüñ'
errs, notes = [], []


def ok(cond, msg):
    (notes if cond else errs).append(('✓ ' if cond else '✗ ') + msg)


def probe(f):
    r = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(f)],
                                  capture_output=True, text=True, check=True).stdout)
    v = next(s for s in r['streams'] if s['codec_type'] == 'video')
    au = next(s for s in r['streams'] if s['codec_type'] == 'audio')
    return v, au


vids = [f for f in (MP4S, MP4H) if f]
for f in vids:
    v, au = probe(f)
    vd, ad = float(v['duration']), float(au['duration'])
    ok(v['codec_name'] == 'h264' and (v['width'], v['height']) == (W, H) and v['r_frame_rate'] == '24/1'
       and v['pix_fmt'] == 'yuv420p' and au['codec_name'] == 'aac' and au['sample_rate'] == '48000',
       f"{f.name}：{v['codec_name']} {v['width']}×{v['height']} {v['r_frame_rate']} {v['pix_fmt']}，{au['codec_name']} {au['sample_rate']} Hz")
    ok(abs(vd - ad) <= 1 / FPS + 0.03, f'{f.name}：视频 {vd:.3f} 秒，音频 {ad:.3f} 秒，帧数 {v.get("nb_frames")}')
DUR = float(probe(MP4H)[0]['duration'])
ok(53 <= DUR <= 67, f'总时长 {DUR:.1f} 秒（53—67）')


def pcm(f, sr=48000):
    return np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-i', str(f), '-vn', '-f', 'f32le', '-ac', '1', '-ar', str(sr), '-'],
                                        capture_output=True, check=True).stdout, np.float32)


xh = pcm(MP4H)
if MP4S:
    xs = pcm(MP4S)
    ok(len(xs) == len(xh) and np.array_equal(xs, xh), f'两个版本音轨相同（{len(xs) / 48000:.3f} 秒）')

import pyloudnorm as pyln  # noqa: E402
il = pyln.Meter(48000).integrated_loudness(xh.astype(np.float64))
pk = 20 * np.log10(np.abs(xh).max())
ok(abs(il + 16) <= 0.7 and pk <= -1.0, f'MP4 音轨整体响度 {il:.2f} LUFS，峰值 {pk:.2f} dBFS')

# ---- 逐句识别
sys.argv = ['make_tracks.py', '.', tempfile.gettempdir(), ASRD, '1']
sys.path.insert(0, str(Path('B1-B2听力练习/tools').resolve()))
import make_tracks as M  # noqa: E402
rec = M.Recognizer()
SR = 48000
asr_bad = []
for s in T['sentences']:
    best = None
    for pre, post in ((0.15, 0.25), (0.3, 0.4), (0.05, 0.15), (0.4, 0.6)):
        x = xh[max(0, int((s['start'] - pre) * SR)):int((s['end'] + post) * SR)]
        hyp = rec(x, SR)
        e, ops = M.compare(s['read'], hyp)
        if best is None or e < best[0]:
            best = (e, ops, hyp)
        if e == 0:
            break
    if best[0]:
        asr_bad.append(s['k'])
    print(f"{'✓' if best[0] == 0 else '✗'} {s['k']:2d} {s['read']}\n     识别：{best[2]}" + (f'  {best[1]}' if best[1] else ''))
ok(not asr_bad, f"逐句识别：{len(T['sentences'])} 句，{len(asr_bad)} 句有出入" + (f'（第 {asr_bad} 句，第 1 句是标题）' if asr_bad else ''))


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
    """对每一张别的源图 C：只看 exp 和 C 不同的像素（各自的高亮处），帧必须明显更接近 exp。返回 (是否通过, (最差的比值, 是哪张))。"""
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
    print(f"{'✓' if good else '✗'} 高亮版 {t:6.2f} 秒 应为 {seg['img']}：和其余 {len(srcs) - 1} 张逐对比，最接近混淆的是 {who}"
          f"（差值比 {ratio:.2f}，要求 < 0.35）；整页差 {whole:.2f}")
if MP4S:
    for t in np.linspace(0.4, DUR - 0.4, 6):
        fr = frame_at(MP4S, float(t))
        good, (ratio, who) = pair_ok(fr, 'page_static.png')
        dd = float(np.abs(fr - static).mean())
        good = good and dd < 2.5
        fr_bad += not good
        print(f"{'✓' if good else '✗'} 静态版 {t:5.1f} 秒 应为静态页：最接近混淆的是 {who}（差值比 {ratio:.2f}）；整页差 {dd:.2f}")
ok(fr_bad == 0, f'画面：高亮版 {len(plan)} 段' + ('、静态版 6 个时间点' if MP4S else '') + f'，{fr_bad} 处不对')

miss = []
for s in T['sentences']:
    for f0 in (int(s['start'] * FPS) + 1, int(s['end'] * FPS) - 1):
        seg = next(g for g in plan if g['from_frame'] <= f0 < g['to_frame'])
        if seg['img'] != f"page_hl_{s['k']:02d}.png":
            miss.append(s['k'])
ok(not miss, f'每句从开口到读完都高亮这一句（{len(T["sentences"])} 句）' + (f'：不对的 {sorted(set(miss))}' if miss else ''))
ok(len(srcs) == len(T['sentences']) + 1, f'源图 {len(srcs)} 张＝静态页＋{len(T["sentences"])} 张高亮页')

# ---- 版面
L = json.loads((PAGE / 'layout.json').read_text('utf-8'))
ok(L['scroll'] == [720, 1008] and L['overflow'] == 0, f"页面不滚动、没有截断（scroll {L['scroll']}，overflow {L['overflow']}）")
bottom = 1008 - max(L['zh'][3], L['aside'][3])
ok(bottom >= 40, f'底部留白 {bottom:.0f} px')
ok(L['es_max_gap'] <= 8, f"西语两端对齐最大词间空白 {L['es_max_gap']} px" + (f"（字号 {L['es_font']}）" if 'es_font' in L else ''))
ok(L['ill'][3] < L['es'][1] and L['es'][3] < L['zh'][1] and L['aside'][0] > L['es'][2], '插图、西语、译文、词汇栏互不重叠')
if 'header_gap' in L:
    ok(L['header_gap'] >= 12, f"标题栏左右留空 {L['header_gap']:.0f} px")
if L.get('ill_title'):
    ok(L['ill_title'][2] <= L['ill'][2] - 10, f"插图上的标题在插图内（右端 {L['ill_title'][2]:.0f}，插图右端 {L['ill'][2]:.0f}）")
if 'vocab_out' in L:
    ok(L['vocab_out'] == 0, f"词汇栏每条都在栏内（换行的 {L.get('vocab_wrapped', 0)} 条）")

# ---- 内容
sents = [x for para in a['paras'] for x in para]
body = ' '.join(x['es'] for x in sents)
FORMS = {'regar': 'riego'}
miss = []
for v in a['vocab']:
    sf = v[2] if len(v) > 2 else FORMS.get(v[0], v[0])
    flags = 0 if len(v) > 2 else re.I
    if not re.search(rf'(?<![{LETTER}]){re.escape(sf)}(?![{LETTER}])', body, flags):
        miss.append(v[0])
ok(len(a['vocab']) == 15 and not miss, f"词汇 {len(a['vocab'])} 条，正文里找不到的：{miss or '无'}")
zh_all = ''.join(x['zh'] for x in sents) + a['title_zh']
half = re.findall(r'[A-Za-z0-9,.;:!?()"\']', zh_all)
ok(not half, f'中文半角字符：{half or "无"}')
read = [s['read'] for s in T['sentences']]
ok(read == [a['title_es'] + '.'] + [x['es'] for x in sents], '朗读文字＝标题＋正文（逐句一致）')

print('\n'.join(notes + errs))
print('全部通过' if not errs else f'{len(errs)} 项不通过')
sys.exit(1 if errs else 0)
