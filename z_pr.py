# -*- coding: utf-8 -*-
import py_compile
f=r"C:/Users/mine/Downloads/quant_research/server.py"
t=open(f,encoding="utf-8").read()
anchor="def _esc(s):"
fn='''def prompts_list(stage="决策"):
    try:
        import os as _os
        kdir = os.path.join(_ROOT, "knowledge", "prompts")
        files = sorted(_os.listdir(kdir)) if _os.path.isdir(kdir) else []
        return {"ok": True, "dir": "knowledge/prompts", "stage": stage,
                "files": files, "count": len(files)}
    except Exception as e:
        return {"ok": False, "error": str(e)}


'''
assert anchor in t
t=t.replace(anchor, fn+anchor, 1)
old='''    if path == "/api/channel":'''
new='''    if path == "/api/prompts":
        return 200, json.dumps(prompts_list(_q("stage", "决策"))), "application/json"
    if path == "/api/channel":'''
assert old in t
t=t.replace(old,new,1)
open(f,"w",encoding="utf-8").write(t)
py_compile.compile(f,doraise=True)
print("prompts route added")
