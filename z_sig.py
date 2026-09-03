# -*- coding: utf-8 -*-
import sys, json
sys.path.insert(0, r'C:/Users/mine/Downloads/quant_research')
from aiquant.signal_engine import signals_for
bands=[{'zone_type':'support','center':1290.0},{'zone_type':'support','center':1280.0},
       {'zone_type':'resist','center':1300.0},{'zone_type':'resist','center':1310.0}]
r=signals_for('600519','A股','daily',price=1295.0,sr_bands=bands,ema5=1296.0,ema10=1293.0,ema20=1290.0)
print('SIG', json.dumps(r,ensure_ascii=False))
# check quote price from realtime
import requests
import aiquant.realtime_sina as RS
q=RS.quote('600519','A股')
print('QUOTE', q)
