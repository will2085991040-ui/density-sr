# -*- coding: utf-8 -*-
"""combine scan + names -> multi-board report"""
import json, os, pandas as pd
base = os.path.dirname(os.path.abspath(__file__))
names = json.load(open(os.path.join(base,"names.json"), encoding="utf-8"))
df = pd.read_csv(os.path.join(base,"out","sr_combined.csv"), dtype={"symbol":str})
df["symbol"] = df["symbol"].apply(lambda s: s.split(".")[0] if "." in s else s)
def board(code):
    if code.startswith("68"): return "科创板"
    if code.startswith("30"): return "创业板"
    if code.startswith("60"): return "沪主板"
    return "深主板"
df["board"] = df["symbol"].apply(board)
df["name"] = df["symbol"].apply(lambda c: names.get(c,""))
df = df.sort_values("p_effective", ascending=False)
df.to_csv(os.path.join(base,"out","sr_combined_named.csv"), index=False, encoding="utf-8-sig")
print("总数:", len(df), " 板块:", df["board"].value_counts().to_dict())
print("\n各板块前5 (有效概率):")
for b in ["沪主板","深主板","创业板","科创板"]:
    sub = df[df["board"]==b].head(5)
    if len(sub)==0: continue
    print("--- %s ---" % b)
    print(sub[["symbol","name","current_price","nearest_support","nearest_resistance","p_effective","trend_label"]].to_string(index=False))
