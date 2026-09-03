import akshare as ak
print("akshare version:", ak.__version__)
# Pull real daily kline for a few blue-chip stocks via eastmoney
import time
ok = []
for code, market in [("000001","sh"),("600519","sh"),("300750","sz"),("000858","sz")]:
    try:
        df = ak.stock_zh_a_hist(symbol=code, period="daily", start_date="20210101", end_date="20260823", adjust="qfq")
        if df is not None and not df.empty:
            ok.append((code, len(df), list(df.columns)))
    except Exception as e:
        ok.append((code, "ERR", str(e)[:80]))
for r in ok:
    print(r)
