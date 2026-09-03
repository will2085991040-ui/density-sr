# -*- coding: utf-8 -*-
p = r'C:/Users/mine/Downloads/quant_research/aiquant/signal_engine.py'
t = open(p, encoding='utf-8').read()
t2 = t.replace("        if zt == 'support' and c < price:",
               "        zz = zt or ''
        if ('sup' in zz.lower()) and c < price:")
t2 = t2.replace("        elif zt == 'resist' and c > price:",
                "        elif ('res' in zz.lower()) and c > price:")
open(p,'w',encoding='utf-8').write(t2)
import py_compile; py_compile.compile(p, doraise=True)
print('ok changed', t!=t2)
