# -*- coding: utf-8 -*-
import sys, threading, time, urllib.request, json
sys.path.insert(0, r"C:/Users/mine/Downloads/quant_research")
import server
sv = server.Server(0)
t = threading.Thread(target=sv.serve_forever, daemon=True); t.start()
time.sleep(0.8)
def get(path):
    with urllib.request.urlopen("http://127.0.0.1:%d/"%sv.port+path, timeout=20) as r:
        return r.read().decode("utf-8")
o = json.loads(get("api/rt/realtime?symbol=600519&tf=daily"))
print("keys:", sorted(o.keys()))
print("source:", o["source"], "| live:", o["live"], "| bars:", len(o["kline"]), "| bands:", len(o["bands"]))
sig = o.get("signal") or {}
print("signal keys:", sorted(sig.keys()))
print("signal:", sig.get("signal"), "| dir:", sig.get("direction"), "| entry:", sig.get("entry"), "| rr:", sig.get("rr"))
print("sentiment:", o.get("sentiment"))
# 60min multi-period
o2 = json.loads(get("api/rt/realtime?symbol=600519&tf=60"))
print("tf60 bars:", len(o2.get("kline") or []), "source:", o2.get("source"), "signal:", (o2.get("signal") or {}).get("signal"))
sv.shutdown()
