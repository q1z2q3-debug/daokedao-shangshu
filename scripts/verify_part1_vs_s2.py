# -*- coding: utf-8 -*-
"""用 S2（gushiwen 注疏本）对本书经文分句做子串复核：S2 为传疏混排，
经文分句大多原样嵌入；报告在 S2 中找不到对应子串的分句，供人工复核。"""
import re, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from part1_data import CHAPTERS

CJK = re.compile(r'[\u4e00-\u9fff]')
S2_DIR = "/home/user/Doubao/chats/38451969562668034/daokedao-shangshu/data/底本/_src/gs"
S2_FILE = {
    "01": "yaodian.txt", "02": "shundian.txt", "03": "dayumo.txt",
    "04": "gaoyao.txt", "05": "yiji.txt", "06": "yugong.txt",
    "07": "ganshi.txt", "08": "wuzige.txt", "09": "yinzheng.txt",
}

def core(s):
    return "".join(CJK.findall(s))

for c in CHAPTERS:
    s2 = open(os.path.join(S2_DIR, S2_FILE[c["no"]]), encoding="utf-8").read()
    s2c = core(s2)
    missing = []
    for seg in c["jing"]:
        for clause in re.split(r'[。！？；]', seg):
            cc = core(clause)
            if len(cc) < 4:
                continue
            if cc not in s2c:
                missing.append(cc)
    print(f"== {c['no']} {c['title']}：未在 S2 命中分句 {len(missing)}")
    for m in missing:
        print("   ✗", m)
