# -*- coding: utf-8 -*-
import sys, time, urllib.request, json
sys.path.insert(0,r"C:/Users/mine/Downloads/quant_research")
import server
sv=server.Server(0).start(); time.sleep(0.8)
def get(p):
    try:
        r=urllib.request.urlopen(sv.url()+p,timeout=120); return r.status, json.loads(r.read())
    except Exception as e: return "ERR", str(e)[:100]
ok=[]
for label,path in [
 ("channel","api/channel?symbol=000004"),
 ("prompts","api/prompts"),
 ("ep004","api/knowledge/ep004"),
 ("factor","api/factor/mine?symbol=600519"),
 ("ai","api/ai/analyze?symbol=600519"),
]:
    st,d=get(path)
    if st==200:
        flag="OK"
        if label=="channel" and isinstance(d,dict):
            flag = "OK-wide-channel" if (d.get("is_wide") and d.get("direction")=="down") else "OK(非宽)"
        ok.append(f"{label}:{flag}")
    else:
        ok.append(f"{label}:FAIL {d}")
print("ALL-CHECKED", " | ".join(ok))
sv.stop()
