# -*- coding: utf-8 -*-
import baostock as bs, collections, os
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
cats = collections.Counter()
for r in eq:
    num = r[0].split(".")[1]
    if num.startswith("60"): cats["SHmain"]+=1
    elif num.startswith("68"): cats["STAR"]+=1
    elif num.startswith("300") or num.startswith("301"): cats["ChiNext"]+=1
    else: cats["SZmain"]+=1
lines = []
lines.append("equity universe: %d" % len(eq))
lines.append("boards: %s" % dict(cats))
lines.append("total rows(trades+funds): %d" % len(rows))
with open(r"C:\Users\mine\Downloads\quant_research\universe_count.txt","w",encoding="utf-8") as f:
    f.write("\n".join(lines))
print("wrote to universe_count.txt")
