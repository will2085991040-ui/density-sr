# -*- coding: utf-8 -*-
p = "C:/Users/mine/Downloads/quant_research/server.py"
t = open(p, encoding="utf-8").read()
old = '''    if bars:
        out["kline"] = [{"open": x["open"], "close": x["close"], "low": x["low"],
                         "high": x["high"], "volume": x.get("volume")} for x in bars]
        out["dates"] = [str(x["date"])[-8:] for x in bars]
        out["closes"] = [float(x["close"]) for x in bars]'''
new = '''    if bars:
        out["kline"] = [{"open": x["open"], "close": x["close"], "low": x["low"],
                         "high": x["high"], "volume": x.get("volume", x.get("vol"))} for x in bars]
        out["dates"] = [str(x.get("date") or x.get("dt"))[-8:] for x in bars]
        out["closes"] = [float(x["close"]) for x in bars]'''
assert old in t, "kline anchor"
t = t.replace(old, new, 1)
open(p, "w", encoding="utf-8").write(t)
import py_compile; py_compile.compile(p, doraise=True)
print("patched kline schema OK")
