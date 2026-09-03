# -*- coding: utf-8 -*-
import sys; sys.path.insert(0,r"C:/Users/mine/Downloads/quant_research")
from aiquant.market import load, MarketCatalog
from aiquant import pa_llm as p
d=load(MarketCatalog(),"A股","600519","daily")
feats=p.price_action_features(d)
prompt=p._build_prompt(d,"600519","A股","6.16",feats)
print("prompt built:", len(prompt), "chars")
print("system payload chars:", len(p._system_prompt()))
# ensure no crash on module-level
print("OK module wired")
