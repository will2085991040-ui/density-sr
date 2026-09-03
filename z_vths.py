# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r"C:/Users/mine/Downloads/quant_research")
import server
r = server.realtime_json("600519", "A股", "daily")
print("src:", r.get("src"))
print("live:", r.get("live"), "kline bars:", len(r.get("kline") or []), "dates:", (r.get("dates") or [])[-1])
print("closes last:", (r.get("closes") or [])[-1])
print("bands:", len(r.get("bands") or []), "first zone:", (r.get("bands") or [{}])[0].get("zone_type"))
