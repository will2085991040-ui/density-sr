# -*- coding: utf-8 -*-
import sys, time
t0 = time.time()
print("start", flush=True)
try:
    import baostock as bs
    print("import", flush=True)
    lg = bs.login()
    print("login code=", lg.error_code, "msg=", lg.error_msg, "t=", round(time.time()-t0,1), flush=True)
    rs = bs.query_all_stock(day="2026-08-21")
    rows = 0
    print("query all ok" if rs.error_code=="0" else "query err "+rs.error_code, flush=True)
    while rs.error_code=="0" and rs.next():
        rows += 1
    print("total rows:", rows, flush=True)
    bs.logout()
except Exception as e:
    print("EXC:", type(e).__name__, e, flush=True)
print("done t=", round(time.time()-t0,1), flush=True)
