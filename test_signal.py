# -*- coding: utf-8 -*-
import sys, io
sys.path.insert(0, r"C:\Users\mine\Downloads\quant_research\aiquant\engine")
import py_compile, os
for f in ["indicators.py","signals.py","sr.py"]:
    try:
        py_compile.compile(os.path.join(r"C:\Users\mine\Downloads\quant_research\aiquant\engine", f), doraise=True)
        print("compile OK:", f)
    except Exception as e:
        print("compile FAIL:", f, e)
# end-to-end signal test
sys.path.insert(0, r"C:\Users\mine\Downloads\quant_research\aiquant")
import pandas as pd
from market.data import MarketCatalog, load
from engine.signals import run_signal
buf=io.StringIO()
cat=MarketCatalog()
df = load(cat, "A股", "000001", "daily")
for st in ("稳","激进"):
    sig = run_signal(df, st)
    print(st, "->", sig["order"], sig["direction"], "conf", sig["confidence"], "score", sig["score"])
    print("   support", sig["support"], "resistance", sig["resistance"], "entry", sig["entry"], "target", sig["target"])
