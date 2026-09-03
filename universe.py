# -*- coding: utf-8 -*-
import os, io
root = r"C:\Users\mine\Desktop\大A量化监控系统"
buf=io.StringIO()
def w(*a): print(*a, file=buf)
ad = os.path.join(root, "A股数据", "parquet")
for sub in ["stocks","indices"]:
    p = os.path.join(ad, sub)
    files = sorted(os.listdir(p))
    codes = set(); tfs = set()
    for f in files:
        try:
            base = f[:-8] if f.endswith(".parquet") else f
            # {code}_{tf} or idx_{code}_{tf}
            parts = base.split("_")
            if parts[0]=="idx":
                code = parts[1]; tf = parts[-1]
            else:
                tf = parts[-1]; code = "_".join(parts[:-1])
            tfs.add(tf); codes.add(code)
        except Exception: pass
    w("%s: %d files, %d stocks, timeframes %s" % (sub, len(files), len(codes), sorted(tfs)))
# MT5 symbols
mt = os.path.join(root, "MT5_K线数据(1)")
for d in os.listdir(mt):
    dd=os.path.join(mt,d)
    if os.path.isdir(dd):
        syms=set(); tfs=set()
        for f in os.listdir(dd):
            base=f[:-8] if f.endswith(".parquet") else f
            s,t = base.rsplit("_",1) if "_" in base else (base,"?")
            syms.add(s); tfs.add(t)
        w("MT5/%s: %d files, %d symbols, tf %s"%(d,len(os.listdir(dd)),len(syms),sorted(tfs)))
ok = os.path.join(root, "OKX_K线数据(1)")
for d in os.listdir(ok):
    dd=os.path.join(ok,d)
    if os.path.isdir(dd):
        syms=set(); tfs=set()
        for f in os.listdir(dd):
            base=f[:-8] if f.endswith(".parquet") else f
            s,t = base.rsplit("_",1) if "_" in base else (base,"?")
            syms.add(s); tfs.add(t)
        w("OKX/%s: %d files, %d syms, tf %s"%(d,len(os.listdir(dd)),len(syms),sorted(tfs)))
open(r"C:\Users\mine\Downloads\quant_research\report_universe.txt","w",encoding="utf-8").write(buf.getvalue())
print("done")
