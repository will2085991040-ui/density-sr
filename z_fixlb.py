# -*- coding: utf-8 -*-
p = r'C:/Users/mine/Downloads/quant_research/aiquant/market_sentiment.py'
t = open(p, encoding='utf-8').read()
old = "        from aiquant.market import list_symbols, load\n        syms = list_symbols('A股')"
new = "        from aiquant.market import MarketCatalog, list_symbols, load\n        cat = MarketCatalog()\n        syms = list_symbols(cat, 'A股')"
assert old in t, 'anch'
t = t.replace(old, new, 1)
old2 = "                df = load(s, 'daily', 'A股')"
new2 = "                df = load(cat, 'A股', s, 'daily')"
assert old2 in t, 'anch2'
t = t.replace(old2, new2, 1)
open(p,'w',encoding='utf-8').write(t)
print('local_breadth fixed')
