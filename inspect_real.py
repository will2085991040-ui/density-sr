# -*- coding: utf-8 -*-
import json, os
p = os.path.join(r"C:\Users\mine\Downloads\quant_research\out", "sr_ashare_real.json")
d = json.load(open(p, encoding="utf-8"))
print("analyzed", d["analyzed"], "failed", d["failed"], "prob_ready", d["prob_ready"], "calibrated", d["calibrated"], "n_adjusted", d["n_adjusted"], "n_unadjusted", d["n_unadjusted"])
print("--- 300750 明细 ---")
for r in d["top_rows"]:
    if r["symbol"] == "300750":
        for k, v in r.items():
            print(f"  {k}: {v}")
print("headline fields available in first row:", sorted(d["top_rows"][0].keys()))
