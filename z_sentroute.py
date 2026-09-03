# -*- coding: utf-8 -*-
p = r'C:/Users/mine/Downloads/quant_research/server.py'
t = open(p, encoding='utf-8').read()
anchor = '            if endpoint == "/api/rt/realtime":'
assert anchor in t, 'a'
route = '''            if endpoint == "/api/rt/sentiment":
                from aiquant.market_sentiment import sentiment_market
                return 200, json.dumps(sentiment_market(), default=str).encode(), 'application/json'
'''
t = t.replace(anchor, route + anchor, 1)
open(p,'w',encoding='utf-8').write(t)
print('sentiment route added')
