# -*- coding: utf-8 -*-
"""生成 公众号排版 HTML(内联样式, 可直接粘进公众号编辑器)。"""
import html as _h
MD = r"C:/Users/mine/Downloads/quant_research/项目介绍书.md"
OUT = r"C:/Users/mine/Downloads/quant_research/项目介绍书_公众号.html"
lines = open(MD, encoding="utf-8").read().split(chr(10))
def esc(s): return _h.escape(s)

CSS = "<style>" + chr(10) + "body{background:#fff;color:#1d1f27;font-family:-apple-system,'PingFang SC','Microsoft YaHei',sans-serif;line-height:1.8;margin:0;padding:16px 12px;font-size:16px}" + chr(10) + "h1{font-size:22px;color:#B4570B;border-left:6px solid #E97C1D;padding-left:10px;margin:6px 0 12px}" + chr(10) + "h2{font-size:19px;color:#E07C10;border-bottom:2px solid #F0C04B;padding-bottom:5px;margin:24px 0 8px}" + chr(10) + "h3{font-size:16px;color:#B4570B;margin:14px 0 5px}" + chr(10) + "blockquote{background:#FFF6E6;border-left:4px solid #F0C04B;padding:7px 11px;border-radius:4px;font-size:15px;margin:8px 0}" + chr(10) + "table{border-collapse:collapse;width:100%;margin:8px 0;font-size:13.5px}" + chr(10) + "th,td{border:1px solid #E3E6EA;padding:5px 7px;text-align:left;font-size:13.5px}" + chr(10) + "th{background:#1D1F27;color:#fff}" + chr(10) + "tr:nth-child(even){background:#FDF3E2}" + chr(10) + "li{margin:3px 0}p{margin:5px 0}" + chr(10) + "</style>"

out = ['<!doctype html><html><head><meta charset="utf-8">' + CSS + '</head><body>']
intable = False
for ln in lines:
    s = ln.strip()
    if not s:
        continue
    if s.startswith("# "):
        out.append('<h1>' + esc(s[2:]) + '</h1>')
    elif s.startswith("## "):
        intable and out.append('</table>'); intable = False
        out.append('<h2>' + esc(s[3:]) + '</h2>')
    elif s.startswith("### "):
        intable and out.append('</table>'); intable = False
        out.append('<h3>' + esc(s[4:]) + '</h3>')
    elif s.startswith("|"):
        cells = [c.strip() for c in s.strip("|").split("|")]
        if all(set(c).issubset("-:") for c in cells):
            continue
        if not intable:
            out.append('<table>'); intable = True
            out.append('<tr>' + ''.join('<th>' + esc(x) + '</th>' for x in cells) + '</tr>')
        else:
            out.append('<tr>' + ''.join('<td>' + esc(x) + '</td>' for x in cells) + '</tr>')
    else:
        if intable:
            out.append('</table>'); intable = False
        body = s
        if s.startswith("- ") or s.startswith("1. "):
            body = s[s.index(" ") + 1:]
            out.append('<li>' + esc(body) + '</li>')
        else:
            out.append('<p>' + esc(body) + '</p>')
if intable:
    out.append('</table>')
out.append('<hr style="border:none;border-top:2px solid #F0C04B;margin:22px 0">'
           '<p style="color:#999;font-size:12px;text-align:center">© DENSITY·SR · 本地量化研究工具 · 仅供学习研究, 不构成投资建议</p>'
           '</body></html>')
open(OUT, "w", encoding="utf-8").write("".join(out))
print("WECHAT_OK", OUT)
