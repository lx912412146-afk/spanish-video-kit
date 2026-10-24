"""检查《西班牙语 B1 教程》一个单元的三个文件：python check_unit.py 01 [02 …]（复习单元 R1、R2，阶段测试 T1、T2）

查：标记格式；学生用书练习连续编号；@音频 和【音频 …】在录音稿里都有，录音稿里每段都被用到；
@音频 引用的不是“听力”类；教师用书每个练习都有答案；生词表格式和词性；录音稿的类型、角色、声音、台词格式。
"""
import re
import sys
from pathlib import Path

B = Path(__file__).resolve().parent.parent
VOICES = {'男1', '男2', '女1', '女2', '女3', '女4'}
TYPES = {'对话', '课文', '听力', '跟读', '发音'}
POS = {'m.', 'f.', 'm. pl.', 'f. pl.', 'm., f.', 'm. o f.', 'adj.', 'v.', 'v. irr.', 'adv.', 'prep.', 'conj.', 'pron.',
       'interj.', 'loc.', 'art.', 'num.', 'adj., pron.', 'adj. inv.'}
TID = r'(?:\d{1,2}|R[123]|T[123])-(?:Q?\d{1,2})'


def lint(path):
    errs = []
    lines = path.read_text('utf-8').split('\n')
    # 一个列表里题号开头的项和不带题号的项混在一起，排版时整个列表都会带项目符号（A2 测试答案出过这个问题）
    block = []
    for i, l in enumerate(lines + [''], 1):
        if l.startswith('- '):
            block.append((i, l[2:]))
            continue
        if l.startswith('  '):
            continue
        num = [k for k, t in block if re.match(r'^(\d{1,3}\.|例 \d+)[ 　]', t)]
        if num and len(num) < len(block):
            k = next(k for k, t in block if k not in num)
            errs.append(f'{k}: 这个列表里有题号开头的项，也有不带题号的项（说明另起一段写）')
        block = []
    first = next((l for l in lines if l.strip()), '')
    if not first.startswith('## '):
        errs.append('第一行必须是 ## 单元标题')
    if sum(1 for l in lines if l.startswith('## ')) != 1:
        errs.append('只能有一个 ## 标题')
    ncols = None
    for i, l in enumerate(lines, 1):
        t = l.strip()
        if not t:
            ncols = None
            continue
        if t.startswith('#'):
            if not re.match(r'^#{2,4} \S', t):
                errs.append(f'{i}: 标题只能用 ##、###、####，# 后要有空格')
            if re.match(r'^#{2,4} 第.+[单章]元', t):
                errs.append(f'{i}: 标题里不要写“第几单元”')
            ncols = None
            continue
        if t.startswith('|'):
            if re.match(r'^\|[\s:|-]+\|$', t):
                continue
            if not t.endswith('|'):
                errs.append(f'{i}: 表格行要以 | 结尾')
            n = len(t.strip('|').split('|'))
            if ncols is None:
                ncols = n
            elif n != ncols:
                errs.append(f'{i}: 表格这一行 {n} 列，表头 {ncols} 列')
            if n > 5:
                errs.append(f'{i}: 表格超过 5 列')
            continue
        ncols = None
        if t.startswith('>'):
            if not t.startswith('> '):
                errs.append(f'{i}: 例句行 > 后要有空格')
            if '｜' not in t:
                errs.append(f'{i}: 例句行要用全角“｜”分隔西语和中文')
            continue
        if re.match(r'^\d+[.、)] ', t):
            errs.append(f'{i}: 不要用数字列表（题目写成“- 1. …”）')
        if '`' in t or re.search(r'<[a-zA-Z/]', t):
            errs.append(f'{i}: 不要用代码或 HTML')
        if re.search(r'\[[^\]]+\]\(', t):
            errs.append(f'{i}: 不要用链接')
        if t.count('**') % 2:
            errs.append(f'{i}: ** 没有成对')
        if re.search(r'(?<![*\w])_[^_\s][^_]*_(?![\w])', t):
            errs.append(f'{i}: 不要用下划线斜体（填空写五个下划线 _____）')
        if re.search(r'_{2,4}(?!_)', t) and not re.search(r'_{5}', t):
            errs.append(f'{i}: 填空要写五个下划线 _____')
    return errs


def parse_audio(path):
    """返回 ({录音号: {title, type, roles{名字: 声音}, lines[(名字, 西语, 中文)]}}, errs)"""
    tracks, errs, cur = {}, [], None
    for i, l in enumerate(path.read_text('utf-8').split('\n'), 1):
        t = l.strip()
        m = re.match(r'^### (\S+)　(.+)$', t)
        if t.startswith('### '):
            if not m or not re.fullmatch(TID, m.group(1)):
                errs.append(f'{i}: 录音标题要写成“### 3-1　标题”（录音号＋全角空格＋标题）')
                cur = None
                continue
            if m.group(1) in tracks:
                errs.append(f'{i}: 录音号 {m.group(1)} 重复')
            cur = tracks.setdefault(m.group(1), {'title': m.group(2), 'type': None, 'roles': {}, 'lines': [], 'at': i})
            continue
        if cur is None:
            continue
        if t.startswith('- 类型：'):
            cur['type'] = t[5:].strip()
            if cur['type'] not in TYPES:
                errs.append(f'{i}: 类型只能是 {"、".join(sorted(TYPES))}')
        elif t.startswith('- 角色：'):
            for part in re.split(r'[；;]', t[5:]):
                if not part.strip():
                    continue
                if '＝' not in part:
                    errs.append(f'{i}: 角色写成“名字＝声音”，用全角等号')
                    continue
                name, voice = (x.strip() for x in part.split('＝', 1))
                if voice not in VOICES:
                    errs.append(f'{i}: 声音只能是 {"、".join(sorted(VOICES))}，这里是“{voice}”')
                cur['roles'][name] = voice
            vs = list(cur['roles'].values())
            if len(vs) != len(set(vs)):
                errs.append(f'{i}: 一段录音里每个声音只能给一个角色')
        elif t.startswith('>'):
            m2 = re.match(r'^> ([^:：｜]+): (.+?)｜(.*)$', t)
            if not m2:
                errs.append(f'{i}: 台词写成“> 名字: 西语｜中文”（半角冒号加空格）')
                continue
            name, es, zh = m2.group(1).strip(), m2.group(2).strip(), m2.group(3).strip()
            if name not in cur['roles']:
                errs.append(f'{i}: 说话人“{name}”不在这段录音的角色里')
            if re.search(r'[（(\[].*[)）\]]', es):
                errs.append(f'{i}: 台词里不要写括号说明：{es[:30]}')
            if re.search(r'[一-鿿]', es):
                errs.append(f'{i}: 西语台词里有汉字：{es[:30]}')
            cur['lines'].append((name, es, zh))
    for k, tr in tracks.items():
        if not tr['type']:
            errs.append(f'{tr["at"]}: 录音 {k} 没写类型')
        if not tr['roles']:
            errs.append(f'{tr["at"]}: 录音 {k} 没写角色')
        if not tr['lines']:
            errs.append(f'{tr["at"]}: 录音 {k} 没有台词')
    return tracks, errs


def vocab_rows(text):
    rows, errs, inside = [], [], False
    for i, l in enumerate(text.split('\n'), 1):
        t = l.strip()
        if t.replace(' ', '') == '|西语|词性|中文|':
            inside = True
            continue
        if inside and t.startswith('|'):
            if re.match(r'^\|[\s:|-]+\|$', t):
                continue
            c = [x.strip() for x in t.strip('|').split('|')]
            if len(c) != 3 or not all(c):
                errs.append(f'{i}: 生词表每行三格都要填')
                continue
            if c[1] not in POS:
                errs.append(f'{i}: 词性“{c[1]}”不在约定的写法里（{"、".join(sorted(POS))}）')
            if re.search(r'^(el|la|los|las|un|una) ', c[0]) and c[1] not in ('loc.',):
                errs.append(f'{i}: 名词不带冠词：{c[0]}')
            rows.append((i, c))
        else:
            inside = False
    return rows, errs


def check(u):
    sid = u if u[0] in 'RT' else f'{int(u):02d}'
    tid = u if u[0] in 'RT' else str(int(u))
    files = {k: B / k / f'u{sid}.md' for k in ('student', 'audio', 'teacher')}
    out = []
    need = ('audio', 'teacher') if u[0] == 'T' else ('student', 'audio', 'teacher')
    for k in need:
        if not files[k].exists():
            out.append(f'缺文件 {files[k].relative_to(B)}')
    if out:
        return out
    for k in need:
        out += [f'{k}/u{sid}.md {e}' for e in lint(files[k])]
    tracks, errs = parse_audio(files['audio'])
    out += [f'audio/u{sid}.md {e}' for e in errs]
    bad_ids = [k for k in tracks if not k.startswith(tid + '-')]
    if bad_ids:
        out.append(f'audio：录音号要以 {tid}- 开头：{"、".join(bad_ids)}')
    used = set()
    stu = files['student'].read_text('utf-8') if 'student' in need else ''
    tea = files['teacher'].read_text('utf-8')
    for name, text in (('student', stu), ('teacher', tea)):
        for m in re.finditer(r'^@音频 (\S+)\s*$', text, re.M):
            k = m.group(1)
            used.add(k)
            if k not in tracks:
                out.append(f'{name}：@音频 {k} 在录音稿里没有')
            elif tracks[k]['type'] == '听力':
                out.append(f'{name}：@音频 {k} 是听力类，学生用书不印原文，题目里写【音频 {k}】就行')
        for m in re.finditer(r'【音频 ([^】]+)】', text):
            k = m.group(1).strip()
            used.add(k)
            if k not in tracks:
                out.append(f'{name}：【音频 {k}】在录音稿里没有')
    for k in tracks:
        if k not in used:
            out.append(f'audio：录音 {k} 在学生用书和教师用书里都没有用到')
    if 'student' in need:
        nums = [int(x) for x in re.findall(r'^#### 练习 (\d+)　', stu, re.M)]
        if nums != list(range(1, len(nums) + 1)):
            out.append(f'student：练习编号不连续：{nums}')
        if re.search(r'^#### 练习 \d+ ', stu, re.M):
            out.append('student：“练习 N”后面用全角空格')
        ans = {int(x) for x in re.findall(r'^- 练习 (\d+)[：:]', tea, re.M)}
        miss = [n for n in nums if n not in ans]
        if miss:
            out.append(f'teacher：这些练习没有答案：{miss}')
        rows, verrs = vocab_rows(stu)
        out += [f'student {e}' for e in verrs]
        if not rows and u[0] != 'R':                     # 复习单元不学新词，可以没有生词表
            out.append('student：没有找到生词表（表头 | 西语 | 词性 | 中文 |）')
    return out


def main():
    fails = 0
    for u in sys.argv[1:]:
        r = check(u)
        if r:
            fails += 1
            print(f'✗ 单元 {u}')
            for e in r[:60]:
                print('   ', e)
        else:
            print(f'✓ 单元 {u}')
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    main()
