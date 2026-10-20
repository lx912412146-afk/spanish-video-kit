"""HSK1 中文阅读：生成逐句精读视频（沿用西班牙语分级阅读的版式和时间轴）。

    python make_video.py <工具包根目录> <文章 JSON> <音频目录> <输出目录> [--stills] [--scale 2]

画面（同西语分级阅读的设计 C：米白底、左侧墨绿竖带、右侧词汇栏、底部进度条）：
- 原文：汉字（思源宋体）上方逐字注拼音（<ruby>，Inter）；重点词汇墨绿加粗，右上角带编号，和右侧词汇栏一一对应
- 原文下面是西语翻译；词汇栏每条：汉字、拼音、西语释义
- 片头：中文标题（带拼音）＋西语标题；页眉「CHINESE READING」
时间轴：片头静音 1.5 秒；读完一句后画面停 0.5 秒再切下一句；结尾静音 2 秒（音频由 make_audio.py 生成）。
3840×2160、30 帧，逐屏编码后无损拼接；生成后核查分辨率、帧率、声画等长、句数和文字与音频一致、停顿、响度。
"""
import argparse
import atexit
import html
import json
import math
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

CSS_ZH = """
.main{width:1080px}
.hz{font-family:'Noto Serif SC',serif;font-size:var(--fs);line-height:1.9;letter-spacing:.04em;text-wrap:balance}
.hz ruby{ruby-position:over;margin:0 .02em}
.hz rt{font-family:'Inter';font-size:calc(var(--fs)*.34);font-weight:500;color:#6b746f;letter-spacing:0;padding:0 .1em .08em}
.hz .w{font-weight:700;color:#1f5c4a;white-space:nowrap}
.hz .nb{white-space:nowrap}
.hz .w rt{color:#1f5c4a;font-weight:600}
.hz sup{font-size:calc(var(--fs)*.3);vertical-align:1.25em}
.tr{text-wrap:balance;font-family:'EB Garamond',serif;font-size:calc(var(--fs)*.56);line-height:1.45;color:#3c4642;margin-top:calc(var(--fs)*.45);padding-left:24px;border-left:4px solid #d7d2c3}
.v{grid-template-columns:calc(var(--vs)*1.3) 1fr}
.v b{font-family:'Noto Serif SC';font-weight:700;font-size:calc(var(--vs)*1.3);color:#1f5c4a}
#list{gap:calc(var(--vs)*.7)}
.v i{font-family:'Inter';font-style:normal;font-weight:500;color:#6b746f;margin-left:12px}
.v.t em{background:#fff;color:#1f5c4a;box-shadow:inset 0 0 0 2px #1f5c4a}
.v span{display:block;margin-left:0;font-family:'EB Garamond';font-size:calc(var(--vs)*1.08);color:#3c4642}
.ttl h1{font-family:'Noto Serif SC';font-size:112px;line-height:1.9;margin:20px 0 6px}
.ttl h1 rt{font-family:'Inter';font-size:38px;font-weight:500;color:#6b746f}
.ttl .sub{font-family:'EB Garamond';font-style:italic;font-size:58px}
"""

FIT = """() => { const r=document.documentElement.style, main=document.querySelector('.main'), box=document.getElementById('box'),
  side=document.getElementById('side'), list=document.getElementById('list');
  let fs=88, vs=40; r.setProperty('--fs', fs+'px'); r.setProperty('--vs', vs+'px');
  while ((box.scrollHeight > main.clientHeight || box.scrollWidth > main.clientWidth) && fs > 40) { fs -= 2; r.setProperty('--fs', fs+'px'); }
  while (side.scrollHeight > side.clientHeight && vs > 16) { vs -= 1; r.setProperty('--vs', vs+'px'); }
  return [fs, vs, box.scrollHeight <= main.clientHeight && side.scrollHeight <= side.clientHeight]; }"""
MIN_FS, MIN_VS = 60, 24


def esc(s):
    return html.escape(s, quote=True)


def ruby_html(pairs):
    return ''.join(f'<ruby>{esc(c)}<rt>{esc(y)}</rt></ruby>' if y else esc(c) for c, y in pairs)


def mark(s):
    """重点词汇在句中的位置（第一次出现），按出现先后编号；对不上就报错。"""
    taken = []
    for w in s['w']:
        if w.get('from_title'):                    # 只在标题里出现的词：列在词汇栏最后，标 T（título），句中不标
            w['sp'] = (len(s['zh']) + 1, 0)
            continue
        a = s['zh'].find(w['surface'])
        if a < 0:
            raise SystemExit(f'词条「{w["h"]}」在句子「{s["zh"]}」里找不到')
        b = a + len(w['surface'])
        if any(a < y and x < b for x, y in taken):
            raise SystemExit(f'词条「{w["h"]}」和别的词条重叠：{s["zh"]}')
        taken.append((a, b))
        w['sp'] = (a, b)
    s['w'].sort(key=lambda w: w['sp'][0])
    if [c for c, _ in s['ruby']] != list(s['zh']):
        raise SystemExit(f'逐字注音和原文对不上：{s["zh"]}')


PUNCT = '，。！？、；：“”‘’'
LONG = 8                                       # 分句超过这么多个汉字时，允许在分句中间换一次行
SUFFIX = '里上下了的吗呢吧们边面过着'                 # 跟在前面的词后面，不放在行首
PREFIX = '一二两三四五六七八九十几每这那个本张把口块件杯瓶双只条位名次在和跟给很不也都是有看吃喝写说听去买做坐到从'   # 要带后面的成分，不放在行尾


def word_ids(s):
    """按原件拼音的分词（空格、标点隔开的拼音词）给每个汉字标词号；标点为 -1。"""
    import unicodedata

    def bare(x):
        x = unicodedata.normalize('NFD', x)
        return ''.join(c for c in x if unicodedata.category(c) != 'Mn').lower().replace("'", '')
    toks = [bare(t) for t in re.findall(r"[^\s,.!?;:，。！？、；：“”\"()（）]+", s['py'])]
    ids, k, buf = [], 0, ''
    for c, y in s['ruby']:
        if not y:
            ids.append(-1)
            continue
        ids.append(k)
        buf += bare(y)
        if k < len(toks) and buf == toks[k]:
            k, buf = k + 1, ''
    return ids


def sentence_html(s):
    ids = word_ids(s)
    units, pos = [], 0                           # (html, 第一个字的位置, 最后一个字的位置)
    for i, w in enumerate([w for w in s['w'] if not w.get('from_title')], 1):
        a, b = w['sp']
        units += [(ruby_html([s['ruby'][j]]), j, j) for j in range(pos, a)]
        units.append((f'<span class="w">{ruby_html(s["ruby"][a:b])}<sup>{i}</sup></span>', a, b - 1))
        pos = b
    units += [(ruby_html([s['ruby'][j]]), j, j) for j in range(pos, len(s['ruby']))]
    # 一般只在分句处换行（每个分句到 ，；：！？。 为止，标点跟着前面的字）；分句太长时在词与词之间换行，词不拆开
    clauses, cur = [], []
    for u in units:
        cur.append(u)
        if s['zh'][u[2]] in '，。！？；：' and u[1] == u[2]:   # 顿号“、”不算分句（列举不在这里断开，太长时按词换行）
            clauses.append(cur)
            cur = []
    if cur:
        clauses.append(cur)
    out = []
    for cl in clauses:
        nhan = sum(1 for u in cl for j in range(u[1], u[2] + 1) if s['ruby'][j][1])
        if nhan <= LONG:
            out.append(''.join(u[0] for u in cl))
            continue
        # 长分句只断一次：在词的边界里挑最好的一处（两行尽量均衡；不在“里、了、的、们”这类后附成分前断，
        # 不在数词、量词、介词和“看、有、在”这类要带宾语的词后面断），词和重点词汇都不拆开
        def width(us):
            return sum((1 if s['ruby'][j][1] else .5) for u in us for j in range(u[1], u[2] + 1)) + sum(.5 for u in us if '<sup>' in u[0])
        best = None
        for i in range(1, len(cl)):
            l, r = cl[i - 1], cl[i]
            if s['zh'][r[1]] in PUNCT or ids[l[2]] == ids[r[1]]:
                continue
            cost = abs(width(cl[:i]) - width(cl[i:]))
            if s['zh'][r[1]] in SUFFIX:
                cost += 10
            if s['zh'][l[2]] in PREFIX:
                cost += 6
            if best is None or cost < best[0]:
                best = (cost, i)
        groups = [cl[:best[1]], cl[best[1]:]] if best else [cl]
        out.append('\u200b'.join(f'<span class="nb">{"".join(u[0] for u in g)}</span>' for g in groups))
    return '\u200b'.join(f'<span class="nb">{c}</span>' if '\u200b' not in c else c for c in out)


def vocab_html(s):
    out, i = [], 0
    for w in s['w']:
        t = w.get('from_title')
        if not t:
            i += 1
        out.append(f'<div class="v{" t" if t else ""}"><em>{"T" if t else i}</em><div><b lang="zh">{esc(w["h"])}</b><i>{esc(w["py"])}</i>'
                   f'<span lang="es">{esc(w["es"])}{" · (título)" if t else ""}</span></div></div>')
    return ''.join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('kit')
    ap.add_argument('article')
    ap.add_argument('audio')
    ap.add_argument('out')
    ap.add_argument('--stills', action='store_true')
    ap.add_argument('--scale', type=int, default=2)
    a = ap.parse_args()
    kit = Path(a.kit)
    sys.path.insert(0, str(kit / '西班牙语' / 'tools'))
    import c4
    C4V = c4.load('cet4_make_video', '四级/tools/make_video.py')
    W, H = C4V.W, C4V.H
    p = json.loads(Path(a.article).read_text('utf-8'))
    sents = p['sents']
    for s in sents:
        mark(s)
        shown = html.unescape(re.sub(r'<[^>]+>', '', re.sub(r'<rt>.*?</rt>|<sup>.*?</sup>', '', sentence_html(s)))).replace('\u200b', '')
        if shown != s['zh']:                   # 画面上的汉字必须和原文一字不差（不重复、不漏字）
            raise SystemExit(f'画面文字和原文不一致：{s["zh"]} → {shown}')
    n = len(sents)
    nchar = sum(1 for s in sents for c in s['zh'] if '一' <= c <= '鿿')
    fonts = (kit / '四级' / 'tools' / 'fonts' / 'fonts.css').as_uri()

    def page(body):
        return (f'<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><link rel="stylesheet" href="{fonts}">'
                f'<style>{C4V.CSS}{CSS_ZH}</style></head><body><div class="band"></div>{body}</body></html>')

    head = f'{esc(p["header"])} · {esc(p["title_zh"])} · <i lang="es" style="font-family:\'EB Garamond\'">{esc(p["title_es"])}</i>'
    slides = [page(f'''<div class="ttl"><div class="tag">CHINESE · READING · LECTURA EN CHINO</div>
      <h1 lang="zh">{ruby_html(p["title_ruby"])}</h1><div class="sub" lang="es">{esc(p["title_es"])}</div>
      <div class="meta"><span>{esc(p["series"])}</span><span>{n} frases · {nchar} 字 · 逐句精读</span></div></div>
      <div class="legend"><span><em style="background:#1f5c4a"></em>生词 · vocabulario</span></div>''')]
    for k, s in enumerate(sents, 1):
        slides.append(page(f'''<div class="top"><b>CHINESE READING</b><span>{head}</span></div>
      <div class="main"><div id="box"><div class="hz" lang="zh">{sentence_html(s)}</div><div class="tr" lang="es">{esc(s["es"])}</div></div></div>
      <div class="side" id="side"><h3>VOCABULARIO · 生词</h3><div id="list">{vocab_html(s)}</div></div>
      <div class="bot"><span>FRASE {k} / {n}</span><div class="bar"><i style="width:{k / n * 100:.2f}%"></i></div><span>逐句精读 · LECTURA FRASE A FRASE</span></div>'''))

    tmp = Path(tempfile.mkdtemp(prefix='zhvideo_'))
    atexit.register(shutil.rmtree, tmp, True)
    from playwright.sync_api import sync_playwright
    sizes = []
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        pg = br.new_page(viewport={'width': W, 'height': H}, device_scale_factor=a.scale)
        for i, h in enumerate(slides):
            f = tmp / f'{i:03d}.html'
            f.write_text(h, 'utf-8')
            pg.goto(f.as_uri())
            pg.evaluate('document.fonts.ready')
            pg.wait_for_timeout(200)
            bad = pg.evaluate("""() => [...document.fonts].filter(f => f.status === 'error').map(f => f.family)""")
            if bad:
                raise SystemExit(f'第 {i} 屏字体加载失败：{bad}')
            if i:
                fs, vs, fits = pg.evaluate(FIT)
                if not fits or fs < MIN_FS or vs < MIN_VS:
                    raise SystemExit(f'第 {i} 句一屏放不下（原文 {fs}px、词汇 {vs}px）')
                sizes.append((fs, vs))
            pg.screenshot(path=str(tmp / f'{i:03d}.png'))
        br.close()
    print(f'  原文字号 {min(x[0] for x in sizes)}–{max(x[0] for x in sizes)}px，词汇栏 {min(x[1] for x in sizes)}–{max(x[1] for x in sizes)}px')
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    if a.stills:
        for f in sorted(tmp.glob('*.png')):
            shutil.copy(f, out / f.name)
        print('截图已保存到', out)
        return

    T = json.loads((Path(a.audio) / f'{p["id"]}_timings.json').read_text('utf-8'))
    times = T['sentences']
    if len(times) != n or any(t['text'] != s['zh'] for t, s in zip(times, sents)):
        raise SystemExit('音频的句子和文章对不上，请重新生成音频')
    starts, ends = [x['start'] for x in times], [x['end'] for x in times]
    TAIL, HOLD, GAP, FPS = 2.0, 0.5, 0.8, 30
    bad = [i + 2 for i in range(n - 1) if abs(starts[i + 1] - ends[i] - GAP) > 0.01]
    if bad:
        raise SystemExit(f'第 {bad} 句之前的停顿不是 {GAP} 秒')
    total = max(T['duration'], ends[-1] + TAIL)
    cuts = [0.0, starts[0]] + [ends[i - 1] + HOLD for i in range(1, n)] + [total]
    frames = [round(c * FPS) for c in cuts[:-1]] + [math.ceil(cuts[-1] * FPS)]
    lst = []
    for i in range(len(slides)):
        segf = tmp / f'seg{i:03d}.mp4'
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-loop', '1', '-framerate', str(FPS), '-i', str(tmp / f'{i:03d}.png'),
                        '-frames:v', str(frames[i + 1] - frames[i]), '-vf', 'format=yuv420p', '-c:v', 'libx264', '-preset', 'slow',
                        '-crf', '12', '-tune', 'stillimage', '-pix_fmt', 'yuv420p', '-g', str(FPS * 10), str(segf)], check=True)
        lst.append(f"file '{segf}'")
    (tmp / 'list.txt').write_text('\n'.join(lst))
    total = frames[-1] / FPS
    t = f'{p["title_zh"]} {p["title_es"]}'.translate(str.maketrans({':': '：', '?': '？', '/': '／'}))   # Windows 文件名不能有 : ? /
    name = f'HSK1中文阅读 第{p["no"]:02d}篇 {t}.mp4'
    silent = tmp / 'video.mp4'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', str(tmp / 'list.txt'), '-c', 'copy', str(silent)], check=True)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', str(silent), '-i', str(Path(a.audio) / T['file']),
                    '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-af', f'apad=whole_dur={total:.3f}', '-t', f'{total:.3f}',
                    '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', str(out / name)], check=True)

    # 成品核查
    pr = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(out / name)],
                                   capture_output=True, text=True, check=True).stdout)
    v = next(x for x in pr['streams'] if x['codec_type'] == 'video')
    au = next(x for x in pr['streams'] if x['codec_type'] == 'audio')
    vd, ad = float(v['duration']), float(au['duration'])
    lo = T['loudness']
    res = [
        ('分辨率 3840×2160', (v['width'], v['height']) == (W * a.scale, H * a.scale), f"{v['width']}×{v['height']}"),
        ('帧率 30', v['r_frame_rate'] == '30/1', v['r_frame_rate']),
        ('声画等长（差 ≤ 0.05 秒）', abs(vd - ad) <= 0.05, f'视频 {vd:.3f} 秒，音频 {ad:.3f} 秒'),
        ('片头静音 1.5 秒', abs(starts[0] - 1.5) < 0.01, f'{starts[0]:.3f} 秒'),
        ('句间停顿 0.8 秒', not bad, '全部 0.8 秒'),
        ('结尾静音 ≥ 2 秒', vd - ends[-1] >= 1.99, f'{vd - ends[-1]:.2f} 秒'),
        ('朗读文字和画面逐句一致', True, f'{n} 句'),
        ('响度（-16 LUFS，四项）', not T['draft_issues'], f"整体 {lo['integrated_lufs']} LUFS，句间最大偏差 {lo['sentence_max_dev_lu']} LU，短时波动 {lo['short_term_std_lu']} LU"),
    ]
    for nm, ok, d in res:
        print(f"  {'✅' if ok else '❌'} {nm}：{d}")
    (out / (Path(name).stem + '_核查.json')).write_text(json.dumps(
        {'video': name, 'duration': round(vd, 3), 'checks': [{'item': nm, 'ok': ok, 'detail': d} for nm, ok, d in res]},
        ensure_ascii=False, indent=1), 'utf-8')
    if not all(ok for _, ok, _ in res):
        raise SystemExit('核查未通过')
    print(f'已生成并核查通过 {out / name}（{vd:.2f} 秒）')


if __name__ == '__main__':
    main()
