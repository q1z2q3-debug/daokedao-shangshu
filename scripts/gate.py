#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""输出未过检篇号（有文件但 check_book 报错者），供 build_site 的 SKIP_IDS 用。"""
import json, re, subprocess, sys
out = subprocess.run([sys.executable, "scripts/check_book.py"], capture_output=True, text=True)
try:
    d = json.loads(out.stdout)
except Exception:
    print("", end=""); sys.exit(0)
ids = []
for f in d.get("FAIL", []):
    m = re.match(r"(SS\d+) ", f)
    if m and "缺文件" not in f:
        ids.append(m.group(1))
print(",".join(sorted(set(ids))), end="")
