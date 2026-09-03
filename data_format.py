# -*- coding: utf-8 -*-
import os, io, pandas as pd
root = r"C:\Users\mine\Desktop\大A量化监控系统"
buf = io.StringIO()
def w(*a): print(*a, file=buf)
# A股 parquet structure detail
adata = os.path.join(root, "A股数据", "parquet")
for sub in ["stocks","indices"]:
    p = os.path.join(adata, sub)
    if os.path.isdir(p):
        w("== A股/%s =="%sub)
        files = os.listdir(p)[:6]
        w("  files sample:", files)
        for f in files[:1]:
            fp = os.path.join(p, f)
            df = pd.read_parquet(fp, engine="pyarrow")
            w("  %s rows=%d" %(f, len(df)))
            if "code" in df.columns: w("  codes:", df["code"].iloc[0], df["code"].nunique() if "code" in df else "?")
    else:
        w("== A股/%s = file =="%sub, os.path.getsize(p))
# MT5
mt = os.path.join(root, "MT5_K线数据(1)")
for d in os.listdir(mt):
    dd = os.path.join(mt, d)
    if os.path.isdir(dd):
        files = os.listdir(dd)[:4]
        w("== MT5/%s =="%d, files)
        for f in files[:1]:
            fp = os.path.join(dd, f)
            df = pd.read_parquet(fp)
            w("   %s : shape=%s cols=%s"%(f, df.shape, list(df.columns)[:10]))
    elif os.path.isfile(dd):
        w("== MT5 file", d, os.path.getsize(dd))
# OKX
ok = os.path.join(root, "OKX_K线数据(1)")
for xt in os.listdir(ok):
    dd = os.path.join(ok, xt)
    if os.path.isdir(dd):
        files = os.listdir(dd)[:4]
        w("== OKX/%s =="%xt, files)
        for f in files[:1]:
            fp = os.path.join(dd, f)
            try:
                df = pd.read_parquet(fp)
                w("   %s : shape=%s cols=%s dtypes=%s"%(f, df.shape, list(df.columns)[:10], {c:str(t) for c,t in df.dtypes.items()}))
            except Exception as e: w("   ERR",e)
open(r"C:\Users\mine\Downloads\quant_research\report_dataformat.txt","w",encoding="utf-8").write(buf.getvalue())
print("ok")
