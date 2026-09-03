# -*- coding: utf-8 -*-
import py_compile
f=r"C:/Users/mine/Downloads/quant_research/server.py"
t=open(f,encoding="utf-8").read()
import re
t=t.replace('json.dumps(knowledge_json())','json.dumps(knowledge_list())')
open(f,"w",encoding="utf-8").write(t)
py_compile.compile(f,doraise=True)
# confirm
g=open(f,encoding="utf-8").read()
print("knowledge_json left:", g.count("knowledge_json"))
print("knowledge_list refs:", g.count("knowledge_list"))
