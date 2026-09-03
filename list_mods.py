# -*- coding: utf-8 -*-
import os, io
root = r"C:\Users\mine\Desktop\大A量化监控系统\PA_Agent6.24（激进但机会多）\PA_Agent\pa_agent"
buf=io.StringIO()
def w(*a): print(*a, file=buf)
for mod in ["data","indicators"]:
    d = os.path.join(root, mod)
    if os.path.isdir(d):
        w("=== "+mod+" ===")
        for f in sorted(os.listdir(d)):
            if f.endswith(".py"):
                w("  "+f)
open(r"C:\Users\mine\Downloads\quant_research\report_mods.txt","w",encoding="utf-8").write(buf.getvalue())
print("done")
