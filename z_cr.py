# -*- coding: utf-8 -*-
import py_compile
f=r"C:/Users/mine/Downloads/quant_research/server.py"
t=open(f,encoding="utf-8").read()
anchor = 'def _esc(s):'
fn = '''def channel_json(symbol, market, price):
    try:
        from aiquant.market import load
        from aiquant.channel_analysis import analyze_ai
        df = None
        try:
            df = load(_cat(), "A股", symbol, "daily")
        except Exception:
            df = None
        if df is None or len(df) < 66:
            from pandas import DataFrame as _DF
            bars = _bars_of(symbol, market, "daily", 160)
            df = _DF(bars) if bars else None
        return analyze_ai(df, symbol, market, price=price)
    except Exception as e:
        return {"detected": False, "is_wide": False, "read_note": "通道分析失败: %s" % e,
                "symbol": symbol, "price": price}


'''
assert anchor in t
t=t.replace(anchor, fn+anchor, 1)
old = '''    if path == "/api/knowledge/ep004":
        return 200, json.dumps(knowledge_list()), "application/json"'''
new = '''    if path == "/api/knowledge/ep004":
        return 200, json.dumps(knowledge_list()), "application/json"
    if path == "/api/channel":
        sym = _q("symbol", "600519"); mk = _q("market", "A股"); pxv = _q("price", None)
        px = float(pxv) if pxv else None
        return 200, json.dumps(channel_json(sym, mk, px)), "application/json"'''
assert old in t, "route anchor"
t=t.replace(old,new,1)
open(f,"w",encoding="utf-8").write(t)
py_compile.compile(f,doraise=True)
print("channel route added")
