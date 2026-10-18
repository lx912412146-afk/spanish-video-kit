"""长段规则：文章 JSON 里登记的“不停顿逗号”，如果合并后那一段超过 100 个字符，就取消登记、恢复停顿。

    python 西班牙语/tools/long_merge_rule.py 编号…          # 改文章 JSON，并在 _说明 里写明取消了哪几条

理由：0.8 倍速下一口气读 100 个字符以上要 8 秒多；同 es01“较长的并列谓语仍然停顿”。短的名词列举（leche, huevos y pan）照样连读。
分级阅读 50 篇补写完后跑过一次（2026-10-18），17 篇里共取消了 23 条。
"""
import datetime
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import c4  # noqa: E402

MAX = 100
ma = c4.load('es_make_audio', '西班牙语/tools/make_audio.py')


def apply(pid):
    f = HERE.parent / '文章' / f'{pid}.json'
    p = json.loads(f.read_text('utf-8'))
    sents = [s for para in p['paras'] for s in para]
    npc = p.get('no_pause_commas', {})
    dropped = []
    for k in [k for k in npc if not k.startswith('_')]:
        ma.PAUSES.clear()
        ma.PAUSES.update({k: npc[k]})
        segs = ma.segments(sents[int(k) - 1]['es'], int(k))
        keep = []
        for it in npc[k]:
            n = len(next(s for s in segs if it['after'] in s))
            if n <= MAX:
                keep.append(it)
            else:
                dropped.append((k, it['after'], n))
        if keep:
            npc[k] = keep
        else:
            del npc[k]
    if dropped:
        note = '；'.join(f'第 {k} 句「{a}」' for k, a, _ in dropped)
        p['_说明'] = p['_说明'].rstrip('。') + (f'。{datetime.date.today()} 统一规则：不停顿合并后超过 {MAX} 字符的一段'
                                              f'恢复逗号停顿（同 es01“较长的并列谓语仍然停顿”），取消了：{note}。')
        f.write_text(json.dumps(p, ensure_ascii=False, indent=1) + '\n', 'utf-8')
    return dropped


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    for pid in sys.argv[1:]:
        d = apply(pid)
        print(pid, '取消：' + '、'.join(f'第 {k} 句「{a}」（{n} 字符）' for k, a, n in d) if d else '无需改动')


if __name__ == '__main__':
    main()
