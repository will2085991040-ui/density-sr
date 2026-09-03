# -*- coding: utf-8 -*-
p = r'C:/Users/mine/Downloads/quant_research/aiquant/market_sentiment.py'
t = open(p, encoding='utf-8').read()
old = 'def _local_breadth(max_stocks=2200):\n    ups = downs = total = 0'
new_ = "_BREAD_CACHE = [None, 0.0]\n\ndef _local_breadth(max_stocks=2200):\n    import time as _t\n    if _BREAD_CACHE[0] is not None and _t.time() - _BREAD_CACHE[1] < 900.0:\n        return _BREAD_CACHE[0]\n    ups = downs = total = 0"
assert old in t, 'anchor1'
t = t.replace(old, new_, 1)
old2 = '        return {"up": ups, "down": downs, "total": total}'
new2 = '        res = {"up": ups, "down": downs, "total": total}\n        _BREAD_CACHE[0] = res; _BREAD_CACHE[1] = _t.time()\n        return res'
assert old2 in t, 'anchor2'
t = t.replace(old2, new2, 1)
open(p,'w',encoding='utf-8').write(t)
import py_compile; py_compile.compile(p, doraise=True)
print('cache ok')