# -*- coding: utf-8 -*-
import urllib.request
def get_sina(codes):
    # codes: list of sh600519/sz000001 style
    url = "https://hq.sinajs.cn/list=" + ",".join(codes)
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Referer": "https://finance.sina.com.cn/"})
    raw = urllib.request.urlopen(req, timeout=25).read().decode("gbk", "replace")
    return raw
r = get_sina(["sh600519","sz000001","sz300750","sh688981"])
print(r[:1200])
