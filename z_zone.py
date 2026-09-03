# -*- coding: utf-8 -*-
p = r'C:/Users/mine/Downloads/quant_research/aiquant/signal_engine.py'
t = open(p, encoding='utf-8').read()
old = "        if zt == 'support' and c < price:"
new = "        normalize_z = zt if zt else ''
        if ('support' in normalize_z or 'sup' in normalize_z) and c < price:"
assert old in t
t = t.replace(old, new, 1)
old2 = "        elif zt == 'resist' and c > price:"
new2 = "        elif ('resist' in normalize_z or 'res' in normalize_z or 'resistance' in normalize_z) and c > price:"
assert old2 in t
t = t.replace(old2, new2, 1)
open(p,'w',encoding='utf-8').write(t)
print('zone_type normalized')
