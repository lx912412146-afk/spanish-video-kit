"""读 sets/NN.md（格式见 编写要求.md），返回一套题的结构；check_sets.py、make_tracks.py 和 export_json.py 共用。"""
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
TYPES = ('选择', '判断', '配对', '填写', '填空')
VOICES = ('男1', '男2', '女1', '女2', '女3')
NARRATOR = '男1'
CN = '零一二三四五六七八九十'
DEFAULT_PAUSE = {'选择': 5, '判断': 5, '配对': 5, '填写': 8, '填空': 10}
OPT = re.compile(r'(?:^|　+)([A-J])\. ')


class SetError(Exception):
    pass


def split_options(s):
    """“A. be　B. de　C. pe” → [('A', 'be'), ('B', 'de'), ('C', 'pe')]（选项之间是全角空格）。"""
    parts = [p for p in re.split(r'　+(?=[A-J]\. )', s.strip()) if p]
    out = []
    for p in parts:
        m = re.match(r'^([A-J])\. (.+)$', p.strip())
        if not m:
            raise SetError(f'选项写法不对：{p}')
        out.append((m.group(1), m.group(2).strip()))
    return out


def parse(path):
    path = Path(path)
    lines = path.read_text('utf-8').replace('\r', '').split('\n')
    st = {'file': path.name, 'num': int(re.match(r'(\d+)', path.stem).group(1)), 'tips': [], 'parts': []}
    part = item = None
    in_audio = False

    def err(k, m):
        raise SetError(f'{path.name}:{k + 1}: {m}')

    for k, raw in enumerate(lines):
        t = raw.strip()
        if not t:
            continue
        if m := re.match(r'^## 第 (\d+) 套　(.+?)　(.+)$', t):
            if int(m.group(1)) != st['num']:
                err(k, '套号和文件名不一致')
            st['es_title'], st['zh_title'] = m.group(2).strip(), m.group(3).strip()
            continue
        if m := re.match(r'^### 第([一二三四])部分　(.+)$', t):
            part = {'idx': CN.index(m.group(1)), 'title': m.group(2).strip(), 'type': '', 'instr_zh': '', 'instr_es': '',
                    'roles': {}, 'pause': None, 'read': 0, 'options': [], 'passage': [], 'audio': [], 'items': []}
            if part['idx'] != len(st['parts']) + 1:
                err(k, '部分顺序不对')
            st['parts'].append(part)
            item, in_audio = None, False
            continue
        if m := re.match(r'^#### (.+)$', t):
            if part is None:
                err(k, '#### 前面没有部分')
            name = m.group(1).strip()
            if name == '录音':
                in_audio, item = True, None
                continue
            in_audio = False
            if name != '例' and not name.isdigit():
                err(k, f'题号写法不对：{name}')
            item = {'num': name if name == '例' else int(name), 'stem': '', 'options': [], 'answer': '', 'basis': '', 'audio': []}
            part['items'].append(item)
            continue
        if t.startswith('> '):
            m = re.match(r'^> ([^:｜]+): (.+?)｜(.+)$', t)
            if not m:
                err(k, f'录音行要写成“> 说话人: 西语｜中文”：{t}')
            who = m.group(1).strip()
            if part is None or who not in part['roles']:
                err(k, f'说话人“{who}”没有写在这一部分的角色里')
            ln = [who, m.group(2).strip(), m.group(3).strip()]
            if in_audio:
                part['audio'].append(ln)
            elif item is not None:
                item['audio'].append(ln)
            else:
                err(k, '录音行不在任何一题下面')
            continue
        if m := re.match(r'^- ([^：]+)：(.*)$', t):
            key, val = m.group(1), m.group(2).strip()
            if part is None:
                if key == '级别':
                    st['level'] = val
                elif key == '内容':
                    st['content'] = val
                elif key == '用时':
                    st['time'] = val
                elif key == '建议':
                    st['tips'].append(val)
                else:
                    err(k, f'套的说明里没有“{key}”这一项')
                continue
            if item is None:
                if key == '题型':
                    if val not in TYPES:
                        err(k, f'题型只能是 {TYPES}')
                    part['type'] = val
                elif key == '指令':
                    if '｜' not in val:
                        err(k, '指令要写成“中文｜西语”')
                    part['instr_zh'], part['instr_es'] = (x.strip() for x in val.split('｜', 1))
                elif key == '角色':
                    for p in re.split(r'[；;]', val):
                        if not p.strip():
                            continue
                        if '＝' not in p:
                            err(k, f'角色写法不对：{p}')
                        n, v = (x.strip() for x in p.split('＝', 1))
                        if v not in VOICES:
                            err(k, f'声音只能是 {VOICES}：{v}')
                        part['roles'][n] = v
                elif key == '停顿':
                    part['pause'] = float(val)
                elif key == '阅读':
                    part['read'] = float(val)
                elif key == '选项':
                    part['options'] += split_options(val)
                elif key == '短文':
                    part['passage'].append(val)
                else:
                    err(k, f'部分的说明里没有“{key}”这一项')
                continue
            if key == '题干':
                item['stem'] = val
            elif key == '选项':
                item['options'] += split_options(val)
            elif key == '答案':
                item['answer'] = val
            elif key == '依据':
                item['basis'] = val
            else:
                err(k, f'题目下面没有“{key}”这一项')
            continue
        err(k, f'看不懂这一行：{t}')
    for p in st['parts']:
        if p['pause'] is None:
            p['pause'] = DEFAULT_PAUSE[p['type']]
    return st


def questions(st):
    """全套的正式题（不含例题）。"""
    return [it for p in st['parts'] for it in p['items'] if it['num'] != '例']


def load_all(d=None):
    d = Path(d or ROOT / 'sets')
    return [parse(f) for f in sorted(d.glob('[0-9][0-9].md'))]


# ---------------------------------------------------------------- 播音员的话（录音和教师版录音原文共用）
def num_es(n):
    from num2words import num2words
    return num2words(n, lang='es')


PART_ES = ['', 'uno', 'dos', 'tres', 'cuatro']
READ_WHAT = {'选择': 'las preguntas', '判断': 'las frases', '配对': 'las opciones', '填空': 'el texto', '填写': 'las preguntas'}
READ_WHAT_ZH = {'选择': '题目', '判断': '句子', '配对': '选项', '填空': '要填的内容', '填写': '题目'}


def intro_lines(p):
    """部分开头播音员读的话：[(西语, 中文)]。"""
    out = [(f"Parte {PART_ES[p['idx']]}. {p['instr_es']}", f"第{CN[p['idx']]}部分。{p['instr_zh']}")]
    if p['read']:
        n = int(p['read'])
        out.append((f"Tienes {num_es(n)} segundos para leer {READ_WHAT[p['type']]}.", f"你有 {n} 秒钟看{READ_WHAT_ZH[p['type']]}。"))
    return out


def item_label(it):
    return ('Ejemplo.', '例题。') if it['num'] == '例' else (f"Número {num_es(it['num'])}.", f"第 {it['num']} 题。")


def outro_line(p):
    return (f"Fin de la parte {PART_ES[p['idx']]}.", f"第{CN[p['idx']]}部分结束。")
