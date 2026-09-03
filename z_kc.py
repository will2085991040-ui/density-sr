# -*- coding: utf-8 -*-
import sys, traceback; sys.path.insert(0,r"C:/Users/mine/Downloads/quant_research")
import server
try:
    d=server.knowledge_list(); print("ok", d.get("ok"), d.get("count"))
except Exception:
    traceback.print_exc()
