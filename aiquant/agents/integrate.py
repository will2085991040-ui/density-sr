# -*- coding: utf-8 -*-
"""双智能体(稳/激进) AI量化决策 —— 融合 signals(双风格) + factor(离线AI) + 可选 LLM.

use_llm: None=自动(有key则LLM), True=强制LLM, False=强制离线。"""
from __future__ import annotations
import json
from ..engine import signals, factor
from ..api.deepseek import load_key as _load_key, deep_chat

def unify(df, stance="稳", use_sr=True, use_llm=None):
    sig = signals.run_signal(df, stance, use_sr=use_sr)
    fac = factor.compute(df)
    a_dir = sig.get("direction"); a_ord = sig.get("order")
    f_dir = fac.get("direction"); f_ord = fac.get("order")
    votes = []
    if a_dir == "做多": votes.append(1)
    elif a_dir == "做空": votes.append(-1)
    if f_dir == "做多": votes.append(1)
    elif f_dir == "做空": votes.append(-1)
    s = sum(votes) if votes else 0
    final_dir = "做多" if s > 0 else ("做空" if s < 0 else None)
    if final_dir is None:
        final_ord = "观望"
    elif final_dir == "做多":
        final_ord = "买入" if ("买入" in (a_ord, f_ord)) else "观望"
    else:
        final_ord = "卖出" if ("卖出" in (a_ord, f_ord)) else "观望"
    conf = int(min(100, 52 + abs(s) * 14)) if votes else 42

    narr = "【双智能体共识】%s %s (置信%d)。" % (final_dir or "中性", final_ord, conf)
    narr += "稳agent: %s %s；" % (a_ord, a_dir or "-")
    narr += "激进agent: %s %s；" % (f_ord, f_dir or "-")
    narr += "离线AI因子: %s。" % fac.get("verdict", "")
    llm = None; llm_active = False
    if use_llm is True or (use_llm is None and _load_key()):
        payload = json.dumps({
            "task": "双智能体深度研判(量化, 简洁, 可执行)",
            "close": fac.get("close"), "atr": fac.get("atr"),
            "consensus": final_dir, "confidence": conf,
            "signal": {k: sig.get(k) for k in ("order", "direction", "support", "resistance")},
            "factors": fac.get("factors", {})}, ensure_ascii=False, default=str)
        llm = deep_chat(payload, key=None)
        llm_active = True
    out = {"consensus": {"direction": final_dir, "order": final_ord, "confidence": conf},
           "signal": sig, "factor": fac, "stance": stance, "narrative": narr,
           "llm": llm, "llm_active": llm_active}
    return out

def summarize(u):
    out = u["narrative"]
    if u.get("llm"):
        out = out + chr(10) + "[LLM]: " + u["llm"]
    elif u.get("llm_active") is False:
        out = out + chr(10) + "[仅离线AI级研判]"
    else:
        out = out + chr(10) + "[无API Key，使用离线因子研判]"
    return out
