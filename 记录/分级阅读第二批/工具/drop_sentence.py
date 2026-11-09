"""删掉文章里的一句（为凑时长加的句子，原速实测太长时用）：python drop_sentence.py <编号> <句号> <新说明文件>
- 删掉第 k 句；no_pause_commas 里 k 以后的句号减 1（第 k 句自己的条目删掉）；_说明 换成新说明文件的内容；段落删空了就报错
- 文件是 json.dump(indent=1) 的格式就整个重写；是“每句一行”的紧凑格式就按行改（保留原来的排版），
  两种做法改完都和“在数据上直接删”的结果逐项比对，必须完全一样"""
import json
import re
import sys
from pathlib import Path
pid, k, note = sys.argv[1], int(sys.argv[2]), Path(sys.argv[3]).read_text('utf-8').strip()
f = Path(f'西班牙语/文章/{pid}.json')
t = f.read_text('utf-8')
p = json.loads(t)
dump = lambda x: json.dumps(x, ensure_ascii=False, indent=1) + '\n'
# 期望结果
want = json.loads(t)
i, loc = 0, None
for a, para in enumerate(want['paras']):
    for b, s in enumerate(para):
        i += 1
        if i == k:
            loc = (a, b)
if loc is None:
    sys.exit(f'没有第 {k} 句')
gone = want['paras'][loc[0]].pop(loc[1])
if not want['paras'][loc[0]]:
    sys.exit('段落删空了')
want['no_pause_commas'] = {(key if int(key) < k else str(int(key) - 1)): v for key, v in want['no_pause_commas'].items() if int(key) != k}
want['_说明'] = note
print(f'删掉第 {k} 句：{gone["es"]}')
if dump(p) == t:
    new = dump(want)
else:
    L = t.split('\n')
    starts = [n for n, line in enumerate(L) if line.startswith('   {"es": ')]
    assert len(starts) == sum(len(q) for q in p['paras']), '找不到每句的开头行'
    s0 = starts[k - 1]
    s1 = s0 + 1
    while not (L[s1].startswith('   {"es": ') or L[s1].startswith('  ]')):
        s1 += 1
    last_in_para = L[s1].startswith('  ]')
    del L[s0:s1]
    if last_in_para:
        assert L[s0 - 1].endswith(']},'), L[s0 - 1][-20:]
        L[s0 - 1] = L[s0 - 1][:-1]
    out = []
    for line in L:
        m = re.match(r'^  "(\d+)": \[', line)
        if m and line.startswith('  "') and int(m.group(1)) > k:
            line = f'  "{int(m.group(1)) - 1}"' + line[len(m.group(0)) - 3:]
        if line.startswith(' "_说明": '):
            line = ' "_说明": ' + json.dumps(note, ensure_ascii=False) + ','
        out.append(line)
    new = '\n'.join(out)
    if p['no_pause_commas'].get(str(k)):
        sys.exit('第 k 句自己有 no_pause_commas 条目，紧凑格式里没有自动删，手工处理')
if json.loads(new) != want:
    sys.exit('改完和期望结果不一致，没有写入')
f.write_text(new, 'utf-8')
print(f'{pid} OK：{sum(len(q) for q in want["paras"])} 句，段落 {[len(q) for q in want["paras"]]}，no_pause_commas {list(want["no_pause_commas"])}')
