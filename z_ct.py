# -*- coding: utf-8 -*-
import sys, threading, time, urllib.request, json
sys.path.insert(0,r"C:/Users/mine/Downloads/quant_research")
import server
sv=server.Server(0).start(); time.sleep(0.8)
def get(p):
    try:
        r=urllib.request.urlopen(sv.url()+p,timeout=25); return r.status, json.loads(r.read())
    except Exception as e: return "ERR", str(e)[:150]
st,d=get("api/channel?symbol=600519")
print("600519:", st, "wide", d.get("is_wide"), "dir", d.get("direction"), "upper", d.get("upper"), "lower", d.get("lower"), "read", (d.get("read_note") or "")[:80])
# find a wide-down channel among liquid symbols
from aiquant.market import load, MarketCatalog, list_symbols
cat=MarketCatalog()
from aiquant.channel_analysis import channel_wide_analysis
found=None
for s in list_symbols(cat,"A股")[:120]:
    try:
        dd=load(cat,"A股",s,"daily")
        if dd is None or len(dd)<80: continue
        r=channel_wide_analysis(dd)
        if r.get("detected") and r.get("is_wide") and r.get("direction")=="down":
            found=(s,r); break
    except Exception: pass
if found:
    s,r=found; print("WIDE FOUND:", s, "upper", r["upper"], "lower", r["lower"], "w%", r["width_pct"], "pos", r["position_pct"]); print(r["read_note"][:150])
else:
    print("no wide-dn channel in first 120")
sv.stop()
