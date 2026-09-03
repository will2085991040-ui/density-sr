# -*- coding: utf-8 -*-
import sys, threading, time, urllib.request, json
sys.path.insert(0, r"C:/Users/mine/Downloads/quant_research")
import server
sv = server.Server(0).start(); base=sv.url(); time.sleep(0.8)
def get(path):
    try:
        r = urllib.request.urlopen(base+path, timeout=60); return r.status, r.read().decode("utf-8","replace")[:400]
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8","replace")[:500]
    except Exception as e:
        return "ERR", repr(e)[:200]
for p in ["api/init?market=A股","api/export?type=csv"]:
    st,body=get(p); print(p,"->",st,"BODY:",body)
sv.stop()
