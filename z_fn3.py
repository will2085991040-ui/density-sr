# -*- coding: utf-8 -*-
import py_compile
f=r"C:/Users/mine/Downloads/quant_research/aiquant/factor_mine.py"
t=open(f,encoding="utf-8").read()
# Fix the whole FACTOR_NAMES block to exact correct values
import re
new_block = 'FACTOR_NAMES = ["mom5","mom10","mom20","mom60","rsi14","macd","macd_dist","atr_pct",\n"vol_ratio","ma20_dist","ma60_dist","volatility20","skew20","kurt20",\n"ret_ratio","vol20_trend","close_pos","ema_ratio","obv_slope",\n"mom_ds","mom_t","mom_som"]'
t = re.sub(r'FACTOR_NAMES = \[[^\]]*\](?=\n\ndef factor_df)', new_block, t, count=1, flags=re.S)
open(f,"w",encoding="utf-8").write(t)
py_compile.compile(f, doraise=True)
print("fixed names")
