# -*- coding: utf-8 -*-
"""把最新阅读版与校勘台装进 APK 资产（assets/index.html + assets/jiaokan.html），可复跑。"""
import os, re, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, 'dist', 'apk-shangshu', 'app', 'src', 'main', 'assets')

book = open(os.path.join(ROOT, 'docs', 'book-full.html'), encoding='utf-8').read()
ver = re.search(r'v(\d+\.\d+\.\d+)', re.search(r'<title>(.*?)</title>', book).group(1)).group(1)

# 首页加一枚固定入口，指向本包内的校勘台
btn = ('<a href="jiaokan.html" style="position:fixed;right:14px;bottom:18px;z-index:99;'
       'background:#994433;color:#fff;text-decoration:none;padding:10px 14px;border-radius:6px;'
       'font:14px/1.4 \'Noto Serif SC\',\'Songti SC\',serif;box-shadow:0 2px 8px rgba(0,0,0,.18);">校勘台</a>')
if 'jiaokan.html" style="position:fixed' not in book:
    book = book.replace('</body>', btn + '\n</body>', 1)
open(os.path.join(ASSETS, 'index.html'), 'w', encoding='utf-8').write(book)

# 校勘台：站内链改成包内链
desk = open(os.path.join(ROOT, 'docs', 'jiaokan.html'), encoding='utf-8').read()
desk = desk.replace('href="fu/03-jiaokan.html">回附录三</a>', 'href="index.html">回全書</a>')
desk = desk.replace('<a href="index.html">回目录</a>', '<a href="index.html">回書首</a>')
open(os.path.join(ASSETS, 'jiaokan.html'), 'w', encoding='utf-8').write(desk)

print('assets/index.html %.2f MB' % (len(book) / 1048576))
print('assets/jiaokan.html %.0f KB' % (len(desk) / 1024))
print('version', ver)
