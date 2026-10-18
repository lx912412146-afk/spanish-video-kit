"""检查文章 JSON（生成音频、视频之前先跑）：

    python 西班牙语/tools/check_articles.py a1_01 a1_02 …      # 只报问题
    python 西班牙语/tools/check_articles.py a1_01 -v            # 另外打印每句的朗读分段（| 处停顿）

检查项：make_video.load（每句有生词；surface 在句中恰好出现一次、互不重叠）；surface 是完整的词（前后不是字母）；
title_zh、每句 zh 都有；每句 3–5 个生词；词性只用 POS 里的标签，pos_legend 恰好列出用到的标签；释义 ≤ 14 字；
同一篇里同一个词头不重复；原文没有朗读程序不支持的字符；no_pause_commas 都能匹配（make_audio.segments）。
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import c4  # noqa: E402

POS = {'m.': '阳性名词', 'f.': '阴性名词', 'adj.': '形容词', 'adv.': '副词', 'tr.': '及物动词', 'intr.': '不及物动词',
       'prnl.': '自复动词', 'prep.': '介词', 'conj.': '连词', 'num.': '数词', 'interj.': '感叹词', 'pron.': '代词',
       'loc.': '短语，固定搭配'}
LETTER = re.compile(r'[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]')


def check(pid, verbose=False):
    mv = c4.load('es_make_video', '西班牙语/tools/make_video.py')
    ma = c4.load('es_make_audio', '西班牙语/tools/make_audio.py')
    errs, warns = [], []
    raw = json.loads((HERE.parent / '文章' / f'{pid}.json').read_text('utf-8'))
    try:
        p = mv.load(pid)
    except SystemExit as e:
        return [f'load：{e}'], warns
    if not p.get('title_zh', '').strip():
        errs.append('缺 title_zh')
    sents = [s for para in p['paras'] for s in para]
    used, heads = set(), {}
    ma.PAUSES.clear()
    ma.PAUSES.update({k: v for k, v in ma.PAUSES_ALL.get(pid, {}).items() if not k.startswith('_')})
    ma.PAUSES.update({k: v for k, v in raw.get('no_pause_commas', {}).items() if not k.startswith('_')})
    for k in ma.PAUSES:
        if not k.isdigit() or not 1 <= int(k) <= len(sents):
            errs.append(f'no_pause_commas 的键 {k!r} 不是 1–{len(sents)} 的句号')
    for k, s in enumerate(sents, 1):
        if not s.get('zh', '').strip():
            errs.append(f'第 {k} 句缺 zh')
        if not 3 <= len(s['w']) <= 5:
            errs.append(f'第 {k} 句有 {len(s["w"])} 个生词（要 3–5 个）')
        for w in s['w']:
            a, b = w['sp'][0]
            if (a and LETTER.match(s['es'][a - 1])) or (b < len(s['es']) and LETTER.match(s['es'][b])):
                errs.append(f'第 {k} 句：「{w["surface"]}」不是完整的词（在「{s["es"][max(0, a - 3):b + 3]}」里）')
            if w['pos'] not in POS:
                errs.append(f'第 {k} 句：「{w["h"]}」的词性 {w["pos"]!r} 不在 {sorted(POS)} 里')
            used.add(w['pos'])
            if not w.get('h', '').strip() or not w.get('zh', '').strip():
                errs.append(f'第 {k} 句：「{w.get("surface")}」缺词头或释义')
            if len(w.get('zh', '').replace(' ', '')) > 14:
                errs.append(f'第 {k} 句：「{w["h"]}」的释义超过 14 字：{w["zh"]}')
            key = w['h'].strip().lower()
            if key in heads:
                warns.append(f'词头「{w["h"]}」在第 {heads[key]}、{k} 句都出现')
            heads.setdefault(key, k)
        try:
            segs = ma.segments(s['es'], k)
        except RuntimeError as e:
            errs.append(str(e))
            continue
        if verbose:
            print(f'  {k:2d}. ' + ' | '.join(segs))
    if set(raw.get('pos_legend', {})) != used:
        errs.append(f'pos_legend {sorted(raw.get("pos_legend", {}))} ≠ 用到的词性 {sorted(used)}')
    for t, name in raw.get('pos_legend', {}).items():
        if POS.get(t) != name:
            warns.append(f'pos_legend：{t} 写成「{name}」，标准是「{POS.get(t)}」')
    return errs, warns


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('-')]
    verbose = '-v' in sys.argv
    bad = 0
    for pid in args:
        if verbose:
            print(pid)
        errs, warns = check(pid, verbose)
        for w in warns:
            print(f'{pid} 提醒：{w}')
        for e in errs:
            print(f'{pid} 错误：{e}')
        if not errs:
            print(f'{pid} OK')
        bad += bool(errs)
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
