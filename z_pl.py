# -*- coding: utf-8 -*-
import py_compile, re
f="C:/Users/mine/Downloads/quant_research/aiquant/pa_llm.py"
t=open(f,encoding="utf-8").read()
t = re.sub(r"def _load_system_prompts.*?(?=def _build_prompt)", "", t, flags=re.S)
anchor="def _build_prompt(df, symbol: str, market: str, stance: str, f: Dict[str, Any]) -> str:"
block='''def _prompt_files(stage):
    """按阶段返回系统提示词文件文本列表(阶段一诊断/阶段二决策)."""
    import os, glob
    here = os.path.dirname(os.path.abspath(__file__))
    kdir = os.path.join(here, "..", "knowledge", "prompts")
    order = (
        ["1-提示词大纲", "2-二元决策", "3-市场诊断框架", "4-文件16"]
        if stage == "诊断"
        else ["1-提示词大纲", "2-二元决策", "5-震荡区间分析", "6-震荡区间交易",
              "7-文件15", "8-文件19", "文件18-突破", "10-文件21", "11-文件22",
              "12-逐棒", "4-文件16", "13-文件17", "文件23"]
    )
    pool = sorted(glob.glob(os.path.join(kdir, "*.txt")))
    picked, out = [], []
    for key in order:
        for p in pool:
            if key in os.path.basename(p) and p not in picked:
                picked.append(p); out.append(open(p, encoding="utf-8").read().strip()); break
    return out


def _system_prompt(stage="决策"):
    try:
        return "\n\n".join(_prompt_files(stage))
    except Exception:
        return ""


'''
if "_prompt_files" not in t:
    t=t.replace(anchor, block+anchor, 1)
open(f,"w",encoding="utf-8").write(t)
py_compile.compile(f,doraise=True)
print("wired cleanly; files loaded:", len(__import__('builtins').__dict__))
