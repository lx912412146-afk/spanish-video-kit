"""“每日一读”批量生产：按选题表顺序，一篇一篇合成朗读（同一时间只跑一个合成进程），
朗读好的篇目在另一条线上排版、出逐句高亮视频、成品核查（和下一篇的合成同时进行）。

    cd <工具包根目录> && python <本文件> <批次目录> <ASR 模型目录> [编号…]      # 不给编号＝全部 50 篇

批次目录里：articles/<id>.json、illust/<id>.svg、选题表.json；输出到 out/<id>/：
  <id>.mp3、<id>_timings.json、page/（静态页＋各句高亮页、layout.json）、<id>.mp4（逐句高亮版）、
  <id>.plan.json、qa.txt（核查报告）。进度写在 <批次目录>/status.json 和 run.log。

- 朗读的文字（标题＋正文＋不停顿逗号）变了才重新合成：输出目录里的 audio_src.txt 记着上次合成用的文字摘要。
- 排版／视频／核查：文章、插图、朗读、工具任何一样变了才重做（post_src.txt 记摘要），核查不过的下次再跑会重做。
- 某篇失败不影响别的篇目；最后列出失败的篇目和原因。插图还没画好的篇目只合成朗读，再跑一次时补出视频。
"""
import hashlib
import json
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

B = Path(sys.argv[1]).resolve()
ASR = sys.argv[2]
TOOLS = Path(__file__).resolve().parent
topics = json.loads((B / '选题表.json').read_text('utf-8'))
order = [t['id'] for t in topics]
ids = sys.argv[3:] or order
LOG = B / 'run.log'
status = {i: {'audio': 'waiting', 'post': 'waiting'} for i in ids}
lock = threading.Lock()


def log(msg):
    line = time.strftime('%H:%M:%S ') + msg
    print(line, flush=True)
    with lock:
        with LOG.open('a', encoding='utf-8') as f:
            f.write(line + '\n')


def save_status():
    with lock:
        (B / 'status.json').write_text(json.dumps(status, ensure_ascii=False, indent=1), 'utf-8')


def sha(*parts):
    h = hashlib.sha256()
    for p in parts:
        h.update(p if isinstance(p, bytes) else str(p).encode('utf-8'))
        h.update(b'\0')
    return h.hexdigest()


def audio_key(a):
    return sha(a['title_es'], json.dumps([[s['es'] for s in p] for p in a['paras']], ensure_ascii=False),
               json.dumps(a.get('no_pause_commas', {}), ensure_ascii=False, sort_keys=True), a.get('voice'),
               (TOOLS / 'make_daily_audio.py').read_bytes())


def run(cmd, logf):
    with open(logf, 'w', encoding='utf-8') as f:
        r = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT, text=True)
    return r.returncode


def tail(f, n=3):
    try:
        return ' / '.join(Path(f).read_text('utf-8').strip().splitlines()[-n:])
    except OSError:
        return ''


def post(i):
    try:
        return post_(i)
    except Exception as e:                                   # 出错只记这一篇，不影响别的
        status[i]['post'] = f'FAIL error: {e!r}'
        save_status()
        log(f'{i} 排版/视频/核查出错：{e!r}')
        return False


def post_(i):
    a_path, svg = B / 'articles' / f'{i}.json', B / 'illust' / f'{i}.svg'
    out = B / 'out' / i
    if not svg.exists():                                     # 插图还没画好：这次只合成朗读，以后再跑一次补上
        status[i]['post'] = 'waiting for illustration'
        save_status()
        log(f'{i} 插图还没有，排版和视频等下次再跑')
        return False
    mp3, tim, mp4 = out / f'{i}.mp3', out / f'{i}_timings.json', out / f'{i}.mp4'
    key = sha(a_path.read_bytes(), svg.read_bytes(), mp3.read_bytes(), tim.read_bytes(),
              *[(TOOLS / t).read_bytes() for t in ('render_page.py', 'make_daily_video.py', 'qa_daily.py')])
    stamp = out / 'post_src.txt'
    if stamp.exists() and stamp.read_text() == key and mp4.exists():
        status[i]['post'] = 'ok (unchanged)'
        save_status()
        return True
    stamp.unlink(missing_ok=True)
    py = sys.executable
    steps = [('render', [py, str(TOOLS / 'render_page.py'), str(a_path), str(svg), str(out / 'page'), str(tim)]),
             ('video', [py, str(TOOLS / 'make_daily_video.py'), str(out / 'page'), str(tim), str(mp3), '-', str(mp4)]),
             ('qa', [py, str(TOOLS / 'qa_daily.py'), str(a_path), str(out), '-', str(mp4), ASR, str(out / 'page')])]
    for name, cmd in steps:
        status[i]['post'] = name
        save_status()
        logf = out / ('qa.txt' if name == 'qa' else f'{name}.log')
        rc = run(cmd, logf)
        if rc:
            status[i]['post'] = f'FAIL {name}: ' + tail(logf)
            save_status()
            log(f'{i} {name} 未通过：{tail(logf)}')
            return False
    stamp.write_text(key)
    status[i]['post'] = 'ok'
    save_status()
    log(f'{i} 视频和核查通过')
    return True


def main():
    save_status()
    log(f'开始：{len(ids)} 篇')
    pool = ThreadPoolExecutor(max_workers=1)
    futs = []
    for i in ids:
        a_path = B / 'articles' / f'{i}.json'
        out = B / 'out' / i
        out.mkdir(parents=True, exist_ok=True)
        a = json.loads(a_path.read_text('utf-8'))
        key = audio_key(a)
        stamp = out / 'audio_src.txt'
        if stamp.exists() and stamp.read_text() == key and (out / f'{i}.mp3').exists():
            status[i]['audio'] = 'ok (unchanged)'
        else:
            stamp.unlink(missing_ok=True)
            status[i]['audio'] = 'running'
            save_status()
            t0 = time.time()
            rc = run([sys.executable, str(TOOLS / 'make_daily_audio.py'), str(a_path), str(out)], out / 'audio.log')
            if rc:
                status[i]['audio'] = 'FAIL: ' + tail(out / 'audio.log')
                status[i]['post'] = 'skipped'
                save_status()
                log(f'{i} 朗读未通过：{tail(out / "audio.log")}')
                continue
            stamp.write_text(key)
            status[i]['audio'] = f'ok ({time.time() - t0:.0f}s)'
            log(f'{i} 朗读完成，用时 {time.time() - t0:.0f} 秒；{tail(out / "audio.log", 1)}')
        save_status()
        futs.append(pool.submit(post, i))
    pool.shutdown(wait=True)
    bad = {i: s for i, s in status.items() if not (s['audio'].startswith('ok') and s['post'].startswith('ok'))}
    log(f'结束：通过 {len(ids) - len(bad)} 篇，未通过 {len(bad)} 篇' + ('：' + '，'.join(bad) if bad else ''))
    save_status()


if __name__ == '__main__':
    main()
