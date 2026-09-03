"--- eastmoney kline api test - sh000001 ---";
curl.exe -s -o NUL -w "http=%{http_code} time=%{time_total}" --max-time 20 "https://push2his.eastmoney.com/api/qt/stock/kline/get?secid=1.000001&fields1=f1,f2,f3&fields2=f51,f52,f53,f54,f55,f56&klt=101&fqt=1&lmt=5"
""