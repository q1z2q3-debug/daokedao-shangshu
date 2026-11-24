#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""合成底本、生成 chapters.json 与篇表.md。

用法：
  python3 scripts/make_index.py base      # 合成 data/底本/part-* → 尚书·五十八篇原文.md，生成 chapters.json（gist 暂空）
  python3 scripts/make_index.py refresh   # 从各篇 md 抽取篇旨首句作 gist，并复核原文数
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(ROOT, "data", "底本")
BOOK = os.path.join(ROOT, "book")
VERSION = open(os.path.join(ROOT, "VERSION"), encoding="utf-8").read().strip()
CN = "第%s篇"


def cjk(t):
    return len(re.findall(r"[\u4e00-\u9fff]", t))


def parse_parts():
    parts = sorted(f for f in os.listdir(BASE) if re.match(r"part-[0-9]+\.md", f))
    if not parts:
        sys.exit("缺 data/底本/part-*.md")
    items = []
    for f in parts:
        t = open(os.path.join(BASE, f), encoding="utf-8").read()
        for blk in re.split(r"(?m)^## ", t)[1:]:
            head = blk.split("\n")[0].strip()
            m = re.match(r"([0-9]{2})[\s　]+(.+)", head)
            if not m:
                continue
            no, name = m.group(1), m.group(2).strip()
            body_lines = blk.split("\n")[1:]
            meta = {}
            sutras, xu = [], []
            for ln in body_lines:
                ln = ln.strip()
                if not ln:
                    continue
                mm = re.match(r"(今古文|书|原文数|首句|来源):\s*(.*)", ln)
                if mm:
                    meta[mm.group(1)] = mm.group(2).strip()
                elif ln.startswith("【经】"):
                    sutras.append(ln)
                elif ln.startswith("【序】"):
                    xu.append(ln)
            cnt = sum(cjk(x) for x in sutras)
            items.append(dict(no=no, name=name, meta=meta, sutras=sutras, xu=xu,
                              count=cnt, declared=int(meta.get("原文数", 0) or 0)))
    items.sort(key=lambda x: x["no"])
    return items


def write_base(items):
    out = ["# 《尚书正义》五十八篇原文（底本核字表）", "",
           "> 底本：《十三经注疏·尚书正义》所载通行本五十八篇。",
           "> 双源比对：维基文库《尚書》为主，中国哲学书电子化计划（ctext.org）为次；差异逐条见 `校勘底账.md`。",
           "> 本文件只做三件事：定字、定篇界、定原文数。译文、义理与今用不入此表。", ""]
    tot = 0
    for it in items:
        out += ["## %s　%s" % (it["no"], it["name"]), "",
                "今古文: %s" % it["meta"].get("今古文", ""),
                "书: %s" % it["meta"].get("书", ""),
                "原文数: %d" % it["count"],
                "首句: %s" % it["meta"].get("首句", ""), ""]
        out += it["xu"] + [""] if it["xu"] else []
        out += it["sutras"] + [""]
        tot += it["count"]
    out.insert(5, "## 合计：五十八篇，原文汉字 %d 字" % tot)
    out.insert(6, "")
    open(os.path.join(BASE, "尚书·五十八篇原文.md"), "w", encoding="utf-8").write("\n".join(out))
    return items, tot


def merge_ledger():
    ledger, outs = [], []
    for f in sorted(os.listdir(BASE)):
        if f.startswith("校勘底账-part") and f.endswith(".md"):
            t = open(os.path.join(BASE, f), encoding="utf-8").read().strip()
            outs.append(t)
    head = "# 校勘底账（五十八篇）\n\n> 双源比对逐条：哪字、哪源作何、本书所取。\n"
    open(os.path.join(BASE, "校勘底账.md"), "w", encoding="utf-8").write(head + "\n" + "\n\n".join(outs) + "\n")


def gist_of(no, name):
    p = os.path.join(BOOK, "%s-%s.md" % ("SS" + no, name))
    if not os.path.exists(p):
        return ""
    md = open(p, encoding="utf-8").read()
    m = re.search(r"## 五　篇旨(.+?)(?=\n## )", md, flags=re.S)
    if not m:
        return ""
    body = m.group(1)
    body = re.sub(r"【.*?】", "", body)
    body = re.sub(r"\*\*", "", body)
    lines = [x.strip() for x in body.split("\n") if x.strip()]
    for ln in lines:
        ln = re.sub(r"^-\s*", "", ln)
        ln = ln.split("。")[0]
        if len(ln) >= 8:
            return ln[:46]
    return ""


def build(items):
    chapters = []
    for it in items:
        no, name = it["no"], it["name"]
        cw = "长" if it["count"] >= 400 else "短"
        chapters.append(dict({
            "id": "SS" + no,
            "篇号": INT2CN(no),
            "篇题": name,
            "书": it["meta"].get("书", ""),
            "今古文": it["meta"].get("今古文", ""),
            "归属": "正经" if it["meta"].get("今古文") == "今文" else "存疑别录",
            "首句": it["meta"].get("首句", ""),
            "原文数": it["count"],
            "档": cw,
            "file": "book/SS%s-%s.md" % (no, name),
            "page": "ch/ss%s.html" % no,
            "fig": "fig/ss%s.svg" % no,
            "gist": gist_of(no, name),
        }))
    json.dump({"book": "润泽说 道可道之尚书", "version": VERSION, "chapters": chapters},
              open(os.path.join(BOOK, "chapters.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    return chapters


def INT2CN(no):
    n = int(no)
    d = ["零", "一", "二", "三", "四", "五", "六", "七", "八", "九"]
    if n < 10:
        return "第" + d[n] + "篇"
    if n < 20:
        return "第十" + ("篇" if n == 10 else d[n % 10] + "篇")
    t, u = divmod(n, 10)
    return "第" + d[t] + "十" + ("篇" if u == 0 else d[u] + "篇")


def write_table(chapters):
    out = ["# 篇表", "",
           "> 与 `book/chapters.json` 同源，改一处须同步另一处。", "",
           "| 篇号 | 篇名 | 卷 | 今古文 | 归属 | 原文数 | 档 | 文件 |",
           "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for c in chapters:
        out.append("| %s | %s | %s | %s | %s | %d | %s | %s |"
                   % (c["id"], c["篇题"], c["书"], c["今古文"], c["归属"],
                      c["原文数"], c["档"], c["file"]))
    n_long = sum(1 for c in chapters if c["档"] == "长")
    tot = sum(c["原文数"] for c in chapters)
    out += ["", "共 %d 篇；长篇 %d、短篇 %d；原文合计 %d 字。"
            % (len(chapters), n_long, len(chapters) - n_long, tot)]
    open(os.path.join(BOOK, "篇表.md"), "w", encoding="utf-8").write("\n".join(out) + "\n")


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "base"
    items = parse_parts()
    if len(items) != 58:
        print("[warn] 解析到 %d 篇，应为 58" % len(items))
    bad = [(it["no"], it["count"], it["declared"]) for it in items if it["count"] != it["declared"]]
    if bad:
        print("[warn] 声明原文数与实核不符（以实核为准）：", bad)
    if mode == "base":
        items, tot = write_base(items)
        merge_ledger()
        print("底本合成：%d 篇，原文 %d 字" % (len(items), tot))
    chapters = build(items)
    write_table(chapters)
    print("chapters.json / 篇表.md 已生成：%d 篇；长 %d、短 %d；原文 %d 字"
          % (len(chapters), sum(1 for c in chapters if c["档"] == "长"),
             sum(1 for c in chapters if c["档"] == "短"),
             sum(c["原文数"] for c in chapters)))


if __name__ == "__main__":
    main()
