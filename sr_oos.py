# -*- coding: utf-8 -*-
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, r"C:\Users\mine\Downloads\quant_research")
from aiquant.market import MarketCatalog, load
from aiquant.backtest.engine import walkforward
cat=MarketCatalog()
agg_wins=[]; agg_lossp=[]; agg_pf=[]
for code in ("600519","600938","002611","002958","601818"):
    try:
        df=load(cat,"A股",code,"daily")
        for x in walkforward(df,0.6,5.0):
            if x.get("strategy")=="短线·支撑反抽":
                print(code, "OOS胜率",x["OOS胜率%"],"OOS-PF",x["OOS-PF"],"收益",x["OOS收益%"])
                if x["OOS交易数"] if False else True: pass
    except Exception as e:
        print(code,"ERR",e)
