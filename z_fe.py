# -*- coding: utf-8 -*-
import urllib.request, json
BASE="http://127.0.0.1:61280/"
def get(p):
    try:
        r=urllib.request.urlopen(BASE+p,timeout=60); return r.status, json.loads(r.read())
    except Exception as e: return "ERR", str(e)[:150]
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
            one=""
            if "files" in d: one=f" files={len(d['files'])}"
            if "is_wide" in d: one=f" wide={d['is_wide']} dir={d.get('direction')}"
            if isinstance(d.get("knowledge"),list): one+=f" kn={len(d['knowledge'])}"
            print(f"{label}: 200{one}")
        elif isinstance(d,list):
            print(f"{label}: 200 list={len(d)}")
        else:
            print(f"{label}: 200")
