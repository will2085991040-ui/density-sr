# -*- coding: utf-8 -*-
import py_compile
f = "C:/Users/mine/Downloads/quant_research/aiquant/pa_llm.py"
t = open(f, encoding="utf-8").read()
old = '{"role": "system", "content": "\u4f60\u662f\u4e25\u683c\u7684\u4ea4\u6613\u4fe1\u53f7\u8f93\u51fa\u52a9\u624b, \u53ea\u8f93\u51fa JSON, \u7981\u6b62\u89e3\u91ca\u6587\u5b57\u3002"}'
new = '{"role": "system", "content": _sys_payload() + chr(10)*2 + "\u53ea\u8f93\u51fa JSON, \u7981\u6b62\u89e3\u91ca\u6587\u5b57\u3002"}'
if old in t:
    t = t.replace(old, new, 1)
else:
    t = t.replace('"role": "system"', '"role": "system", "content": _sys_payload()')
if "_sys_payload" not in t:
    NL = chr(10)
    head = ("def _sys_payload():" + NL +
            "    try:" + NL +
            "        return _system_prompt(\"决策\")" + NL +
            "    except Exception:" + NL +
            "        return \"\"" + NL + NL + NL)
    anchor = "def _build_prompt("
    assert anchor in t
    t = t.replace(anchor, head + anchor, 1)
open(f, "w", encoding="utf-8").write(t)
py_compile.compile(f, doraise=True)
print("system injected")