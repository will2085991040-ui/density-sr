# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r"C:\Users\mine\Downloads\quant_research")
from aiquant.features.sentiment import crawl_news, sentiment
live = crawl_news("600519")
print("live count:", len(live))
for h in live[:5]: print("  -", h)
ch = [t for t in live if t]
r = sentiment(headlines=ch, symbol="600519")
print("sentiment:", r["score"], r["label"], "src", r["source"])
