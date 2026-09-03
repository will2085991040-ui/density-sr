# -*- coding: utf-8 -*-
import sys, threading, time, urllib.request, urllib.parse, json
sys.path.insert(0, r"C:/Users/mine/Downloads/quant_research")
import server
sv = server.Server(0).start(); base=sv.url(); time.sleep(0.8)
def get(path):
    try:
        r=urllib.request.urlopen(base+path, timeout=120); return r.status, r.read().decode("utf-8","replace")
    except Exception as e: return "ERR", repr(e)[:200]
q = urllib.parse.urlencode({"symbol":"600519","market":urllib.parse.quote("A股"),"tf":urllib.parse.quote("日线 (D1)"),"stance":"6.16"})
st,b=get("api/pa/llm?"+q)
print("PA:", st, b[:400])
sv.stop()
