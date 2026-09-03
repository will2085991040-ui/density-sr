# -*- coding: utf-8 -*-
import re, os
for m in ("kline","minute"):
    p=r"C:/Users/mine/Downloads/quant_research/_dom_"+m+".txt"
    t=open(p,encoding="utf-8",errors="replace").read()
    ttl=re.search(r"<title>(.*?)</title>", t, re.S)
    rp=re.search(r'data-r="([^"]*)"', t)
    print("=="+m+"== title:", ttl.group(1)[:400] if ttl else "NONE")
    print("   report:", rp.group(1)[:500] if rp else "NONE")
