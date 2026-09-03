# -*- coding: utf-8 -*-
"""DENSITY-SR 项目介绍书 -> A4 PDF (reportlab CJK, 自动分页+换行)."""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

MD = r"C:/Users/mine/Downloads/quant_research/项目介绍书.md"
OUT = r"C:/Users/mine/Downloads/quant_research/项目介绍书.pdf"
pdfmetrics.registerFont(UnicodeCIDFont("STSong-Light"))
F = "STSong-Light"
C1 = colors.HexColor("#E97C16")   # section 标题橙
C2 = colors.HexColor("#B4570B")   # h1 深橙
C3 = colors.HexColor("#F0A500")   # 强调
INK = colors.HexColor("#1D1F27")

W, H = A4
M = 20*mm
MAXW = (W - 2*M)
lines = open(MD, encoding="utf-8").read().split(chr(10))

c = canvas.Canvas(OUT, pagesize=A4)
c.setTitle("DENSITY-SR 项目详细介绍书")
y = float(H - 26*mm)

def nl(dy):
    global y
    y -= dy
    if y < 26*mm:
        c.showPage()
        y = H - 26*mm

def draw_wrapped(text, size, fill, indent=0, leading_mult=1.5):
    global y
    c.setFont(F, size)
    c.setFillColor(fill)
    lw = (W - 2*M) - indent
    # 近似: 中文一个字符约=size pt 的宽度(全角), ASCII 约 0.55*size
    half = 0.55
    # 估算每行最大字符数
    maxchars = int(lw / (size * 0.5))  # 全角占 0.5*size? 实际全角≈1.0em. 用 0.5em估算宽度=size*0.5
    # 更稳妥: 用全角宽度 size (即每字符 size 磅). 行内可容纳 char = lw/ (size*0.5)
    chars_per_line = int(lw / (size * 0.5))
    # 按字形宽拆分(CHN fullwidth ~ size; ascii ~0.5size; 混合, 简化按 0.5size 平均)
    # 只是一个参考: 我们按可用宽度把文本断行
    cur = ""
    col = 0.0
    for ch in text:
        wch = size*1.0 if ord(ch) > 0x2E80 else size*0.5  # 全角/半角
        if col + wch > lw - size*0.5:
            c.drawString(M+indent, y, cur)
            y -= size*1.9
            if y < 26*mm: c.showPage(); y = H-26*mm
            cur = ch; col = wch
        else:
            cur += ch; col += wch
    if cur:
        c.drawString(M+indent, y, cur)
        y -= size*1.9
        if y < 26*mm: c.showPage(); y = H-26*mm

seen_title = False
for raw in lines:
    s = raw.rstrip()
    if not s.strip():
        y -= 2*mm; 
        if y < 26*mm: c.showPage(); y = H-26*mm
        continue
    if s.startswith("# "):
        if seen_title:
            c.showPage(); y = H-26*mm
        seen_title = True
        y -= 4*mm
        c.setFont(F, 20); c.setFillColor(C2)
        c.drawString(M, y, s[2:].strip())
        c.setStrokeColor(C2); c.setLineWidth(1.2)
        c.line(M, y-2.5*mm, W-M, y-2.5*mm)
        y -= 12*mm
    elif s.startswith("## "):
        y -= 5*mm
        c.setFont(F, 14); c.setFillColor(C1)
        c.drawString(M, y, s[3:].strip())
        c.setStrokeColor(C1); c.setLineWidth(0.5)
        c.line(M, y-1.6*mm, W-M, y-1.6*mm)
        y -= 7*mm
    elif s.startswith("### "):
        y -= 4*mm
        c.setFont(F, 12); c.setFillColor(C2)
        c.drawString(M, y, s[4:].strip())
        y -= 6*mm
    elif s.startswith("|"):
        cells = [x.strip() for x in s.strip("|").split("|")]
        if all(set(x).issubset("-:") for x in cells):
            y -= 1.5*mm; continue
        y -= 1.6*mm
        draw_wrapped("   |   ".join(cells), 9, INK)
        y -= 1.5*mm
    else:
        body = s
        if s.startswith(("- ", "1. ")):
            body = "  " + s[s.index(" ")+1:]
        body = body.replace("**", "")
        draw_wrapped(body, 10.5, INK)

c.showPage()
c.save()
print("PDF_OK", OUT)