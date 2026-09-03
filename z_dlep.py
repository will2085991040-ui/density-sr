# -*- coding: utf-8 -*-
import urllib.request, os
base="https://raw.githubusercontent.com/frank-quant/ai-trading-videos/main/EP004_four-llm-quant-benchmark/"
dirp=r"C:/Users/mine/Downloads/quant_research/knowledge/ep004"
os.makedirs(dirp, exist_ok=True)
hdr={"User-Agent":"dsh"}
for rel in ["results/REPORT.md","README.md","RUNBOOK.md"]:
    name=rel.replace("/","_")
    try:
        req=urllib.request.Request(base+rel, headers=hdr)
        body=urllib.request.urlopen(req, timeout=30).read().decode("utf-8","replace")
        open(os.path.join(dirp,name),"w",encoding="utf-8").write(body)
        print("saved", name, len(body))
    except Exception as e:
        print("ERR", name, str(e)[:120])
