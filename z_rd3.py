# -*- coding: utf-8 -*-
import re
for m in ("kline","minute"):
    t=open(r"C:/Users/mine/Downloads/quant_research/_dom3_"+m+".txt",encoding="utf-8",errors="replace").read()
    pre=re.search(r'<pre id="R">(.*?)</pre>', t, re.S)
    print("=="+m+"==", (pre.group(1)[:500] if pre else "NO PRE len="+str(len(t))))
