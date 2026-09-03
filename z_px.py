# -*- coding: utf-8 -*-
p = r'C:/Users/mine/Downloads/quant_research/server.py'
t = open(p, encoding='utf-8').read()
old = "        qq = out.get('quote') or {}; px = qq.get('price')"
new = "        qq = out.get('quote') or {}; px = qq.get('price') or (cl[-1] if cl else None)"
assert old in t
t = t.replace(old, new, 1)
open(p,'w',encoding='utf-8').write(t)
print('price fallback ok')
