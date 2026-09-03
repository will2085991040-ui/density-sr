# -*- coding: utf-8 -*-
"""把 项目介绍书.md 排版为 Excel(.xlsx) 与 公众号(HTML 内联样式) 两版。"""
import os
MD = r'C:/Users/mine/Downloads/quant_research/项目介绍书.md'
XLSX = r'C:/Users/mine/Downloads/quant_research/项目介绍书_Excel.xlsx'
HTMLWECHAT = r'C:/Users/mine/Downloads/quant_research/项目介绍书_公众号.html'
txt = open(MD, encoding='utf-8').read()
lines = txt.split('\n')

# ---------- Excel ----------
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
wb = Workbook(); ws = wb.active; ws.title = '项目介绍'
orange = 'F0A500'; dark = '1B1F27'; white = 'FFFFFF'
hdr_f = Font(bold=True, color=white, size=13)
hdr_fill = PatternFill('solid', fgColor='1B1F27')
sec_f = Font(bold=True, color='FF8C00', size=13)
sub_f = Font(bold=True, size=11)
thin = Side(style='thin', color='B8C0CC')
border = Border(left=thin,right=thin,top=thin,bottom=thin)
title_cell = ws.cell(1,1, txt.splitlines()[0].lstrip('# ').strip())
title_cell.font = Font(bold=True, size=16, color=orange)
title_cell.alignment = Alignment(horizontal='left', vertical='center')
ws.merge_cells('A1:E1'); ws.row_dimensions[1].height = 28

# 功能全景 / 情绪表 / 原理 手动表数据
tables = [
  ('功能全景', [('模块','功能','入口'),
    ('支撑阻力引擎','全量A股SR带(日线/60分/15分); 支撑/压力/触及与守住概率','品种行点击/搜索'),
    ('多周期图表','日线/60分/15分; K线+MA5/10/20/60+量能+MACD','顶部周期下拉'),
    ('分时实时盯盘','白现价/黄均价/灰昨收; 涨跌停参考线; 每15秒刷新','实时盘/分时按钮'),
    ('AI联网研判','双agent + AI K线分析 / 因子挖掘','AI面板按钮'),
    ('市场情绪','温度0-100°; 涨跌结构; 涨停; 建议仓位','情绪卡'),
    ('策略信号','触发位→方向/入场/止损/目标/风比/情绪过滤','策略信号卡'),
    ('本地数据','内嵌全量数据、离线可用、数据不出本机','内置')]),
  ('温度-建议映射', [('温度','情绪','策略 / 仓位'),
    ('78-100','亢奋','警惕过热, 减仓不追高'),
    ('55-77','偏多','顺势为主, 可适度加仓'),
    ('45-54','中性','精选控仓'),
    ('27-44','偏空','防守降仓'),
    ('0-26','冰点','观望或分批左侧埋伏, 等赚钱效应修复')])
]
r = 3
for name, rows in tables:
    ws.cell(r,1,name).font = sec_f; r += 1
    for idx,h in enumerate(rows[0], start=1):
        c = ws.cell(r,idx,h); c.font=hdr_font; c.fill=hdr_fill; c.border=border; c.alignment=Alignment(horizontal='center')
    r += 1
    for row in rows[1:]:
        for idx,val in enumerate(row, start=1):
            c = ws.cell(r,idx,val); c.border=border; c.alignment=Alignment(vertical='top', wrap_text=True)
        r += 1
    r += 1
for col in range(1,5): ws.column_dimensions[get_column_letter(col)].width = 22
wb.save(XLSX)
print('EXCEL_OK', XLSX)

# ========= 公众号 HTML ==========
import html
def esc(s): return html.escape(s)
# 标题映射工具
out = []
out.append('''<!doctype html><html><head><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1"><title>DENSITY·SR 项目介绍</title>
<style>body{background:#fff;color:#1d1f27;font-family:-apple-system,'PingFang SC','Microsoft YaHei',sans-serif;line-height:1.75;margin:0;padding:18px 14px;font-size:16px}
h1{font-size:24px;color:#B4660B;border-left:6px solid #E97C1D;padding-left:10px}
h2{font-size:20px;color:#E97C1D;border-bottom:2px solid #F0C04B;padding-bottom:5px;margin-top:26px}
h3{font-size:17px;color:#B4660B}
blockquote{background:#FFF6E6;border-left:4px solid #F0C04B;padding:6px 10px;border-radius:4px;font-size:15px}
table{border-collapse:collapse;width:100%;margin:8px 0;font-size:14px}
th,td{border:1px solid #E3E6EA;padding:6px 8px;text-align:left}th{background:#1D1F27;color:#fff}tr:nth-child(even){background:#FAF8F3}
.kv{border-left:3px solid #E97C1D;background:#FBF7F0;padding:8px 12px;border-radius:4px;margin:6px 0}
li{margin:3px 0}</style></head><body>'''

#turn md to simple html
def em(s): return esc(s)
for ln in lines:
    s = ln.strip()
    if not s: continue
    if s.startswith('# '):
        out.append('<h1>'+esc(s[2:])+'</h1>')
    elif s.startswith('## '):
        out.append('<h2>'+esc(s[3:])+'</h2>')
    elif s.startswith('### '):
        out.append('<h3>'+esc(s[4:])+'</h3>')
    elif s.startswith('|') :
        # 简易表格（第一行表头）
        cells=[c.strip() for c in s.strip('|').split('|')]
        if all(set(c) <= set('-') for c in cells): continue
        if len(cells)==1: continue
        if not rows:
            out.append('<table><tr>'+''.join('<th>'+esc(x)+'</th>' for x in cells)+'</tr>')
            rows=True
        else:
            out.append('<tr>'+''.join('<td>'+esc(x)+'</td>' for x in cells)+'</tr>')
    elif s=='' : rows=False 
    else:
 # 普通文本/列表
        if rows: out.append('</table>', rows=False
        if s.startswith('- '):
            out.append('<li>'+esc(s[2:])+'</li>'
        elif s.startswith('1. '):
            out.append('<li>'+esc(s[3:])+'</li>'
        else:
            out.append('<p>'+esc(s)+'</p>')
if rows: out.append('</table>')
out.append('''<hr style="border:none;border-top:2px solid #F0C04B;margin:22px 0">
<p style="color:#888;font-size:12px;text-align:center">© DENSITY·SR · 本地量化工具 · 仅供学习研究, 不构成投资建议</p></body></html>''')
open(HTMLWECHAT,'w',encoding='utf-8').write(''.join('
', out))
print('HTML_OK', OUTWECHAT)