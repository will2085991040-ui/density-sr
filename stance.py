# -*- coding: utf-8 -*-
import os, io
base = r"C:\Users\mine\Desktop\大A量化监控系统\PA_Agent6.24（激进但机会多）\PA_Agent\pa_agent\ai"
buf=io.StringIO()
def w(*a): print(*a, file=buf)
for f in ["decision_stance.py","structure_levels.py"]:
    p=os.path.join(base,f)
    w("="*20, f, "="*20)
    try:
        w(open(p,encoding="utf-8").read()[:2500])
    except Exception as e: w("ERR "+str(e))
# two_stage head
p=os.path.join(r"C:\Users\mine\Desktop\大A量化监控系统\PA_Agent6.24（激进但机会多）\PA_Agent\pa_agent\orchestrator","two_stage.py")
w("="*20,"two_stage.py head","="*20)
try:
    t=open(p,encoding="utf-8").read().splitlines()
    w("\n".join(t[:80]))
except Exception as e: w("ERR "+str(e))
open(r"C:\Users\mine\Downloads\quant_research\report_stance.txt","w",encoding="utf-8").write(buf.getvalue())
print("done")
