# -*- coding: utf-8 -*-
import sys, threading, time, urllib.request, json, traceback
sys.path.insert(0, r"C:/Users/mine/Downloads/quant_research")
import server
sv = server.Server(0).start()
base = sv.url()
time.sleep(0.8)
def get(path):
    try:
        req = urllib.request.urlopen(base+path, timeout=30)
        return req.status, req.read()
    except Exception as e:
        return "ERR", str(e)[:150].encode()
checks = [
 ("index", ""),
 ("app.js", "app.js"),
 ("sentiment_panel.js","sentiment_panel.js"),
 ("init","api/init?market=A股"),
 ("detail","api/detail?symbol=600519&tf=daily&n=120&levels=4"),
 ("scan","api/scan?limit=5"),
 ("rt/realtime","api/rt/realtime?symbol=600519&tf=daily"),
 ("rt/sentiment","api/rt/sentiment"),
 ("live","api/live/quotes?symbols=600519,000001"),
 ("ai","api/ai/analyze?symbol=600519&n=120"),
 ("factor","api/factor/mine?limit=3"),
 ("pa","api/pa/llm?symbol=600519&stance=6.16"),
 ("export csv","api/export?type=csv"),
 ("export html","api/export?type=html"),
]
for name,path in checks:
    st, body = get(path)
    extra=""
    if st==200 and path.startswith("api"):
        try:
            o=json.loads(body)
            extra = list(o.keys())[:6] if isinstance(o,dict) else type(o).__name__
        except Exception:
            extra = body[:40].decode("utf-8","replace")
    print(name, st, extra)
sv.stop()
