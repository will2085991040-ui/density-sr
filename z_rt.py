# -*- coding: utf-8 -*-
import sys, json; sys.path.insert(0, r"C:/Users/mine/Downloads/quant_research")
import server
d = server.realtime_json("600519","A股","daily")
print("keys:", sorted(d.keys()))
print("minute:", len(d.get("minute") or []), (d.get("minute") or [{}])[0] if d.get("minute") else None)
print("m5:", len(d.get("m5") or []), (d.get("m5") or [{}])[-1] if d.get("m5") else None)
print("kline:", len(d.get("kline") or []), (d.get("kline") or [{}])[-1] if d.get("kline") else None)
print("bands:", len(d.get("bands") or []), (d.get("bands") or [{}])[0] if d.get("bands") else None)
print("quote keys:", list((d.get("quote") or {}).keys()))
print("signal:", (d.get("signal") or {}).get("signal"), "sent:", (d.get("sentiment") or {}).get("label"))
