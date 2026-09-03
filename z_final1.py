# -*- coding: utf-8 -*-
import os, sys, py_compile
root=r"C:/Users/mine/Downloads/quant_research"
# 1) files exist
files = {
 "channel_analysis.py": os.path.join(root,"aiquant","channel_analysis.py"),
 "factor_mine.py": os.path.join(root,"aiquant","factor_mine.py"),
 "pa_llm.py": os.path.join(root,"aiquant","pa_llm.py"),
 "server.py": os.path.join(root,"server.py"),
 "channel_panel.js": os.path.join(root,"webui","channel_panel.js"),
}
for k,v in files.items():
    e=os.path.exists(v)
    try:
        py_compile.compile(v,doraise=True); c="compiles-OK"
    except Exception as ex:
        c="COMPILE-ERR:"+str(ex)[:60]
    print(f"{k}: exists={e} {c}")
# 2) prompt suite
pd=os.path.join(root,"knowledge","prompts")
print("prompts files:", len([f for f in os.listdir(pd) if f.endswith('.txt')]) if os.path.isdir(pd) else 0)
# 3) ep004
ep=os.path.join(root,"knowledge","ep004")
print("ep004 files:", (os.listdir(ep)) if os.path.isdir(ep) else [])
# 4) frozen exe exists + size
exe=os.path.join(root,"dist_v92","dsr_sr.exe")
print("frozen exe:", os.path.exists(exe), os.path.getsize(exe)//(1024**2),"MB" if os.path.exists(exe) else "")
