# -*- coding: utf-8 -*-
import urllib.request, json
BASE="http://127.0.0.1:55105/"
def get(p):
    try:
        r=urllib.request.urlopen(BASE+p,timeout=120); return r.status, json.loads(r.read())
    except Exception as e: return "ERR", str(e)[:140]
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
        one=""
        if isinstance(d,dict):
            if "files" in d: one=f" files={len(d['files'])}"
            if "is_wide" in d: one=f" wide={d['is_wide']} dir={d.get('direction')}"
            if isinstance(d.get("knowledge"),list): one+=f" kn={len(d['knowledge'])}"
        elif isinstance(d,list): one=f" list={len(d)}"
        print(f"{label}: 200{one}")
