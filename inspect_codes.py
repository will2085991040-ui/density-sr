# -*- coding: utf-8 -*-
import os, collections
d = r"C:\Users\mine\Downloads\quant_research\ashare_full"
files = [f for f in os.listdir(d) if f.endswith(".parquet")]
codes = [f.split("_")[0] for f in files]
def cat(code):
    if code.startswith("5"): return "5fundETF"
    if code.startswith("1"): return "1bondETF"
    if code.startswith("68"): return "STAR"
    if code.startswith("60"): return "SHmain"
    if code.startswith("30"): return "ChiNext"
    if code.startswith("00"): return "SZmain"
    if code.startswith("2"): return "2Bsh"
    if code.startswith("8") or code.startswith("4"): return "NJSE"
    return "?"
cnts = collections.Counter(cat(x) for x in codes)
print("total files:", len(codes))
print("buckets:", dict(cnts))
print("sample sorted:", sorted(codes)[:8])
