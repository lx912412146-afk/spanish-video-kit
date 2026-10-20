"""检查 HSK1 文章 JSON：python check_json.py <文章 JSON>…  全部通过打印 ✓，否则列出问题并以 1 退出。

查：每句有西语翻译；逐字注音的字和原文一致；每句至少一个词条；词条的 surface 在句中出现、互不重叠；
词条有 h、py、es、source；拼音只含字母、空格、声调符号和撇号；标题注音和标题一致；非专有名词的拼音不以大写开头。
"""
import json
import re
import sys
import unicodedata

PROPER = ('中国', '中文', '北京', '大卫', '安娜', '小林', '李', '王', '英语')
PY_OK = re.compile(r"^[a-zA-ZāáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜüĀÁǍÀĒÉĚÈĪÍǏÌŌÓǑÒŪÚǓÙ' ]+$")


def check(f):
    p = json.load(open(f, encoding='utf-8'))
    bad = []
    if [c for c, _ in p['title_ruby']] != list(p['title_zh']):
        bad.append('标题注音和标题对不上')
    for c, y in p['title_ruby']:
        if y and not PY_OK.match(y):
            bad.append(f'标题注音「{c}{y}」有非法字符')
    for k, s in enumerate(p['sents'], 1):
        if not s.get('es', '').strip():
            bad.append(f'第 {k} 句没有西语翻译')
        if [c for c, _ in s['ruby']] != list(s['zh']):
            bad.append(f'第 {k} 句逐字注音和原文对不上')
        if not s['w']:
            bad.append(f'第 {k} 句没有词条')
        taken = []
        for w in s['w']:
            for key in ('h', 'py', 'es', 'source'):
                if not str(w.get(key, '')).strip():
                    bad.append(f'第 {k} 句词条「{w.get("h")}」缺 {key}')
            if w.get('source') not in ('doc', 'supplement'):
                bad.append(f'第 {k} 句词条「{w.get("h")}」source 只能是 doc 或 supplement')
            if not PY_OK.match(unicodedata.normalize('NFC', w.get('py', ''))):
                bad.append(f'第 {k} 句词条「{w.get("h")}」拼音「{w.get("py")}」有非法字符')
            if w.get('py', '')[:1].isupper() and not any(w['h'].startswith(n) for n in PROPER):
                bad.append(f'第 {k} 句词条「{w["h"]}」拼音大写开头，但不是专有名词')
            if w.get('from_title'):
                if w['h'] not in p['title_zh']:
                    bad.append(f'标题词条「{w["h"]}」不在标题里')
                continue
            a = s['zh'].find(w.get('surface', '\0'))
            if a < 0:
                bad.append(f'第 {k} 句词条「{w["h"]}」的 surface「{w.get("surface")}」不在句中')
                continue
            b = a + len(w['surface'])
            if any(a < y and x < b for x, y in taken):
                bad.append(f'第 {k} 句词条「{w["h"]}」和别的词条重叠')
            taken.append((a, b))
    return bad


def main():
    fails = 0
    for f in sys.argv[1:]:
        bad = check(f)
        if bad:
            fails += 1
            print(f'✗ {f}')
            for b in bad:
                print('   ', b)
        else:
            print(f'✓ {f}')
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    main()
