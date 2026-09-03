# -*- coding: utf-8 -*-
import pandas as pd, os
base = r"C:\Users\mine\Downloads\quant_research"
df = pd.read_csv(os.path.join(base,"out","sr_ashare_market.csv"), dtype={"symbol":str})
df["symbol"] = df["symbol"].str.replace(".0","",regex=False)
def cat(code):
    code = "%06d" % int(float(code)) if code.isdigit() else code
    if code.startswith("68"): return "科创板"
    if code.startswith("60"): return "沪主板"
    if code.startswith("30"): return "创业板"
    return "深主板"
df["board"] = df["symbol"].apply(cat)
print(df["board"].value_counts().to_string())
df.to_csv(os.path.join(base,"out","sr_ashare_market_annotated.csv"), index=False, encoding="utf-8-sig")
print("annotated saved, rows:", len(df))
