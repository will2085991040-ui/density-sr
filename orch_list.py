# -*- coding: utf-8 -*-
import os, io
base = r"C:\Users\mine\Desktop\大A量化监控系统\PA_Agent6.24（激进但机会多）\PA_Agent\pa_agent"
buf=io.StringIO()
def w(*a): print(*a, file=buf)
for mod in ["orchestrator","ai"]:
    d=os.path.join(base,mod)
    w("=== "+mod+" ===")
    if os.path.isdir(d):
        for f in sorted(os.listdir(d)):
            p=os.path.join(d,f)
            sz = os.path.getsize(p) if os.path.isfile(p) else 0
            w("  {:18} {}".format(f, sz))
    else:
        w("  (not dir)")
open(r"C:\Users\mine\Downloads\quant_research\report_orch.txt","w",encoding="utf-8").write(buf.getvalue())
print("done")
