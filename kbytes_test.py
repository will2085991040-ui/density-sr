# -*- coding: utf-8 -*-
import sys, io; sys.path.insert(0, r"C:\Users\mine\Downloads\quant_research")
from aiquant.market import MarketCatalog, load
from aiquant.engine.indicators import add_indicators
from aiquant.report.report import kline_macd_bytes
cat = MarketCatalog()
df = load(cat, "A股", "600519", "daily")
df = add_indicators(df)
b = kline_macd_bytes(df, title="贵州茅台 600519 日线", tail=150)
print("bytes", len(b))
print("PNG magic:", b[:8].hex())
# PIL present?
try:
    from PIL import Image; im = Image.open(io.BytesIO(b)); print("PIL OK size", im.size)
except Exception as e:
    print("PIL MISSING:", e)
open(r"C:\Users\mine\Downloads\quant_research\out\k600519.png","wb").write(b)
print("saved png")
