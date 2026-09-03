# -*- coding: utf-8 -*-
import sys, threading, time, urllib.request, urllib.parse, json
sys.path.insert(0, r"C:/Users/mine/Downloads/quant_research")
import server
sv = server.Server(0).start(); base=sv.url(); time.sleep(0.8)
mk = urllib.parse.quote("A股")
def get(path):
    try:
        r = urllib.request.urlopen(base+path, timeout=60); return r.status, r.read()
    except Exception as e: return "ERR", str(e)[:200]
st,body=get("api/init?market="+mk)
print("init:", st, json.loads(body).get("ok"), json.loads(body).get("count"))
# detail already fine; just verify scan+export statuses
for p in ["api/scan?limit=5","api/export?type=csv","api/export?type=html"]:
    st,b=get(p); print(p,"->",st, (len(b) if st==200 else b))
sv.stop()
