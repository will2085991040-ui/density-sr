# -*- coding: utf-8 -*-
"""并行下载全A股股票(剔除基金)日线 -> ashare_stocks/{code}_daily.parquet
复权 adjustflag=2 前复权; 断点续传; 失败重试1次; 进度写 progress.log
用法: python download_ashare_complete.py [--max N] [--threads T]
"""
import os, time, argparse, collections
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(BASE, "ashare_stocks")
os.makedirs(OUTDIR, exist_ok=True)
START, END = "2021-01-01", "2026-08-23"
MIN_BARS = 60
LOG = os.path.join(BASE, "progress.log")

def log(msg):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(msg + "\n")

def is_equity(code):
    pre, num = code.split(".")
    if pre == "sh" and (num.startswith("60") or num.startswith("68")): return True
    if pre == "sz" and (num.startswith("000") or num.startswith("001") or num.startswith("002") or num.startswith("003") or num.startswith("300") or num.startswith("301")): return True
    return False

def get_universe(day="2026-08-21"):
    import baostock as bs
    bs.login()
    rs = bs.query_all_stock(day=day)
    rows = []
    while rs.error_code == "0" and rs.next():
        rows.append(rs.get_row_data())
    bs.logout()
    return [r[0] for r in rows if r[1] == "1" and is_equity(r[0])]

def _download(sym):
    code = sym.split(".")[1]
    fp = os.path.join(OUTDIR, f"{code}_daily.parquet")
    if os.path.exists(fp) and os.path.getsize(fp) > 500:
        return code, "cached", 0
    import baostock as bs
    for attempt in (1, 2):
        try:
            bs.login()
            rs = bs.query_history_k_data_plus(
                sym, "date,open,high,low,close,volume",
                start_date=START, end_date=END, frequency="d", adjustflag="2")
            rows = []
            while rs.error_code == "0" and rs.next():
                rows.append(rs.get_row_data())
            if rs.error_code != "0":
                bs.logout()
                if attempt == 1:
                    continue
                return code, "err:" + rs.error_code, 0
            bs.logout()
            if len(rows) < MIN_BARS:
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
            try: bs.logout()
            except Exception: pass
            if attempt == 1:
                continue
            return code, "err:" + str(e)[:40], 0
    return code, "err", 0

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max", type=int, default=0)
    ap.add_argument("--threads", type=int, default=8)
    args = ap.parse_args()
    stocks = get_universe()
    print("equity universe:", len(stocks))
    if args.max and args.max > 0:
        stocks = stocks[:args.max]
    print("to download:", len(stocks))
    log("[start] universe=%d target=%d threads=%d" % (len(stocks), len(stocks), args.threads))
    t0 = time.time()
    stat = collections.Counter()
    done = 0
    with ThreadPoolExecutor(max_workers=args.threads) as ex:
        futs = {ex.submit(_download, s): s for s in stocks}
        for fut in as_completed(futs):
            try:
                code, res, n = fut.result()
            except Exception as e:
                code, res = "?", "crash"
            stat[res if res in ("ok","cached","short") else "err"] += 1
            done += 1
            if done % 200 == 0:
                m = "[%d/%d] %s elapsed=%.0fs" % (done, len(stocks), dict(stat), time.time()-t0)
                print(m, flush=True); log(m)
    m = "DONE %s elapsed=%.0fs dir=%s files=%d" % (dict(stat), time.time()-t0, OUTDIR, len(os.listdir(OUTDIR)))
    print(m, flush=True); log(m)

if __name__ == "__main__":
    main()
