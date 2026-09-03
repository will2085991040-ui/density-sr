# -*- coding: utf-8 -*-
import marshal
b = open(r"C:/Users/mine/Downloads/quant_research/__pycache__/server.cpython-313.pyc","rb").read()
code = marshal.loads(b[16:])
def walk(c, depth=0, path=""):
    name = c.co_name or "<module>"
    print("  "*depth + "FUNC:", name, "args=", c.co_varnames[:c.co_argcount], "conststrs=", [x for x in c.co_consts if isinstance(x,str)][:4])
    for sub in c.co_consts:
        if isinstance(sub, type(code)):
            walk(sub, depth+1)
walk(code)
