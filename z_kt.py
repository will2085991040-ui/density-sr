# -*- coding: utf-8 -*-
import sys, threading, time, urllib.request, json
sys.path.insert(0,r"C:/Users/mine/Downloads/quant_research")
import server
sv=server.Server(0).start(); time.sleep(0.8)
try:
    r=urllib.request.urlopen(sv.url()+"api/knowledge/ep004",timeout=20)
    d=json.loads(r.read())
    print("route:", r.status, "ok", d.get("ok"), "count", d.get("count"), "files", [f["name"] for f in d.get("files",[])])
except Exception as e:
    print("ERR", str(e)[:160])
sv.stop()
