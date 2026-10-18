"""语音识别核对有错词的句子，换随机种子重新合成，挑识别得最准的一版：

    python asr_retry.py 工具包目录 试卷.md 音频目录 识别模型目录 [每句最多试几个种子，默认 4]

种子用 2000、3000、4000 …（引擎自己因时长不对重试时用 种子+1、+2，隔开不重叠）。每句一旦识别全对就停；
都没全对就留错词最少的一版（和原来一样少就不换）。挑中的种子写进 音频目录/seed_overrides.json，
之后重跑 make_listening.py 生成音频、asr_check.py 复核。
"""
import importlib.util
import json
import sys
from pathlib import Path

N = int(sys.argv[5]) if len(sys.argv) > 5 else 4
spec = importlib.util.spec_from_file_location('ac', Path(__file__).with_name('asr_check.py'))
ac = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ac)
ml = ac.ml


def main():
    rec, eng = ac.recognizer(), ml.engines()
    texts = ml.parse(ac.PAPER.read_text('utf-8'))
    ov = ml.seed_overrides()
    best = {}                                            # (说话人, 句子) → (错词数, 种子)
    for k, spk, s in ac.sentences(texts):
        f = ml.cached_file(eng, spk, s)
        if not f.exists():
            raise SystemExit(f'Texto {k}：这句还没有合成，先跑 make_listening.py：{s}')
        if (spk, s) not in best:
            err, _ = ac.compare(s, ac.transcribe(rec, f))
            if err:
                best[(spk, s)] = (err, ov.get(s))
    print(f'有错词的句子 {len(best)} 句：', *(f'  [{spk}] {s}（{e} 个）' for (spk, s), (e, _) in best.items()), sep='\n')
    for i in range(1, N + 1):
        seed = 1000 + 1000 * i
        for spk in 'MF':
            todo = [s for (p, s), (e, _) in best.items() if p == spk and e]
            if not todo:
                continue
            w = ml.worker(eng, spk, seed)
            w.synth_all(todo)
            for s in todo:
                hyp = ac.transcribe(rec, w._cached(s))
                err, ops = ac.compare(s, hyp)
                print(f'  种子 {seed} [{spk}] {err} 个错词：{s} → {hyp}', flush=True)
                if err < best[(spk, s)][0]:
                    best[(spk, s)] = (err, seed)
    for (spk, s), (err, seed) in best.items():
        if seed is not None:
            ov[s] = seed
        print(f'{"✓" if not err else "✗"} [{spk}] 种子 {seed or "默认"}，剩 {err} 个错词：{s}')
    (ac.AUDIO / 'seed_overrides.json').write_text(json.dumps(ov, ensure_ascii=False, indent=1), 'utf-8')


if __name__ == '__main__':
    main()
