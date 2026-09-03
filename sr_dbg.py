# -*- coding: utf-8 -*-
import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0, r"C:\Users\mine\Downloads\quant_research")
from aiquant.market import MarketCatalog, load
from aiquant.engine.indicators import add_indicators
from aiquant.backtest.engine import _nearest_support
cat=MarketCatalog()
df=add_indicators(load(cat,"A股","600519","daily"))
print("has time:", "time" in df.columns, "tick_volume:", "tick_volume" in df.columns)
print("nearest_support ->", _nearest_support(df))
import os, sys as s2
vendor=r"C:\Users\mine\Downloads\quant_research\aiquant\engine\vendor"
s2.path.insert(0, vendor)
import pandas as pd
f=df[["open","high","low","close","tick_volume"]].rename(columns={"tick_volume":"volume"}).copy()
f["date"]=pd.to_datetime(f["time"],unit="s")
from src.sr_engine import SREngine
zones,info=SREngine(n_zones=6).detect(f,"X")
print("zones:", len(zones))
for z in zones[:8]:
    print("  ", z.get("zone_type"), z.get("center"), "tp", z.get("touch_prob"), "hp", z.get("hold_prob"))
