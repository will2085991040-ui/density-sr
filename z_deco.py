# -*- coding: utf-8 -*-
import importlib.util, sys
for name in ("decompyle3","uncompyle6","xdis","marscode"):
    try:
        m = importlib.util.find_spec(name)
        print(name, "FOUND" if m else "missing")
    except Exception as e:
        print(name,"err",e)
# try to load the 313 pyc code object manually
import marshal, types, dis
p = r"C:/Users/mine/Downloads/quant_research/__pycache__/server.cpython-313.pyc"
b = open(p,"rb").read()
print("pyc size", len(b))
# header is 16 bytes for 3.13? magic(4)+flags(4)+timestamp(4)+size(4) =16
code = marshal.loads(b[16:])
print("code co_names count top:", len(code.co_names))
print("top consts:", code.co_consts[:3])
