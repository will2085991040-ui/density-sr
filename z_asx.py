# -*- coding: utf-8 -*-
import sys, time, urllib.request
sys.path.insert(0,r"C:/Users/mine/Downloads/quant_research")
import server
sv=server.Server(0).start(); time.sleep(0.8)
def raw(p):
    try:
        r=urllib.request.urlopen(sv.url()+p,timeout=25); return r.status, len(r.read()), r.headers.get("Content-Type","")
    except Exception as e: return "ERR", str(e)[:80],""
for p in ["index.html","channel_panel.js","styles.css","app.js","pa_llm_ui.js"]:
    st,n,ct=raw(p); print(f"{p}: {st} bytes={n} ct={ct}")
sv.stop()
