# -*- coding: utf-8 -*-
import sys, threading, time, urllib.request, urllib.error
sys.path.insert(0,r"C:/Users/mine/Downloads/quant_research")
import server
sv=server.Server(0).start(); time.sleep(0.8)
try:
    urllib.request.urlopen(sv.url()+"api/knowledge/ep004",timeout=20)
except urllib.error.HTTPError as e:
    print("code", e.code, "body:", e.read().decode("utf-8","replace")[:300])
except Exception as e:
    print("ERR", repr(e)[:200])
sv.stop()
