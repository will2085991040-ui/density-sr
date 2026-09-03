# -*- coding: utf-8 -*-
import os, io, json
root = r"C:\Users\mine\Desktop\大A量化监控系统\PA_Agent6.24（激进但机会多）\PA_Agent"
buf=io.StringIO()
def w(*a): print(*a, file=buf)
for cfg in [os.path.join(root,"config"), os.path.join(root,"pa_agent","config")]:
    if os.path.isdir(cfg):
        w("=== config dir:", cfg, "===")
        for f in os.listdir(cfg):
            fp=os.path.join(cfg,f)
            w("  -- "+f)
            try:
                if f.endswith((".json",".yml",".yaml",".toml",".txt")):
                    txt=open(fp,encoding="utf-8").read()
                    w("     "+txt.replace("\n","\n     ")[:1200])
            except Exception as e: w("     ERR "+str(e))
# thinking route probe
trp = os.path.join(root,"thinking_route_probe_result.json")
if os.path.exists(trp):
    w("=== thinking_route_probe_result.json ===")
    w(open(trp,encoding="utf-8").read()[:1800])
open(r"C:\Users\mine\Downloads\quant_research\report_agentconfig.txt","w",encoding="utf-8").write(buf.getvalue())
print("done")
