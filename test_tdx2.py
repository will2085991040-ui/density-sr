# -*- coding: utf-8 -*-
"""AlphaMaster 风格 pytdx 测试：拉 创业板/科创板 日线"""
from pytdx.hq import TdxHq_API
_SERVERS = [
    ("115.238.90.165", 7709),("180.153.18.170", 7709),("119.147.212.81", 7709),
    ("14.17.75.71", 7709),("59.173.18.77", 7709),("114.67.62.91", 7709),
    ("115.238.56.198", 7709),("115.238.90.166", 7709),("60.12.136.218", 7709),
]
def market_of(code):
    if code.startswith(("002","003","300","301")): return 0
    if code.startswith(("60","688","689")): return 1
    return 1
api = TdxHq_API()
conn=None
for host,port in _SERVERS:
    try:
        if api.connect(host,port):
            conn=(host,port); break
    except Exception: pass
print("connected:", conn)
n=0
for code,mkt in [("300750",0),("688981",1),("300059",0),("688008",1)]:
    raw = api.get_security_bars(9, mkt, code, 0, 5)
    if raw:
        n+=1
        print(code, "bars=%d" % len(raw), "fields:", sorted(raw[0].keys()))
        print("   last:", raw[-1])
    else:
        print(code, "None")
print("ok count", n) if conn else print("no conn")
