"""每日一读文章自查：python check_daily.py <文章.json>… [-v]

逐篇检查格式、字符、句数、词数、估算时长、重点词汇、中文标点、逗号停顿登记，全部通过打印 OK；-v 另外打印每句的朗读分段
（| 是停顿 0.28 秒的地方，列举里的逗号应该已经登记成不停顿）。有 ✗ 就要改；“提醒”要自己判断。
选题表（工具目录旁边的 批量/选题表.json；工作目录里叫 batch/）里的编号、级别、音色必须一致；标题可以微调，但会提醒。
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOPICS_FILE = next(f for f in (HERE.parent / '批量' / '选题表.json', HERE.parent / 'batch' / '选题表.json') if f.exists())
TOPICS = {t['id']: t for t in json.loads(TOPICS_FILE.read_text('utf-8'))}
SLOGAN = '每日一读 积少成多'
# 级别：句数、正文词数、每句最多词数、估算每词秒数（含逗号停顿；A1—A2 是 0.8 倍速）
LEVEL = {'A1': ((11, 13), (108, 124), 15, 0.385), 'A2': ((10, 12), (105, 120), 16, 0.40),
         'B1': ((9, 11), (130, 146), 22, 0.34), 'B2': ((8, 10), (116, 132), 24, 0.39), 'C1': ((7, 9), (118, 134), 26, 0.39)}
DUR = (56.0, 64.0)
ES_OK = re.compile(r"[^A-Za-zÁÉÍÓÚÜÑáéíóúüñ¿¡\s.,;:!?]")
WORD = re.compile(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+")
CLAUSE = re.compile(r'(?<=[,;:])\s+(?=\S)')
ZH_BAD = re.compile(r'[A-Za-z0-9,.;:!?()\[\]"\'<>]')
RISKY = {'dependienta': '曾被读成 dependiente', 'prohib': 'prohibir 词尾曾被吞', 'rural': 'zonas rurales 曾被连读',
         'cuánt': 'cuánto/cuántas 后面的名词曾读不出', 'pícnic': '识别会写成 picnic', 'picnic': '外来词'}
VERBOSE = '-v' in sys.argv


def words(s):
    return WORD.findall(s)


def segments(text, free):
    parts = [x for x in CLAUSE.split(text) if x.strip()]
    merged = []
    for x in parts:
        if merged and any(merged[-1].endswith(f['after']) for f in free):
            merged[-1] += ' ' + x
        else:
            merged.append(x)
    return merged


def check(path):
    errs, notes = [], []
    a = json.loads(Path(path).read_text('utf-8'))
    need = ['id', 'level', 'no', 'title_es', 'title_zh', 'slogan', 'voice', '_说明', 'no_pause_commas', 'vocab', 'paras']
    miss = [k for k in need if k not in a]
    if miss:
        return [f'缺字段 {miss}'], notes, None
    t = TOPICS.get(a['id'])
    if not t:
        return [f"编号 {a['id']} 不在选题表里"], notes, None
    if Path(path).stem != a['id']:
        errs.append(f"文件名 {Path(path).name} 和 id {a['id']} 不一致")
    for k in ('level', 'no', 'voice'):
        if a[k] != t[k]:
            errs.append(f'{k} 应为 {t[k]!r}，现在是 {a[k]!r}')
    for k in ('title_es', 'title_zh'):
        if a[k] != t[k]:
            notes.append(f'{k} 和选题表不同：{t[k]} → {a[k]}（主题不能变）')
    if a['slogan'] != SLOGAN:
        errs.append(f'slogan 应为 {SLOGAN}')
    if len(a['title_es']) > 30 or len(a['title_zh']) > 9:
        errs.append('标题太长（西语 ≤ 30 字符，中文 ≤ 9 字）')
    if ES_OK.search(a['title_es']) or a['title_es'][-1] in '.!?':
        errs.append('西语标题里有不允许的字符，或以标点结尾')
    if ZH_BAD.search(a['title_zh']):
        errs.append('中文标题里有半角字符')
    (smin, smax), (wmin, wmax), wsent, rate = LEVEL[a['level']]
    paras = a['paras']
    sents = [s for p in paras for s in p]
    if len(paras) != 2 or min(len(p) for p in paras) < 3:
        errs.append(f'要两段，每段至少 3 句（现在 {[len(p) for p in paras]}）')
    if not smin <= len(sents) <= smax:
        errs.append(f'{a["level"]} 要 {smin}—{smax} 句，现在 {len(sents)} 句')
    nw = sum(len(words(s['es'])) for s in sents)
    if not wmin <= nw <= wmax:
        errs.append(f'{a["level"]} 正文要 {wmin}—{wmax} 词，现在 {nw} 词')
    for k, s in enumerate(sents, 1):
        if set(s) != {'es', 'zh'}:
            errs.append(f'第 {k} 句只能有 es、zh 两个字段')
            continue
        es, zh = s['es'].strip(), s['zh'].strip()
        if es != s['es'] or zh != s['zh'] or '  ' in es:
            errs.append(f'第 {k} 句首尾或中间有多余空格')
        if ES_OK.search(es):
            errs.append(f'第 {k} 句西语有不允许的字符：{ES_OK.findall(es)}')
        if not re.search(r'[.!?]$', es) or re.search(r'[.!?]\s', es):
            errs.append(f'第 {k} 句必须是一句话，以 . ? ! 结尾、中间没有句末标点')
        if es.count('¿') != es.count('?') or es.count('¡') != es.count('!'):
            errs.append(f'第 {k} 句 ¿? 或 ¡! 不成对')
        if not es[0].isupper() and es[0] not in '¿¡':
            errs.append(f'第 {k} 句开头要大写')
        n = len(words(es))
        if n > wsent:
            errs.append(f'第 {k} 句 {n} 词，{a["level"]} 每句最多 {wsent} 词')
        if n < 4:
            errs.append(f'第 {k} 句太短（{n} 词），合成容易出错')
        if ZH_BAD.search(zh):
            errs.append(f'第 {k} 句译文有半角字符或阿拉伯数字：{ZH_BAD.findall(zh)}')
        if not re.search(r'[。？！]$', zh):
            errs.append(f'第 {k} 句译文要以。？！结尾')
        low = es.lower()
        for w, why in RISKY.items():
            if w in low:
                errs.append(f'第 {k} 句有朗读识别的高风险词 {w}（{why}），请换说法')
    # 估算时长：片头 0.5 + 标题 + 1.0 + 正文 + 句间 1.0 ×（句数 − 1）+ 结尾 1.2
    dur = 0.5 + rate * len(words(a['title_es'])) + 0.3 + 1.0 + rate * nw + 1.0 * (len(sents) - 1) + 1.2
    if not DUR[0] <= dur <= DUR[1]:
        errs.append(f'估算时长 {dur:.1f} 秒，要在 {DUR[0]:.0f}—{DUR[1]:.0f} 秒')
    es_chars = sum(len(s['es']) for s in sents)
    zh_chars = sum(len(s['zh']) for s in sents)
    if es_chars > 900 or zh_chars > 330:
        errs.append(f'太长，页面放不下：西语 {es_chars} 字符（≤ 900），译文 {zh_chars} 字（≤ 330）')
    # 重点词汇
    voc = a['vocab']
    full = ' '.join(s['es'] for s in sents)
    if len(voc) != 15:
        errs.append(f'重点词汇要 15 个，现在 {len(voc)} 个')
    heads = [v[0] for v in voc if isinstance(v, list)]
    if len(set(h.lower() for h in heads)) != len(heads):
        errs.append('重点词汇词头有重复')
    last = -1
    for v in voc:
        if not (isinstance(v, list) and len(v) == 3 and all(isinstance(x, str) and x.strip() == x and x for x in v)):
            errs.append(f'词汇条目格式应为 [词头, 释义, 原文写法]：{v}')
            continue
        h, g, sf = v
        if ES_OK.search(h) or len(h) > 18:
            errs.append(f'词头 {h} 有不允许的字符或太长（≤ 18 字符）')
        if not re.fullmatch(r'[一-鿿，、]+', g) or len(g) > 6:
            errs.append(f'释义「{g}」只能是汉字（可用，、），不超过 6 个字')
        pat = r'(?<![A-Za-zÁÉÍÓÚÜÑáéíóúüñ])' + re.escape(sf) + r'(?![A-Za-zÁÉÍÓÚÜÑáéíóúüñ])'
        m = re.search(pat, full)
        if not m:
            errs.append(f'词汇 {h} 的原文写法「{sf}」在正文里找不到（要和原文完全一样，是完整的词）')
            continue
        pos = -1 if re.search(pat, a['title_es'], re.I) else m.start()      # 标题里的词排在最前面
        if pos < last:
            errs.append(f'词汇顺序要按第一次出现的先后（标题里的词在最前）：{h} 应该往前挪')
        last = max(last, pos)
    # 逗号停顿
    npc = a['no_pause_commas']
    if not isinstance(npc, dict):
        errs.append('no_pause_commas 要是对象')
        npc = {}
    for key, lst in npc.items():
        if not key.isdigit() or not 1 <= int(key) <= len(sents):
            errs.append(f'no_pause_commas 的键 {key} 不是正文的句号（从 1 开始）')
            continue
        es = sents[int(key) - 1]['es']
        for f in lst:
            if set(f) != {'after', 'why'} or not f['after'].endswith(','):
                errs.append(f'no_pause_commas 第 {key} 句：每条要有 after（以逗号结尾）和 why')
            elif not any(x.endswith(f['after']) for x in CLAUSE.split(es)):
                errs.append(f'no_pause_commas 第 {key} 句的 after「{f["after"]}」在这句的停顿处找不到')
    segs = [segments(s['es'], npc.get(str(k), [])) for k, s in enumerate(sents, 1)]
    info = f"{len(sents)} 句 {nw} 词，估算 {dur:.1f} 秒，西语 {es_chars} 字符，译文 {zh_chars} 字"
    return errs, notes, (info, segs, sents)


def main():
    files = [x for x in sys.argv[1:] if x != '-v']
    if not files:
        sys.exit(__doc__)
    bad = 0
    for f in files:
        errs, notes, extra = check(f)
        name = Path(f).stem
        if errs:
            bad += 1
            print(f'✗ {name}')
            for e in errs:
                print('   ✗', e)
        else:
            print(f'OK {name}  {extra[0]}')
        for n in notes:
            print('   提醒：', n)
        if VERBOSE and extra:
            for k, sg in enumerate(extra[1], 1):
                print(f'   {k:2d} ' + ' | '.join(sg))
    print('全部通过' if not bad else f'{bad} 篇有问题')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
