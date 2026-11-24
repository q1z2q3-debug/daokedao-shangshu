# -*- coding: utf-8 -*-
"""4-gram 窗口复核：S2 传疏混排打断经文连续序列，故按 4-gram 命中率定位真缺口。"""
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
    s2c = core(open(os.path.join(S2_DIR, S2_FILE[c["no"]]), encoding="utf-8").read())
    flags = []
    for seg in c["jing"]:
        for clause in re.split(r'[。！？；]', seg):
            cc = core(clause)
            if len(cc) < 6:
                continue
            grams = [cc[i:i+4] for i in range(len(cc)-3)]
            miss = [g for g in grams if g not in s2c]
            if len(miss) / len(grams) > 0.25:
                flags.append((cc, miss[:4]))
    print(f"== {c['no']} {c['title']}：高缺口分句 {len(flags)}")
    for cc, miss in flags:
        print("   ✗", cc, "| 缺:", " ".join(miss))
