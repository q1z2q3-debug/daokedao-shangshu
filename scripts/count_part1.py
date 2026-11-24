# -*- coding: utf-8 -*-
"""实核 part-1 各篇原文数（去标点汉字，CJK \\u4e00-\\u9fff），并生成 part-1.md。"""
import re, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from part1_data import CHAPTERS

CJK = re.compile(r'[\u4e00-\u9fff]')
# 允许出现的标点/符号（中文标点、书名号、引号、顿号等）；其余字符列入复核
ALLOWED_PUNCT = set("，。、；：？！“”‘’《》〈〉‘’·！？—…「」『』（）‘’")

def cjk_count(s):
    return len(CJK.findall(s))

def odd_chars(s):
    out = []
    for ch in s:
        if CJK.match(ch):
            continue
        if ch in ALLOWED_PUNCT or ch.isspace():
            continue
        out.append(ch)
    return out

total = 0
rows = []
for c in CHAPTERS:
    jing = "".join(c["jing"])
    n = cjk_count(jing)
    total += n
    odd = sorted(set(odd_chars(jing)))
    rows.append((c["no"], c["title"], c["jinwen"], c["book"], n, odd))

for no, title, jw, book, n, odd in rows:
    flag = f"  [非常规字符: {''.join(odd)}]" if odd else ""
    print(f"{no} {title} ({jw}/{book}) 原文数={n}{flag}")
print(f"总字数(9篇经文) = {total}")
