# -*- coding: utf-8 -*-
import sys, traceback; sys.path.insert(0, r"C:/Users/mine/Downloads/quant_research")
import server
for name,fn in [("init",lambda: server.init_json("A股")), ("export",lambda: server.export_csv(server.scan_rows(50).get("rows",[])) )]:
    try:
        r=fn()
        print(name,"OK", type(r).__name__, (list(r.keys()) if isinstance(r,dict) else ""))
    except Exception:
        print("=="+name+"=="); traceback.print_exc()
