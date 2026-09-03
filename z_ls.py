# -*- coding: utf-8 -*-
f = r"C:/Users/mine/Downloads/quant_research/server.py"
t = open(f, encoding="utf-8").read()
import re, py_compile
# replace list_symbols("X") -> list_symbols(_cat(), "X") and list_symbols(market)/list_symbols("A股") in init_json etc
t = t.replace('list_symbols(market)', 'list_symbols(_cat(), market)')
t = t.replace('syms = list_symbols("A股")', 'syms = list_symbols(_cat(), "A股")')
t = t.replace('for s in list_symbols("A股")', 'for s in list_symbols(_cat(), "A股")')
t = t.replace('syms = list_symbols("A股")[:400]', 'syms = list_symbols(_cat(), "A股")[:400]')
# also list_symbols("指数") etc
t = t.replace('list_symbols(mk)', 'list_symbols(_cat(), mk)')
open(f,"w",encoding="utf-8").write(t)
py_compile.compile(f, doraise=True)
# show remaining bare list_symbols
import re
for m in re.finditer(r'list_symbols\([^)]*\)', t):
    print(m.group(0))
