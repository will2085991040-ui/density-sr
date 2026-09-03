# -*- coding: utf-8 -*-
"""把 项目介绍书.md 排版为 Excel(.xlsx) 与 公众号 HTML 两版。"""
import os
MD = r"C:/Users/mine/Downloads/quant_research/项目介绍书.md"
XLSX = r"C:/Users/mine/Downloads/quant_research/项目介绍书_Excel.xlsx"
HTMLF = r"C:/Users/mine/Downloads/quant_research/项目介绍书_公众号.html"
txt = open(MD, encoding="utf-8").read()
lines = txt.split(chr(10))

# ===== Excel =====
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter
wb = Workbook(); ws = wb.active; ws.title = "项目介绍"
hdr_fill = PatternFill("solid", fgColor="1B1F27")
sec_font = Font(bold=True, color="E97C1D", size=13)
tcell = ws.cell(1, 1, txt.splitlines()[0].lstrip("# ").strip())
tcell.font = Font(bold=True, size=16, color="E97C1D")
ws.merge_cells("A1:E1"); ws.row_dimensions[1].height = 28
tables = [
 ("功能全景",
  [("模块","功能","入口"),
   ("支撑阻力引擎","全量A股SR带(日线/60分/15分); 支撑/压力/触及与守住概率","品种行点击/搜索"),
   ("多周期图表","日线/60分/15分; K线+MA5/10/20/60+量能+MACD","顶部周期下拉"),
   ("分时实时盯盘","白现价/黄均价/灰昨收; 涨跌停参考线; 每15秒刷新","实时盘/分时按钮"),
   ("AI联网研判","双agent + AI K线分析 / 因子挖掘","AI面板按钮"),
   ("市场情绪","温度0-100°; 涨跌结构; 涨停; 仓位建议","市场情绪卡"),
   ("策略信号(自动量化)","触发位 -> 方向/入场/止损/目标/风比/情绪过滤","策略信号卡"),
   ("使用手册","内置弹窗: 图表怎么读/怎么做量化/风险提示","图表工具栏 ? 按钮"),
   ("本地数据","内嵌全量数据、离线可用、数据不出本机","内置")]),
 ("温度-建议映射",
  [("温度","情绪","策略 / 仓位"),
   ("78-100","亢奋","警惕过热, 减仓不追高"),
   ("55-77","偏多","顺势为主, 可适度加仓"),
   ("45-54","中性","精选控仓"),
   ("27-44","偏空","防守降仓"),
   ("0-26","冰点","观望或分批左侧埋伏, 等赚钱效应修复")]),
 ("为什么值钱(对比)",
  [("维度","传统看盘/数据","DENSITY·SR"),
   ("支撑阻力","手工画线或只有均线","密度+斐波回撤+概率, 自动化"),
   ("市场情绪","文字新闻","温度计+涨跌结构+涨停高度, 给仓位"),
   ("自动交易","全手动","触发信号+盈亏比+情绪过滤"),
   ("数据/隐私","云端订阅","本地内嵌离线, 数据不出本机"),
   ("部署","装环境/账号","单文件双击即用")]),
]
r0 = 3
for name, rows in tables:
    ws.cell(r0, 1, name).font = sec_font
    r0 += 1
    for idx, hh in enumerate(rows[0], start=1):
        c = ws.cell(r0, idx, hh)
        c.font = Font(bold=True, color="FFFFFF"); c.fill = hdr_fill
        c.alignment = Alignment(horizontal="center")
    r0 += 1
    for row in rows[1:]:
        for idx, val in enumerate(row, start=1):
            c = ws.cell(r0, idx, val)
            c.alignment = Alignment(vertical="top", wrap_text=True)
        r0 += 1
    r0 += 1
for col in range(1, 5):
    ws.column_dimensions[get_column_letter(col)].width = 26
wb.save(XLSX)
print("EXCEL OK", os.path.getsize(XLSX))
