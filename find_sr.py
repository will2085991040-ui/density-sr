# -*- coding: utf-8 -*-
import os
root = r"C:\Users\mine\Downloads\quant_research"
hits=[]
for dirpath, dirs, files in os.walk(root):
    if "node_modules" in dirpath or ".git" in dirpath: continue
    for f in files:
        if f == "sr_engine.py" or f == "local_data_loader.py":
            hits.append(os.path.join(dirpath, f))
print("FOUND")
for h in hits: print(h)
