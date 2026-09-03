# -*- coding: utf-8 -*-
"""Test baostock connection and pull a few stocks' daily kline"""
import sys
try:
    import baostock as bs
except ImportError as e:
    print("baostock not installed:", e); sys.exit(1)

lg = bs.login()
print("login code/msg:", lg.error_code, lg.error_msg)
if lg.error_code != '0':
    print("baostock login FAILED"); sys.exit(1)

# Query a few blue chips
for code in ["sh.600519", "sz.000001", "sz.300750", "sh.000858"]:
    rs = bs.query_history_k_data_plus(
        code, "date,open,high,low,close,volume",
        start_date="2023-01-01", end_date="2026-08-23",
        frequency="d", adjustflag="2")  # 2 = 前复权
    rows = []
    while (rs.error_code == '0') and rs.next():
        rows.append(rs.get_row_data())
    print(code, "-> rows:", len(rows), "sample:", rows[0] if rows else None)

bs.logout()
