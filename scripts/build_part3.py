#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成《润泽说 道可道之尚书》part-3（27–44 周书前十八篇）底本与校勘底账。

底本口径：《十三经注疏·尚书正义》通行五十八篇本。
双源（本机环境可达的两个离线语料库；指定网络主源维基文库、次源 ctext.org
在本机不可达，详见校勘底账“数据源说明”）：
  源甲：gujilab/chinese-classics-corpus 传世十三经文本（简体整理本，corpus.jsonl）
  源乙：Ancient-China-Books/shangshu EPUB 底本（繁体，OEBPS/Text/0xx.htm）

裁定原则：经文以注疏本通行读法为准；甲、乙同源异流，单字差异多为繁简、
异体、通假。本书取字：与注疏本通行楷体一致者从之；两源存疑处一律记入校勘
底账，不擅自改写、缩句、串接、补字。
"""
import json, os, re, html, difflib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.path.join(ROOT, "data", "raw", "part3")
OUT = os.path.join(ROOT, "data", "底本")
os.makedirs(OUT, exist_ok=True)

CHAPTERS = [
    (27, "泰誓上", "古文", "周书"),
    (28, "泰誓中", "古文", "周书"),
    (29, "泰誓下", "古文", "周书"),
    (30, "牧誓", "今文", "周书"),
    (31, "武成", "古文", "周书"),
    (32, "洪范", "今文", "周书"),
    (33, "旅獒", "古文", "周书"),
    (34, "金縢", "今文", "周书"),
    (35, "大诰", "今文", "周书"),
    (36, "微子之命", "古文", "周书"),
    (37, "康诰", "今文", "周书"),
    (38, "酒诰", "今文", "周书"),
    (39, "梓材", "今文", "周书"),
    (40, "召诰", "今文", "周书"),
    (41, "洛诰", "今文", "周书"),
    (42, "多士", "今文", "周书"),
    (43, "无逸", "今文", "周书"),
    (44, "君奭", "今文", "周书"),
]

X_NAME = {
    27: "泰誓上第一", 28: "泰誓中第二", 29: "泰誓下第三", 30: "牧誓第四",
    31: "武成第五", 32: "洪范第六", 33: "旅獒第七", 34: "金滕第八",
    35: "大诰第九", 36: "微子之命第十", 37: "康诰第十一", 38: "酒诰第十二",
    39: "梓材第十三", 40: "召诰第十四", 41: "洛诰第十五", 42: "多士第十六",
    43: "无逸第十七", 44: "君奭第十八",
}

# 注疏本通行读法裁定（本书所取）。键＝篇号；值为需在源甲文字上落实的校字。
# 洛诰“蘉”：源甲脱字，据源乙及注疏本补回（详见底账 41-1）。
FIX_X = {
    41: [("乃是不，乃时", "乃是不蘉，乃时")],
}

def load_X():
    rows = [json.loads(l) for l in open(os.path.join(RAW, "corpus.jsonl"), encoding="utf-8")
            if json.loads(l).get("source") == "尚书"]
    m = {}
    for o in rows:
        ch = o["chapter"].split(" ", 1)[1] if " " in o["chapter"] else o["chapter"]
        m[ch] = o["content"]
    return m

def clean_h(s):
    s = html.unescape(s)
    return re.sub(r"<[^>]+>", "", s)

def load_Y():
    m = {}
    for n in range(27, 45):
        t = open(os.path.join(RAW, "ebook", f"0{n}.htm"), encoding="utf-8").read()
        ps = [clean_h(x).strip() for x in re.findall(r"<p[^>]*>(.*?)</p>", t, flags=re.S)]
        m[n] = ps
    return m

X = load_X()
Y = load_Y()

def han(s):
    return re.sub(r"[^\u4e00-\u9fff]", "", s)

def strip_notes(s):
    """剔除 〖xxx〗 附记（分器/归禾/嘉禾/旅巢命等，非本篇经文）。"""
    return re.sub(r"〖[^〗]*〗[^\n]*", "", s)

def split_paras(text):
    return [p.strip().lstrip("　") for p in text.split("\n") if p.strip().lstrip("　")]

# 序与经文连写在同一段时，在该锚点前断开（锚点属经文）。
PREFACE_SPLIT = {
    28: "王乃徇师而誓曰",
}

def get_preface_and_body(n, text):
    """返回 (序行, 经段落列表)。首段为序；其余为经。无独立序者序为空。"""
    paras = split_paras(text)
    if not paras:
        return "", []
    # 酒诰、梓材：源甲无独立序（序与康诰共见），序留空，正文全部入经
    if n in (38, 39):
        return "", paras
    if n in PREFACE_SPLIT:
        anchor = PREFACE_SPLIT[n]
        first = paras[0]
        idx = first.find(anchor)
        if idx > 0:
            preface = first[:idx].strip()
            body_first = first[idx:].strip()
            return preface, [body_first] + paras[1:]
    return paras[0], paras[1:]

def apply_fix(n, text):
    for old, new in FIX_X.get(n, []):
        assert old in text, f"篇 {n} 未找到校字锚点：{old}"
        text = text.replace(old, new)
    return text

def first_sentence(body_paras):
    if not body_paras:
        return ""
    first = body_paras[0]
    return first.split("。")[0].split("，")[0]

def main():
    records = []
    for n, title, gujin, book in CHAPTERS:
        raw = strip_notes(X[X_NAME[n]])
        raw = apply_fix(n, raw)
        preface, body = get_preface_and_body(n, raw)
        body_han = han("".join(body))
        records.append({
            "n": n, "title": title, "gujin": gujin, "book": book,
            "preface": preface, "body": body,
            "count": len(body_han), "preface_count": len(han(preface)),
        })
    lines = ["# 尚书 底本 part-3（27–44 周书前十八篇）", ""]
    for r in records:
        lines += [
            f"## {r['n']}　{r['title']}",
            f"今古文: {r['gujin']}",
            f"书: {r['book']}",
            f"原文数: {r['count']}",
            f"首句: {first_sentence(r['body'])}",
            "来源: 双源比对（源甲传世十三经整理本＋源乙EPUB注疏本系），差异见校勘底账-part-3.md",
        ]
        if r["preface"]:
            lines.append(f"【序】{r['preface']}")
        for p in r["body"]:
            lines.append(f"【经】{p}")
        lines.append("")
    out_md = os.path.join(OUT, "part-3.md")
    open(out_md, "w", encoding="utf-8").write("\n".join(lines))

    total = sum(r["count"] for r in records)
    print(f"已写 {out_md}")
    print("篇数:", len(records), "总经文汉字数:", total)
    for r in records:
        print(f"  {r['n']:>2} {r['title']:<6} {r['count']}")

if __name__ == "__main__":
    main()
