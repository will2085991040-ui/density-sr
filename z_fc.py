# -*- coding: utf-8 -*-
import sys, time
sys.path.insert(0,r"C:/Users/mine/Downloads/quant_research")
from aiquant.market import load, MarketCatalog
from aiquant.factor_mine import factor_df, FACTOR_NAMES
print("FACTOR_NAMES:", FACTOR_NAMES)
d=load(MarketCatalog(),"A股","600519","daily")
fd=factor_df(d)
print("computed cols:", list(fd.columns))
# check new factors non-NaN
print("has mom_ds/mom_t/mom_som:", [c for c in ("mom_ds","mom_t","mom_som") if c in fd.columns])
if "mom_ds" in fd.columns:
    print("mom_ds last10 nonnull:", fd["mom_ds"].dropna().tail(3).tolist())
