"""第二册分阶段高考模拟卷：查超范围的语法（按卷子的最后一课 N）和可能超纲的生词。

    python scan_range.py 试卷.md [N]

N 不写就从标题“第 1–N 课”读。查的是学生看得到的部分（四部分试题）、听力原文和两篇范文。
动词形式表取自仓库 课件/第一册～第四册/单词表/data/vocab.json 的变位表（另按规则补全将来时、条件式、
虚拟式现在时和过去时、副动词），再按《现代西班牙语》第二册课程大纲（课件/第二册/第二册课程大纲.md）的“起点”判断：

  副动词、否定命令式、acabar de、连词 u     第 3 课起
  将来未完成时                           第 7 课起
  ir + 副动词                            第 8 课起
  虚拟式现在时用在名词性从句（que + 虚拟式）  第 9 课起
  seguir / llevar + 副动词                第 10 课起
  101 以上的基数词                        第 11 课起
  现在完成时                             第 13 课起
  过去完成时                             第 15 课起
  简单条件式、ser + 过去分词的被动语态        第 16 课起
  整个第二册都不用：将来完成时、复合条件式、虚拟式过去时和完成时、虚拟式用在状语从句和形容词从句里

“✗”是肯定超范围（退出码 1）；“?”要人看上下文判断（ser + 分词可能只是形容词，que + 虚拟式可能是形容词从句，
没有 no、que 的虚拟式形式通常是 usted、nosotros 的肯定命令式）。“生词”只列第一册和第二册第 1–N 课课件和单词表里没出现过的词形，供出题人决定加中文注还是换词。
课件是另写的，没有收全课本的词（cada、correr 这类常用词也可能列出来），所以这一栏只作参考，要自己判断。
"""
import json
import os
import re
import sys
import unicodedata
from pathlib import Path

PAPER = Path(sys.argv[1])
MD = PAPER.read_text('utf-8')
if len(sys.argv) > 2:
    N = int(sys.argv[2])
else:
    m = re.search(r'第 1[–-](\d+) 课', MD.splitlines()[0])
    N = int(m.group(1))
ROOT = Path(os.environ['KIT']) if os.environ.get('KIT') else Path(__file__).resolve().parents[3]
VOC = ROOT / '课件'
PRON = {'me', 'te', 'se', 'nos', 'os', 'lo', 'la', 'le', 'los', 'las', 'les'}
WORD = r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+"


def strip(f):
    """'me llamo' → 'llamo'；'no cubras' → 'cubras'；'—' → ''"""
    ws = [w for w in f.replace('—', '').split() if w not in PRON and w != 'no']
    return ws[-1].lower() if ws else ''


def accent(v):
    return {'a': 'á', 'e': 'é', 'i': 'í', 'o': 'ó', 'u': 'ú'}.get(v, v)


TAGS = {}          # 词形 → {标签}
LEMMA_LESSON = {}  # 第二册动词 → 课次
CONJ_KNOWN = set()  # 第一册动词和第二册第 1–N 课动词的变位形式（算学过的词形）


def tag(form, t):
    if form:
        TAGS.setdefault(form.lower(), set()).add(t)


def from_pret3pl(p3):
    """简单过去时第三人称复数 → 虚拟式过去时（-ra、-se 两套）。"""
    if not p3.endswith('ron'):
        return
    st = p3[:-3]
    for end in ('ra', 'ras', 'rais', 'ran', 'se', 'ses', 'seis', 'sen'):
        tag(st + end, 'impsubj')
    for end in ('ramos', 'semos'):
        tag(st[:-1] + accent(st[-1]) + end, 'impsubj')


def from_stems(fut1, cond1, subj1, subj4):
    if fut1 and fut1.endswith('é'):
        s = fut1[:-1]
        for end in ('é', 'ás', 'á', 'emos', 'éis', 'án'):
            tag(s + end, 'fut')
    if cond1 and cond1.endswith('ía'):
        s = cond1[:-2]
        for end in ('ía', 'ías', 'íamos', 'íais', 'ían'):
            tag(s + end, 'cond')
    if subj1 and subj4:
        v = subj1[-1]
        s1, s4 = subj1[:-1], subj4[:-4]
        for f in (subj1, s1 + v + 's', s1 + v + 'n', subj4, s4 + accent(v) + 'is'):
            tag(f, 'subj')


def load():
    for book in ('第二册', '第三册', '第四册'):
        d = json.loads((VOC / book / '单词表' / 'data' / 'vocab.json').read_text('utf-8'))
        if book == '第二册':
            for L in d['lessons']:
                for v in L['verbs']:
                    LEMMA_LESSON[v] = L['lesson']
            for b in d['book1_verbs']:
                g = lambda k: strip(b[k]['f']) if b.get(k) else ''
                from_stems(g('fut'), g('cond'), g('subj1'), g('subj4'))
        for lemma, c in d['conj'].items():
            top, bot = c['top'], c['bottom']
            if book == '第二册' and LEMMA_LESSON.get(lemma, 99) <= N:
                CONJ_KNOWN.update(strip(x['f']) for row in top + bot for x in row)
            for row in top:
                tag(strip(row[3]['f']), 'fut')
                tag(strip(row[4]['f']), 'cond')
            for row in bot:
                tag(strip(row[0]['f']), 'subj')
            from_pret3pl(strip(top[5][1]['f']))
            tag(strip(c['ger']['f']), 'ger')
            tag(strip(c['part']['f']), 'part')
    d1 = json.loads((VOC / '第一册' / '单词表' / 'data' / 'vocab.json').read_text('utf-8'))
    for c in d1['conj'].values():
        CONJ_KNOWN.update(strip(x['f']) for row in c['rows'] for x in row)
        from_pret3pl(strip(c['rows'][5][1]['f']))
        tag(strip(c['ger']['f']), 'ger')
        tag(strip(c['part']['f']), 'part')
    # 课件里没有表的动词：按词形补副动词和分词（-ando、-iendo、-ado、-ido）
    known = set()
    for book, cap in (('第一册', 99), ('第二册', N)):
        for f in json.loads((VOC / book / '单词表' / 'data' / 'forms.json').read_text('utf-8')):
            if f['lesson'] <= cap:
                known.add(f['form'].lower())
        for L in json.loads((VOC / book / '单词表' / 'data' / 'vocab.json').read_text('utf-8'))['lessons']:
            if L['lesson'] <= cap:
                for w in L['words']:
                    known.update(x.lower() for x in w.get('forms', []))
    return known | CONJ_KNOWN


KNOWN = load()
for f in list(TAGS):
    if 'ger' in TAGS[f] or 'part' in TAGS[f] or 'fut' in TAGS[f] or 'cond' in TAGS[f] or 'subj' in TAGS[f] or 'impsubj' in TAGS[f]:
        KNOWN.add(f)
NOT_GER = {'cuando', 'mando', 'ando', 'fernando', 'orlando', 'blando', 'comando', 'bando', 'grande', 'demando'}
NOT_IMPSUBJ = {'fuera', 'para'}   # fuera 也是副词（外面），要看上下文
NOT_SUBJ = {'una', 'unas', 'sobre', 'entre', 'nombre', 'nombres', 'como', 'viaje', 'viajes', 'baile', 'bailes', 'cante', 'pase', 'pases',
            'cambie', 'llame', 'regalo', 'regalos', 'gane', 'cuente', 'desee', 'fin'}
DET = {'un', 'una', 'el', 'la', 'los', 'las', 'mi', 'mis', 'tu', 'tus', 'su', 'sus', 'este', 'esta', 'estos', 'estas', 'ese', 'esa',
       'del', 'al', 'de', 'nuestro', 'nuestra', 'nuestros', 'nuestras', 'vuestro', 'vuestra', 'otro', 'otra', 'cada', 'buen', 'buena', 'primer'}


def is_ger(w):
    return 'ger' in TAGS.get(w, ()) or (re.search(r'(ando|iendo|yendo)$', w) and w not in NOT_GER)


def is_part(w):
    return 'part' in TAGS.get(w, ()) or bool(re.search(r'(ado|ada|ados|adas|ido|ida|idos|idas|ído|ída)$', w))


def scan_parts():
    """[(地方, 文本)]：四部分试题、听力原文、范文；括号里的中文注去掉。"""
    out = []
    for m in re.finditer(r'(?m)^## (.+)$', MD):
        name = m.group(1)
        nxt = re.search(r'(?m)^## ', MD[m.end():])
        body = MD[m.end(): m.end() + nxt.start()] if nxt else MD[m.end():]
        if re.match(r'第[一二三四]部分', name) or name.startswith('听力原文'):
            out.append((name.split('（')[0], body))
        elif name.startswith('参考答案'):
            for q in re.finditer(r'\*\*第[一二]节范文\*\*.*?\n\n((?:>.*\n?)+)', body):
                out.append(('范文', q.group(1)))
    return [(w, re.sub(r'\([^()]*[一-鿿][^()]*\)|（[^（）]*）', ' ', t)) for w, t in out]


HARD, SOFT, NEW = [], [], {}


def ctx(toks, i, n=6):
    return ' '.join(toks[max(0, i - n): i + n + 1])


def need(lesson, what, where, toks, i, soft=False):
    if N < lesson:
        (SOFT if soft else HARD).append((what + f'（第 {lesson} 课起）', where, ctx(toks, i)))


def never(what, where, toks, i, soft=False):
    (SOFT if soft else HARD).append((what + '（第二册不用）', where, ctx(toks, i)))


AUX = {'he': 'perf', 'has': 'perf', 'ha': 'perf', 'hemos': 'perf', 'habéis': 'perf', 'han': 'perf',
       'había': 'plusc', 'habías': 'plusc', 'habíamos': 'plusc', 'habíais': 'plusc', 'habían': 'plusc',
       'habré': 'futperf', 'habrás': 'futperf', 'habrá': 'futperf', 'habremos': 'futperf', 'habréis': 'futperf', 'habrán': 'futperf',
       'habría': 'condperf', 'habrías': 'condperf', 'habríamos': 'condperf', 'habríais': 'condperf', 'habrían': 'condperf',
       'haya': 'subjperf', 'hayas': 'subjperf', 'hayamos': 'subjperf', 'hayáis': 'subjperf', 'hayan': 'subjperf',
       'hubiera': 'impsubjperf', 'hubieras': 'impsubjperf', 'hubiéramos': 'impsubjperf', 'hubieran': 'impsubjperf',
       'haber': 'inf'}
SER = {'es', 'son', 'era', 'eran', 'fue', 'fueron', 'será', 'serán', 'sido', 'ser', 'sea', 'sean', 'eres', 'somos', 'fui'}
ADV_CONJ = ('cuando', 'aunque', 'ojalá', 'quizá', 'quizás', 'hasta que', 'para que', 'antes de que', 'sin que',
            'como si', 'tal vez', 'en cuanto', 'a menos que', 'después de que', 'mientras que', 'donde')
BIG = re.compile(r'^(ciento|doscient|trescient|cuatrocient|quinient|seiscient|setecient|ochocient|novecient|mil|millón|millones)')


def main():
    for where, text in scan_parts():
        for line in text.splitlines():
            toks = [t.lower() for t in re.findall(WORD, line)]
            raw = re.findall(WORD, line)
            for i, w in enumerate(toks):
                tg = TAGS.get(w, set())
                prev = toks[max(0, i - 3): i]
                core = [p for p in prev if p not in PRON]
                if is_ger(w):
                    need(3, f'副动词 {w}', where, toks, i)
                    if prev and prev[-1] in ('voy', 'vas', 'va', 'vamos', 'vais', 'van', 'iba', 'iban', 'fue', 'ir'):
                        need(8, f'ir + 副动词 {w}', where, toks, i)
                    if prev and re.match(r'(sig|segu|llev)', prev[-1]):
                        need(10, f'seguir / llevar + 副动词 {w}', where, toks, i)
                if 'fut' in tg:
                    need(7, f'将来时 {w}', where, toks, i)
                if 'cond' in tg:
                    need(16, f'简单条件式 {w}', where, toks, i)
                if 'impsubj' in tg and w not in NOT_IMPSUBJ:
                    never(f'虚拟式过去时 {w}', where, toks, i)
                elif w == 'fuera':
                    never(f'fuera（虚拟式过去时还是副词“外面”？）', where, toks, i, soft=True)
                if 'subj' in tg and w not in NOT_SUBJ and not (prev and prev[-1] in DET):
                    pj = ' '.join(prev)
                    if core and core[-1] == 'no':
                        need(3, f'否定命令式 / no + 虚拟式 {w}', where, toks, i)
                    elif any(pj.endswith(c) or f' {c} ' in f' {pj} ' for c in ADV_CONJ):
                        never(f'状语从句里的虚拟式 {w}', where, toks, i, soft=True)
                    elif 'que' in prev:
                        if N < 9:
                            need(9, f'que + 虚拟式 {w}', where, toks, i)
                        else:
                            SOFT.append((f'que + 虚拟式 {w}：名词性从句可以，形容词从句不行', where, ctx(toks, i)))
                    elif N < 9 and not (raw[i][0].isupper() or (i and toks[i - 1] in PRON)):
                        SOFT.append((f'虚拟式形式 {w}：是 usted / nosotros 的肯定命令式吗？', where, ctx(toks, i)))
                if w in AUX and i + 1 < len(toks) and is_part(toks[i + 1]):
                    k = AUX[w]
                    if k == 'perf':
                        need(13, f'现在完成时 {w} {toks[i + 1]}', where, toks, i)
                    elif k == 'plusc':
                        need(15, f'过去完成时 {w} {toks[i + 1]}', where, toks, i)
                    elif k == 'inf':
                        need(17, f'haber + 过去分词 {toks[i + 1]}', where, toks, i, soft=True)
                    else:
                        never(f'{k} {w} {toks[i + 1]}', where, toks, i)
                if w in SER and i + 1 < len(toks) and is_part(toks[i + 1]) and N < 16:
                    SOFT.append((f'ser + 过去分词 {w} {toks[i + 1]}：是被动语态（第 16 课起）还是形容词？', where, ctx(toks, i)))
                if w.startswith('acab') and i + 1 < len(toks) and toks[i + 1] == 'de':
                    need(3, 'acabar de', where, toks, i)
                if w == 'u':
                    need(3, '连词 u', where, toks, i)
                if BIG.match(w):
                    need(11, f'101 以上的数词 {w}', where, toks, i)
                if w not in KNOWN and not (raw[i][0].isupper() and i > 0):
                    NEW.setdefault(w, where)
            for num in ([] if '词数' in line else re.findall(r'\b\d{3,}\b', line)):
                if int(num) > 100 and N < 11:
                    SOFT.append((f'数字 {num}（101 以上的数词第 11 课起；年份、价格在听力里要读出来）', where, line.strip()[:80]))
    print(f'按第二册第 1–{N} 课的范围：')
    for title, items in (('✗ 超范围', HARD), ('? 要看上下文', SOFT)):
        print(f'{title}：{len(items)} 处')
        for what, where, c in items:
            print(f'  {what}　［{where}］　…{c}…')
    print(f'生词参考（第一册和第二册第 1–{N} 课课件、单词表里没有的词形；课件词表不全，常用词也会列出来）：{len(NEW)} 个')
    print('  ' + '、'.join(sorted(NEW, key=lambda x: unicodedata.normalize('NFD', x))))
    sys.exit(1 if HARD else 0)


if __name__ == '__main__':
    main()
