# -*- coding: utf-8 -*-
"""补拉 创业板/科创板 代表股（带节流等待）-> ashare_multi2"""
import os, time, pandas as pd
BASE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(BASE, "ashare_multi")
os.makedirs(OUTDIR, exist_ok=True)
START, END = "2019-01-01", "2026-08-23"
CODES = [
 "sz.300750","sz.300059","sz.300124","sz.300760","sz.300014","sz.300999",
 "sz.300274","sz.300308","sz.300413","sh.688981","sh.688111","sh.688008",
 "sh.688036","sh.688169","sh.688068","sh.688126","sh.688185",
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
        rs = bs.query_history_k_data_plus(sym, "date,open,high,low,close,volume",
            start_date=START, end_date=END, frequency="d", adjustflag="2")
        rows = []
        while rs.error_code == "0" and rs.next():
            rows.append(rs.get_row_data())
        if len(rows) < 60:
            fail.append((code,"short")); continue
        df = pd.DataFrame(rows, columns=["date","open","high","low","close","volume"])
        for c in ["open","high","low","close","volume"]:
            df[c] = pd.to_numeric(df[c], errors="coerce")
        df = df.dropna()
        df["time"] = pd.to_datetime(df["date"]).astype("int64")//10**9
        df = df.rename(columns={"volume":"tick_volume"})
        df[["time","open","high","low","close","tick_volume"]].to_parquet(fp, index=False)
        ok.append(code)
        print("ok", code, flush=True)
    except Exception as e:
        fail.append((code,"err"+str(e)[:30]))
        print("fail", code, str(e)[:40], flush=True)
    time.sleep(1.2)   # 节流等待
bs.logout()
print("done ok:%d fail:%d" % (len(ok), len(fail)))
