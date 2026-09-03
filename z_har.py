# -*- coding: utf-8 -*-
import os, json
base=r"C:/Users/mine/Downloads/quant_research/webui"
# emit payload from server
import sys; sys.path.insert(0, r"C:/Users/mine/Downloads/quant_research")
import server
d = server.realtime_json("600519","A股","daily")
d["mode"]="kline"; d["showM5"]=False; d["showMacd"]=False
open(r"C:/Users/mine/Downloads/quant_research/_harness_payload.json","w").write(json.dumps(d))
d2=dict(d); d2["mode"]="minute"
open(r"C:/Users/mine/Downloads/quant_research/_harness_payload_min.json","w").write(json.dumps(d2))
print("payloads written")
