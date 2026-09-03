# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, r"C:\Users\mine\Downloads\quant_research")
from aiquant.market import MarketCatalog, load
from aiquant.engine.indicators import add_indicators
from aiquant.engine.signals import run_signal
from aiquant.backtest.strategies import compare
from aiquant.features.sentiment import sentiment
import aiquant.report.report as rep
cat = MarketCatalog()
df = load(cat, "A股", "600519", "daily")
df = add_indicators(df)
sig = run_signal(df, "稳")
ss = sentiment(headlines=["贵州茅台业绩说明超预期", "回购利好", "净利润增长 分红提升"])
strat = compare(df)
out = rep.build_report(df, sig, ss, strat, r"C:\Users\mine\Downloads\quant_research\out\report_600519.html", symbol="600519")
print("done", os.path.exists(out), os.path.getsize(out))
