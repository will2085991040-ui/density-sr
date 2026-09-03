# -*- coding: utf-8 -*-
import requests
tests = {
 'ths_d71': 'http://d.10jqka.com.cn/v6/line/hs_600519/01/last.js',
 'ths_d71s':'https://d.10jqka.com.cn/v6/line/hs_600519/01/last.js',
 'ths_hq':'http://hq.10jqka.com.cn/hq_portrait_ws/',
 'ths_quote':'http://qd.10jqka.com.cn/quote.php?cate=real&type=stock&callback=cb&return=json&code=600519',
 'ths_sina':'http://hq.sinajs.cn/list=sh600519',
 'tx':'http://qt.gtimg.cn/q=sh600519',
}
h={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64)','Referer':'http://www.10jqka.com.cn/'}
for k,url in tests.items():
    try:
        r=requests.get(url,headers=h,timeout=6)
        print(k, r.status_code, repr(r.text[:90]))
    except Exception as e:
        print(k, 'ERR', repr(e))
