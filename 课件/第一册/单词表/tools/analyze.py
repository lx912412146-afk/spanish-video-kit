"""分析一个动词形式：analyze('levántate', 'levantarse') → ['命令式 tú + te']。对不上任何形式时返回 []。"""
import re

import conj

TENSE = {'pres': '陈述式现在时', 'pret': '简单过去时', 'impf': '过去未完成时', 'subj': '虚拟式现在时'}
PNAME = ['第一人称单数', '第二人称单数', '第三人称单数', '第一人称复数', '第二人称复数', '第三人称复数']
CLITICS = ['me', 'te', 'se', 'nos', 'os', 'lo', 'la', 'los', 'las', 'le', 'les']
_cache = {}


def paradigm(lemma):
    if lemma not in _cache:
        refl = lemma.endswith('se') and lemma[:-2].endswith(('ar', 'er', 'ir', 'ír'))
        inf = lemma[:-2] if refl else lemma
        _cache[lemma] = (conj.base_conj(inf), conj.conjugate(lemma), inf, refl)
    return _cache[lemma]


def split_clitics(w):
    """词尾连写的代词（最多两个）：dímelo → [('dí', 'me lo'), ('díme', 'lo'), ('dímelo', '')]，去掉重音后再比。"""
    out = [(w, [])]
    for c1 in CLITICS:
        if w.endswith(c1) and len(w) > len(c1) + 1:
            a = w[:-len(c1)]
            out.append((a, [c1]))
            for c2 in CLITICS:
                if a.endswith(c2) and len(a) > len(c2) + 1:
                    out.append((a[:-len(c2)], [c2, c1]))
    return out


def analyze(form, lemma):
    base, full, inf, refl = paradigm(lemma)
    f = form.lower()
    res = []
    for k in ('pres', 'pret', 'impf'):
        for i, x in enumerate(base[k]):
            if (x == f or (not refl and full[k][i] == f)) and full[k][i] != '—':   # 无人称的 hay、hubo、había 只在 full 里
                res.append(f'{TENSE[k]} {PNAME[i]}')
    if f == inf or f == lemma:
        res.append('不定式')
    if f == base['ger']:
        res.append('副动词')
    if f == base['part'] or (f[:-1] == base['part'][:-1] and f[-1] in 'as' and base['part'].endswith('o')) or f in (base['part'] + 's', base['part'][:-1] + 'as'):
        res.append('过去分词')
    imp = base['imp']
    for p, x in imp.items():
        if x == f and full['imp'][p] != '—':
            res.append(f'命令式 {p}')
    for i, x in enumerate(base['subj']):
        if x == f and not any(f == imp[p] for p in ('usted', 'nosotros', 'ustedes')):
            res.append(f'{TENSE["subj"]} {PNAME[i]}')
    # 连写代词：不定式、副动词、命令式后面
    for stem, cl in (split_clitics(f)[1:] if f != lemma else []):
        s0 = conj.strip_acc(stem)
        tag = ' + ' + ', '.join(cl)
        cands = [('不定式', inf), ('副动词', base['ger'])] + [(f'命令式 {p}', x) for p, x in imp.items()]
        for name, x in cands:
            x0 = conj.strip_acc(x)
            if name == '命令式 nosotros' and cl and cl[0] in ('nos', 'se'):
                x0 = x0[:-1] if x0.endswith('s') else x0
            if name == '命令式 vosotros' and cl and cl[0] == 'os':
                x0 = x0[:-1] if x0.endswith('d') else x0
                if inf == 'ir':
                    x0 = 'id'
            if s0 == x0 and conj.attach(x, ''.join(cl), drop='s' if name == '命令式 nosotros' and cl[0] in ('nos', 'se') else
                                         'd' if name == '命令式 vosotros' and cl[0] == 'os' and inf != 'ir' else '') == f:
                res.append(name + tag)
            elif s0 == x0 and name in ('不定式', '副动词') and conj.strip_acc(f) == conj.strip_acc(x + ''.join(cl)):
                res.append(name + tag + ('（重音不对？）' if conj.attach(x, ''.join(cl)) != f else ''))
    return list(dict.fromkeys(res))


if __name__ == '__main__':
    import sys
    for a in sys.argv[1:]:
        f, l = a.split(':')
        print(f, l, analyze(f, l))
