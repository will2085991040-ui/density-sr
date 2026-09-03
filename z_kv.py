# -*- coding: utf-8 -*-
import sys; sys.path.insert(0,r"C:/Users/mine/Downloads/quant_research")
import server
d=server.knowledge_list()
print("ep004 ok:", d["ok"], "count", d.get("count"))
for f in d.get("files",[]):
    print(" -", f.get("name"), f.get("size"))
# show first 120 chars of first file
if d.get("files"):
    print("sample:", d["files"][0].get("text","")[:100].replace("\n"," "))
