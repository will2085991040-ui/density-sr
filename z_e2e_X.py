# -*- coding: utf-8 -*-
import sys, time, urllib.request, json
sys.path.insert(0,r"C:/Users/mine/Downloads/quant_research")
import server
sv=server.Server(0).start(); time.sleep(0.8)
def get(p):
    try:
        r=urllib.request.urlopen(sv.url()+p,timeout=90); return r.status, json.loads(r.read())
    except Exception as e: return "ERR", str(e)[:120]
for label,path in [
  ("index.html","index.html"),
  ("channel_panel.js","channel_panel.js"),
  ("api/channel","api/channel?symbol=600519"),
  ("api/prompts","api/prompts"),
  ("api/knowledge/ep004","api/knowledge/ep004"),
  ("api/factor/mine","api/factor/mine?symbol=600519&horizon=3&topk=5"),
  ("api/ai/analyze","api/ai/analyze?symbol=600519"),
]:
    st,d=get(path)
    if st!=200:
        print(f"{label}: {st} {d}")
    else:
        if isinstance(d,dict):
            ks=list(d.keys())[:8]
            one=""
            if "files" in d: one=f" files={len(d['files'])}"
            if "is_wide" in d: one=f" wide={d['is_wide']} dir={d.get('direction')}"
            if isinstance(d.get("knowledge"),list): one+=f" kn={len(d['knowledge'])}"
            print(f"{label}: 200 keys={ks}{one}")
        elif isinstance(d,list):
            print(f"{label}: 200 list len={len(d)}")
        else:
            print(f"{label}: 200 {str(d)[:60]}")
sv.stop()
