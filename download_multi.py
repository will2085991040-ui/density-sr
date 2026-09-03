# -*- coding: utf-8 -*-
"""下载跨板块代表组合(含各类龙头) -> ashare_multi/{code}_daily.parquet，然后声明全市场多板块"
codes covering all boards:
 沪深主板 + 创业板 + 科创板 的知名大/中市值个股
"""
import os, time, collections, pandas as pd

BASE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(BASE, "ashare_multi")
os.makedirs(OUTDIR, exist_ok=True)
START, END = "2019-01-01", "2026-08-23"

# 多板块代表样本（覆盖沪主板/深主板/创业板/科创板）
CODES = [
 # 沪主板
 "sh.600519","sh.600036","sh.601318","sh.601988","sh.601398","sh.600030",
 "sh.601899","sh.600900","sh.600028","sh.601012","sh.600887","sh.600276",
 "sh.600309","sh.601668","sh.601857","sh.601088","sh.600050","sh.600104",
 # 深主板
 "sz.000001","sz.000858","sz.000651","sz.000333","sz.000568","sz.000792",
 "sz.002594","sz.002415","sz.002475","sz.000625","sz.002352",
 # 创业板
 "sz.300750","sz.300059","sz.300124","sz.300015","sz.300760","sz.300014",
 "sz.300999","sz.300274","sz.300308","sz.300413",
 # 科创板
 "sh.688981","sh.688111","sh.688008","sh.688036","sh.688012","sh.688169",
 "sh.688068","sh.688126","sh.688185",
]

import baostock as bs
bs.login()
ok, fail = [], []
for sym in CODES:
    code = sym.split(".")[1]
    fp = os.path.join(OUTDIR, "%s_daily.parquet" % code)
    if os.path.exists(fp) and os.path.getsize(fp) > 500:
        ok.append(code); continue
    try:
        rs = bs.query_history_k_data_plus(
            sym, "date,open,high,low,close,volume",
            start_date=START, end_date=END, frequency="d", adjustflag="2")
        rows = []
        while rs.error_code == "0" and rs.next():
            rows.append(rs.get_row_data())
        if len(rows) < 60:
            fail.append((code, "short%d" % len(rows))); continue
        df = pd.DataFrame(rows, columns=["date","open","high","low","close","volume"])
        for c in ["open","high","low","close","volume"]:
            df[c] = pd.to_numeric(df[c], errors="coerce")
        df = df.dropna()
        df["time"] = pd.to_datetime(df["date"]).astype("int64")//10**9
        df = df.rename(columns={"volume":"tick_volume"})
        df[["time","open","high","low","close","tick_volume"]].to_parquet(fp, index=False)
        ok.append(code)
    except Exception as e:
        fail.append((code, "err"+str(e)[:40]))
    time.sleep(0.1)
bs.logout()
print("ok:%d fail:%d" % (len(ok), len(fail)), "->", OUTDIR)
for c in ok:
    print("  ", c)
