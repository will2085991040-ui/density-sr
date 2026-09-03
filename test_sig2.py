# -*- coding: utf-8 -*-
import sys, io
sys.path.insert(0, r"C:\Users\mine\Downloads\quant_research\aiquant")
from market import MarketCatalog, load, list_symbols
from engine.signals import run_signal
cat=MarketCatalog()
buf=io.StringIO()
def w(*a): print(*a,file=buf)
# try several A股 + a runaway gold
tests = [("A股","600519"),("A股","000858"),("A股","300750"),("MT5","XAUUSDm"),("OKX","BTCUSDT" if "BTCUSDT" in list_symbols(cat,"OKX") else list_symbols(cat,"OKX")[0])]
for mkt,sym in tests:
    df = load(cat, mkt, sym, "daily")
    if df is None or len(df)<30:
        w("skip", mkt, sym); continue
    try:
        sig = run_signal(df, "激进")
        w("%s %s: vote=%s mom=%s score=%d conf=%d -> %s %s support=%s resis=%s" % (
            mkt, sym, sig["direction_vote"], sig["momentum"], sig["score"], sig["confidence"],
            sig["order"], sig["direction"], sig["support"], sig["resistance"]))
    except Exception as e:
        w("%s %s ERR %s" % (mkt, sym, str(e)[:80]))
open(r"C:\Users\mine\Downloads\quant_research\report_sigtest.txt","w",encoding="utf-8").write(buf.getvalue())
print("done")
