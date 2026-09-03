# -*- coding: utf-8 -*-
import os, pandas as pd, io
root = r"C:\Users\mine\Desktop\大A量化监控系统"
buf = io.StringIO()
def w(*a):
    print(*a, file=buf)
pk = os.path.join(root, "PA_Agent6.24（激进但机会多）\PA_Agent", "pa_agent", "main.py")
w("=== main.py head ===")
try:
    txt = open(pk, encoding="utf-8").read()
    for l in txt.splitlines()[:80]: w(l)
except Exception as e:
    w("ERR "+str(e))
w("\n=== A股 sample ===")
adata = os.path.join(root, "A股数据", "parquet")
try:
    flist = os.listdir(adata)[:6]
    w("files: %s" % flist)
    for f in flist[:3]:
        fp = os.path.join(adata, f)
        df = pd.read_parquet(fp)
        w("  %s shape=%s cols=%s" % (f, df.shape, list(df.columns)[:12]))
        w("   dtypes=%s" % {c: str(t) for c,t in df.dtypes.items()})
except Exception as e:
    w("ERR "+str(e))
op = r"C:\Users\mine\Downloads\quant_research\report_schema.txt"
open(op, "w", encoding="utf-8").write(buf.getvalue())
print("WRITTEN", op)
