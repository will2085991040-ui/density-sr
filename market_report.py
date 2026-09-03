# -*- coding: utf-8 -*-
import json, os, collections
base = r"C:\Users\mine\Downloads\quant_research"
d = json.load(open(os.path.join(base,"out","sr_ashare_market.json"), encoding="utf-8"))
rows = d["top_rows"]
print("analyzed:", d["analyzed"], "failed:", d["failed"], "prob_ready:", d["prob_ready"], "calibrated:", d["calibrated"])
def cat(code):
    if code.startswith("68"): return "科创板"
    if code.startswith("60"): return "沪主板"
    if code.startswith("30"): return "创业板"
    return "深主板"
cnt = collections.Counter(cat(r["symbol"]) for r in rows)
print("板块分布:", dict(cnt))
# Top 25 by effective prob
print("\n=== 全市场品种 Top 25 (有效概率) ===")
for i, r in enumerate(rows[:25]):
    print("%2d %s 现价%8.2f 支撑%8.2f 阻力%8.2f 触及p%.2f 守p%.2f 有效p%.2f 档%2d %s(%s)" % (
        i+1, r["symbol"], r["current_price"], r["nearest_support"] or 0, r["nearest_resistance"] or 0,
        r["p_touch"] or 0, r["p_hold"] or 0, r["p_effective"] or 0, r["n_zones"], r["trend_label"], cat(r["symbol"])))
