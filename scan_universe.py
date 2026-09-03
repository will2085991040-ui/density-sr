# -*- coding: utf-8 -*-
import baostock as bs, sys
lg = bs.login()
if lg.error_code != "0":
    print("login fail", lg.error_msg); sys.exit(1)
rs = bs.query_all_stock(day="2026-08-21")
rows = []
while rs.error_code == "0" and rs.next():
    rows.append(rs.get_row_data())
bs.logout()
print("total stocks returned:", len(rows))
# 按交易所/板块统计
import collections
cnt = collections.Counter()
for r in rows:
    code = r[0]
    if code.startswith("sh.68"): cnt["科创板"]+=1
    elif code.startswith("sh.60"): cnt["沪主板"]+=1
    elif code.startswith("sz.30"): cnt["创业板"]+=1
    elif code.startswith("sz.00"): cnt["深主板"]+=1
    elif code.startswith("sh.9") or code.startswith("sz.2"): cnt["B股"]+=1
    elif code.startswith("sz.0o"): cnt["北交所"]+=1
    else: cnt["other"]+=1
print(dict(cnt))
print("sample:", rows[:3])
