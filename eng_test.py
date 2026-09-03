# -*- coding: utf-8 -*-
import sys; sys.path.insert(0, r"C:\Users\mine\Downloads\quant_research")
from aiquant.market import MarketCatalog, load
from aiquant.backtest.engine import run_engine, walkforward, STRATEGIES, backtest_trades
cat = MarketCatalog()
df = load(cat, "A股", "600519", "daily")
print("bars", len(df))
print("== run_engine ==")
for r in run_engine(df, 5.0):
    print(r)
print("== walkforward OOS ==")
for r in walkforward(df, 0.6, 5.0):
    print(r)
