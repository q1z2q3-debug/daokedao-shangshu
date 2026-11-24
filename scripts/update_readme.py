#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""按 book/ 实况回填 README 的进度表（正文/图/附录/版本），不写虚数。"""
import json, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
book = os.path.join(ROOT, "book")
V = open(os.path.join(ROOT, "VERSION"), encoding="utf-8").read().strip()
CH = json.load(open(os.path.join(book, "chapters.json"), encoding="utf-8"))["chapters"]
SKIP = set(x.strip() for x in os.environ.get("SKIP_IDS", "").split(",") if x.strip())
have = [c for c in CH if os.path.exists(os.path.join(ROOT, c["file"])) and c["id"] not in SKIP]
figs = len([f for f in os.listdir(os.path.join(ROOT, "assets", "fig")) if f.endswith(".svg")])
fu = len([f for f in os.listdir(book) if f.startswith("附录-") and f.endswith(".md")])
names = "、".join(c["篇题"] for c in have)
p = os.path.join(ROOT, "README.md")
s = open(p, encoding="utf-8").read()
s = re.sub(r"版本：\*\*v[0-9.]+（阶段稿）\*\*", "版本：**v%s（阶段稿）**" % V, s)
s = re.sub(r"\| 正文 \| \d+/58 \|[^\n]*\|", "| 正文 | %d/58 | %s |" % (len(have), names), s)
s = re.sub(r"\| 义理图 \| \d+ 张 \|[^\n]*\|", "| 义理图 | %d 张 | figlib 六式 SVG，纸墨五色，逐张过自检 |" % figs, s)
s = re.sub(r"\| 附录 \| \d+/7 \|[^\n]*\|",
           "| 附录 | %d/7 | 已出篇目对照、古本源流等 %d 件（总索引页已出） |" % (fu, fu), s)
open(p, "w", encoding="utf-8").write(s)
print("README: 正文 %d/58，图 %d，附录 %d/7，v%s" % (len(have), figs, fu, V))
