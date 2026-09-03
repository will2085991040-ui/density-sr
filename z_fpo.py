# -*- coding: utf-8 -*-
import py_compile
f=r"C:/Users/mine/Downloads/quant_research/server.py"
t=open(f,encoding="utf-8").read()
old="pairs.append((s, d))"
new="pairs.append((d, s))"
assert t.count(old)==1, t.count(old)
t=t.replace(old,new,1)
open(f,"w",encoding="utf-8").write(t)
py_compile.compile(f,doraise=True)
print("factor pairs order fixed")
