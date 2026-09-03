# -*- coding: utf-8 -*-
"""
并行下载全A股【股票】(剔除基金/ETF/债基/指数/B股/北交所) 日线
-> ashare_stocks/{code}_daily.parquet
复权: baostock adjustflag=2 (前复权)
断点续传。 用法: python download_ashare_stocks.py [--max N] [--threads T]
"""
import os, time, argparse, collections
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(BASE, "ashare_stocks")
os.makedirs(OUTDIR, exist_ok=True)
START, END = "2021-01-01", "2026-08-23"
MIN_BARS = 60

def is_equity(code):
    """仅保留 A股个股：60/00/30/68 开头且非指数非B股"""
    # code 形如 'sh.600519'
    pre, num = code.split(".")
    if pre == "sh":
        if num.startswith("60") or num.startswith("68"):
            return True
        if num.startswith("900") or num.startswith("now."):
            return False
    if pre == "sz":
        if num.startswith("000") or num.startswith("001") or num.startswith("002") or num.startswith("003"):
            return True
        if num.startswith("300") or num.startswith("301"):
            return True
        if num.startswith("200") or num.startswith("201") or num.startswith("399"):
            return False  # B股/指数
    return False

def get_universe(day="2026-08-21"):
    import baostock as bs
    bs.login()
    rs = bs.query_all_stock(day=day)
    rows = []
    while rs.error_code == "0" and rs.next():
        rows.append(rs.get_row_data())
    bs.logout()
    out = [r[0] for r in rows if r[1] == "1" and is_equity(r[0])]
    return out

def pull_stock(sym, min_bars):
    code = sym.split(".")[1]
    fp = os.path.join(OUTDIR, f"{code}_daily.parquet")
    if os.path.exists(fp) and os.path.getsize(fp) > 500:
        return code, "cached", 0
    import baostock as bs
    bs.login()
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
        return code, "err:%s" % str(e)[:40], 0
    finally:
        bs.logout()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max", type=int, default=0)
    ap.add_argument("--threads", type=int, default=10)
    args = ap.parse_args()
    stocks = get_universe()
    print("equity universe:", len(stocks))
    if args.max and args.max > 0:
        stocks = stocks[:args.max]
    print("to download:", len(stocks))
    t0 = time.time()
    stat = collections.Counter()
    done = 0
    with ThreadPoolExecutor(max_workers=args.threads) as ex:
        futs = {ex.submit(pull_stock, s, args.threads): s for s in stocks}
        for fut in as_completed(futs):
            try:
                code, res, n = fut.result()
            except Exception as e:
                code, res = "?", "crash"
            stat[res if res in ("ok","cached","short","loginfail") else "err"] += 1
            done += 1
            if done % 500 == 0:
                print("[%d/%d] %s elapsed=%.0fs" % (done, len(stocks), dict(stat), time.time()-t0))
    print("DONE", dict(stat), "elapsed=%.0fs -> %s" % (time.time()-t0, OUTDIR))

if __name__ == "__main__":
    main()
