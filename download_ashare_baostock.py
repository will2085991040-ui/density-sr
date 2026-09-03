# -*- coding: utf-8 -*-
"""
用 baostock 下载真实 A股 日线数据 -> 保存为 batch_sr_scan.py 需要的 parquet 格式。
输出格式（与 detect_support 的 A股 约定一致）：
    {code}_daily.parquet  列: time(unix秒), open, high, low, close, tick_volume
"""
import os, sys, time
import numpy as np, pandas as pd
import baostock as bs

BASE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(BASE, "ashare_real_data")
os.makedirs(OUTDIR, exist_ok=True)

# 一个代表性股票池（覆盖沪深主板/创业板/科创板、不同市值）
STOCKS = [
    "sh.600519","sz.000001","sz.000858","sh.600036","sh.601318",
    "sz.002594","sz.300750","sh.688981","sh.600030","sz.000651",
    "sh.601012","sz.002415","sh.600887","sz.000333","sh.600809",
    "sh.601888","sz.002475","sh.603288","sz.000568","sh.600309",
    "sh.600276","sz.002230","sh.601899","sz.000792","sh.600028",
]
START = "2021-01-01"
END = "2026-08-23"

def main():
    lg = bs.login()
    if lg.error_code != "0":
        print("login fail", lg.error_msg); sys.exit(1)
    print("baostock logged in")
    ok, fail = 0, 0
    t0 = time.time()
    for sym in STOCKS:
        code = sym.split(".")[1]
        try:
            rs = bs.query_history_k_data_plus(
                sym, "date,open,high,low,close,volume",
                start_date=START, end_date=END, frequency="d", adjustflag="2")
            rows = []
            while rs.error_code == "0" and rs.next():
                rows.append(rs.get_row_data())
            if len(rows) < 100:
                print(f"  [skip] {code} rows={len(rows)}"); fail += 1; continue
            df = pd.DataFrame(rows, columns=["date","open","high","low","close","volume"])
            for c in ["open","high","low","close","volume"]:
                df[c] = pd.to_numeric(df[c], errors="coerce")
            df = df.dropna()
            df["volume"] = df["volume"].astype("float64")
            df["time"] = pd.to_datetime(df["date"]).astype("int64") // 10**9
            df = df.rename(columns={"volume":"tick_volume"})
            df[["time","open","high","low","close","tick_volume"]].to_parquet(
                os.path.join(OUTDIR, f"{code}_daily.parquet"), index=False)
            ok += 1
            print(f"  [ok] {code}: {len(df)} bars -> {code}_daily.parquet")
        except Exception as e:
            fail += 1
            print(f"  [err] {code}: {e}")
        time.sleep(0.1)
    bs.logout()
    print(f"\n完成: 成功 {ok} 只, 失败 {fail} 只, 用时 {time.time()-t0:.1f}s -> {OUTDIR}")

if __name__ == "__main__":
    main()
