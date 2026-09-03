# -*- coding: utf-8 -*-
import marshal, dis
b = open(r"C:/Users/mine/Downloads/quant_research/__pycache__/server.cpython-313.pyc","rb").read()
code = marshal.loads(b[16:])
import types
# capture every nested code's string consts & names with hierarchy
out=[]
def walk(c, d=0):
    tag = "M " if c.co_name=="<module>" else ("  "*d + ("DEF " if 'def' else ""))
    out.append("  "*d + (":" if d==0 else "") + repr(c.co_name) + " arg=" + str(c.co_argcount))
    strs=[x for x in c.co_consts if isinstance(x,str)]
    names=c.co_names
    if strs: out.append("  "*(d+1)+"STRS: " + repr(strs))
    if names: out.append("  "*(d+1)+"NAMES: " + repr(names))
    for sub in c.co_consts:
        if isinstance(sub, types.CodeType): walk(sub, d+1)
    # disassemble body (skip trivial)
    if c.co_code and len(c.co_code)>4:
        lines=dis.split_lines(c)
        out.append("  "*(d+1)+"BYTECODE lines: "+str(len(lines)))
walk(code)
open('C:/Users/mine/Downloads/quant_research/_recon_dump.txt','w',encoding='utf-8').write("\n".join(out))
print("dumped", len(out), "lines")
