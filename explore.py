# -*- coding: utf-8 -*-
import os, collections, json
root = r"C:\Users\mine\Desktop\大A量化监控系统"
depth_map = {
    "A股数据": 2, "MT5_K线数据(1)": 1, "OKX_K线数据(1)": 1,
    "PA_Agent-6.16（稳但机会少）": 3, "PA_Agent6.24（激进但机会多）": 3,
}
report = {}
for sub, mdepth in depth_map.items():
    d = os.path.join(root, sub)
    if not os.path.isdir(d):
        print("MISSING:", sub); continue
    n_files = 0; n_dirs = 0; exts = {}
    entries = []
    def walk(cur, depth):
        global n_files, n_dirs
        if depth > mdepth: return
        try:
            items = sorted(os.listdir(cur))
        except Exception as e:
            entries.append("ERR "+str(e)); return
        for it in items:
            p = os.path.join(cur, it)
            if os.path.isdir(p):
                if depth == 0: entries.append("DIR "+it)
                n_dirs += 1
                if depth < mdepth: walk(p, depth+1)
            else:
                if depth == 0: entries.append("file "+it)
                n_files += 1
                e = os.path.splitext(it)[1].lower()
                exts[e] = exts.get(e,0)+1
    print("===== "+sub+" =====")
    walk(d, 0)
    print("files:", n_files, "bytes_total_unknown, ext:", dict(exts))
    for e in entries[:25]:
        print("  ", e)
    print()
