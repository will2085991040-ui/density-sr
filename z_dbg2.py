# -*- coding: utf-8 -*-
import sys, time, requests, json
sys.path.insert(0, r'C:/Users/mine/Downloads/quant_research')
from aiquant.market_sentiment import _EM
# correct ulist.np endpoint
url='https://push2.eastmoney.com/api/qt/ulist.np/get?fltt=2&secids=1.000001,0.399001,1.000300,0.399006&fields=f2,f3,f4,f6,f12,f14'
for i in range(2):
    try:
        r=requests.get(url,headers=_EM,timeout=12)
        print('idx',r.status_code,r.text[:240]); break
    except Exception as e:
        print('RE',repr(e)); time.sleep(1)
# test local breadth load
import aiquant.market as M
print('has load', hasattr(M,'load'), 'list', hasattr(M,'list_symbols'))
try:
    syms=M.list_symbols('A股'); print('nsym', len(syms))
    df=M.load(syms[0],'daily','A股'); print('df', None if df is None else df.tail(2).to_dict('records'))
except Exception as e:
    import traceback; print('LOADERR', repr(e)); traceback.print_exc()
