"""生成模拟卷听力音频（按高考新课标卷的播放方式）：

    python make_listening.py 工具包目录 试卷.md 输出目录

- 台词直接读试卷的「听力原文」一节（**Texto N** 下的「男：」「女：」行），改了录音稿重跑即可。
- 男声：工具包推荐音色 qwen3_M1F5_25（Qwen3-TTS 克隆，原速）。
- 女声：先用 Supertonic 3 女声 F1 合成一段参考录音（与男声参考同一句话），再用 Qwen3-TTS 克隆它
  （工具包男声也是这么做的：克隆合成声音，比直接用 Supertonic 自然）。
- 第一节（Texto 1–5）：每段只播一遍，之后留 10 秒。第二节（Texto 6–9）：先留读题时间（每题 5 秒），播两遍，
  再留作答时间（每题 5 秒）。每段前有提示音和西语段号（男声）。全部结束不再加 2 分钟转涂时间。
- 个别句子读错（语音识别核对出来的）可以换随机种子重新合成：asr_retry.py 把挑中的种子写进 输出目录/seed_overrides.json，这里照着用。
- 原始合成走工具包的合成缓存；处理链同工具包：裁剪 → K 加权电平 → 淡入淡出 → 母带（−16 LUFS、限幅）→ MP3 128k。
输出：听力_全部.mp3（整套）、Texto_1.mp3 … Texto_9.mp3（每段只播一遍，供练习）、听力_时间轴.json。
"""
import json
import re
import sys
from pathlib import Path

import numpy as np

KIT, PAPER, OUT = (Path(p).resolve() for p in sys.argv[1:4])   # 绝对路径：参考录音的相对路径会按工具包根目录解析
sys.path.insert(0, str(KIT / '西班牙语' / 'tools'))
import c4  # noqa: E402

MA = c4.load('es_make_audio', '西班牙语/tools/make_audio.py')
G, C4A, buzz = MA.G, MA.C4A, MA.buzz
SR = G.SR
NUM = ['', 'uno', 'dos', 'tres', 'cuatro', 'cinco', 'seis', 'siete', 'ocho', 'nueve']
QUESTIONS = {1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 3, 7: 4, 8: 4, 9: 4}
TURN_GAP, SENT_GAP, AFTER_LABEL, BETWEEN_PLAYS = 0.45, 0.3, 0.8, 2.0


def pieces(s):
    """一句台词按句号、问号、感叹号切成几段分别合成（长段一口气合成容易漏读、吞音；asr_check.py 也用它）。"""
    return [p for p in re.split(r'(?<=[.!?…])\s+', s.strip()) if p]


def parse(md):
    """读「## 听力原文」一节：返回 {段号: [(说话人, 台词), …]}。"""
    sec = md.split('## 听力原文', 1)[1].split('\n## ', 1)[0]
    texts, cur = {}, None
    for line in sec.splitlines():
        m = re.match(r'\*\*Texto (\d+)\*\*', line.strip())
        if m:
            cur = int(m.group(1))
            texts[cur] = []
            continue
        m = re.match(r'^(?:- )?([男女])：(.+)$', line.strip())
        if m and cur:
            texts[cur].append(('M' if m.group(1) == '男' else 'F', m.group(2).strip()))
    if sorted(texts) != list(range(1, 10)) or not all(texts.values()):
        raise SystemExit(f'听力原文解析不完整：{ {k: len(v) for k, v in texts.items()} }')
    return texts


def female_ref(male_cfg):
    """Supertonic 3 F1 合成女声参考录音（去帧频梳状线），写到 OUT/ref_female_F1.wav。"""
    import soundfile as sf
    path = OUT / 'ref_female_F1.wav'
    if not path.exists():
        cfg = {'engine': 'worker', 'python': 'self', 'script': 'sherpa.py', 'kind': 'supertonic',
               'model_dir': '西班牙语/models/supertonic3', 'sid': 0, 'lang': 'es', 'num_steps': 32, 'speed': 1.0}
        (a, sr), = MA.Worker(cfg).synth_all([male_cfg['ref_text']])
        a = buzz.deline(a, sr, buzz.load_comb('supertonic3_comb.json'))
        a = G.trim(MA.to_sr(a, sr))
        sf.write(str(path), a / max(1e-6, np.abs(a).max()) * 0.7, SR, subtype='FLOAT')
    return path


def engines():
    """男、女声的 Worker（{'M': …, 'F': …}）；.src 留着原始设置，换种子时用。asr_check.py、asr_retry.py 也用它。"""
    male = dict(MA.VOICES['qwen3_M1F5_25'])
    female = dict(male, ref_audio=str(female_ref(male)),
                  label='Qwen3-TTS 1.7B 克隆 Supertonic 3 F1 女声（模拟卷听力用）')
    MA.chain(male)                                       # 电平、压缩用工具包的西语处理链
    out = {}
    for spk, cfg in (('M', male), ('F', female)):
        w = MA.Worker(cfg)
        w.src = cfg
        out[spk] = w
    return out


def worker(engines, spk, seed):
    """换了种子的 Worker（seed 为 None 就是默认的）。"""
    return engines[spk] if seed is None else MA.Worker(dict(engines[spk].src, seed=seed))


def seed_overrides():
    """OUT/seed_overrides.json：{句子: 种子}。语音识别发现某句读得不准时，换种子重新合成、核对通过后记在这里。"""
    f = OUT / 'seed_overrides.json'
    return json.loads(f.read_text('utf-8')) if f.exists() else {}


def group_by_seed(lines):
    """{(说话人, 种子或 None): [句子…]}，同一组一次合成。"""
    ov, groups = seed_overrides(), {}
    for spk, ss in lines.items():
        for s in dict.fromkeys(ss):
            groups.setdefault((spk, ov.get(s)), []).append(s)
    return groups


def cached_file(engines, spk, s):
    """这句合成结果在缓存里的文件（考虑种子覆盖）。"""
    return worker(engines, spk, seed_overrides().get(s))._cached(s)


def tone(sec=0.3, hz=880.0):
    t = np.arange(int(sec * SR)) / SR
    return G.fade((0.08 * np.sin(2 * np.pi * hz * t)).astype(np.float32), ms=20)


def silence(sec):
    return np.zeros(int(round(sec * SR)), np.float32)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    texts = parse(PAPER.read_text('utf-8'))
    eng = engines()

    lines = {'M': [], 'F': []}
    for k, tx in texts.items():
        for spk, s in tx:
            lines[spk] += pieces(s)
    lines['M'] += [f'Texto {NUM[k]}.' for k in texts]
    audio = {}
    for (spk, seed), uniq in group_by_seed(lines).items():
        for s, (a, sr) in zip(uniq, worker(eng, spk, seed).synth_all(uniq)):
            audio[(spk, s)] = G.fade(G.level(G.trim(MA.to_sr(a, sr))))

    def dialogue(k):
        parts = []
        for i, (spk, s) in enumerate(texts[k]):
            for j, p in enumerate(pieces(s)):
                parts += ([silence(SENT_GAP)] if j else []) + [audio[(spk, p)]]
            parts += [silence(TURN_GAP)] if i < len(texts[k]) - 1 else []
        return np.concatenate(parts)

    def label(k):
        return np.concatenate([tone(), silence(0.4), audio[('M', f'Texto {NUM[k]}.')], silence(AFTER_LABEL)])

    import lameenc  # noqa: F401  （G.encode_mp3 用）
    full, marks, t = [silence(1.0)], [], 1.0
    for k in sorted(texts):
        n, d = QUESTIONS[k], dialogue(k)
        seg = [label(k)]
        if k <= 5:
            seg += [d, silence(10.0)]
        else:
            seg += [silence(5.0 * n), d, silence(BETWEEN_PLAYS), d, silence(5.0 * n)]
        seg = np.concatenate(seg)
        marks.append({'texto': k, 'start': round(t, 2), 'duration': round(len(seg) / SR, 2), 'questions': n,
                      'plays': 1 if k <= 5 else 2, 'dialogue_s': round(len(d) / SR, 2)})
        full.append(seg)
        t += len(seg) / SR
        one = G.master(np.concatenate([silence(0.5), d, silence(1.0)]), -16.0)
        (OUT / f'Texto_{k}.mp3').write_bytes(G.encode_mp3(one, kbps=128))
    full.append(silence(2.0))
    mix = G.master(np.concatenate(full), -16.0)
    (OUT / '听力_全部.mp3').write_bytes(G.encode_mp3(mix, kbps=128))
    (OUT / '听力_时间轴.json').write_text(json.dumps({'total_s': round(len(mix) / G.OUT_SR, 2), 'texts': marks},
                                                ensure_ascii=False, indent=1), 'utf-8')
    print(f'听力_全部.mp3：{len(mix) / G.OUT_SR / 60:.1f} 分钟；', ', '.join(f"Texto {m['texto']} {m['dialogue_s']}s" for m in marks))


if __name__ == '__main__':
    main()
