# -*- coding: utf-8 -*-
"""生成校勘台：单文件 HTML，七块面板 + 筛选 + 勾选进度 + 导出 CSV（全内联，零外链）"""
import csv, os, html

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(name):
    return list(csv.DictReader(open(os.path.join(ROOT, 'data', name), encoding='utf-8')))


dizhang = load('jiaokan-dizhang.csv')
duikan = load('jingwen-duikan.csv')
yanshou = load('jiaokan-yanshou.csv')
zhushu = load('zhushu-yiwen.csv')
daijiao = load('jiaokan-daijiao.csv')
dunhuang = load('dunhuang-shangshu.csv')
pang = load('shijing-pangzheng.csv')
ok = sum(1 for r in duikan if r['结论'] == '一致')


def tbl(rows, cols, label, checkbox=False):
    th = ''.join('<th>%s</th>' % html.escape(c) for c in cols)
    body = []
    for i, r in enumerate(rows):
        cells = []
        if checkbox:
            cells.append('<td class="ck"><input type="checkbox" data-key="%s-%d"></td>' % (label, i))
        for c in cols:
            v = r.get(c, '')
            cls = ''
            if c in ('结论', '校核状态', '状态'):
                if v.startswith('一致') or v.startswith('已'):
                    cls = ' class="good"'
                elif '未' in v or '待' in v:
                    cls = ' class="wait"'
                elif '差异' in v:
                    cls = ' class="bad"'
            cells.append('<td%s>%s</td>' % (cls, html.escape(v)))
        body.append('<tr data-text="%s">%s</tr>' % (html.escape(' '.join(r.get(c, '') for c in cols)), ''.join(cells)))
    return ('<section class="panel" id="%s"><h2>%s <span class="cnt">%d 条</span></h2>'
            '<div class="tw"><table><thead><tr>%s%s</tr></thead><tbody>%s</tbody></table></div></section>'
            % (label, html.escape(label), len(rows), '<th class="ck">核</th>' if checkbox else '', th, ''.join(body)))


T = r'''<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8">
<title>校勘台 · 润泽说 道可道之尚书</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
:root{--paper:#F7F4EE;--ink:#25211D;--red:#994433;--brown:#7C6D5C;--line:#DCD5C8}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);font:15px/1.75 "Noto Serif SC","Songti SC",serif}
.wrap{max-width:1180px;margin:0 auto;padding:28px 20px 80px}
h1{font-size:26px;margin:0 0 6px;letter-spacing:.08em}
.lead{color:var(--brown);font-size:14px;margin:0 0 18px}
.bar{position:sticky;top:0;z-index:9;background:var(--paper);border-bottom:1px solid var(--line);padding:12px 0;display:flex;gap:10px;flex-wrap:wrap;align-items:center}
input[type=search]{flex:1;min-width:200px;border:1px solid var(--line);background:#fff;padding:8px 10px;font:inherit}
select{border:1px solid var(--line);background:#fff;padding:8px;font:inherit}
.meter{display:flex;gap:14px;flex-wrap:wrap;margin:14px 0 22px}
.card{flex:1;min-width:150px;border:1px solid var(--line);background:#FCFAF6;padding:12px 14px}
.card b{display:block;font-size:22px;color:var(--red)}
.card span{font-size:13px;color:var(--brown)}
.panel{margin:26px 0 10px;border-top:2px solid var(--ink);padding-top:12px}
.panel h2{font-size:17px;margin:0 0 10px;letter-spacing:.05em}
.cnt{font-weight:400;font-size:12px;color:var(--brown);letter-spacing:0}
.tw{overflow:auto;border:1px solid var(--line);background:#fff}
table{border-collapse:collapse;width:100%;font-size:13px}
th,td{border-bottom:1px solid var(--line);padding:7px 9px;text-align:left;vertical-align:top}
thead th{background:#F1ECE2;position:sticky;top:0;font-weight:600;white-space:nowrap}
td.ck,th.ck{width:34px;text-align:center}
td.good{color:#3E6B4F}td.wait{color:#8A6A2F}td.bad{color:var(--red)}
tr:hover td{background:#FCF8F1}
.foot{margin-top:40px;border-top:1px solid var(--line);padding-top:14px;color:var(--brown);font-size:13px}
.tools{display:flex;gap:8px;flex-wrap:wrap}
button{border:1px solid var(--line);background:#fff;padding:8px 12px;font:inherit;cursor:pointer}
button:hover{border-color:var(--red);color:var(--red)}
@media(max-width:640px){table{font-size:12px}th,td{padding:6px}}
</style></head><body><div class="wrap">
<h1>校勘台</h1>
<p class="lead">润泽说 道可道之尚书 · 校勘工作面　v0.3.8　底本《尚书正义》通行本五十八篇　一页可筛、可勾、可导出。</p>
<div class="bar">
  <input id="q" type="search" placeholder="搜字、搜句、搜篇名（如「尊王之路」「酒诰」）">
  <select id="f"><option value="">全部面板</option>
  <option>底账十五目</option><option>自校五十八篇</option><option>到影即核</option><option>注疏异文</option><option>施工账</option><option>敦煌写本</option><option>石经旁证</option></select>
  <div class="tools"><button id="all">全勾</button><button id="none">全清</button><button id="exp">导出已勾 CSV</button></div>
</div>
<div class="meter">
  <div class="card"><b>@@OK@@ / @@N@@</b><span>自校一致（稿与底本逐字）</span></div>
  <div class="card"><b>15</b><span>底账异文条目</span></div>
  <div class="card"><b>@@ZH@@</b><span>注疏异文条目</span></div>
  <div class="card"><b id="ckn">0 / @@YS@@</b><span>已核对（本地保存）</span></div>
</div>
@@P1@@
@@P2@@
@@P3@@
@@P4@@
@@P5@@
@@P6@@
@@P7@@
<div class="foot">
  用法：勾选「核」列记下每一条已核对者，进度存本机（localStorage），换机不带走。搜索框对全表生效，面板下拉只留一块。<br>
  四表口径：底账＝异文（不改）；自校＝误录（已改）；到影即核＝待影核对（不预设结论）；注疏＝异说（两存待裁）。<br>
  数据文件：data/jiaokan-dizhang.csv、jingwen-duikan.csv、jiaokan-yanshou.csv、zhushu-yiwen.csv、jiaokan-daijiao.csv、dunhuang-shangshu.csv、shijing-pangzheng.csv　<a href="fu/03-jiaokan.html">回附录三</a>　<a href="index.html">回目录</a>
</div></div>
<script>
const KEY='ss-jiaokan-check-v1';
const store=JSON.parse(localStorage.getItem(KEY)||'{}');
const boxes=[...document.querySelectorAll('input[type=checkbox][data-key]')];
function upd(){
  let n=0;
  boxes.forEach(b=>{b.checked=!!store[b.dataset.key];if(b.checked)n++;});
  const el=document.getElementById('ckn'); if(el) el.textContent=n+' / '+boxes.length;
}
boxes.forEach(b=>b.addEventListener('change',()=>{if(b.checked)store[b.dataset.key]=1;else delete store[b.dataset.key];localStorage.setItem(KEY,JSON.stringify(store));upd();}));
upd();
</script><script>
const q=document.getElementById('q'), f=document.getElementById('f');
document.querySelectorAll('section.panel').forEach(sec=>{
  const c=sec.querySelector('.cnt'); const n=sec.querySelectorAll('tbody tr').length; if(c){c.dataset.n=n;c.textContent=n+' 条';}
});
function filt(){
  const kw=(q.value||'').trim().toLowerCase(), pan=f.value;
  document.querySelectorAll('section.panel').forEach(sec=>{
    sec.style.display=(!pan||sec.id===pan)?'':'none';
    let hit=0;
    sec.querySelectorAll('tbody tr').forEach(tr=>{
      const t=(tr.dataset.text||'').toLowerCase();
      const need=!kw||t.includes(kw);
      tr.style.display=need?'':'none'; if(need)hit++;
    });
    const c=sec.querySelector('.cnt');
    const base=c?c.dataset.n:0;
    if(c) c.textContent = kw ? (hit+' 条命中 / 原 '+base) : (base+' 条');
  });
}
q.addEventListener('input',filt); f.addEventListener('change',filt);
</script><script>
document.getElementById('all').onclick=()=>{boxes.forEach(b=>{store[b.dataset.key]=1;b.checked=true});localStorage.setItem(KEY,JSON.stringify(store));upd();};
document.getElementById('none').onclick=()=>{Object.keys(store).forEach(k=>delete store[k]);localStorage.setItem(KEY,'{}');upd();};
document.getElementById('exp').onclick=()=>{
  const lines=['面板,核,内容'];
  document.querySelectorAll('section.panel').forEach(sec=>{
    sec.querySelectorAll('tbody tr').forEach(tr=>{
      const cb=tr.querySelector('input[type=checkbox]');
      if(cb&&store[cb.dataset.key]) lines.push([sec.id,'已核',tr.dataset.text.replace(/"/g,'""')].map(x=>'"'+x+'"').join(','));
    });
  });
  const blob=new Blob(['\ufeff'+lines.join('\n')],{type:'text/csv;charset=utf-8'});
  const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='校勘台-已核.csv';a.click();
};
</script></body></html>'''

blocks = [
    tbl(dizhang, ['篇序', '篇名', '条目', '底本原句', '异文与异读', '本书处置', '校核状态'], '底账十五目'),
    tbl(duikan, ['篇序', '篇名', '底本字数', '稿字数', '结论', '首处差异', '差异段数'], '自校五十八篇'),
    tbl(yanshou, ['篇序', '篇名', '条目', '待核字', '现存异说', '到影验收标准', '状态'], '到影即核', True),
    tbl(zhushu, ['篇序', '篇名', '类型', '原文摘录', '出处', '本书处置'], '注疏异文', True),
    tbl(daijiao, ['序', '项', '所需材料', '取得渠道', '验收标准', '状态'], '施工账'),
    tbl(dunhuang, ['编号', '藏地', '内容', '依据', '可核项', '状态'], '敦煌写本', True),
    tbl(pang, ['条目', '年代', '刻立地', '数目与尺寸', '性质', '可核项与限度'], '石经旁证'),
]

out = T
for k, v in {'@@OK@@': str(ok), '@@N@@': str(len(duikan)), '@@ZH@@': str(len(zhushu)), '@@YS@@': str(len(yanshou))}.items():
    out = out.replace(k, v)
for i, b in enumerate(blocks, 1):
    out = out.replace('@@P%d@@' % i, b)

path = os.path.join(ROOT, 'docs', 'jiaokan.html')
open(path, 'w', encoding='utf-8').write(out)
print('校勘台已生成 docs/jiaokan.html', len(out) // 1024, 'KB')
