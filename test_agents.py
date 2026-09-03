# -*- coding: utf-8 -*-
import sys; sys.path.insert(0, r"C:\Users\mine\Downloads\quant_research")
from aiquant.market import MarketCatalog, load
from aiquant.agents.integrate import unify, summarize
cat = MarketCatalog()
df = load(cat, "A股", "600519", "daily")
for st in ("稳", "激进"):
    u = unify(df, stance=st)
    print("==", st, "==")
    print("consensus:", u["consensus"])
    print("narr:", u["narrative"])
print("------ summary ------")
print(summarize(unify(df, "稳")))
