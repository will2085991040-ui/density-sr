# -*- coding: utf-8 -*-
import sys; sys.path.insert(0, r"C:/Users/mine/Downloads/quant_research")
from aiquant import realtime_ths, realtime_sina as RS
b = realtime_ths.ths_kline("600519","A股","01",3)
print("ths daily last bar:", b[-1] if b else None)
mm = RS.mkline5("600519","A股",40)
print("mkline5 last bar:", mm[-1] if mm else None)
