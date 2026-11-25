# -*- coding: utf-8 -*-
"""稿与底本逐字对勘：book/SSnn-*.md 的【经】段 vs data/底本 原文，输出 data/jingwen-duikan.csv"""
import re,glob,csv,difflib,os
base=open('data/底本/尚书·五十八篇原文.md',encoding='utf-8').read()
def segs(txt):
    return [l.strip() for l in txt.split('\n') if l.strip().startswith('【经】')]
rows=[]
for f in sorted(glob.glob('book/SS[0-9][0-9]-*.md')):
    m=re.match(r'SS(\d\d)-(.+)\.md',os.path.basename(f)); pid,name=m.group(1),m.group(2)
    blk=[x for x in re.split(r'\n## ',base) if x.startswith(pid)]
    if not blk: rows.append([pid,name,0,0,'底本缺','',0]); continue
    bsegs=[re.sub(r'^【经】','',s) for s in segs(blk[0])]
    t=open(f,encoding='utf-8').read()
    jt=t.split('## 二　经文')[1].split('\n## ')[0]
    msegs=[re.sub(r'^【经】','',s) for s in segs(jt)]
    b=''.join(bsegs); mm=''.join(msegs)
    sm=difflib.SequenceMatcher(None,b,mm,autojunk=False)
    diffs=[op for op in sm.get_opcodes() if op[0]!='equal']
    first=''
    if diffs:
        t,a1,a2,b1,b2=diffs[0]
        first=f"{t}：底本「{b[max(0,a1-4):a2+4]}」→ 稿「{mm[max(0,b1-4):b2+4]}」"
    rows.append([pid,name,len(b),len(mm),'一致' if not diffs else f'差异{len(diffs)}',first,len(diffs)])
with open('data/jingwen-duikan.csv','w',encoding='utf-8',newline='') as fp:
    w=csv.writer(fp);w.writerow(['篇序','篇名','底本字数','稿字数','结论','首处差异','差异段数']);w.writerows(rows)
ok=sum(1 for r in rows if r[4]=='一致')
print(f'篇数 {len(rows)}　一致 {ok}　有差异 {len(rows)-ok}')
for r in rows:
    if r[4]!='一致': print(r[0],r[1],r[2],r[3],r[6],r[5][:120])
