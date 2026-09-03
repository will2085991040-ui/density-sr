# -*- coding: utf-8 -*-
import requests
h={'User-Agent':'Mozilla/5.0','Referer':'http://www.10jqka.com.cn/','Host':'d.10jqka.com.cn'}
# 同花顺分时/实时尝试
for path in ['/v6/line/hs_600519/02/last.js','/time.html?code=600519','/v6/minute/hs_600519','/data/hq_today.php']:
    try:
        rr=requests.get('http://d.10jqka.com.cn'+path,headers=h,timeout=6)
        print(path, rr.status_code, repr(rr.text[:70]))
    except Exception as e:
        print(path,'ERR',repr(e)[:80])
