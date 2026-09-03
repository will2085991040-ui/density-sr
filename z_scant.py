# -*- coding: utf-8 -*-
import sys, traceback; sys.path.insert(0, r"C:/Users/mine/Downloads/quant_research")
import server
try:
    r = server.scan_rows(3)
    print("scan ok:", r.keys() if r else None)
except Exception:
    traceback.print_exc()
