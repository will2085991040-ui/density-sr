# -*- coding: utf-8 -*-
import baostock as bs, collections
bs.login()
rs = bs.query_all_stock(day="2026-08-21")
rows = []
while rs.error_code == "0" and rs.next():
    rows.append(rs.get_row_data())
bs.logout()
def is_equity(code):
    pre, num = code.split(".")
    if pre == "sh" and (num.startswith("60") or num.startswith("68")): return True
    if pre == "sz" and (num.startswith("000") or num.startswith("001") or num.startswith("002") or num.startswith("003") or num.startswith("300") or num.startswith("301")): return True
    return False
eq = [r for r in rows if r[1]=="1" and is_equity(r[0])]
# count by board
cats = collections.Counter()
for r in eq:
    num = r[0].split(".")[1]
    if num.startswith("60"): cats["SHmain"]+=1
    elif num.startswith("68"): cats["STAR"]+=1
    elif num.startswith("300") or num.startswith("301"): cats["ChiNext"]+=1
    else: cats["SZmain"]+=1
print("equity universe:", len(eq))
print("boards:", dict(cats))
# sample first 10 equity codes
print("sample:", [e[0] for e in eq[:10]])
bs.login()
rs2 = bs.query_history_k_data_plus(eq[0][0], "date,open,high,low,close,volume", start_date="2024-01-01", end_date="2026-08-23", frequency="d", adjustflag="2")
r0=0
if rs2.error_code=="0":
    while rs2.next(): r0+=1
bs.logout()
print("sample code", eq[0][0], "bars 2024-2026:", r0)
