# -*- coding: utf-8 -*-
import sys, io
sys.path.insert(0, r"C:\Users\mine\Downloads\quant_research\aiquant\engine\vendor")
import pandas as pd
buf=io.StringIO()
def w(*a): print(*a, file=buf)
import os
adata = r"C:\Users\mine\Desktop\大A量化监控系统\A股数据\parquet\stocks\000001_daily.parquet"
df = pd.read_parquet(adata).rename(columns={"tick_volume":"volume"})
df["date"] = pd.to_datetime(df["time"], unit="s")
w("frame:", df.shape, list(df.columns))
try:
    from src.sr_engine import SREngine, build_summary
    zones, info = SREngine(n_zones=8).detect(df, "000001")
    sm = build_summary(zones, df, "both", info)
    w("SREngine OK zones=%d info=%s" % (len(zones), list(info.keys())[:8]))
    if zones:
        z = zones[0]
        w("top zone:", {k:(round(v,3) if isinstance(v,float) else v) for k,v in list(z.items())[:6]})
except Exception as e:
    import traceback; w("ERR", e); w(traceback.format_exc()[:1200])
open(r"C:\Users\mine\Downloads\quant_research\report_srvend.txt","w",encoding="utf-8").write(buf.getvalue())
print("done")
