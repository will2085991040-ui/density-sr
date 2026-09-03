# -*- coding: utf-8 -*-
import sys; sys.path.insert(0, r"C:\Users\mine\Downloads\quant_research")
from aiquant.market import MarketCatalog, load
from aiquant.engine.factor import compute
cat = MarketCatalog()
df = load(cat, "A股", "600519", "daily")
if df is None: print("no data"); sys.exit()
r = compute(df)
import json
print(json.dumps({k: r[k] for k in ("composite","verdict","order","direction","confidence","vol_ratio","pos")}, ensure_ascii=False))
print("rec:", r["recommendation"], "rr", r["rr"])
print("FACTORS:", {k: round(v,2) for k,v in r["factors"].items()})
print("NARR:", r["narrative"])
