# -*- coding: utf-8 -*-
import io, importlib.util
buf=io.StringIO()
def w(*a): print(*a, file=buf)
mods = ["pandas","numpy","pyarrow","matplotlib","wordcloud","jinja2","requests","plotly","sklearn","scipy","baostock","pytdx","PyQt6","pyinstaller","yfinance","akshare"]
for m in mods:
    w("{:14} {}".format(m, "OK" if importlib.util.find_spec(m) else "MISSING"))
# A股 filename conventions for key lookup
import os
st = os.path.join(r"C:\Users\mine\Desktop\大A量化监控系统\A股数据\parquet\stocks")
fs = os.listdir(st)[:8]
w("A股 stocks samples:", fs)
w("has 000001:", os.path.exists(os.path.join(st,"000001_daily.parquet")))
w("has sh600519:", any(x.startswith("600519") for x in fs))
# check what a full symbol to file looks like for indices
ix = os.path.join(r"C:\Users\mine\Desktop\大A量化监控系统\A股数据\parquet\indices")
w("idx samples:", os.listdir(ix)[:6])
open(r"C:\Users\mine\Downloads\quant_research\report_deps.txt","w",encoding="utf-8").write(buf.getvalue())
print("written")
