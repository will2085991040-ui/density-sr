# -*- coding: utf-8 -*-
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, r"C:\Users\mine\Downloads\quant_research")
from aiquant.market import MarketCatalog, load
from aiquant.backtest.engine import run_engine, walkforward
cat=MarketCatalog()
for code in ("600519","600938","002611"):
    df=load(cat,"A股",code,"daily"); print("=== ",code, len(df))
    for r in run_engine(df,5.0):
        if "短线" in r["strategy"] or "波段" in r["strategy"]:
            print("   ",r["strategy"],"胜率",r["胜率%"],"PF",r["盈利因子"],"亏损概率",r["亏损概率%"],"收益",r["累计收益%"])
