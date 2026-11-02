"""格式和内容检查：python check_sets.py [套号…]（不写就查全部）。有错误时退出码 1；“提示”只列出来，不算错。
A1—A2 的要求：每套 4 个部分、25 题，第一部分是 7 道各自录音的短对话选择题；题干和选项全用西语（填空、填写的题干除外不查）。"""
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sets as S  # noqa: E402

ES_OK = re.compile(r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9¿¡ ,.;:!?'«»\-–—…()/€%]+$")


def check(st):
    errs, notes = [], []
    E = lambda m: errs.append(f"第 {st['num']} 套：{m}")
    N = lambda m: notes.append(f"第 {st['num']} 套：{m}")
    for key in ('es_title', 'zh_title', 'level', 'content', 'time'):
        if not st.get(key):
            E(f'缺少 {key}')
    if len(st['tips']) < 2:
        E('使用建议至少两条')
    if len(st['parts']) != 4:
        E(f"部分数 {len(st['parts'])}，应为 4")
    qs = S.questions(st)
    if len(qs) != 25:
        E(f'题数 {len(qs)}，应为 25')
    if st['parts'] and (st['parts'][0]['type'] != '选择' or st['parts'][0]['audio']
                        or len([i for i in st['parts'][0]['items'] if i['num'] != '例']) != 7):
        E('第一部分应为 7 道各自录音的短对话选择题')
    if [q['num'] for q in qs] != list(range(1, len(qs) + 1)):
        E(f"题号不连续：{[q['num'] for q in qs]}")
    letters = Counter()
    for p in st['parts']:
        P = f"第{S.CN[p['idx']]}部分"
        if p['audio'] or p['type'] == '配对':
            if p['read'] < 20:
                E(f"{P}：整段录音和配对的部分要写“阅读”，至少 20 秒")
        # 同一段录音（整段录音，或各题单独的一段）里不同角色要用不同的声音；各题单独录音时不同题里的人可以用同一个声音
        for clip in ([p['audio']] if p['audio'] else [it['audio'] for it in p['items']]):
            who = list(dict.fromkeys(ln[0] for ln in clip))
            vs = [p['roles'][w] for w in who if w in p['roles']]
            if len(set(vs)) != len(vs):
                E(f"{P}：同一段录音里两个角色用了同一个声音 {who}")
        if not p['type'] or not p['instr_zh'] or not p['instr_es'] or not p['roles']:
            E(f'{P}：题型、指令、角色不全')
        if not p['instr_es'].endswith('.') or not ES_OK.match(p['instr_es']):
            E(f"{P}：西语指令 {p['instr_es']}")
        items = p['items']
        shared = bool(p['audio'])
        exs = [it for it in items if it['num'] == '例']
        if len(exs) != 1 or items[0]['num'] != '例':
            E(f'{P}：每个部分都要有一个例题（#### 例），放在最前面')
        if not [it for it in items if it['num'] != '例']:
            E(f'{P}：没有题')
        if p['read'] and not shared and p['type'] != '配对':
            E(f'{P}：每题单独录音的部分只有配对题要写“阅读”（先看选项）')
        for it in items:
            Q = f"{P}第 {it['num']} 题"
            if shared and it['audio']:
                E(f'{Q}：整段录音的部分，题目下面不能再有录音')
            if not shared and not it['audio']:
                E(f'{Q}：没有录音')
            if not it['answer']:
                E(f'{Q}：没有答案')
            if it['num'] != '例' and not it['basis']:
                E(f'{Q}：没有依据')
            t = p['type']
            if t == '选择':
                if len(it['options']) != 3 or [o[0] for o in it['options']] != ['A', 'B', 'C']:
                    E(f'{Q}：选择题要有 A、B、C 三个选项')
                if it['answer'] not in [o[0] for o in it['options']]:
                    E(f"{Q}：答案 {it['answer']} 不是选项")
                if it['num'] != '例':
                    letters[it['answer']] += 1
                if len({o[1] for o in it['options']}) != len(it['options']):
                    E(f'{Q}：选项重复')
            elif t == '判断':
                if it['answer'] not in ('V', 'F') or not it['stem']:
                    E(f'{Q}：判断题要有题干，答案是 V 或 F')
            elif t == '配对':
                if it['answer'] not in [o[0] for o in p['options']] or not it['stem']:
                    E(f"{Q}：配对题要有题干，答案 {it['answer']} 要在选项里")
            elif t == '填写':
                if not it['stem']:
                    E(f'{Q}：填写题要有题干')
            elif t == '填空':
                key = '{例}' if it['num'] == '例' else '{%d}' % it['num']
                if not any(key in s for s in p['passage']):
                    E(f'{Q}：短文里没有 {key}')
            for o in it['options']:
                if re.search(r'[一-鿿]', o[1]):
                    E(f'{Q}：选项要用西语：{o[1]}')
            if t in ('选择', '判断', '配对') and re.search(r'[一-鿿]', it['stem']):
                E(f"{Q}：题干要用西语：{it['stem']}")
            if t in ('填空', '填写') and it['answer'] and not re.search(r'\d', it['answer']):
                heard = ' '.join(ln[1] for ln in (p['audio'] or it['audio'])).lower()
                if it['answer'].split('（')[0].strip().lower() not in heard:
                    N(f"{Q}：答案“{it['answer']}”在录音原文里找不到原词（数字、拼读的可以忽略）")
            for who, es, zh in it['audio']:
                pass
        if p['type'] == '配对':
            ans = [it['answer'] for it in items]
            if len(set(ans)) != len(ans):
                E(f'{P}：配对答案有重复 {ans}')
            if len(p['options']) < len(items) + 2:
                E(f"{P}：配对选项 {len(p['options'])} 个，至少要比题目（含例题）多 2 个")
            if [o[0] for o in p['options']] != [chr(65 + i) for i in range(len(p['options']))]:
                E(f'{P}：配对选项字母不连续')
        if p['type'] == '判断':
            c = Counter(it['answer'] for it in items if it['num'] != '例')
            if min(c.get('V', 0), c.get('F', 0)) < 2:
                E(f'{P}：对错分布太偏 {dict(c)}')
        if p['type'] == '填空':
            used = set(re.findall(r'\{([^}]+)\}', ' '.join(p['passage'])))
            want = {str(it['num']) for it in items}
            if used != want:
                E(f'{P}：短文里的空 {sorted(used)} 和题目 {sorted(want)} 对不上')
        lines = p['audio'] + [ln for it in items for ln in it['audio']]
        for who, es, zh in lines:
            if not ES_OK.match(es):
                E(f'{P}：西语里有不该有的字符：{es}')
            if not re.search(r'[.!?…]$', es):
                E(f'{P}：西语句末没有标点：{es}')
            if es.count('¿') != es.count('?') or es.count('¡') != es.count('!'):
                N(f'{P}：问号、感叹号不成对（检查是否有意）：{es}')
            if any(re.fullmatch(r'[¡¿]?S[ií][.!?…]+', s) for s in S.sentences(es)) if hasattr(S, 'sentences') else False:
                E(f'{P}：单独的“Sí.”会被识别成字母 C，改成“Sí, claro.”这类说法：{es}')
            if not re.search(r'[一-鿿]', zh):
                E(f'{P}：译文不是中文：{zh}')
            if re.search(r'[一-鿿]', es):
                E(f'{P}：西语里混了汉字：{es}')
        used_roles = {ln[0] for ln in lines}
        if set(p['roles']) - used_roles:
            E(f"{P}：角色 {set(p['roles']) - used_roles} 没有说话")
        if lines and S.NARRATOR in p['roles'].values() and False:
            pass
    if letters:
        tot = sum(letters.values())
        if max(letters.values()) > tot * 0.5 or len(letters) < 3:
            E(f'选择题答案分布太偏：{dict(letters)}')
    return errs, notes


def main():
    want = set(int(x) for x in sys.argv[1:])
    allerr = []
    for f in sorted((S.ROOT / 'sets').glob('[0-9][0-9].md')):
        try:
            st = S.parse(f)
        except S.SetError as e:
            allerr.append(str(e))
            continue
        if want and st['num'] not in want:
            continue
        errs, notes = check(st)
        qs = S.questions(st)
        print(f"第 {st['num']} 套 {st['zh_title']}：{len(st['parts'])} 部分 {len(qs)} 题；"
              + '、'.join(f"{p['type']}{len([i for i in p['items'] if i['num'] != '例'])}" for p in st['parts']))
        for n in notes:
            print('  提示：', n)
        allerr += errs
    for e in allerr:
        print('错误：', e)
    print('检查通过' if not allerr else f'{len(allerr)} 处错误')
    sys.exit(1 if allerr else 0)


if __name__ == '__main__':
    main()
