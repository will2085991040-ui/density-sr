# -*- coding: utf-8 -*-
import os
root = r"C:\Users\mine\Desktop\大A量化监控系统\PA_Agent6.24（激进但机会多）\PA_Agent"
pkg = os.path.join(root, "pa_agent")
print("=== run.py ===")
print(open(os.path.join(root,"run.py"),encoding="utf-8").read())
print("=== pa_agent package files ===")
for d in sorted(os.listdir(pkg)):
    p=os.path.join(pkg,d)
    print("{:<6} {}".format("DIR" if os.path.isdir(p) else "file", d))
