# -*- coding: utf-8 -*-
"""whole-market scan summary from sr_ashare_537.json"""
import json, os, collections
base = r"C:\Users\mine\Downloads\quant_research"
d = json.load(open(os.path.join(base, "out", "sr_ashare_537.json"), encoding="utf-8"))
rows = d["top_rows"]
print("analyzed:", d["analyzed"], "failed:", d["failed"])
print("prob_ready:", d["prob_ready"], "calibrated:", d["calibrated"], "elapsed_s:", d["elapsed_s"])

def cat(code):
    c = code[0]
    if code.startswith("5"): return "基金/ETF"
    if code.startswith("6"): return "沪主板"
    if code.startswith("68"): return "科创板"
    if code.startswith("00"): return "深主板"
    if code.startswith("30"): return "创业板"
    if code.startswith("8") or code.startswith("4"): return "北交所/其他"
    return "其他"

cats = {}
for r in rows:
    k = cat(r["symbol"])
    cats[k] = cats.get(k, 0) + 1
print("板块分布:", cats)

stocks = [r for r in rows if not r["symbol"].startswith("5")]
print("股票数(剔除基金/ETF):", len(stocks))

# 距离约束下的"有效位"统计：最近的支撑/阻力离现价在15%以内才算贴近市场的关键位
frame = []
for r in stocks:
    sp = r.get("nearest_support"); rp = r.get("nearest_resistance")
    supd = abs(r.get("nearest_support_dist_pct") or 999)
    resd = abs(r.get("nearest_resistance_dist_pct") or 999)
    frame.append((r["symbol"], r["current_price"], sp, rp,
                  r.get("p_effective"), r.get("p_touch"), r.get("p_hold"),
                  r.get("n_zones"), r.get("trend_label"), supd, resd))
df = pd.DataFrame(frame, columns=["code","price","sup","res","p_eff","p_touch","p_hold","n_zones","trend","supd%","resd%"])
df = df.sort_values("p_eff", ascending=False)
print("\n=== 全市场股票 Top 20 (按有效概率) ===")
print(df.head(20).to_string(index=False))

# 贴近现价(最近关键位 <10%)的股票 —— 更实用：现价附近就有大概率关键位
near = df[(df["supd%"]<=10) | (df["resd%"]<=10)].sort_values("p_eff", ascending=False)
print("\n当前价位附近(<10%)有关键位的股票数:", len(near))
print("\n=== 现价附近的强关键位 (Top 20) ===")
print(near.head(20)[["code","price","sup","res","p_eff","trend"]].to_string(index=False))
