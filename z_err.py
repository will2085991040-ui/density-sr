# -*- coding: utf-8 -*-
import sys, threading, time, urllib.request, json, traceback
sys.path.insert(0, r"C:/Users/mine/Downloads/quant_research")
import server
sv = server.Server(0).start(); base=sv.url(); time.sleep(0.8)
def get(path):
    try:
        req=urllib.request.urlopen(base+path, timeout=30); return req.status, req.read().decode("utf-8","replace")
    except Exception as e:
        return "ERR", repr(e)[:300]
for p in ["api/scan?limit=3","api/export?type=csv"]:
    st,body=get(p); print(p,"->",st, body[:200])
sv.stop()
