"""检查 content/*.json：字数是否在官方范围内、题号是否连续、答案分布、正确选项是否总是最长。

    python tools/check_content.py [content_dir]
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

D = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parents[1] / 'content')
cl, ca, eie, eio = (json.loads((D / f'{p}.json').read_text('utf-8')) for p in ('cl', 'ca', 'eie', 'eio'))
ERR = []


def words(t):
    if isinstance(t, list):
        t = ' '.join(t)
    t = re.sub(r'\[\d+\]', ' ', t)
    return len(re.findall(r"[0-9A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+(?:['’-][A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+)*", t))


def rng(label, n, lo, hi):
    ok = lo <= n <= hi
    print(f"  {'OK ' if ok else 'BAD'} {label}: {n} 词（{lo}–{hi}）")
    if not ok:
        ERR.append(f'{label}: {n} not in {lo}-{hi}')


LET = 'ABCDEFGHIJKLMNO'
keys3 = []        # 三选一题：(题号, 正确字母, 选项)


def mc(q):
    assert len(q['opciones']) == 3, q['n']
    keys3.append((q['prueba'] if 'prueba' in q else '', q['n'], q['clave'], q['opciones']))


print('== 阅读 CL')
nums = []
t1, t2, t3, t4, t5 = cl['tareas']
for tx in t1['textos']:
    rng(f"T1 文本{tx['id']}", words(tx['cuerpo']), 40, 80)
    for q in tx['preguntas']:
        nums.append(q['n']); q['prueba'] = 'CL'; mc(q)
tx = t2['textos'][0]
rng('T2 邮件（正文）', words(tx['cuerpo']), 250, 300)
for q in tx['preguntas']:
    nums.append(q['n']); q['prueba'] = 'CL'; mc(q)
for tx in t3['textos']:
    rng(f"T3 文本{tx['id']}", words(tx['cuerpo']), 100, 120)
c3 = Counter(q['clave'] for q in t3['preguntas'])
print('  T3 答案分布', dict(c3)); nums += [q['n'] for q in t3['preguntas']]
for tx in t4['textos']:
    frag = {f['letra']: f['texto'] for f in tx['fragmentos']}
    full = ' '.join(tx['cuerpo'])
    for g, L in tx['claves'].items():
        assert f'[{g}]' in full, g
        full = full.replace(f'[{g}]', frag[L])
    rng(f"T4 {tx['id']}（含填回的片段）", words(full), 230, 280)
    print(f"      不含片段 {words(tx['cuerpo'])} 词")
    assert len(frag) == 5 and tx['sobra'] not in tx['claves'].values() and len(set(tx['claves'].values())) == 4
    nums += [int(g) for g in tx['claves']]
full = ' '.join(t5['cuerpo'])
foc = Counter()
for q in t5['preguntas']:
    assert f"[{q['n']}]" in full
    full = full.replace(f"[{q['n']}]", q['opciones'][LET.index(q['clave'])])
    foc[q['foco'].split(' ')[0]] += 1
    nums.append(q['n']); q['prueba'] = 'CL'; mc(q)
rng('T5（填好答案）', words(full), 375, 425)
print('  T5 考点', dict(foc), ' B2:', [q['n'] for q in t5['preguntas'] if 'B2' in q['foco']])
if nums != list(range(1, 39)):
    ERR.append(f'CL 题号 {nums}')
print('  题号 1–38 连续' if nums == list(range(1, 39)) else f'  BAD 题号 {nums}')

print('== 听力 CA')
nums = []
T = ca['tareas']
seg = lambda a: ' '.join(s['es'] for s in a['segs'])
rng('T1 对话', words([seg(a) for a in T[0]['audio']]), 150, 170)
assert len(T[0]['banco']) == 15 and T[0]['banco'] == sorted(T[0]['banco'], key=lambda w: w.lower().translate(str.maketrans('áéíóú', 'aeiou')))
for q in T[0]['preguntas']:
    nums.append(q['n'])
    w = T[0]['banco'][LET.index(q['clave'])]
    print(f"    {q['n']} {q['clave']}={w}  {'OK' if w in seg(T[0]['audio'][0]) else 'BAD 录音里没有'}")
rng('T2 五条新闻合计', words([seg(a) for a in T[1]['audio']]), 250, 300)
for a in T[1]['audio']:
    print(f"      {a['label']}: {words(seg(a))}")
for q in T[1]['preguntas']:
    nums.append(q['n']); q['prueba'] = 'CA'; mc(q)
for a in T[2]['audio']:
    rng(f"T3 {a['label']}", words(seg(a)), 50, 70)
k3 = [q['clave'] for q in T[2]['preguntas']]
assert len(T[2]['enunciados']) == 11 and len(set(k3)) == 8 and not set(k3) & set(T[2]['sobran'])
assert sorted(k3 + T[2]['sobran']) == list(LET[:11])
nums += [q['n'] for q in T[2]['preguntas']]
rng('T4 访谈', words([seg(a) for a in T[3]['audio']]), 550, 600)
for q in T[3]['preguntas']:
    nums.append(q['n']); q['prueba'] = 'CA'; mc(q)
rng('T5 讲座 6 段合计', words([seg(a) for a in T[4]['audio']]), 450, 500)
print('      各段', [words(seg(a)) for a in T[4]['audio']])
for q in T[4]['preguntas']:
    nums.append(q['n']); q['prueba'] = 'CA'; mc(q)
rng('T6 讲座', words([seg(a) for a in T[5]['audio']]), 450, 500)
assert len(T[5]['enunciados']) == 12 and len(T[5]['claves']) == 6 and set(T[5]['explicaciones']) == set(LET[:12])
for L in LET[:12]:
    good = T[5]['explicaciones'][L].startswith('正确')
    assert good == (L in T[5]['claves']), L
nums += list(range(33, 39))
print('  题号 1–38 连续' if nums == list(range(1, 39)) else f'  BAD 题号 {nums}')
if nums != list(range(1, 39)):
    ERR.append(f'CA 题号 {nums}')

print('== 写作 EIE')
e1, e2 = eie['tareas']
rng('T1 来信', words(e1['estimulo']['cuerpo']), 30, 50)
rng('T1 范文', words(e1['modelo']['texto']), 100, 150)
for o in e2['opciones']:
    rng(f"T2 Opción {o['n']} 新闻（标题+正文）", words(o['estimulo']['titular'] + ' ' + o['estimulo']['cuerpo']), 50, 70)
    rng(f"T2 Opción {o['n']} 范文", words(o['modelo']['texto']), 250, 300)

print('== 口语 EIO')
o4 = eio['tareas'][3]
for t in o4['temas']:
    rng(f"T4 话题{t['n']} 短文", words(t['texto']), 80, 120)
o5 = eio['tareas'][4]
print(f"  T5 范文 {words(o5['modelo']['texto'])} 词（3–4 分钟口语约 350–500 词）")
print(f"  T2 范文 {words(eio['tareas'][1]['modelo']['texto'])} 词（1–2 分钟）")
for m in eio['tareas'][2]['modelos']:
    print(f"  T3 {m['parte']} 范文 {words(m['texto'])} 词（≤1 分 30 秒）")

print('== 三选一答案分布、长度偏向')
for p in ('CL', 'CA'):
    ks = [k for k in keys3 if k[0] == p]
    c = Counter(k[2] for k in ks)
    longest = sum(1 for _, n, k, ops in ks if len(ops[LET.index(k)]) == max(map(len, ops)))
    shortest = sum(1 for _, n, k, ops in ks if len(ops[LET.index(k)]) == min(map(len, ops)))
    print(f"  {p}: {len(ks)} 题，分布 {dict(sorted(c.items()))}；正确项最长 {longest} 次，最短 {shortest} 次")
    run = 1
    for a, b in zip(ks, ks[1:]):
        run = run + 1 if a[2] == b[2] else 1
        if run >= 3:
            print(f"    注意：{p} 第 {b[1]} 题前连续 {run} 个 {b[2]}")
print()
print('没有问题' if not ERR else '问题：\n  ' + '\n  '.join(ERR))
