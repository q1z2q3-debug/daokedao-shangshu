#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""输出未过检篇号（有文件但 check_book 报错者），供 build_site 的 SKIP_IDS 用。"""
import json, re, subprocess, sys
out = subprocess.run([sys.executable, "scripts/check_book.py"], capture_output=True, text=True)
try:
    d = json.loads(out.stdout)
except Exception:
    print("", end=""); sys.exit(0)
# 只把「稿件本身」的硬伤算作未过检；站点产物类问题（页脚版本、缺页、sitemap、
# 首页目录、SVG 直链）是构建结果，构建后自然消失，不能据此拦稿。
SITE_MARKS = ("缺文件", "页脚版本不符", "页缺 SVG 直链", "站点缺")
ids = []
for f in d.get("FAIL", []):
    m = re.match(r"(SS\d+) ", f)
    if m and not any(k in f for k in SITE_MARKS):
        ids.append(m.group(1))
print(",".join(sorted(set(ids))), end="")
