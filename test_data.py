# -*- coding: utf-8 -*-
import sys, io
sys.path.insert(0, r"C:\Users\mine\Downloads\quant_research\aiquant")
from market.data import MarketCatalog, load, list_symbols
buf=io.StringIO()
def w(*a): print(*a, file=buf)
cat = MarketCatalog()
stk = list_symbols(cat, "A股")
w("A股 symbols: %d sample %s" % (len(stk), stk[:5]))
df = load(cat, "A股", "000001", "daily")
if df is not None:
    w("000001 daily shape=%s cols=%s" % (df.shape, list(df.columns)))
    w("ts range %s .. %s" % (df["time"].iloc[0], df["time"].iloc[-1]))
mt = list_symbols(cat, "MT5")
w("MT5 symbols: %d sample %s" % (len(mt), mt[:6]))
if mt:
    dft = load(cat, "MT5", mt[0], "H1")
    if dft is not None:
        w("MT5 %s H1 shape=%s ts %s..%s" % (mt[0], dft.shape, dft.time.iloc[0], dft.time.iloc[-1]))
ix = list_symbols(cat, "指数")
w("指数: %d sample %s" % (len(ix), ix[:4]))
ok = list_symbols(cat, "OKX")
w("OKX: %d sample %s" % (len(ok), ok[:4]))
open(r"C:\Users\mine\Downloads\quant_research\report_datatest.txt","w",encoding="utf-8").write(buf.getvalue())
print("done")
