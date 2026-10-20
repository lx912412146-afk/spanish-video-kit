"""从《HSK1 中文阅读教材》Word 原件生成文章 JSON 骨架。

    python prep.py <docx> <输出目录> [篇号…]

每篇：标题（中文、西语）、逐句汉字和拼音（照原件）、重点词汇（汉字、拼音、西语释义，照原件的表格）。
- 逐字注音：把原件那一行拼音按音节对到每个汉字上（用 pypinyin 只判断音节边界，声调、变调、轻声、大小写都照原件）。
  对不上的字报错，不静默跳过。句首大写的普通词改成小写，专有名词（原件在句中也大写的词）保留大写。
- 重点词汇放在第一次出现它的句子里（surface = 句中写法）。
- 西语逐句翻译（es）和补充词条原件里没有，留空，由人工填写后再生成音频和视频。
"""
import json
import os
import re
import sys
import unicodedata
import zipfile
from pathlib import Path

if os.environ.get('PYLIB'):                                  # pypinyin 装在别处时用 PYLIB 指定
    sys.path.insert(0, os.environ['PYLIB'])
from pypinyin import Style, pinyin  # noqa: E402

HAN = re.compile(r'[一-鿿]')


def paras_and_tables(docx):
    """按文档顺序返回块：('p', 样式, 文字) 或 ('t', [[格, 格, 格], …])。"""
    x = zipfile.ZipFile(docx).read('word/document.xml').decode('utf-8')
    body = x[x.index('<w:body>') + 8:x.index('</w:body>')]
    out, pos = [], 0
    for m in re.finditer(r'<w:tbl>.*?</w:tbl>|<w:p[ >].*?</w:p>|<w:p/>', body, flags=re.S):
        blk = m.group(0)
        if blk.startswith('<w:tbl>'):
            rows = []
            for tr in re.findall(r'<w:tr[ >].*?</w:tr>', blk, flags=re.S):
                rows.append([''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', tc)).strip()
                             for tc in re.findall(r'<w:tc>.*?</w:tc>', tr, flags=re.S)])
            out.append(('t', rows))
        else:
            sty = re.search(r'<w:pStyle w:val="([^"]+)"', blk)
            out.append(('p', sty.group(1) if sty else '', ''.join(re.findall(r'<w:t[^>]*>([^<]*)</w:t>', blk)).strip()))
    return out


def articles(docx):
    arts, cur, mode = [], None, None
    for b in paras_and_tables(docx):
        if b[0] == 'p' and b[1].startswith('Heading'):
            m = re.match(r'第(\d+)篇[：:]\s*(.+)', b[2])
            cur = {'no': int(m.group(1)), 'title_zh': m.group(2).strip(), 'title_es': None, 'lines': [], 'vocab': []}
            arts.append(cur)
            mode = 'title'
            continue
        if cur is None:
            continue
        if b[0] == 't':
            rows = [r for r in b[1] if r and r[:3] != ['汉字', '拼音', 'Español']]   # 只去掉表头行（词条本身也可能是「汉字」）
            cur['vocab'] += [{'h': r[0], 'py': r[1], 'es': r[2]} for r in rows if len(r) >= 3]
            continue
        t = b[2]
        if not t:
            continue
        if mode == 'title':
            cur['title_es'] = t
            mode = None
        elif t.startswith('一、'):
            mode = 'text'
        elif t.startswith('二、'):
            mode = 'vocab'
        elif mode == 'text':
            cur['lines'].append(t)
    for a in arts:
        if len(a['lines']) % 2:
            raise SystemExit(f'第 {a["no"]} 篇：课文行数是单数（汉字行和拼音行要成对）')
        a['sents'] = [{'zh': a['lines'][i], 'py': a['lines'][i + 1]} for i in range(0, len(a['lines']), 2)]
        for s in a['sents']:
            if not HAN.search(s['zh']) or HAN.search(s['py']):
                raise SystemExit(f'第 {a["no"]} 篇：汉字行和拼音行没有对齐：{s}')
    return arts


def strip_tone(s):
    s = unicodedata.normalize('NFD', s)
    return ''.join(c for c in s if unicodedata.category(c) != 'Mn').replace('ü', 'v').lower()


def ruby(zh, py, proper=(), keep_case=False):
    """把一句的拼音按音节对到每个汉字上。返回 [[字, 拼音], …]（标点的拼音为空）。"""
    py = unicodedata.normalize('NFC', py)
    letters = [c for c in py if c.isalpha()]
    wid, w, prev = [], 0, True
    for c in py:                                           # 每个字母属于原件拼音里的第几个词（空格、标点分词）
        if c.isalpha():
            if not prev:
                w += 1
            wid.append(w)
            prev = True
        else:
            prev = False
    flat = ''.join(letters)
    base = strip_tone(flat)
    out, i = [], 0
    starts = {0}                                           # 句首（含句中 ！？。 之后、引号和冒号之后）：大写可能只是句首大写
    for m in re.finditer(r'[!?.。！？:：“"「]\s*', py):
        starts.add(len([c for c in py[:m.end()] if c.isalpha()]))
    for ch in zh:
        if not HAN.match(ch):
            out.append((ch, '', False, -1) if keep_case else [ch, ''])
            continue
        cands = sorted({strip_tone(x) for x in pinyin(ch, style=Style.TONE, heteronym=True)[0]} |
                       {strip_tone(x) for x in pinyin(ch, style=Style.NORMAL, heteronym=True)[0]}, key=len, reverse=True)
        hit = next((c for c in cands if base.startswith(c, i)), None)
        if not hit:
            raise SystemExit(f'对不上拼音：「{zh}」的「{ch}」在“{py}”第 {i} 个字母处（候选 {cands}）')
        syl = flat[i:i + len(hit)]
        if keep_case:
            out.append((ch, syl, i in starts, wid[i]))
            i += len(hit)
            continue
        if syl[0].isupper() and ((i in starts and not any(zh.startswith(n, len(out)) for n in proper))
                                 or any(zh[max(0, len(out) - j):].startswith(n) for n in NOT_PROPER for j in range(len(n)))):
            syl = syl[0].lower() + syl[1:]                 # 句首的普通词、原件习惯大写的普通词（汉字 Hànzì）改小写
        out.append([ch, syl])
        i += len(hit)
    if i != len(base):
        raise SystemExit(f'拼音多出来：「{zh}」→“{py}”只用到第 {i}/{len(base)} 个字母')
    return out


NOT_PROPER = {'明天', '汉字'}       # 原件在句中写成大写、但不是专有名词的词（引号里的句首“Míngtiān jiàn!”、原件习惯写 Hànzì）
# 词汇表里的词和课文写法不同：(篇, 词表写法) → 课文里的写法、拼音、西语释义
VOCAB_FIX = {(45, '听懂'): ('听得懂', 'tīng de dǒng', 'poder entender (al escuchar); 听懂 tīng dǒng con 得 en medio')}


def proper_words(arts):
    """原件里在句中（不在句首）也大写的拼音词，记下它对应的汉字（如 安娜 Ānnà、中文 Zhōngwén）。"""
    names = set()
    for a in arts:
        for s in a['sents']:
            words = {}
            for ch, syl, start, w in ruby(s['zh'], s['py'], keep_case=True):
                if syl:
                    words.setdefault(w, []).append((ch, syl, start))
            for w in words.values():
                if w[0][1][0].isupper() and not w[0][2]:
                    names.add(''.join(ch for ch, *_ in w))
    return names - NOT_PROPER


def title_ruby(title, sents, proper):
    """标题没有原件拼音：标题里的词在课文里出现过就用课文的注音，其余用 pypinyin（之后人工核对）。"""
    out, i = [], 0
    while i < len(title):
        ch = title[i]
        if not HAN.match(ch):
            out.append([ch, '']); i += 1; continue
        hit = None
        for L in range(min(4, len(title) - i), 0, -1):          # 先找最长的、在课文里出现过的片段
            frag = title[i:i + L]
            for s in sents:
                k = s['zh'].find(frag)
                if k >= 0:
                    hit = s['ruby'][k:k + L]; break
            if hit:
                break
        if not hit:
            hit = [[ch, pinyin(ch, style=Style.TONE)[0][0]]]
        out += [list(x) for x in hit]
        i += len(hit)
    if out and out[0][1] and out[0][1][0].isupper() and not any(title.startswith(n) for n in proper):
        out[0][1] = out[0][1][0].lower() + out[0][1][1:]
    return out


def main():
    docx, outdir = Path(sys.argv[1]), Path(sys.argv[2])
    pick = {int(x) for x in sys.argv[3:]}
    arts = articles(docx)
    proper = proper_words(arts)
    print(f'共 {len(arts)} 篇；专有名词：{"、".join(sorted(proper))}')
    outdir.mkdir(parents=True, exist_ok=True)
    for a in arts:
        if pick and a['no'] not in pick:
            continue
        sents = []
        for s in a['sents']:
            sents.append({'zh': s['zh'], 'py': s['py'], 'es': '', 'ruby': ruby(s['zh'], s['py'], proper), 'w': []})
        for v in a['vocab']:
            py = v['py'] if any(v['h'].startswith(n) for n in proper) else v['py'][:1].lower() + v['py'][1:]
            if (a['no'], v['h']) in VOCAB_FIX:
                h, py, es = VOCAB_FIX[(a['no'], v['h'])]
                v = dict(v, h=h, es=es)
            k = next((k for k, s in enumerate(sents) if v['h'] in s['zh']), None)
            if k is None and v['h'] in a['title_zh']:            # 只在标题里出现：放在第一句的词汇栏里，注明“标题”
                sents[0]['w'].append({'h': v['h'], 'py': py, 'es': v['es'], 'surface': '', 'from_title': True, 'source': 'doc'})
                continue
            if k is None:
                raise SystemExit(f'第 {a["no"]} 篇：词汇「{v["h"]}」在课文里找不到')
            sents[k]['w'].append({'h': v['h'], 'py': py, 'es': v['es'], 'surface': v['h'], 'source': 'doc'})
        p = {'id': f'hsk1_{a["no"]:02d}', 'no': a['no'], 'title_zh': a['title_zh'], 'title_es': a['title_es'],
             'title_ruby': title_ruby(a['title_zh'], sents, proper),
             'series': f'HSK 1级中文阅读 · 第一册：我的中文生活 · 第{a["no"]:02d}篇', 'header': f'HSK 1 · 第{a["no"]:02d}篇',
             'sents': sents}
        f = outdir / f'{p["id"]}.json'
        f.write_text(json.dumps(p, ensure_ascii=False, indent=1), 'utf-8')
        print('写好', f, f'{len(sents)} 句，词汇 {sum(len(s["w"]) for s in sents)} 条')


if __name__ == '__main__':
    main()
