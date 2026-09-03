# -*- coding: utf-8 -*-
import shutil, os
base = r"C:\Users\mine\Downloads\quant_research\aiquant\engine\vendor"
old = os.path.join(base, "detect_support")
if os.path.isdir(old):
    shutil.rmtree(old, ignore_errors=True)
os.makedirs(base, exist_ok=True)
src_orig = r"C:\Users\mine\Downloads\quant_research\detect_support_resistance_extract\Detect_support_and_resistance_levels-main\src"
dst = os.path.join(base, "src")
if os.path.isdir(dst):
    shutil.rmtree(dst, ignore_errors=True)
shutil.copytree(src_orig, dst)
# ensure __init__.py at src root and key subdirs
for rel in ["", "srlab", "srlm_tmp"]:
    p = os.path.join(dst, rel) if rel else dst
    if os.path.isdir(p):
        ip = os.path.join(p, "__init__.py")
        if not os.path.exists(ip):
            open(ip, "w", encoding="utf-8").write("# -*- coding: utf-8 -*-\n")
print("vendor src ready:", os.path.exists(os.path.join(dst,"sr_engine.py")))
print("src/srlab:", os.path.isdir(os.path.join(dst,"srlab")))
