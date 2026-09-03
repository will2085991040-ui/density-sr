# -*- coding: utf-8 -*-
import shutil, os
src = r"C:\Users\mine\Downloads\quant_research\detect_support_resistance_extract\Detect_support_and_resistance_levels-main\src"
dst = r"C:\Users\mine\Downloads\quant_research\aiquant\engine\vendor\detect_support"
if os.path.isdir(dst):
    shutil.rmtree(dst, ignore_errors=True)
shutil.copytree(src, dst)
print("copied to", dst)
print("sr_engine exists:", os.path.exists(os.path.join(dst,"sr_engine.py")))
print("files:", sum(len(fs) for _,_,fs in os.walk(dst)))
