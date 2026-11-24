#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成单文件自包含阅读版：docs/book-full.html

把 cover、frontis、序、前言、五十八篇、七件附录全部内联成一个 HTML：
CSS 内联、义理图内联 SVG、脚注自建编号、零外链、零脚本。
用法：python3 scripts/build_reader.py
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import build_site as bs  # noqa: E402
import daokedao_book as kit  # noqa: E402

book = os.path.join(ROOT, "book")
docs = os.path.join(ROOT, "docs")
VERSION = bs.VERSION
CH = bs.CH

READER_CSS = bs.CSS + """
.toc a{display:block;padding:3px 0;border:0;color:#25211D;font-size:14px}
.toc a:hover{color:#994433}
.toc .no{color:#994433;font-size:11.5px;letter-spacing:.16em;margin-right:10px}
.toc h3{font-size:13px;letter-spacing:.3em;color:#994433;margin:22px 0 6px}
.part{page-break-before:always;border-top:1px solid #DCD5C8;padding-top:26px;margin-top:40px}
.part h1.ch{font-size:30px}
"""


def fig_inline(ch, link=False):
    path = os.path.join(ROOT, "assets", "fig", ch["id"].lower() + ".svg")
    if not os.path.exists(path):
        return ""
    svg = open(path, encoding="utf-8").read()
    if svg.lstrip().startswith("<?xml"):
        svg = svg.lstrip()[svg.lstrip().index("?>") + 2:].lstrip()
    svg = re.sub(r"<svg ", '<svg class="fig" ', svg, count=1)
    return ('<div class="figbox">%s<div class="figcap">图 · %s 义理图　%s</div></div>'
            % (svg, ch["篇号"], ch["篇题"]))


def chapter_html(ch):
    md = open(os.path.join(ROOT, ch["file"]), encoding="utf-8").read()
    frag = bs.md2html(md)
    fig = fig_inline(ch)
    if fig:
        frag = re.sub(r'(<h2[^>]*>少年读</h2>)', fig + r"\1", frag, count=1)
    return '<section class="part" id="%s">%s</section>' % (ch["id"].lower(), frag)


def simple_md(path):
    if not os.path.exists(path):
        return ""
    frag = bs.md2html(open(path, encoding="utf-8").read())
    frag = re.sub(r"<h1", "<h2", frag, count=1)
    return frag


def toc_block():
    out = ['<div class="toc" id="toc">']
    out.append('<h3>卷首</h3><a href="#xu"><span class="no">序</span>为什么读尚书</a>'
               '<a href="#qianyan"><span class="no">前言</span>读尚书之前</a>')
    vols = [("虞书", 1, 5), ("夏书", 6, 9), ("商书", 10, 26), ("周书", 27, 58)]
    for vol, a, b in vols:
        out.append('<h3>%s</h3>' % vol)
        for c in bs.WRITTEN:
            n = int(c["id"][2:])
            if a <= n <= b:
                bd = '　存疑别录' if c["归属"] != "正经" else ''
                out.append('<a href="#%s"><span class="no">%s</span>%s%s</a>'
                           % (c["id"].lower(), c["篇号"], c["篇题"], bd))
    out.append('<h3>附录（已出）</h3>')
    for tg in sorted(os.listdir(book)):
        if tg.startswith("附录-") and tg.endswith(".md"):
            out.append('<a href="#%s">%s</a>' % (tg[:-3], bs.fm_value(
                open(os.path.join(book, tg), encoding="utf-8").read(), "title")))
    out.append("</div>")
    return "\n".join(out)


def appendix_html(f):
    p = os.path.join(book, f + ".md")
    if not os.path.exists(p):
        return ""
    frag = bs.md2html(open(p, encoding="utf-8").read())
    return '<section class="part" id="%s">%s</section>' % (f, frag)


def main():
    xu = simple_md(os.path.join(book, "序-为什么读尚书.md"))
    pre = simple_md(os.path.join(book, "前言-读尚书之前.md"))
    parts = "".join(chapter_html(c) for c in bs.WRITTEN)
    fus = "".join(appendix_html(f[:-3]) for f in sorted(os.listdir(book))
                  if f.startswith("附录-") and f.endswith(".md"))
    total = sum(c["原文数"] for c in bs.CH)
    fu_n = len([f for f in os.listdir(book) if f.startswith("附录-") and f.endswith(".md")])
    body = """
<div class="wrap" style="padding-bottom:0">%s%s</div>
<div class="wrap" style="padding-top:0">
%s
<div class="xu-sep" aria-hidden="true">※　※　※</div>
<span id="xu"></span>%s
<span id="qianyan"></span>%s
<div class="xu-sep" aria-hidden="true">※　※　※</div>
<h2>目录<small>已成稿 %d 篇 · 附录 %d 件</small></h2>
<p class="lead">底本 58 篇全部定稿（原文 %d 字）；本版为<b>阶段稿</b>，只收已成稿 %d 篇与已出附录，未写篇目不在其中。v%s　单文件自包含（零外链、零脚本）。</p>
%s
</div>
%s%s
<div class="wrap"><div class="foot"><div>润泽说 道可道之尚书 · 通释　阶段稿（正文 %d/58）　v%s　（%s）</div>
<div>底本：《十三经注疏·尚书正义》通行本五十八篇　注参：蔡沈《书集传》</div>
<div>单文件阅读版：CSS 内联、义理图内联 SVG、脚注自注编号；可直接离线阅读。</div></div></div>
""" % (bs.cover_block(), bs.frontis_block(), "", xu, pre,
       len(bs.WRITTEN), fu_n, total, len(bs.WRITTEN), VERSION, toc_block(), parts, fus,
       len(bs.WRITTEN), VERSION, bs.DATE)
    html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>润泽说 道可道之尚书 · 通释（阶段稿 正文 %d/58 ·单文件阅读版）v%s</title>
<meta name="description" content="《尚书》通释阶段稿单文件阅读版：底本 58 篇定稿，正文已成稿 %d 篇，十二节、篇末少年读。">
<meta name="author" content="润泽">
<style>%s</style>
</head>
<body>
%s
</body>
</html>
""" % (len(bs.WRITTEN), VERSION, len(bs.WRITTEN), READER_CSS, body)
    out = os.path.join(docs, "book-full.html")
    open(out, "w", encoding="utf-8").write(html)
    n = len(re.findall(r'class="part"', html))
    print("阅读版已生成：%s（%d 节，%.1f MB）" % (out, n, len(html.encode()) / 1048576))
    bad = re.findall(r'(?:src|href)="(http[^"]+)"', html)
    if bad:
        print("[warn] 存在外链：", bad[:5])


if __name__ == "__main__":
    main()
