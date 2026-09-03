# -*- coding: utf-8 -*-
import re
for m in ("kline","minute"):
    p=r"C:/Users/mine/Downloads/quant_research/_dom2_"+m+".txt"
    t=open(p,encoding="utf-8",errors="replace").read()
    pre=re.search(r'<pre id="R">(.*?)</pre>', t, re.S)
    print("=="+m+"==")
    print((pre.group(1)[:600] if pre else "NO PRE"))
