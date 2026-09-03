# -*- coding: utf-8 -*-
import os
root = r"C:\Users\mine\Desktop\大A量化监控系统\PA_Agent6.24（激进但机会多）\PA_Agent"
print("=== TOP-LEVEL files ===")
for it in sorted(os.listdir(root)):
    p = os.path.join(root, it)
    sz = os.path.getsize(p) if os.path.isfile(p) else 0
    print("{:<6} {:40} {}".format("DIR " if os.path.isdir(p) else "file", it, sz))
