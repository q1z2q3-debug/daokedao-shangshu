# -*- coding: utf-8 -*-
"""由 part1_data.py 生成 data/底本/part-1.md。"""
import re, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from part1_data import CHAPTERS

CJK = re.compile(r'[\u4e00-\u9fff]')

FIRST_LINE = {
    "01": "曰若稽古帝尧",
    "02": "曰若稽古帝舜",
    "03": "曰若稽古大禹",
    "04": "曰若稽古",
    "05": "帝曰来禹",
    "06": "禹敷土",
    "07": "大战于甘",
    "08": "太康尸位",
    "09": "惟仲康肇位四海",
}

DIFF_COUNT = {
    "01": 3, "02": 6, "03": 5, "04": 5, "05": 4,
    "06": 7, "07": 0, "08": 3, "09": 3,
}

SHARED_XU_NOTE = {
    "04": "（《皋陶谟》《益稷》与《大禹谟》共序，序文见 03 篇，本篇不重录。）",
    "05": "（《益稷》与《大禹谟》《皋陶谟》共序，序文见 03 篇，本篇不重录。）",
}

def cjk_count(s):
    return len(CJK.findall(s))

lines = []
lines.append("# 润泽说 道可道之尚书 · 底本 part-1（虞书 5 篇＋夏书 4 篇，01–09）")
lines.append("")
lines.append("- 底本口径：《十三经注疏·尚书正义》通行本五十八篇。")
lines.append("- 经文逐字照录，不改写、不缩句、不串接、不补字；标点依底本通行读法。")
lines.append("- 原文数＝去标点后汉字数（CJK 统一表意文字），脚本实核；书序单列【序】，不计入原文数。")
lines.append("- 来源说明与异文取舍：见同目录《校勘底账-part-1.md》。")
lines.append("")

total = 0
for c in CHAPTERS:
    n = cjk_count("".join(c["jing"]))
    total += n
    k = DIFF_COUNT[c["no"]]
    lines.append(f"## {c['no']}　{c['title']}")
    lines.append(f"今古文: {c['jinwen']}")
    lines.append(f"书: {c['book']}")
    lines.append(f"原文数: {n}")
    lines.append(f"首句: {FIRST_LINE[c['no']]}")
    if k:
        lines.append(f"来源: ctext（《武英殿十三经注疏》本《尚书正义》）＋古诗文网《尚书正义》注疏本系双源比对，差异 {k} 条（见校勘底账）；维基文库主源本执行环境不可达，待复校")
    else:
        lines.append("来源: ctext（《武英殿十三经注疏》本《尚书正义》）＋古诗文网《尚书正义》注疏本系双源比对，无实义异文（见校勘底账）；维基文库主源本执行环境不可达，待复校")
    if c["xu"]:
        lines.append(f"【序】{c['xu']}")
    else:
        lines.append(f"【序】{SHARED_XU_NOTE[c['no']]}")
    for seg in c["jing"]:
        lines.append(f"【经】{seg}")
    lines.append("")

lines.append(f"— part-1 九篇经文总字数（去标点汉字）: {total} —")
lines.append("")

out = "/home/user/Doubao/chats/38451969562668034/daokedao-shangshu/data/底本/part-1.md"
with open(out, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("written:", out, "total:", total)
