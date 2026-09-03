# -*- coding: utf-8 -*-
import sys, traceback; sys.path.insert(0, r"C:/Users/mine/Downloads/quant_research")
import server
try:
    rows=server.scan_rows(20).get("rows",[])
    h=server.export_html(rows)
    print("export_html ok", len(h), h[:80].decode("utf-8","replace"))
except Exception:
    traceback.print_exc()
