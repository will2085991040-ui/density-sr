# -*- coding: utf-8 -*-
import sys; sys.path.insert(0, r"C:/Users/mine/Downloads/quant_research")
from aiquant import realtime_sina as RS
try:
    b = RS.mkline("600519","A股",60,160)
    print("60mkline:", type(b).__name__, len(b) if b else 0)
    if b: print("keys:", list(b[0].keys()), "| sample:", b[-1])
except Exception as e:
    import traceback; traceback.print_exc()
