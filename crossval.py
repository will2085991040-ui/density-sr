# -*- coding: utf-8 -*-
import pandas as pd, numpy as np, os
base = r"C:\Users\mine\Downloads\quant_research"

# 交叉验证 300750 的支撑位 379.64 / 阻力位 415.27
df = pd.read_parquet(os.path.join(base, "ashare_real_data", "300750_daily.parquet"))
df["date"] = pd.to_datetime(df["time"], unit="s")
for name, lvl in [("SUPPORT", 379.6402), ("RESISTANCE", 415.2695)]:
    # 该价位上下1.5%内被触碰的次数(收盘价)
    tol = lvl * 0.015
    touches = df[(df["close"] >= lvl - tol) & (df["close"] <= lvl + tol)]
    struck = touches[touches["close"] <= lvl] if name=="RESISTANCE" else touches[touches["close"] >= lvl]
    print(f"{name} {lvl:.2f}: 全区间接触{len(touches)}根K, 从下方靠近{len(struck)}根")
    # 近期接触
    recent = touches[touches["date"] >= "2024-06-01"]
    print(f"   2024-06后接触: {len(recent)}根, e.g. {list(recent['date'].dt.date.astype(str)[-5:])}")
print("current close:", round(float(df["close"].iloc[-1]),2))
