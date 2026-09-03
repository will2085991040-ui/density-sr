# -*- coding: utf-8 -*-
import re, os, glob
web = r"C:/Users/mine/Downloads/quant_research/webui"
for f in sorted(glob.glob(os.path.join(web,"*.js"))):
    name=os.path.basename(f)
    if name in ("echarts.min.js",): continue
    txt=open(f,encoding="utf-8",errors="replace").read()
    urls=re.findall(r"['\"](/api/[^'\"]+)['\"]", txt)
    fets=re.findall(r"fetch\([^)]*\)", txt)
    if urls or fets:
        print("###", name)
        for u in sorted(set(urls)): print("   URL:", u)
        for f_ in fets: print("   FETCH:", f_.strip()[:80])
