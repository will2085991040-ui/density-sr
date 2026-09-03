# -*- coding: utf-8 -*-
import sys, json, requests
sys.path.insert(0, r'C:/Users/mine/Downloads/quant_research')
from aiquant.market_sentiment import _index_quotes, _zt_pool, _local_breadth, _EM
import aiquant.ensure_data as ED
print('ROOT', ED.existing_root())
# test index directly with retry via requests
for i in range(2):
    try:
        r=requests.get('https://push2.eastmoney.com/api/qt/ulist.get?fltt=2&secids=1.000001,0.399001,1.000300,0.399006&fields=f2,f3,f4,f6,f12,f14',headers=_EM,timeout=12)
        print('idx req', r.status_code, r.text[:200]); break
    except Exception as e:
        print('idx RE', repr(e))
print('idquote', _index_quotes())
print('breadth', _local_breadth(300))
