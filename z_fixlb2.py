# -*- coding: utf-8 -*-
p = r'C:/Users/mine/Downloads/quant_research/aiquant/market_sentiment.py'
t = open(p, encoding='utf-8').read()
t = t.replace("from aiquant.market import list_symbols, load\n        syms = list_symbols(\"A股\")", "from aiquant.market import MarketCatalog, list_symbols, load\n        cat = MarketCatalog()\n        syms = list_symbols(cat, \"A股\")", 1)
t = t.replace("df = load(s, \"daily\", \"A股\")", "df = load(cat, \"A股\", s, \"daily\")", 1)
open(p,'w',encoding='utf-8').write(t)
print('fixed')
