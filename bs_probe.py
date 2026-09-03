# -*- coding: utf-8 -*-
import baostock as bs, json, os, time
t0=time.time()
try:
    lg = bs.login()
    print("login:", lg.error_code, lg.error_msg, round(time.time()-t0,1), "s")
    if lg.error_code=="0":
        rs = bs.query_history_k_data_plus("sz.300750","date,close",start_date="2026-08-10",end_date="2026-08-23",frequency="d",adjustflag="2")
        rows=[]
        while rs.error_code=="0" and rs.next(): rows.append(rs.get_row_data())
        print("test sz.300750 (创业板) rows:", len(rows), rs.error_code)
        bs.logout()
except Exception as e:
    print("EXC:", type(e).__name__, e)
