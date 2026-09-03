# -*- coding: utf-8 -*-
p = r"C:\Users\mine\Downloads\quant_research\out\report_600519.html"
html = open(p, encoding="utf-8").read()
print("size", len(html))
print("PNG charts:", html.count("data:image/png;base64"))
print("K线+MACD:", "K线 + MACD" in html)
print("雷达:", "综合评分雷达" in html)
print("策略表:", "6 种策略一键对比" in html)
print("信号表:", "双智能体融合信号" in html)
