# -*- coding: utf-8 -*-
import sys, json; sys.path.insert(0, r"C:/Users/mine/Downloads/quant_research")
from aiquant import realtime_sina as RS
try:
    q=RS.quote("600519","A股"); print("quote:", json.dumps(q,ensure_ascii=False)[:400])
except Exception as e: print("quote err", e)
try:
    m=RS.minute("600519","A股"); print("minute:", type(m).__name__, len(m) if m else 0, (m[0] if m else None))
except Exception as e: print("minute err", e)
try:
    k5=RS.mkline5("600519","A股",40); print("m5:", len(k5) if k5 else 0, (k5[-1] if k5 else None))
except Exception as e: print("m5 err", e)
