# -*- coding: utf-8 -*-
import py_compile
f=r"C:/Users/mine/Downloads/quant_research/server.py"
t=open(f,encoding="utf-8").read()
old="syms = list_symbols(_cat(), \"A股\")[:400]"
new="syms = list_symbols(_cat(), \"A股\")[:60]"
assert old in t, "universe"
t=t.replace(old,new,1)
open(f,"w",encoding="utf-8").write(t)
py_compile.compile(f,doraise=True)
print("universe -> 60")
