# -*- coding: utf-8 -*-
import sys, threading, time, urllib.request, json, re
sys.path.insert(0,r"C:/Users/mine/Downloads/quant_research")
import server
sv=server.Server(0).start(); time.sleep(0.8)
def get(p):
    try:
        r=urllib.request.urlopen(sv.url()+p,timeout=25); ctype=r.headers.get("Content-Type",""); return r.status, r.read(), ctype
    except Exception as e: return "ERR", str(e).encode(), ""
st,body,ct=get("index.html"); print("index:", st, "len", len(body) if st==200 else body)
s=body.decode("utf-8","replace") if st==200 else ""
print("  has btn-channel:", 'id="btn-channel"' in s, "| has script:", "channel_panel.js" in s)
st2,cp,ct2=get("channel_panel.js"); print("channel_panel.js:", st2, len(cp) if st2==200 else cp, ct2)
st3,d,ct3=get("api/channel?symbol=600519"); print("api/channel:", st3, ct3)
if st3==200:
    o=json.loads(d); print("  wide",o.get("is_wide"),"dir",o.get("direction"),"upper",o.get("upper"))
sv.stop()
