# -*- coding: utf-8 -*-
import re, os
base = r"C:/Users/mine/Downloads/quant_research"
for fn in ["server_rec.py","server_tmp.py","server_tmp2.py","server.py"]:
    p = os.path.join(base, fn)
    if not os.path.exists(p): print(fn, "MISSING"); continue
    t = open(p, encoding="utf-8").read()
    print("="*20, fn, "len", len(t))
    # find realtime_json definition
    i = t.find("def realtime_json")
    if i<0: print("  no realtime_json"); continue
    seg = t[i:i+1600]
    print(seg[:1600])
