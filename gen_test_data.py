# -*- coding: utf-8 -*-
"""生成合成测试数据集，用于验证 batch_sr_scan.py。"""
import os, numpy as np, pandas as pd

BASE = r"C:\Users\mine\Downloads\quant_research"
TESTDIR = os.path.join(BASE, "test_data")
os.makedirs(TESTDIR, exist_ok=True)

def make_klines(code, n, base=100, trend=0.0008, freq="D", start="2020-01-01"):
    rng = np.random.default_rng(abs(hash(code)) % 10**9)
    idx = pd.date_range(start, periods=n, freq=freq)
    drift = np.cumsum(rng.standard_normal(n)) * 0.008 + np.arange(n)*trend
    close = base * (1 + drift)
    open_ = np.roll(close, 1); open_[0]=close[0]
    high = np.maximum(open_, close) * (1+0.006*np.abs(rng.standard_normal(n)))
    low = np.minimum(open_, close) * (1-0.006*np.abs(rng.standard_normal(n)))
    vol = rng.integers(5000, 300000, n).astype(float)
    return pd.DataFrame({"date": idx, "open": open_, "high": high, "low": low,
                          "close": close, "volume": vol})

def save_ashare(code, tf="daily", n=400):
    df = make_klines(code, n)
    df["tick_volume"] = df["volume"]
    df["time"] = (df["date"].astype("int64")//10**9).astype(int)
    df[["time","open","high","low","close","tick_volume"]].to_parquet(
        os.path.join(TESTDIR, f"{code}_{tf}.parquet"))

def save_mt5(sym, tf, n=300, base=1.1, trend=0.0003):
    freq = {"D1":"D","H1":"h","W1":"W"}[tf]
    df = make_klines(sym, n, base=base, trend=trend, freq=freq)
    df = df.rename(columns={"volume":"tick_volume"})
    df["time"] = (df["date"].astype("int64")//10**9).astype(int)
    df[["time","open","high","low","close","tick_volume"]].to_parquet(
        os.path.join(TESTDIR, f"{sym}_{tf}.parquet"))

for code in ["000001","600519","300750","000858"]:
    save_ashare(code, "daily")
save_ashare("600519", "60min", 600)

for sym in ["EURUSD","XAUUSD","US30.cash"]:
    save_mt5(sym, "D1", 260)
    save_mt5(sym, "H1", 300)

for fut in ["螺纹钢主连","沪金主连","原油主连","铁矿石主连"]:
    save_mt5(fut, "D1", 300, base=100, trend=0.0006)

print("已生成测试数据:")
for f in sorted(os.listdir(TESTDIR)):
    print("  ", f)
