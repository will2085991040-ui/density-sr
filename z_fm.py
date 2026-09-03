# -*- coding: utf-8 -*-
import sys, threading, time, urllib.request
sys.path.insert(0, r"C:/Users/mine/Downloads/quant_research")
import server
sv=server.Server(0).start(); time.sleep(0.8)
try:
    r=urllib.request.urlopen(sv.url()+"api/factor/mine?limit=12", timeout=120)
    import json; d=json.loads(r.read())
    print("factor mine:", r.status, d.get("ok"), "samples", d.get("samples"), "rows", len(d.get("rows",[])))
    print([(x.get("factor"), x.get("importance")) for x in d.get("rows",[])][:12])
except Exception as e:
    print("ERR", str(e)[:160])
sv.stop()
