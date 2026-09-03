# -*- coding: utf-8 -*-
import py_compile
f=r"C:/Users/mine/Downloads/quant_research/aiquant/factor_mine.py"
t=open(f,encoding="utf-8").read()
t=t.replace('"mom13_ds","risk_t","mom13_norm"]','"mom_d","mom_t","mom_som"]')
# restore correct names
t=t.replace('"mom_d","risk_t","mom_norm"]','"mom_d,"risk_t","mom_norm"]') + ""  # noop guard
open(f,"w",encoding="utf-8").write(t)
py_compile.compile(f, doraise=True)
print("done")
