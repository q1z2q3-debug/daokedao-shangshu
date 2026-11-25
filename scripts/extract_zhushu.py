# -*- coding: utf-8 -*-
"""从 book/SSnn-*.md 的注疏节与脚注中抽取异文异读异训，输出 data/zhushu-yiwen.csv"""
import glob,re,csv,os
PAT=re.compile(r'(一作|或作|亦作|异文|一本|读为|读曰|释文|今文作|古文作|俗本|音义|异读|两存|从孔|从郑|蔡传|孔传|孔疏)')
NOISE=re.compile(r'(把「[^」]*」当作|当作实迹|当作事功|当作心法|当作口号|不把)')
BOOK=re.compile(r'《[^》]{2,12}》')
rows=[]
for f in sorted(glob.glob('book/SS*.md')):
    pid=os.path.basename(f)[:4]; pid=pid[2:]
    name=re.match(r'SS\d\d-(.+)\.md',os.path.basename(f)).group(1)
    t=open(f,encoding='utf-8').read()
    secs=re.split(r'\n## ',t)
    zh=[s for s in secs if s.startswith('六　注疏') or s.startswith('七　分寸')]
    fn=[l for l in t.split('\n') if re.match(r'^\[\^\d+\]', l)]
    cand=[]
    for s in zh:
        cand += [l for l in s.split('\n') if PAT.search(l) and not NOISE.search(l)]
    cand += [l for l in fn if PAT.search(l) and not NOISE.search(l)]
    seen=set()
    for l in cand:
        s=l.strip()
        if s in seen: continue
        seen.add(s)
        typ=('异文' if re.search(r'(一作|或作|亦作|异文|一本|今文作|古文作|俗本)',s) else
             '异读' if re.search(r'(读为|读曰|音义|异读|释文)',s) else
             '异训' if re.search(r'(孔传|蔡传|孔疏|训)',s) else '异说')
        src='／'.join(sorted(set(BOOK.findall(s)))) or '注疏'
        disp='本书从底本' if re.search(r'(本书从|照录|照底本)',s) else ('两存' if '两存' in s else '见本篇注疏')
        body=re.sub(r'^\[[^\]]*\]\s*:?\s*','',s); body=re.sub(r'^\*\*|\*\*$','',body)
        rows.append([pid,name,typ,body[:120],src,disp])
with open('data/zhushu-yiwen.csv','w',encoding='utf-8',newline='') as f:
    w=csv.writer(f); w.writerow(['篇序','篇名','类型','原文摘录','出处','本书处置']); w.writerows(rows)
print('条数',len(rows),'篇数',len({r[0] for r in rows}))
