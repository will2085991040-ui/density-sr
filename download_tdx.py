# -*- coding: utf-8 -*-
"""pytdx(通达信) 下载 A股日线 -> ashare_tdx/{code}_daily.parquet (创业板/科创板等)
列: time(unix秒), open, high, low, close, tick_volume
"""
import os, time, collections
import pandas as pd
from pytdx.hq import TdxHq_API

BASE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(BASE, "ashare_tdx")
os.makedirs(OUTDIR, exist_ok=True)
_WANT = 2400
_SERVERS = [
    ("115.238.90.165",7709),("180.153.18.170",7709),("119.147.212.81",7709),
    ("14.17.75.71",7709),("59.173.18.77",7709),("114.67.62.91",7709),
]

def market_of(code):
    if code.startswith(("002","003","300","301")): return 0
    if code.startswith(("60","688","689")): return 1
    return 1

def connect():
    last=None
    for h,p in _SERVERS:
        a=TdxHq_API()
        try:
            if a.connect(h,p,time_out=10): return a
        except Exception as e:
            last=e
    raise RuntimeError("all tdx down: %s" % last)

def fetch_daily(api, mkt, code, want=_WANT):
    """分页拉日线返回正序 dict 列表"""
    rows=[]; seen=set(); off=0
    while len(seen) < want:
        try:
            raw=api.get_security_bars(9, mkt, code, off, 800)
        except Exception:
            break
        if not raw:
            break
        new=0
        for r in raw:
            dt=str(r.get("datetime",""))
            if dt and dt not in seen:
                seen.add(dt); rows.append(r); new+=1
        if new==0:
            break
        off += len(raw)
    rows.reverse()
    return rows

CODES = [
    "300750","300059","300124","300760","300014","300999","300274","300308",
    "300413","300015","300033","300408","688981","688111","688008","688036",
    "688169","688068","688126","688185","688390","688777","688005","688012",
]

def main():
    try:
        api=connect()
    except Exception as e:
        print("CONNECT FAIL:", e); return
    stat=collections.Counter()
    for code in CODES:
        fp=os.path.join(OUTDIR,"%s_daily.parquet"%code)
        if os.path.exists(fp) and os.path.getsize(fp)>500:
            stat["cached"]+=1; continue
        try:
            rows=fetch_daily(api, market_of(code), code)
            if len(rows)<60:
                stat["short"]+=1; continue
            df=pd.DataFrame(rows)
            df["time"]=pd.to_datetime(df["datetime"]).astype("int64")//10**9
            df=df.rename(columns={"vol":"tick_volume"})
            df[["time","open","high","low","close","tick_volume"]].to_parquet(fp,index=False)
            stat["ok"]+=1
            print("ok", code, len(rows), flush=True)
        except Exception as e:
            stat["err"]+=1
            print("err", code, str(e)[:40], flush=True)
        time.sleep(0.1)
    try: api.disconnect()
    except Exception: pass
    print("done", dict(stat), "->", OUTDIR)

if __name__ == "__main__":
    main()
