# -*- coding: utf-8 -*-
"""测试 pytdx 通达信通道拉A股日线 (创业板/科创板)"""
import pytdx
from pytdx.hq import TdxHq_API
api = TdxHq_API()
# 尝试多个通达信行情服务器
servers = [
    ("119.147.212.81", 7709),
    ("124.71.187.122", 7709),
    ("115.238.90.165", 7709),
    ("101.227.77.254", 7709),
]
ok=False
for ip,port in servers:
    try:
        if api.connect(ip, port, time_out=8):
            print("connected", ip)
            ok=True
            break
    except Exception as e:
        print("fail", ip, str(e)[:50])
if ok:
    # 创业板 300750, 科创板 688981. market: 0=深,1=沪
    for code, mkt in [("300750",0),("688981",1),("000001",0)]:
        try:
            df = api.get_security_bars(9, mkt, code, 0, 5)  # 9=daily, last 5 bars
            if df is not None:
                print(code, "bars=", len(df), "last=", df.iloc[-1].to_dict() if len(df) else None)
            else:
                print(code, "None")
        except Exception as e:
            print(code, "err", str(e)[:60])
    api.disconnect()
else:
    print("ALL TDX SERVERS UNREACHABLE")
