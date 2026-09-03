# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r"C:\Users\mine\Downloads\quant_research")
from aiquant.market import MarketCatalog, load
from aiquant.backtest.strategies import compare
cat = MarketCatalog()
df = load(cat, "A股", "600519", "daily")
if df is None or len(df) < 60:
    print("load failed")
else:
    res = compare(df)
    for r in res:
        if "error" in r:
            print(r["strategy"], "ERR", r["error"]); continue
        print("%-10s ret=%6.2f%% sharpe=%4.2f mdd=%5.2f%% trades=%d" % (
            r["strategy"], r["total_return"]*100, r["sharpe"], r["max_drawdown"]*100, r["trades"]))
    print("total:", len(res))
