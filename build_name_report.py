# -*- coding: utf-8 -*-
"""结合扫面结果+名称，生成可读的全市场支撑/阻力位报告"""
import json, os, sys
base = os.path.dirname(os.path.abspath(__file__))
names = json.load(open(os.path.join(base, "names.json"), encoding="utf-8"))

# 读取最新扫描 CSV（用 pandas 处理符号转字符串）
import pandas as pd
csv_path = os.path.join(base, "out", "sr_ashare_market.csv")
df = pd.read_csv(csv_path, dtype={"symbol": str})
df["symbol"] = df["symbol"].apply(lambda s: s.split(".")[0] if "." in s else s)

def board(code):
    if code.startswith("68"): return "科创板"
    if code.startswith("30"): return "创业板"
    if code.startswith("60"): return "沪主板"
    return "深主板"
df["board"] = df["symbol"].apply(board)
df["name"] = df["symbol"].apply(lambda c: names.get(c, ""))
df = df.sort_values("p_effective", ascending=False)

# 保存名称标注版
df.to_csv(os.path.join(base, "out", "sr_ashare_market_named.csv"), index=False, encoding="utf-8-sig")

print("共", len(df), "只")
print("\n=== 全市场支撑/阻力位 Top 25（含名称，按有效概率）===")
cols = ["symbol","name","board","current_price","nearest_support","nearest_resistance","p_effective","n_zones","trend_label"]
print(df[cols].head(25).to_string(index=False))

# 板块分布
print("\n板块分布:", df["board"].value_counts().to_dict())
