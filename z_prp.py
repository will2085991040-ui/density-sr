# -*- coding: utf-8 -*-
import py_compile
f = r"C:/Users/mine/Downloads/quant_research/server.py"
t = open(f, encoding="utf-8").read()
old = '''def run_pa(symbol, market, tf, stance):
    try:
        from aiquant.market import load
        from aiquant.pa_llm import run_agent
        df = load(_cat(), "A股", symbol, "daily")
        return run_agent(df, symbol=symbol, market="A股",
        tf=tf, stance=stance)
    except Exception as e:
        return {"label": "激进" if "对应6.24" in (stance or "") else "稳健",
                "direction": "观望", "entry": None, "stop": None, "target": None,
                "reason": "AI 调用失败: %s" % e, "tone": stance}'''
new = '''def run_pa(symbol, market, tf, stance):
    try:
        from aiquant.market import load
        from aiquant.pa_llm import run_agent
        try:
            df = load(_cat(), "A股", symbol, "daily")
        except Exception:
            df = None
        res = run_agent(df, symbol=symbol, market="A股", stance=stance)
        if not isinstance(res, dict):
            res = {}
        # 归一化前端 paCard 需要的字段
        llm = res.get("llm") or {}
        out = {
            "label": res.get("label") or ("稳健 Agent" if "6.16" in str(stance) else "激进 Agent"),
            "tone": res.get("tone") or str(stance),
            "direction": res.get("direction") or "观望",
            "action": res.get("action") or "",
            "entry": res.get("entry") or ((llm.get("entry") if isinstance(llm, dict) else None)),
            "stop": res.get("stop") or ((llm.get("stop") if isinstance(llm, dict) else None)),
            "target": res.get("target") or ((llm.get("target") if isinstance(llm, dict) else None)),
            "rr": res.get("rr"),
            "risk_pct": res.get("risk_pct"),
            "reason": res.get("reason") or (res.get("llm_err") or "研判完成"),
            "llm": llm if isinstance(llm, dict) else {},
        }
        return out
    except Exception as e:
        return {"label": "激进" if "6.24" in str(stance) else "稳健", "direction": "观望",
                "action": "", "entry": None, "stop": None, "target": None,
                "reason": "AI 调用失败: %s" % e, "tone": str(stance)}'''
assert old in t, "run_pa block"
t = t.replace(old, new, 1)
open(f,"w",encoding="utf-8").write(t)
py_compile.compile(f, doraise=True)
print("run_pa fixed")
