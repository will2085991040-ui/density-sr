# -*- coding: utf-8 -*-
import py_compile
f=r"C:/Users/mine/Downloads/quant_research/aiquant/factor_mine.py"
t=open(f,encoding="utf-8").read()
t=t.replace('"mom13_ds","risk_t","mom13_norm"','"mom_ds","mom_t","mom_som"')
open(f,"w",encoding="utf-8").write(t)
py_compile.compile(f, doraise=True)
print("fixed")
