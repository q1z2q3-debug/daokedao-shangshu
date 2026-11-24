#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""逐字比对：本书底本片段 vs ctext.org 录文（十三经注疏本系）。

用法：
  python3 scripts/diff_ctext.py data/底本/part-1.md            # 全片段
  python3 scripts/diff_ctext.py data/底本/part-1.md 01         # 只比 SS01
  （ctext 录文放 data/底本/_ctext/ss<号>.txt，纯文本或含「| 篇名: |」行皆可）

输出：每篇的差异块（含上下文），以及汉字数对照。退出码 0=无差异，1=有差异。
"""
import difflib
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(ROOT, "data", "底本")
CT = os.path.join(BASE, "_ctext")

VARIANTS = {"敍": "叙", "敘": "叙", "甯": "宁", "臯": "皋", "啓": "启", "啟": "启",
            "羣": "群", "衆": "众", "祗": "祗", "眎": "视", "眡": "视", "凖": "准",
            "冋": "回", "囘": "回", "迺": "乃", "廼": "乃", "寜": "宁", "寕": "宁",
            "彊": "强", "僣": "僭", "晢": "哲", "晰": "哲", "祇": "祗"}


def norm(t):
    try:
        import zhconv
        t = zhconv.convert(t, "zh-cn")
    except Exception:
        pass
    t = "".join(VARIANTS.get(c, c) for c in t)
    return re.sub(r"[^\u4e00-\u9fff]", "", t)


def read_parts(path):
    out = {}
    t = open(path, encoding="utf-8").read()
    for blk in re.split(r"(?m)^## ", t)[1:]:
        head = blk.split("\n")[0]
        m = re.match(r"([0-9]{2})[\s　]+(.+)", head)
        if not m:
            continue
        lines = [l for l in blk.split("\n")[1:] if l.strip().startswith("【经】")]
        sutra = "".join(re.sub(r"^【经】", "", l) for l in lines)
        out[m.group(1)] = (m.group(2).strip(), norm(sutra))
    return out


def ctx(s, i, k=6):
    return s[max(0, i - k):i + k]


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    parts = read_parts(sys.argv[1])
    only = sys.argv[2] if len(sys.argv) > 2 else None
    total_diff, total_char = 0, 0
    for no, (name, ours) in sorted(parts.items()):
        if only and no != only:
            continue
        f = os.path.join(CT, "ss%s.txt" % no)
        if not os.path.exists(f):
            print("## %s　%s　[缺 ctext 录文 %s]" % (no, name, f))
            continue
        ref = norm(open(f, encoding="utf-8").read())
        sm = difflib.SequenceMatcher(None, ours, ref, autojunk=False)
        blocks = [op for op in sm.get_opcodes() if op[0] != "equal"]
        print("## %s　%s　本书 %d 字 / ctext %d 字 差异块 %d"
              % (no, name, len(ours), len(ref), len(blocks)))
        total_char += len(ours)
        for tag, i1, i2, j1, j2 in blocks:
            total_diff += 1
            print("  [%s] 本书「%s」(%d-%d) → ctext「%s」(%d-%d)  ｜…%s…｜…%s…"
                  % (tag, ours[i1:i2] or "∅", i1, i2, ref[j1:j2] or "∅", j1, j2,
                     ctx(ours, i1), ctx(ref, j1)))
    print("\n合计：%d 篇，汉字 %d，差异块 %d" % (len(parts) if not only else 1, total_char, total_diff))
    return 0 if total_diff == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
