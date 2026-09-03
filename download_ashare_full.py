# -*- coding: utf-8 -*-
"""
并行下载全A股日线 -> ashare_full/{code}_daily.parquet
- 从 baostock 取全部股票（剔除指数/B股/北交所）
- 多线程并行，每个任务独立 login/logout
- 断点续传：已存在的文件跳过（幂等）
用法: python download_ashare_full.py [--max N] [--threads T]
输出列 time(unix秒),open,high,low,close,tick_volume (与 batch_sr_scan 兼容)
"""
import os, sys, time, argparse
import pandas as pd, numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(BASE, "ashare_full")
os.makedirs(OUTDIR, exist_ok=True)
START, END = "2021-01-01", "2026-08-23"
MIN_BARS = 60

def get_universe(day="2026-08-21"):
    import baostock as bs
    bs.login()
    rs = bs.query_all_stock(day=day)
    rows = []
    while rs.error_code == "0" and rs.next():
        rows.append(rs.get_row_data())
    bs.logout()
    out = []
    for r in rows:
        code, status, name = r[0], r[1], r[2]
        if "指数" in name: continue
        if code.startswith("sh.000"): continue      # 上证指数段
        if code.startswith("sz.399"): continue       # 深证指数段
        if code.startswith("sh.9") or code.startswith("sz.2"): continue  # B股
        if code.startswith("sz.8") or code.startswith("sz.4"): continue  # 北交所
        if code.startswith("bj."): continue
        if status != "1": continue
        out.append(code)
    return out

def pull_stock(sym, min_bars):
    code = sym.split(".")[1]
    fp = os.path.join(OUTDIR, f"{code}_daily.parquet")
    if os.path.exists(fp) and os.path.getsize(fp) > 500:
        return code, "cached", 0
    import baostock as bs
    lg = bs.login()
    if lg.error_code != "0":
        return code, "loginfail", 0
    try:
        rs = bs.query_history_k_data_plus(
            sym, "date,open,high,low,close,volume",
            start_date=START, end_date=END, frequency="d", adjustflag="2")
        rows = []
        while rs.error_code == "0" and rs.next():
            rows.append(rs.get_row_data())
        if len(rows) < min_bars:
            return code, "short", len(rows)
        df = pd.DataFrame(rows, columns=["date","open","high","low","close","volume"])
        for c in ["open","high","low","close","volume"]:
            df[c] = pd.to_numeric(df[c], errors="coerce")
        df = df.dropna()
        df["time"] = pd.to_datetime(df["date"]).astype("int64") // 10**9
        df = df.rename(columns={"volume":"tick_volume"})
        df[["time","open","high","low","close","tick_volume"]].to_parquet(fp, index=False)
        return code, "ok", len(df)
    except Exception as e:
        return code, "err:" + str(e)[:40], 0
    finally:
        bs.logout()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max", type=int, default=0, help="限制下载数量(0=全部)")
    ap.add_argument("--threads", type=int, default=6)
    args = ap.parse_args()

    print("获取股票列表...")
    stocks = get_universe()
    if args.max and args.max > 0:
        stocks = stocks[:args.max]
    print(f"目标股票数: {len(stocks)}")

    t0 = time.time()
    stat = {"ok":0,"cached":0,"short":0,"loginfail":0,"err":0,"other":0}
    done = 0
    with ThreadPoolExecutor(max_workers=args.threads) as ex:
        futs = {ex.submit(pull_stock, s, args.threads): s for s in stocks}
        for fut in as_completed(futs):
            try:
                code, res, n = fut.result()
            except Exception as e:
                res = "crash"; n = 0; code = "?"
            stat[res if res in stat else "other"] += 1
            done += 1
            if done % 500 == 0:
                print(f"[{done}/{len(stocks)}] 统计={stat} elapsed={time.time()-t0:.0f}s")
    print("全部完成:", stat, "总耗时", round(time.time()-t0,0), "s", "->", OUTDIR)

if __name__ == "__main__":
    main()
