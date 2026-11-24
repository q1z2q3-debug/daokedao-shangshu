#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""《润泽说 道可道之尚书》义理图库（参数化 SVG，禁手写坐标）。

六种图式：
  1 duizhao  对照（两栏，俗见／正解、今文／古文）
  2 ticheng  递进（横排 3–5 步，带箭头）
  3 sanlie   三列（三才配位一类，每列小标题＋条目）
  4 huan     环列（4–6 节点绕中心，中心一句主断语）
  5 juzhen   矩阵（行列格，如九畴、九州、三德）
  6 ceng     层叠（上下数层，如天／人／地、体／用）

用法（写图）：
    from figlib import duizhao, emit
    svg = duizhao("标题", "图说一句", "俗见", ["…","…"], "正解", ["…","…"], note="…")
    emit("assets/fig/ss01.svg", svg)

规矩：只用纸墨五色；字号 ≥11；必有 title／desc／viewBox；不写 width／height；
中文一律 font-family="'Noto Serif SC','Songti SC',serif"。
"""
import os
import re

PAPER = "#F7F4EE"
PAPER2 = "#FCFAF6"
INK = "#25211D"
OCHRE = "#994433"
BROWN = "#7C6D5C"
LINE = "#DCD5C8"

FONT = "'Noto Serif SC','Songti SC','Source Han Serif SC',serif"
SANS = "'Noto Sans SC','PingFang SC',sans-serif"
W = 760


def _esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def _lines(text, per_line):
    """按字数粗断行（中文等宽近似）。"""
    out, cur = [], ""
    for ch in text:
        if ch == "\n":
            out.append(cur)
            cur = ""
            continue
        cur += ch
        if len(cur) >= per_line:
            out.append(cur)
            cur = ""
    if cur:
        out.append(cur)
    return out or [""]


def _texts(items, x, y, size, fill, per_line, lh, anchor="start"):
    out, yy = [], y
    for it in items:
        for ln in _lines(it, per_line):
            out.append('<text x="%d" y="%d" font-size="%d" fill="%s" text-anchor="%s">%s</text>'
                       % (x, yy, size, fill, anchor, _esc(ln)))
            yy += lh
        yy += lh * 0.25
    return "".join(out), yy


def _svg(title, desc, h, body):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" role="img">\n'
            '<title>%s</title>\n<desc>%s</desc>\n'
            '<rect x="0" y="0" width="%d" height="%d" fill="%s"/>\n%s\n</svg>\n'
            % (W, h, _esc(title), _esc(desc), W, h, PAPER2, body))


def _head(title, y=44):
    return ('<text x="32" y="%d" font-size="17" fill="%s" font-family="%s" '
            'letter-spacing="2">%s</text><line x1="32" y1="%d" x2="%d" y2="%d" '
            'stroke="%s" stroke-width="1"/>' % (y, OCHRE, FONT, _esc(title), y + 12, W - 32, y + 12, LINE))


def _foot(note, y, h):
    if not note:
        return ""
    t, _ = _texts([note], 32, h - 26, 12, BROWN, 60, 16)
    return t


def duizhao(title, desc, left_head, left_items, right_head, right_items,
            note="", left_label="", right_label=""):
    """两栏对照图。宽 760，两栏各 330，中间箭头。"""
    pad, gap = 32, 46
    colw = (W - pad * 2 - gap) // 2
    x1, x2 = pad, pad + colw + gap
    top = 84
    lh, size = 21, 13
    _, yl = _texts(left_items, x1 + 18, top + 66, size, INK, 24, lh)
    _, yr = _texts(right_items, x2 + 18, top + 66, size, INK, 24, lh)
    bh = max(yl, yr) - top + 34
    body = [_head(title)]
    body.append('<rect x="%d" y="%d" width="%d" height="%d" rx="2" fill="%s" stroke="%s"/>'
                % (x1, top, colw, bh, PAPER, LINE))
    body.append('<rect x="%d" y="%d" width="%d" height="%d" rx="2" fill="%s" stroke="%s"/>'
                % (x2, top, colw, bh, PAPER, LINE))
    body.append('<rect x="%d" y="%d" width="%d" height="30" fill="%s"/>'
                % (x1, top, colw, LINE))
    body.append('<rect x="%d" y="%d" width="%d" height="30" fill="%s"/>'
                % (x2, top, colw, LINE))
    body.append('<text x="%d" y="%d" font-size="14" fill="%s" font-family="%s" letter-spacing="3">%s</text>'
                % (x1 + 14, top + 21, OCHRE, FONT, _esc(left_head + ("　" + left_label if left_label else ""))))
    body.append('<text x="%d" y="%d" font-size="14" fill="%s" font-family="%s" letter-spacing="3">%s</text>'
                % (x2 + 14, top + 21, OCHRE, FONT, _esc(right_head + ("　" + right_label if right_label else ""))))
    lt, _ = _texts(left_items, x1 + 18, top + 66, size, INK, 24, lh)
    rt, _ = _texts(right_items, x2 + 18, top + 66, size, INK, 24, lh)
    body += [lt, rt]
    cy = top + bh // 2
    body.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="1" '
                'marker-end="url(#ar)"/>' % (x1 + colw + 10, cy, x2 - 12, cy, BROWN))
    body.append('<defs><marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" '
                'markerHeight="6" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="%s"/></marker></defs>' % BROWN)
    h = top + bh + 54
    body.append(_foot(note, 0, h))
    return _svg(title, desc, h, "\n".join(body))


def ticheng(title, desc, steps, note=""):
    """横排递进图。steps=[(主标, 小注), ...] 3–5 个。"""
    n = len(steps)
    pad = 32
    top, boxh = 100, 96
    avail = W - pad * 2
    gap = 26
    bw = (avail - gap * (n - 1)) // n
    body = [_head(title)]
    for i, st in enumerate(steps):
        label, sub = st if isinstance(st, (list, tuple)) else (st, "")
        x = pad + i * (bw + gap)
        body.append('<rect x="%d" y="%d" width="%d" height="%d" rx="2" fill="%s" stroke="%s"/>'
                    % (x, top, bw, boxh, PAPER, LINE))
        lt, _ = _texts([label], x + bw // 2, top + 42, 16, OCHRE, max(4, bw // 17), 24, "middle")
        body.append(lt)
        if sub:
            st_, _ = _texts([sub], x + bw // 2, top + 72, 12, BROWN, max(6, bw // 11), 17, "middle")
            body.append(st_)
        if i < n - 1:
            ax = x + bw + 4
            body.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s" stroke-width="1.2" '
                        'marker-end="url(#ar)"/>' % (ax, top + boxh // 2, ax + gap - 8, top + boxh // 2, BROWN))
    body.append('<defs><marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" '
                'markerHeight="6" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="%s"/></marker></defs>' % BROWN)
    h = top + boxh + 60
    body.append(_foot(note, 0, h))
    return _svg(title, desc, h, "\n".join(body))


def sanlie(title, desc, cols, note=""):
    """三列图。cols=[(列题, [条目…]), …]，2–3 列。"""
    n = len(cols)
    pad, gap = 32, 20
    cw = (W - pad * 2 - gap * (n - 1)) // n
    top = 92
    lh, size = 20, 13
    ymax, blocks = top, []
    for i, (hd, items) in enumerate(cols):
        x = pad + i * (cw + gap)
        t, yend = _texts(items, x + 16, top + 58, size, INK, max(6, cw // 15), lh)
        ymax = max(ymax, yend)
        blocks.append((x, hd, t))
    bh = ymax - top + 26
    body = [_head(title)]
    for i, (x, hd, t) in enumerate(blocks):
        body.append('<rect x="%d" y="%d" width="%d" height="%d" rx="2" fill="%s" stroke="%s"/>'
                    % (x, top, cw, bh, PAPER, LINE))
        body.append('<rect x="%d" y="%d" width="%d" height="30" fill="%s"/>' % (x, top, cw, LINE))
        body.append('<text x="%d" y="%d" font-size="14" fill="%s" font-family="%s" letter-spacing="2">%s</text>'
                    % (x + 14, top + 21, OCHRE, FONT, _esc(hd)))
        body.append(t)
    h = top + bh + 56
    body.append(_foot(note, 0, h))
    return _svg(title, desc, h, "\n".join(body))


def huan(title, desc, center, items, note=""):
    """环列图。items 4–6 个，绕中心（中心为主断语）。"""
    import math
    n = len(items)
    cx, cy = W // 2, 250
    R = 138
    body = [_head(title)]
    body.append('<circle cx="%d" cy="%d" r="%d" fill="none" stroke="%s" stroke-width="1" '
                'stroke-dasharray="4 5"/>' % (cx, cy, R, LINE))
    for i, it in enumerate(items):
        ang = -math.pi / 2 + 2 * math.pi * i / n
        x, y = cx + R * math.cos(ang), cy + R * math.sin(ang)
        body.append('<circle cx="%d" cy="%d" r="38" fill="%s" stroke="%s"/>' % (x, y, PAPER, LINE))
        label = it if isinstance(it, str) else it[0]
        t, _ = _texts([label], x, y + 5, 13, OCHRE if i % 2 == 0 else INK, 4, 16, "middle")
        body.append(t)
        if not isinstance(it, str) and len(it) > 1:
            s, _ = _texts([it[1]], x, y + 62, 11, BROWN, 6, 14, "middle")
            body.append(s)
    ct, _ = _texts([center], cx, cy + 6, 15, INK, 8, 22, "middle")
    body.append(ct)
    h = cy + R + 96
    body.append(_foot(note, 0, h))
    return _svg(title, desc, h, "\n".join(body))


def juzhen(title, desc, row_head, col_head, rows, note=""):
    """矩阵图。row_head=左侧行题列表；col_head=列题列表；rows=[[行题, 格1, 格2…], …]。"""
    pad = 32
    top = 96
    ncol = len(col_head)
    labw = 96
    cw = (W - pad * 2 - labw) // ncol
    rh = 46
    body = [_head(title)]
    y = top
    for j, c in enumerate(col_head):
        x = pad + labw + j * cw
        body.append('<text x="%d" y="%d" font-size="12.5" fill="%s" font-family="%s" '
                    'text-anchor="middle">%s</text>' % (x + cw // 2, y - 12, OCHRE, FONT, _esc(c)))
        body.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s"/>'
                    % (x, y, x, y + rh * len(rows), LINE))
    body.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s"/>'
                % (pad, y, W - pad, y, LINE))
    for i, row in enumerate(rows):
        yy = y + i * rh
        body.append('<line x1="%d" y1="%d" x2="%d" y2="%d" stroke="%s"/>'
                    % (pad, yy + rh, W - pad, yy + rh, LINE))
        body.append('<text x="%d" y="%d" font-size="13" fill="%s" font-family="%s" '
                    'letter-spacing="1">%s</text>' % (pad + 6, yy + 27, INK, FONT, _esc(row[0])))
        for j, cell in enumerate(row[1:]):
            t, _ = _texts([cell], pad + labw + j * cw + cw // 2, yy + 27, 12.5, INK,
                          max(6, cw // 14), 17, "middle")
            body.append(t)
    h = y + rh * len(rows) + 54
    body.append(_foot(note, 0, h))
    return _svg(title, desc, h, "\n".join(body))


def ceng(title, desc, layers, note=""):
    """层叠图。layers=[(层题, 说明), …] 自上而下，2–4 层。"""
    pad = 32
    top = 92
    bh = 74
    body = [_head(title)]
    for i, lay in enumerate(layers):
        label, sub = lay if isinstance(lay, (list, tuple)) else (lay, "")
        x, y = pad + i * 10, top + i * (bh + 12)
        w = W - pad * 2 - i * 20
        body.append('<rect x="%d" y="%d" width="%d" height="%d" rx="2" fill="%s" stroke="%s"/>'
                    % (x, y, w, bh, PAPER, LINE))
        body.append('<text x="%d" y="%d" font-size="15" fill="%s" font-family="%s" '
                    'letter-spacing="2">%s</text>' % (x + 18, y + 32, OCHRE, FONT, _esc(label)))
        if sub:
            t, _ = _texts([sub], x + 18, y + 56, 12, INK, 46, 16)
            body.append(t)
    h = top + len(layers) * (bh + 12) + 44
    body.append(_foot(note, 0, h))
    return _svg(title, desc, h, "\n".join(body))


def emit(path, svg):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    return path


def _selfcheck(path):
    s = open(path, encoding="utf-8").read()
    bad = set(re.findall(r"#[0-9A-Fa-f]{6}", s)) - {PAPER, PAPER2, INK, OCHRE, BROWN, LINE}
    assert not bad, "非规定色 %s" % bad
    assert "<title>" in s and "<desc>" in s and "viewBox" in s, "缺 title/desc/viewBox"
    assert not re.search(r'<svg[^>]*(width|height)="[0-9]', s), "写了固定宽高"
    assert all(int(x) >= 11 for x in re.findall(r'font-size="([0-9]+)"', s)), "字号 <11"
    return path


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/figdemo"
    os.makedirs(out, exist_ok=True)
    emit(out + "/duizhao.svg", duizhao("天命与德", "左为俗见，右为正解", "俗见",
                                      ["天命写在天上，人只能服从"], "正解",
                                      ["天命看德，德看民", "民的安否，是天命的凭据"], note="看图看两栏的方向"))
    emit(out + "/ticheng.svg", ticheng("稽古三段", "递进示意",
                                      [("稽古", "先问"), ("慎德", "自约"), ("安民", "可验")], note="三步一线"))
    emit(out + "/sanlie.svg", sanlie("三才配位", "三层各归其位",
                                    [("天", ["识：神明了别"]), ("人", ["受想行：裁断"]), ("地", ["色：承载与民"])], note=""))
    emit(out + "/huan.svg", huan("五行", "环而无端", "皇极", ["水", "火", "木", "金", "土"], note=""))
    emit(out + "/juzhen.svg", juzhen("九畴", "九类九列", [], ["一", "二", "三"],
                                    [["五行", "水", "火", "木"], ["敬用", "貌", "言", "视"]], note=""))
    emit(out + "/ceng.svg", ceng("体用", "上体下用", [("体", "未发之度"), ("用", "发而中节")], note=""))
    for f in os.listdir(out):
        print(_selfcheck(os.path.join(out, f)))
