# -*- coding: utf-8 -*-
import sys; sys.path.insert(0, r"C:\Users\mine\Downloads\quant_research")
# full pipeline: load -> indicators -> report + dual-agent, for 600519 daily
from aiquant.market import MarketCatalog, load
from aiquant.engine.indicators import add_indicators
from aiquant.agents.integrate import unify, summarize
from aiquant.features.sentiment import sentiment

cat = MarketCatalog()
df = load(cat, "A股", "600519", "daily")
df = add_indicators(df)
u = unify(df, "稳")
print("=== 双智能体研判 ===")
print(summarize(u))
print("consensus:", u["consensus"], "llm_active:", u["llm_active"])

# 名称解析与情感(离线词库)
ss = sentiment(symbol="600519")
print("sentiment:", ss.get("label"), ss.get("score"))
print("PIPELINE OK")
