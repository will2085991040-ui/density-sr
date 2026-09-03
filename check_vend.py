# -*- coding: utf-8 -*-
import os
v = r"C:\Users\mine\Downloads\quant_research\aiquant\engine\vendor"
print("vendor contents:", os.listdir(v) if os.path.isdir(v) else "MISSING")
src = os.path.join(v, "src")
if os.path.isdir(src):
    print("src top:", sorted(os.listdir(src))[:20])
    print("src/sr_engine.py exists:", os.path.exists(os.path.join(src,"sr_engine.py")))
    print("init exists:", os.path.exists(os.path.join(src,"__init__.py")))
    for root,dirs,files in os.walk(src):
        for f in files:
            if f=="__init__.py":
                print("  init at:", os.path.relpath(root, src))
