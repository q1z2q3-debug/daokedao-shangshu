#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""构建《润泽说 道可道之尚书》站点（docs/）。

源：book/SS*.md（一篇一文件，五十八篇）＋ book/序-*.md、前言-*.md ＋ assets/fig/ss*.svg
产出：docs/index.html、docs/book.html、docs/ch/ssNN.html（58）、docs/fu/*.html（7）、
      docs/fig/*.svg、favicon.svg、sitemap.xml、robots.txt、llms.txt、404.html
用法：python3 scripts/build_site.py
"""
import json
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
book = os.path.join(ROOT, "book")
docs = os.path.join(ROOT, "docs")
figs = os.path.join(ROOT, "assets", "fig")
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import daokedao_book as kit  # noqa: E402
from site_css import CSS as BASE_CSS  # noqa: E402

SITE = "https://q1z2q3-debug.github.io/daokedao-shangshu"
VERSION = open(os.path.join(ROOT, "VERSION"), encoding="utf-8").read().strip()
DATE = "2026-11-24"
CFG = json.load(open(os.path.join(book, "chapters.json"), encoding="utf-8"))
CH = CFG["chapters"]

# ---- 阶段模式：只按真实落盘的篇目出页，缺篇不生成空页、不给链接 ----
TOTAL = len(CH)
SKIP = set(x.strip() for x in os.environ.get("SKIP_IDS", "").split(",") if x.strip())
WRITTEN = [c for c in CH if os.path.exists(os.path.join(ROOT, c["file"])) and c["id"] not in SKIP]
if SKIP:
    print("[skip] 未过检草稿不出页：", "、".join(sorted(SKIP)))
MISSING = [c for c in CH if c not in WRITTEN]
STAGE_CN = "底本地基完成·正文 %d/%d" % (len(WRITTEN), TOTAL)
# 阶段稿待办标（据 check_book：超短档上限、缺图）
TODO_BADGE = {}  # 欠账已清零；某篇再出现超档或缺图时，按实际回填

SERIES = [
    ("道德经", "https://q1z2q3-debug.github.io/runze-daodejing/"),
    ("论语", "https://q1z2q3-debug.github.io/daokedao-lunyu/"),
    ("中庸", "https://q1z2q3-debug.github.io/daokedao-zhongyong/"),
    ("大学", "https://q1z2q3-debug.github.io/daokedao-daxue/"),
    ("千字文", "https://q1z2q3-debug.github.io/daokedao-qianziwen/"),
    ("三字经", "https://q1z2q3-debug.github.io/daokedao-sanzijing/"),
    ("甲骨文", "https://q1z2q3-debug.github.io/daokedao-jiaguwen/"),
    ("心经", "https://q1z2q3-debug.github.io/daokedao-xinjing/"),
    ("金刚经", "https://q1z2q3-debug.github.io/daokedao-jingang/"),
    ("坛经", "https://q1z2q3-debug.github.io/daokedao-tanjing/"),
    ("易传", "https://q1z2q3-debug.github.io/daokedao-yijing/"),
    ("庄子", "https://q1z2q3-debug.github.io/daokedao-zhuangzi/"),
]

FU = [
    ("fu/index.html", "附录", "总索引", "七件附录的入口与全书数据"),
    ("fu/01-duizhao.html", "附录一", "篇目与今古文对照", "五十八篇、二十八篇、三十三目三张对照"),
    ("fu/02-yuanliu.html", "附录二", "古本与源流", "伏生口传、孔壁古文、伪古文的来路"),
    ("fu/03-jiaokan.html", "附录三", "校勘记（正编·底账）", "十五目异文异读回底本定位，附底账 CSV"),
    ("fu/04-cunyi.html", "附录四", "存疑录", "全书未决处，按篇归并"),
    ("fu/05-suoyin.html", "附录五", "关键字索引", "德、民、天、命、敬、中、刑等"),
    ("fu/06-pianzhi.html", "附录六", "五十八篇篇旨表", "一篇一句：篇旨、关键字、所属"),
]

CSS = BASE_CSS + kit.COVER_CSS + kit.FIG_CSS + "@media (max-width:640px){" + kit.COVER_MQ + "}" + """
.pb{margin:26px 0 8px;border:1px solid #DCD5C8;background:#FCFAF6;padding:16px 18px}
.pb-hd{display:flex;justify-content:space-between;align-items:baseline;
 font-size:11.5px;letter-spacing:.26em;color:#994433}
.pb-stage{letter-spacing:.08em;color:#25211D;font-size:12.5px}
.pb-bar{height:6px;background:#EDE7DC;margin:10px 0 8px;border-radius:3px;overflow:hidden}
.pb-fill{height:100%;background:#994433;transition:width .3s}
.pb-num{font-size:12px;color:#7C6D5C;letter-spacing:.04em;margin-bottom:12px}
.pb-row{display:flex;gap:10px;align-items:baseline;padding:6px 0;border-top:1px dotted #DCD5C8}
.pb-k{width:44px;flex:0 0 44px;font-size:12px;color:#7C6D5C;letter-spacing:.14em}
.pb-v{font-size:13px;font-weight:600;min-width:64px}
.pb-v.done{color:#3F5D48}.pb-v.run{color:#994433}
.pb-d{font-size:12px;color:#4A443C;line-height:1.6}
.badge.wait{background:#EDE7DC;color:#7C6D5C;border:1px solid #DCD5C8}
.badge.todo{background:#F6E9E3;color:#994433;border:1px solid #E5C9BC}
.item-todo{opacity:.62}
.item-todo .locked{color:#7C6D5C}
.stage-note{margin:0 0 22px;padding:9px 13px;background:#F6E9E3;border-left:3px solid #994433;
 font-size:12.5px;color:#5C4A3F;line-height:1.7}
"""

FAVICON = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">
<rect width="64" height="64" rx="10" fill="#994433"/>
<text x="32" y="45" font-size="40" text-anchor="middle" fill="#F7F4EE"
font-family="'Noto Serif SC','Songti SC',serif">书</text></svg>"""


def shell(title, desc, body, canonical="", prefix=""):
    can = '<link rel="canonical" href="%s">' % canonical if canonical else ""
    from urllib.parse import quote
    fav = "data:image/svg+xml," + quote(FAVICON, safe="")
    return """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%s</title>
<meta name="description" content="%s">
<meta name="author" content="润泽">
<meta name="robots" content="index,follow,max-image-preview:large">
<meta property="og:type" content="book">
<meta property="og:title" content="%s">
<meta property="og:description" content="%s">
<meta property="og:site_name" content="润泽说 道可道">
%s<link rel="icon" href="%s" type="image/svg+xml">
<style>%s</style>
</head>
<body>
%s
</body>
</html>
""" % (title, desc, title, desc, can, fav, CSS, body)


def strip_fm(text):
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end > 0:
            return text[end + 4:].lstrip("\n")
    return text


def fm_value(text, key):
    m = re.search(r"^%s:\s*(.+)$" % re.escape(key), text, re.M)
    return m.group(1).strip() if m else ""


def prep_notes(text):
    defs, body = {}, []
    for line in text.split("\n"):
        m = re.match(r"^\[\^([^\]]+)\]:\s*(.+)$", line)
        if m:
            t = re.sub(r"`([^`]+)`", r"<code>\1</code>", m.group(2))
            defs[m.group(1)] = t
        else:
            body.append(line)
    txt = "\n".join(body)
    order = []
    for m in re.finditer(r"\[\^([^\]]+)\]", txt):
        if m.group(1) in defs and m.group(1) not in order:
            order.append(m.group(1))
    num = {k: i + 1 for i, k in enumerate(order)}
    txt = re.sub(r"\[\^([^\]]+)\]",
                 lambda m: ('<sup class="fn"><a href="#fn%s">%d</a></sup>'
                            % (num[m.group(1)], num[m.group(1)]))
                 if m.group(1) in num else m.group(0), txt)
    lis = "".join('<li id="fn%d"><p>%s　<a class="footnote-back" href="#fn%d">↩</a></p></li>'
                  % (num[k], defs[k], num[k]) for k in order)
    if not lis:
        return txt
    return txt + ('\n\n<aside class="footnotes"><ol>%s</ol></aside>\n' % lis)


def tag_line(html):
    def rep(m):
        parts = [p.strip() for p in m.group(1).split("·")]
        if len(parts) == 3:
            jw = parts[1]
            cls = "jw" if jw == "今文" else "by"
            bd = "" if parts[2] == "正经" else '<span class="badge gu">存疑别录</span>'
            return ('<p class="tagline">%s <span class="%s">· %s</span> · %s%s</p>'
                    % (parts[0], cls, jw, parts[2], bd))
        return m.group(0)
    return re.sub(r'<p class="tag">(.*?)</p>', rep, html)


def md2html(text):
    frag = subprocess.run(
        ["pandoc", "-f", "markdown+pipe_tables", "-t", "html5", "--no-highlight"],
        input=prep_notes(strip_fm(text)).encode("utf-8"), stdout=subprocess.PIPE, check=True,
    ).stdout.decode()
    frag = frag.replace("<h1", "<h1 class=\"ch\"", 1)
    for tg, cls in (("序", "x"), ("经", "k"), ("注", "z"), ("义", "y"), ("用", "yong")):
        frag = frag.replace("【%s】" % tg, '<span class="mk %s">%s</span>' % (cls, tg))
    return tag_line(frag)


def fig_html(ch):
    path = os.path.join(figs, ch["id"].lower() + ".svg")
    if not os.path.exists(path):
        return ""
    svg = open(path, encoding="utf-8").read()
    if svg.lstrip().startswith("<?xml"):
        svg = svg.lstrip()[svg.lstrip().index("?>") + 2:].lstrip()
    svg = re.sub(r"<svg ", '<svg class="fig" ', svg, count=1)
    return ('<div class="figbox"><a class="figlink" href="../fig/%s.svg" target="_blank" '
            'rel="noopener" title="点开看大图">%s</a>'
            '<div class="figcap">图 · %s 义理图　%s　<a href="../fig/%s.svg" target="_blank" '
            'rel="noopener">点图放大</a></div></div>'
            % (ch["id"].lower(), svg, ch["篇号"], ch["篇题"], ch["id"].lower()))


def bar(left_html, right=""):
    return ('<div class="bar"><div>%s</div><div>润 泽 说 · 道 可 道 之 尚 书　%s</div></div>'
            % (left_html, right))


def chapter_body(idx, ch):
    """idx 为在 WRITTEN（已成稿篇）中的位置；导航只在已成稿篇之间跳，不指向空缺篇。"""
    src = os.path.join(ROOT, ch["file"])
    if not os.path.exists(src):
        return None
    frag = md2html(open(src, encoding="utf-8").read())
    note = TODO_BADGE.get(ch["id"], "")
    if note:
        todo = []
        if "待压" in note:
            todo.append("压回短档上限（现超 2,500 字）")
        if "缺图" in note:
            todo.append("补配义理图")
        frag = ('<p class="stage-note">阶段稿 · %s　本篇按阶段稿发布，尚欠%s；'
                '经文、注疏与结论均不受影响。</p>' % (STAGE_CN, "、".join(todo))) + frag
    fig = fig_html(ch)
    if fig:
        frag = re.sub(r'(<h2[^>]*>少年读</h2>)', fig + r"\1", frag, count=1)
    else:
        print("[warn] 缺图：", ch["id"])
    prev_h = "../book.html" if idx == 0 else WRITTEN[idx - 1]["page"].split("/")[-1]
    prev_n = "卷首" if idx == 0 else WRITTEN[idx - 1]["篇号"]
    if idx + 1 < len(WRITTEN):
        next_h, next_n = WRITTEN[idx + 1]["page"].split("/")[-1], WRITTEN[idx + 1]["篇号"]
    else:
        next_h, next_n = "../fu/index.html", "附录"
    pn = ('<div class="pn"><div><a href="%s">← %s</a></div>'
          '<div class="mid"><a href="../index.html">目录</a>　<a href="../book.html">卷首</a></div>'
          '<div class="right"><a href="%s">%s →</a></div></div>'
          % (prev_h, prev_n, next_h, next_n))
    foot = ('<div class="foot"><div>润泽说 道可道之尚书 · %s　%s　v%s　（%s）</div>'
            '<div>底本：《十三经注疏·尚书正义》通行本五十八篇　注参：蔡沈《书集传》</div>'
            '<div><a href="../index.html">目录</a><a href="../book.html">卷首</a>'
            '<a href="../fu/index.html">附录</a><a href="https://github.com/q1z2q3-debug/daokedao-shangshu">GitHub</a>'
            '<a href="../%s">义理图 SVG</a></div></div>' % (ch["篇号"], ch["篇题"], VERSION, DATE, ch["fig"]))
    body = bar('<a href="../index.html">← 目录</a>', ch["篇号"]) + \
        '<div class="wrap">' + frag + pn + foot + "</div>"
    return shell("%s　%s｜润泽说 道可道之尚书" % (ch["篇号"], ch["篇题"]), ch["gist"], body,
                 "%s/%s" % (SITE, ch["page"]), "../")


def cover_block():
    return kit.cover(
        title="尚书",
        tag="五 十 八 篇 · 今 文 二 十 八 · 古 文 二 十 五",
        seal="书",
        gatha_first=("天命靡常", "敬德保民"),
        gatha_second=("曰若稽古", "协和万邦"),
        meta=["底本　《十三经注疏·尚书正义》", "注参　蔡沈《书集传》· 孔传孔疏",
              "体例　五十八篇 · 十二节 · 篇末少年读", "v" + VERSION + " · 二〇二六"],
    )


def frontis_block():
    return kit.frontis(
        title="润泽说 道可道之尚书",
        sub="尚书 · 通释读本（全本）",
        lines=[
            ("底本", "《十三经注疏·尚书正义》所载通行本，五十八篇"),
            ("注参", "蔡沈《书集传》；旧题孔安国《传》、孔颖达《疏》；郑玄注有者并陈"),
            ("体例", "一篇一页；每篇十二节，末附少年读；四层分离：序／经／注／义／用"),
            ("正经", "今文二十八篇（注疏本分题三十三目）"),
            ("别录", "古文二十五篇，单列存疑别录：经文照录，不入道统叙述"),
            ("版本", "v" + VERSION),
        ],
        seal="书",
    )


def progress_board():
    """首屏进度板：底本地基 + 正文进度 + 附录进度，全部按真实文件计数。"""
    pct = int(len(WRITTEN) * 100 / TOTAL)
    fu_done = len([f for f in os.listdir(book) if f.startswith("附录-") and f.endswith(".md")])
    fig_done = len([f for f in os.listdir(figs) if f.endswith(".svg")])
    rows = [
        ("底本", "58/58", "五十八篇经文定稿，24,849 汉字，两轮 ctext 逐字终校完成", "done"),
        ("正文", "%d/58" % len(WRITTEN), "十二节＋少年读成稿；其余 %d 篇在建，本页不预生成" % (TOTAL - len(WRITTEN)), "run"),
        ("义理图", "%d/58" % fig_done, "figlib 六式 SVG，纸墨五色，逐张过自检", "run"),
        ("附录", "%d/7" % fu_done, "已出总索引外 01 篇目对照、02 古本源流", "run"),
    ]
    trs = "".join(
        '<div class="pb-row"><div class="pb-k">%s</div><div class="pb-v %s">%s</div>'
        '<div class="pb-d">%s</div></div>' % (k, cls, v, d) for k, v, d, cls in rows)
    return """
<div class="pb">
  <div class="pb-hd"><span>在建 · 阶段稿</span><span class="pb-stage">%s</span></div>
  <div class="pb-bar"><div class="pb-fill" style="width:%d%%"></div></div>
  <div class="pb-num">正文 %d / 58　·　v%s　·　未写篇目不生成页面，不出占位页</div>
  %s
</div>""" % (STAGE_CN, pct, len(WRITTEN), VERSION, trs)


def toc_items():
    vols = [("虞书", "01", "05"), ("夏书", "06", "09"), ("商书", "10", "26"), ("周书", "27", "58")]
    out = []
    for vol, a, b in vols:
        items = [c for c in CH if int(c["id"][2:]) >= int(a) and int(c["id"][2:]) <= int(b)]
        if not items:
            continue
        done = [c for c in items if c in WRITTEN]
        out.append('<div class="vol">%s　<span style="letter-spacing:.1em;font-size:11.5px;color:#7C6D5C">'
                   '%d 篇 · 已成稿 %d · 原文 %d 字</span></div>'
                   % (vol, len(items), len(done), sum(c["原文数"] for c in items)))
        for c in items:
            bd = ('<span class="badge gu">存疑别录</span>' if c["归属"] != "正经"
                  else '<span class="badge">正经</span>')
            if c in WRITTEN:
                todo = TODO_BADGE.get(c["id"], "")
                td = "".join('<span class="badge todo">%s</span>' % t
                             for t in ("待压", "缺图") if t in todo)
                fig = "" if c["id"] in TODO_BADGE and TODO_BADGE[c["id"]] != "缺图" else ""
                out.append('<div class="item"><div class="no">%s　原文 %d 字</div>'
                           '<div class="t"><a href="%s" style="border:0;color:#25211D">%s　%s</a>%s%s</div>'
                           '<div class="s">%s</div><div class="k">%s</div></div>'
                           % (c["篇号"], c["原文数"], c["page"], c["篇号"], c["篇题"], bd, td,
                              c["gist"], c["首句"]))
            else:
                out.append('<div class="item item-todo"><div class="no">%s　原文 %d 字</div>'
                           '<div class="t"><span class="locked">%s　%s</span>%s'
                           '<span class="badge wait">在建</span></div>'
                           '<div class="s">%s</div><div class="k">%s</div></div>'
                           % (c["篇号"], c["原文数"], c["篇号"], c["篇题"], bd,
                              c["gist"], c["首句"]))
    return "".join(out)


def fu_pages():
    """已落盘的附录页：以 book/附录-*.md 的 page 字段为唯一依据。"""
    out = []
    for f in sorted(os.listdir(book)):
        if f.startswith("附录-") and f.endswith(".md"):
            text = open(os.path.join(book, f), encoding="utf-8").read()
            p = fm_value(text, "page")
            if p:
                out.append((p, fm_value(text, "title") or f, fm_value(text, "desc")))
    return out


def fu_items():
    have = {p for p, _, _ in fu_pages()}
    out = []
    for href, no, name, desc in FU:
        if href in have:
            out.append('<div class="item"><div class="no">%s</div><div class="t">'
                       '<a href="%s" style="border:0;color:#25211D">%s</a></div>'
                       '<div class="s">%s</div></div>' % (no, href, name, desc))
        else:
            out.append('<div class="item item-todo"><div class="no">%s</div>'
                       '<div class="t"><span class="locked">%s</span>'
                       '<span class="badge wait">在建</span></div><div class="s">%s</div></div>'
                       % (no, name, desc))
    return "".join(out)


def build_index():
    total = sum(c["原文数"] for c in CH)
    nj = sum(1 for c in CH if c["归属"] == "正经")
    ng = len(CH) - nj
    body = bar('<span>首页 · 目录</span>', "阶段 v" + VERSION) + """
<div class="wrap">
""" + cover_block() + progress_board() + """
<div class="hd" style="padding:26px 0 0">
  <div class="series" style="font-size:12px;letter-spacing:.42em;color:#994433">润 泽 说 · 道 可 道</div>
  <h1 class="title">尚书 · 通释</h1>
  <p class="lead" style="font-size:15px">五十八篇，一篇一页；成人十二节可考，篇末少年读一段可念。底本《尚书正义》通行本，今文为正经，古文列别录。<b>本站在建，只发布已成稿篇目。</b></p>
  <p class="lead">全书 <b>58</b> 篇　正经 <b>%d</b>　别录 <b>%d</b>　原文 <b>%d</b> 字　已成稿 <b>%d</b> 篇　版本 v%s（阶段稿）　（%s）</p>
</div>

<h2>卷首语<small>为什么这样读</small></h2>
<p>《尚书》最容易被读成两件事：一件是「上古史料」，一件是「圣王格言」。前者把它交给考据，后者把它交给口号。<b>本书既不把它当信史照单全收，也不把它当训诫集随手摘句</b>：先把五十八篇各归其位——哪一篇是今文、哪一篇晚出，然后逐篇读它的「事」与「言」。</p>
<p>全书的主线只有一条：<b>天命靡常，敬德保民</b>。天命不是写在星象上的判决，它的凭据在「德」，德的可验处在「民」。从尧典的「协和万邦」到秦誓的「民讫自若是多盘」，五十八篇都是这条线的刻度——包括那些晚出的篇章，它们也在替这条线说话。</p>

<h2>目录<small>五十八篇 · 按虞夏商周分卷 · 已成稿 %d 篇可点</small></h2>
<p class="lead">按注疏本次序；每篇十二节，末附少年读。点篇号进阅读页。标「存疑别录」者为古文二十五篇；标「在建」者尚未成稿，<b>不出页面、不占位</b>。</p>
%s

<h2>附录<small>已出：篇目对照 · 古本源流（其余五件在建）</small></h2>
<div class="list">%s</div>

<h2>体例<small>四层分离，一篇十二节</small></h2>
<div class="rows">
  <div class="row"><div class="kk">四层标记</div><div class="vv">【序】书序照录；【经】原文只抄底本；【注】注疏标明谁说的；【义】义理须指回原文；【用】今用不冒充原文。一段只归一层。</div></div>
  <div class="row"><div class="kk">十二节</div><div class="vv">本篇导读、经文、字义与句读、今译、篇旨、注疏、分寸与边界、义理、时代之问、跨典、存疑、双卡与图。</div></div>
  <div class="row"><div class="kk">正经与别录</div><div class="vv">今文二十八篇为正经；古文二十五篇单列存疑别录，经文照录、义理可读，但不混入正经的道统叙述，也不销毁。</div></div>
  <div class="row"><div class="kk">少年读</div><div class="vv">每篇末一百至二百字，加一件事、三个问题；不删繁就简，只换一种说法。</div></div>
  <div class="row"><div class="kk">图</div><div class="vv">义理图手写 SVG，一图一文件；纸 #F7F4EE、墨 #25211D、赭 #994433、棕 #7C6D5C、线 #DCD5C8。</div></div>
</div>

<h2>五步读法<small>前三步求真，后两步求活</small></h2>
<div class="rows">
  <div class="row"><div class="kk">一　校</div><div class="vv">校字：底本、异文、音读、今古文的真伪。</div></div>
  <div class="row"><div class="kk">二　境</div><div class="vv">还境：制度、称谓、诸侯与王官的来历。</div></div>
  <div class="row"><div class="kk">三　义</div><div class="vv">立义：这一篇要立的一个判断。</div></div>
  <div class="row"><div class="kk">四　疑</div><div class="vv">存疑：说不清就写出来，晚出的篇章不入道统叙述。</div></div>
  <div class="row"><div class="kk">五　用</div><div class="vv">致用：在自己的世代里做一件。</div></div>
</div>

<h2>同系列<small>润泽说 · 道可道</small></h2>
<div class="series-grid">%s</div>
<a class="btn" href="book.html">从卷首读起（序 · 封面 · 扉页 · 前言）</a>

<div class="foot">
  <div>润泽说 道可道之尚书 · 通释　阶段稿（正文 %d/58）　v%s　（%s）</div>
  <div>底本：《十三经注疏·尚书正义》通行本五十八篇　注参：蔡沈《书集传》</div>
  <div>全书五十八篇：今文二十八篇正经、古文二十五篇存疑别录；七件附录另立。本站只发布已成稿篇目，未写篇目不生成页面。</div>
  <div><a href="https://github.com/q1z2q3-debug/daokedao-shangshu">GitHub 仓库</a><a href="book.html">卷首</a><a href="sitemap.xml">站点地图</a></div>
</div>
</div>
""" % (nj, ng, total, len(WRITTEN), VERSION, DATE, len(WRITTEN), toc_items(), fu_items(),
       "".join('<a href="%s">%s<small>通释读本</small></a>' % (u, n) for n, u in SERIES),
       len(WRITTEN), VERSION, DATE)
    open(os.path.join(docs, "index.html"), "w", encoding="utf-8").write(
        shell("润泽说 道可道之尚书 · 通释（阶段稿 正文 %d/58）｜《尚书》读本" % len(WRITTEN),
              "《尚书》通释阶段稿：底本五十八篇全部定稿（24,849 字），正文已成稿 %d 篇并发布，其余在建；今文二十八篇正经、古文二十五篇存疑别录。底本《尚书正义》通行本。" % len(WRITTEN),
              body, SITE + "/"))


def build_book():
    xu = os.path.join(book, "序-为什么读尚书.md")
    pre = os.path.join(book, "前言-读尚书之前.md")
    xu_frag = md2html(open(xu, encoding="utf-8").read())
    pre_frag = md2html(open(pre, encoding="utf-8").read())
    body = bar('<a href="index.html">← 目录</a>', "卷首") + """
<div class="wrap" style="padding-bottom:0">
%s
%s
</div>
<div class="wrap" style="padding-top:0">
%s
<div class="xu-sep" aria-hidden="true">※　※　※</div>
%s
<div class="pn"><div><a href="index.html">← 目录</a></div><div class="mid">卷首</div>
<div class="right"><a href="%s">第一篇 →</a></div></div>
<div class="foot"><div>润泽说 道可道之尚书 · 卷首　v%s　（%s）</div>
<div>底本：《十三经注疏·尚书正义》通行本　注参：蔡沈《书集传》</div></div>
</div>
""" % (cover_block(), frontis_block(), xu_frag, pre_frag, CH[0]["page"], VERSION, DATE)
    open(os.path.join(docs, "book.html"), "w", encoding="utf-8").write(
        shell("卷首：序 · 封面 · 扉页 · 前言｜润泽说 道可道之尚书",
              "《尚书》通释卷首：序与前言（为什么读、一条主线、两个本子、四层分离、十二节、正经与别录）。",
              body, SITE + "/book.html"))


def build_chapters():
    outdir = os.path.join(docs, "ch")
    os.makedirs(outdir, exist_ok=True)
    n = 0
    for i, ch in enumerate(WRITTEN):
        html = chapter_body(i, ch)
        if html is None:
            print("[warn] 缺篇：", ch["file"])
            continue
        open(os.path.join(outdir, ch["id"].lower() + ".html"), "w", encoding="utf-8").write(html)
        n += 1
    print("篇页 %d / %d（缺 %d 篇不生成）" % (n, len(WRITTEN), len(MISSING)))


def build_fu():
    outdir = os.path.join(docs, "fu")
    os.makedirs(outdir, exist_ok=True)
    pages = []
    for f in sorted(os.listdir(book)):
        if not f.startswith("附录-") or not f.endswith(".md"):
            continue
        text = open(os.path.join(book, f), encoding="utf-8").read()
        page = fm_value(text, "page")
        if not page:
            print("[warn] 附录缺 page：", f)
            continue
        frag = md2html(text)
        pn = ('<div class="pn"><div><a href="../index.html">← 目录</a></div>'
              '<div class="mid"><a href="index.html">附录</a></div>'
              '<div class="right"><a href="../%s">第一篇 →</a></div></div>' % CH[0]["page"])
        foot = ('<div class="foot"><div>润泽说 道可道之尚书 · 附录　v%s　（%s）</div>'
                '<div>底本：《十三经注疏·尚书正义》通行本五十八篇　注参：蔡沈《书集传》</div></div></div>'
                % (VERSION, DATE))
        body = bar('<a href="../index.html">← 目录</a>',
                   fm_value(text, "章号") or "附录") + '<div class="wrap">' + frag + pn + foot
        out = os.path.join(docs, page)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        open(out, "w", encoding="utf-8").write(
            shell("%s｜润泽说 道可道之尚书附录" % fm_value(text, "title"),
                  fm_value(text, "desc") or "《尚书》附录", body, SITE + "/" + page, "../"))
        pages.append(page)
    print("附录页 %d：%s" % (len(pages), "、".join(pages)))

    # 附录总索引（阶段版）：只列已出附录，未出者标「在建」，不给死链
    list_html = fu_items().replace('href="fu/', 'href="../fu/')
    body = bar('<a href="../index.html">← 目录</a>', "附录") + (
        '<div class="wrap"><h2 class="ch">附录</h2>'
        '<p class="lead">七件附录，先出什么就先挂什么。标「在建」者尚未成稿，不生成空白页。'
        '当前阶段 v%s，正文 %d/58。</p><div class="list">%s</div>'
        '<div class="pn"><div><a href="../index.html">← 目录</a></div>'
        '<div class="mid">附录</div><div class="right"><a href="../%s">第一篇 →</a></div></div>'
        '<div class="foot"><div>润泽说 道可道之尚书 · 附录　阶段稿 v%s　（%s）</div>'
        '<div>底本：《十三经注疏·尚书正义》通行本五十八篇　注参：蔡沈《书集传》</div></div></div>'
        % (VERSION, len(WRITTEN), list_html, CH[0]["page"], VERSION, DATE))
    open(os.path.join(outdir, "index.html"), "w", encoding="utf-8").write(
        shell("附录 · 总索引（阶段稿）｜润泽说 道可道之尚书",
              "《尚书》附录总索引：当前阶段已出版的附录页与在建清单。", body,
              SITE + "/fu/index.html", "../"))
    pages.append("fu/index.html")
    return pages


def build_meta(pages):
    open(os.path.join(docs, "favicon.svg"), "w", encoding="utf-8").write(FAVICON)
    os.makedirs(os.path.join(docs, "fig"), exist_ok=True)
    for f in os.listdir(figs):
        if f.endswith(".svg"):
            shutil.copy(os.path.join(figs, f), os.path.join(docs, "fig", f))

    urls = [""] + ["book.html"] + [c["page"] for c in WRITTEN] + pages + \
        ["fig/" + c["id"].lower() + ".svg" for c in WRITTEN
         if os.path.exists(os.path.join(figs, c["id"].lower() + ".svg"))]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for u in urls:
        sm += "<url><loc>%s/%s</loc><lastmod>%s</lastmod><changefreq>weekly</changefreq></url>\n" % (SITE, u, DATE)
    sm += "</urlset>\n"
    open(os.path.join(docs, "sitemap.xml"), "w", encoding="utf-8").write(sm)

    open(os.path.join(docs, "robots.txt"), "w", encoding="utf-8").write(
        "User-agent: *\nAllow: /\n\nUser-agent: GPTBot\nAllow: /\n\nUser-agent: ClaudeBot\nAllow: /\n\n"
        "Sitemap: %s/sitemap.xml\n" % SITE)

    llms = "# 润泽说 道可道之尚书 · 通释（阶段稿 v%s）\n\n" % VERSION
    llms += "> 《尚书》通释读本。**当前为阶段稿：正文 %d/58 篇已成稿并发布，其余在建，未生成页面。**\n" % len(WRITTEN)
    llms += "> 底本《十三经注疏·尚书正义》通行本，58 篇经文已全部定稿（24,849 汉字，两轮逐字终校）。今文二十八篇为正经，古文二十五篇列存疑别录。\n"
    llms += "> 正文每篇十二节：本篇导读、经文、字义与句读、今译、篇旨、注疏、分寸与边界、义理、时代之问、跨典、存疑、双卡与图；篇末附少年读。\n"
    llms += "> 七件附录：总索引、篇目与今古文对照、古本与源流、校勘记、存疑录、关键字索引、篇旨表。\n\n## 卷首\n"
    llms += "- 序 · 前言：%s/book.html\n" % SITE
    llms += "\n## 已成稿篇（%d）\n" % len(WRITTEN)
    for c in WRITTEN:
        llms += "- %s｜%s｜%s｜%s｜原文 %d 字：%s/%s\n" % (
            c["篇号"], c["篇题"], c["书"], c["归属"], c["原文数"], SITE, c["page"])
    llms += "\n## 在建篇（%d，未生成页面）\n" % len(MISSING)
    llms += "、".join("%s %s" % (c["篇号"], c["篇题"]) for c in MISSING) + "\n"
    llms += "\n## 已成稿附录\n"
    for p, t, _ in fu_pages():
        llms += "- %s：%s/%s\n" % (t, SITE, p)
    llms += "\n## 引用\n润泽《润泽说 道可道之尚书》v%s，%s/\n" % (VERSION, SITE)
    llms += "\n## 义理口径\n天命靡常，敬德保民：天命的凭据在德，德的可验处在民。稽古是问学不是复古。三才配位：天识、地色、人受想行。\n"
    llms += "和是本具无界，合是构框划界。皇极是度，不是折中。古文二十五篇为存疑别录：可读其义，不引为道统证据。\n"
    open(os.path.join(docs, "llms.txt"), "w", encoding="utf-8").write(llms)

    open(os.path.join(docs, "404.html"), "w", encoding="utf-8").write(
        shell("未找到｜润泽说 道可道之尚书",
              "页面未找到。",
              bar('<a href="index.html">← 目录</a>') +
              '<div class="wrap"><h2 class="ch">未找到</h2><p>此页不在书中。</p>'
              '<p><a href="index.html">回目录</a></p></div>'))


def main():
    os.makedirs(docs, exist_ok=True)
    # 清掉上一轮的篇页与图，避免已撤下的草稿留下残页
    for sub, pat in ((os.path.join(docs, "ch"), ".html"), (os.path.join(docs, "fig"), ".svg")):
        if os.path.isdir(sub):
            for f in os.listdir(sub):
                if f.endswith(pat):
                    os.remove(os.path.join(sub, f))
    build_index()
    build_book()
    build_chapters()
    pages = build_fu()
    build_meta(pages)
    print("站点已生成：", docs)


if __name__ == "__main__":
    main()
