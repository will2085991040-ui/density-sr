# -*- coding: utf-8 -*-
import sys; sys.path.insert(0, r"C:/Users/mine/Downloads/quant_research")
import server
r = server.realtime_json("600519","A股","daily")
print("src:", r.get("src"), "| bars:", len(r.get("kline") or []))
