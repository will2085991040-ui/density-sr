# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, r"C:\Users\mine\Downloads\quant_research")
from aiquant.market import MarketCatalog, load
cat = MarketCatalog()
df = load(cat, "A股", "600519", "daily")
print("rows", len(df), "cols", list(df.columns))
print(df.tail(5).to_string())
root = cat.root
print("data root exists:", os.path.isdir(root))
# mt5 sample
df2 = load(cat, "MT5", "AAPL", "H1")
print("MT5 AAPL H1 rows:", None if df2 is None else len(df2))
