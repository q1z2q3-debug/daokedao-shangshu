# -*- coding: utf-8 -*-
"""站点样式（纸墨五色），全书唯一 CSS 源。.mk.x{color:#7C6D5C;border-color:#C9BFAF;background:#F5F1E8}
"""

CSS = """
:root{--paper:#F7F4EE;--paper2:#FCFAF6;--ink:#25211D;--ink2:#3B352F;
  --ochre:#994433;--brown:#7C6D5C;--line:#DCD5C8}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:#F7F4EE;color:#25211D;
  font-family:"Noto Serif SC","Songti SC","Source Han Serif SC",serif;
  font-size:17px;line-height:1.95;letter-spacing:.01em}
a{color:#994433;text-decoration:none;border-bottom:1px solid rgba(153,68,51,.28)}
a:hover{border-bottom-color:#994433}
.bar{background:#FCFAF6;border-bottom:1px solid #DCD5C8;padding:9px 16px;
  font-family:"Noto Sans SC","PingFang SC",sans-serif;font-size:12px;letter-spacing:.1em;
  color:#7C6D5C;display:flex;justify-content:space-between;align-items:baseline;gap:12px}
.wrap{max-width:780px;margin:0 auto;padding:34px 22px 64px}
h1.title{font-size:40px;line-height:1.4;margin:0 0 10px;font-weight:600;letter-spacing:.1em}
h1.ch,h2.ch{font-size:30px;letter-spacing:.16em;margin:6px 0 6px;font-weight:600}
h2{font-size:23px;margin:44px 0 8px;letter-spacing:.14em;font-weight:600}
h2 small{font-size:12px;color:#7C6D5C;letter-spacing:.1em;margin-left:10px;font-weight:400}
h3{font-size:15px;letter-spacing:.08em;color:#994433;margin:26px 0 6px;
  padding-bottom:4px;border-bottom:1px solid #DCD5C8}
p{margin:0 0 1.05em;text-align:justify}
blockquote{margin:1.1em 0;padding:14px 18px;background:#FCFAF6;
  border-left:3px solid #DCD5C8;color:#3B352F}
blockquote p{margin:0 0 .7em}
blockquote p:last-child{margin-bottom:0}
.mk{display:inline-block;font-size:11px;line-height:1.6;letter-spacing:.08em;
  padding:0 5px;margin-right:6px;border:1px solid #DCD5C8;border-radius:2px;
  vertical-align:2px;font-family:"Noto Sans SC","PingFang SC",sans-serif}
.mk.k{color:#994433;border-color:#D8B9AD;background:#FBF1EC}
.mk.z{color:#7C6D5C;border-color:#DCD5C8;background:#FCFAF6}
.mk.y{color:#25211D;border-color:#BDB4A6;background:#F5F1E8}
.mk.yong{color:#3B352F;border-color:#C9BFAF;background:#F1ECE2}
.figbox{margin:26px 0 8px;padding:14px;background:#FCFAF6;border:1px solid #DCD5C8}
.figbox svg,.fig{width:100%;height:auto;max-width:720px;display:block;margin:0 auto}
.figlink{display:block;text-decoration:none;color:inherit}
.figcap a{color:#7C6D5C;text-decoration:none;border-bottom:1px solid #DCD5C8}
.figcap{font-size:12px;color:#7C6D5C;text-align:center;margin-top:8px;letter-spacing:.06em}
.lead{font-size:13.5px;color:#7C6D5C;margin:0 0 16px;letter-spacing:.03em}
.list{border-top:1px solid #DCD5C8}
.item{padding:16px 0 14px;border-bottom:1px solid #E7E0D4}
.item .no{font-size:11.5px;letter-spacing:.22em;color:#994433;
  font-family:"Noto Sans SC",sans-serif;margin-bottom:5px}
.item .t{font-size:19px;letter-spacing:.03em;margin:0 0 4px}
.item .s{font-size:13px;color:#5C5348;margin:0 0 6px}
.item .k{font-size:12.5px;color:#7C6D5C}
.rows{border-top:1px solid #DCD5C8;margin-top:6px}
.row{display:grid;grid-template-columns:132px 1fr;gap:14px;padding:13px 0;
  border-bottom:1px solid #E7E0D4}
.row .kk{font-size:12.5px;color:#994433;letter-spacing:.12em;
  font-family:"Noto Sans SC",sans-serif}
.row .vv{font-size:15px}
.series-grid{display:grid;grid-template-columns:repeat(4,1fr);
  gap:1px;margin-top:8px;border-top:1px solid #DCD5C8;border-left:1px solid #E7E0D4}
.series-grid a{display:block;padding:11px 12px;font-size:14px;border:0;
  border-right:1px solid #E7E0D4;border-bottom:1px solid #E7E0D4;background:#FCFAF6}
.series-grid a small{display:block;font-size:11px;color:#8E8071;letter-spacing:.08em;margin-top:2px}
.btn{display:inline-block;border:1px solid #994433;color:#994433;padding:6px 16px;
  font-size:13px;letter-spacing:.12em;margin-top:10px}
.pn{display:grid;grid-template-columns:1fr auto 1fr;gap:12px;align-items:center;
  margin:48px 0 0;padding:16px 0;border-top:1px solid #DCD5C8;
  font-size:13px;letter-spacing:.06em}
.pn a{border:0}
.pn .mid{text-align:center;color:#7C6D5C}
.pn .right{text-align:right}
.xu-sep{text-align:center;color:#7C6D5C;letter-spacing:.4em;margin:44px 0 40px;font-size:15px}
.foot{margin-top:36px;padding-top:14px;border-top:1px solid #DCD5C8;
  font-size:12px;color:#7C6D5C;line-height:2}
.foot a{margin-right:12px}
aside.footnotes,section.footnotes{font-size:13px;color:#3B352F;border-top:1px solid #DCD5C8;margin-top:40px;padding-top:6px}
aside.footnotes li p,section.footnotes li p{margin:.4em 0}
aside.footnotes hr,section.footnotes hr{display:none}
aside.footnotes ol,section.footnotes ol{padding-left:1.6em}
sup.fn a{font-size:11px;color:#994433;text-decoration:none;padding:0 1px}
a,code,td,th{overflow-wrap:anywhere;word-break:break-word}
ol,ul{padding-left:1.3em}
table.t{width:100%;border-collapse:collapse;margin:16px 0;table-layout:fixed;
  font-size:14px;border-top:1px solid #DCD5C8}
table.t th,table.t td{border-bottom:1px solid #E7E0D4;padding:9px 8px;text-align:left;
  vertical-align:top;word-break:break-word}
table.t th{color:#994433;font-weight:600;letter-spacing:.08em;background:#FCFAF6}
@media (max-width:640px){
  .wrap{padding:24px 16px 52px}
  h1.title{font-size:27px;letter-spacing:.05em}
  h1.ch,h2.ch{font-size:23px;letter-spacing:.08em}
  h2{font-size:19px;margin:34px 0 6px;letter-spacing:.06em}
  .row{grid-template-columns:1fr;gap:4px}
  .bar{font-size:11.5px;letter-spacing:.04em}
  .pn{grid-template-columns:1fr 1fr;row-gap:8px}
  .pn .mid{display:none}
  table.t{font-size:12.5px}
  .series-grid{grid-template-columns:1fr 1fr}
  .figbox{padding:8px 0 4px;overflow-x:auto;-webkit-overflow-scrolling:touch}
  .figbox svg{width:620px;max-width:none;margin:0 4px}
  .figcap{font-size:11.5px;padding:0 8px}
}

.tagline{margin:6px 0 26px;font-family:"Noto Sans SC","PingFang SC",sans-serif;font-size:12px;letter-spacing:.22em;color:#7C6D5C}
.tagline .jw{color:#994433}
.tagline .by{color:#7C6D5C}
.badge{display:inline-block;font-size:10.5px;line-height:1.7;padding:0 5px;margin-left:6px;border:1px solid #D8B9AD;background:#FBF1EC;color:#994433;letter-spacing:.1em;vertical-align:1px;font-family:"Noto Sans SC",sans-serif}
.badge.gu{color:#7C6D5C;border-color:#DCD5C8;background:#F7F4EE}
.vol{font-size:13px;letter-spacing:.3em;color:#994433;margin:34px 0 2px;padding-bottom:6px;border-bottom:1px solid #DCD5C8}
"""
