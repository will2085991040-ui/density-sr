# -*- coding: utf-8 -*-
"""可离线 AI 级量化因子挖掘 + 综合研判（不依赖 LLM/API）。

从原始K线挖掘多组因子（趋势/动量/波动/位置/量能/结构），按权重聚合成 0~100 综合分，
给出 AI 级文本研判：方向、触发条件、建议入场/止损/目标、风险提示。
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from . import indicators as ind

_WEIGHTS = {"trend": 0.22, "momentum": 0.20, "volatility": 0.14,
            "position": 0.16, "volume": 0.12, "structure": 0.16}

def _clamp(x):
    return min(1.0, max(0.0, float(x)))

def compute(df):
    if "ema20" not in df.columns:
        df = ind.add_indicators(df)
    d = ind.last_values(df)
    c = float(d["close"]); atr = float(d["atr14"] or c * 0.01)
    ema20 = float(d["ema20"] or c)
    ema_prev = float(df["ema20"].iloc[-6]) if ("ema20" in df.columns and len(df) >= 6) else ema20 * 0.99
    rsi = d["rsi14"]; mh = d["macd_hist"]
    lo20 = float(df["low"].iloc[-20:].min()) if len(df) >= 20 else c * 0.95
    hi20 = float(df["high"].iloc[-20:].max()) if len(df) >= 20 else c * 1.05
    rng = max(hi20 - lo20, 1e-9)

    # 趋势
    trend = _clamp(0.5 + (c - ema20) / max(atr * 3.0, 1e-9) + (0.1 if ema20 > ema_prev else -0.1))
    t_label = "多头" if trend > 0.6 else ("空头" if trend < 0.4 else "震荡")
    # 动量
    mom = 0.5
    if rsi is not None and not np.isnan(rsi):
        mom = _clamp((float(rsi) - 30) / 40.0)
    if mh is not None and not np.isnan(mh):
        mom = _clamp(mom + (0.12 if mh > 0 else -0.12))
    m_label = "强势" if mom > 0.62 else ("弱势" if mom < 0.38 else "中性")
    # 波动(低=稳, 对应高因子值)
    vol = _clamp(1.0 - (atr / max(c, 1e-9)) * 12.0)
    # 位置(区间的0..1)
    pos = _clamp((c - lo20) / rng)
    # 量能
    v = df["tick_volume"] if "tick_volume" in df.columns else pd.Series([0.0])
    v_ratio = float(v.iloc[-1] / max(v.iloc[-10:].mean(), 1e-9)) if len(v) >= 10 else 1.0
    vol_f = _clamp(0.5 + (v_ratio - 1.0) * 0.4)
    # 结构(HH/LL)
    win = df.iloc[-20:] if len(df) >= 20 else df
    hh = bool(win["high"].iloc[-1] == win["high"].max())
    ll = bool(win["low"].iloc[-1] == win["low"].min())
    struct = _clamp(pos + (0.15 if hh else (-0.15 if ll else 0.0)))

    fac = {"trend": trend, "momentum": mom, "volatility": vol,
           "position": pos, "volume": vol_f, "structure": struct}
    composite = float(sum(fac[k] * _WEIGHTS[k] for k in _WEIGHTS))
    if composite >= 0.68: verdict, order, dirn = "强烈看多", "买入", "做多"
    elif composite >= 0.56: verdict, order, dirn = "看多", "买入", "做多"
    elif composite <= 0.32: verdict, order, dirn = "强烈看空", "卖出", "做空"
    elif composite <= 0.44: verdict, order, dirn = "看空", "卖出", "做空"
    else: verdict, order, dirn = "观望", "观望", None

    if dirn == "做多":
        rec = {"entry": round(c,4), "stop": round(max(lo20, c - atr*1.6),4),
               "target": round(min(hi20, c + atr*2.4),4)}
    elif dirn == "做空":
        rec = {"entry": round(c,4), "stop": round(min(hi20, c + atr*1.6),4),
               "target": round(max(lo20, c - atr*2.4),4)}
    else:
        rec = {"entry": None, "stop": None, "target": None}
    rr = (abs(rec["target"]-c)/max(abs(c-rec["stop"]),1e-9)) if dirn and rec["stop"] else 0.0

    narr = narrative(composite, verdict, t_label, m_label, v_ratio, pos,
                     rec=rec, rr=rr, c=c, atr=atr)
    out = {"factors": fac, "weights": _WEIGHTS, "composite": round(composite,3),
           "verdict": verdict, "order": order, "direction": dirn,
           "confidence": int(round(composite*100)), "close": round(c,4),
           "atr": round(atr,4), "vol_ratio": round(v_ratio,2), "pos": round(pos,3),
           "recommendation": rec, "rr": round(rr,2), "narrative": narr,
           "rsi": None if rsi is None or np.isnan(rsi) else round(float(rsi),1)}
    return out

def narrative(composite, verdict, t_label, m_label, v_ratio, pos, rec, rr, c, atr):
    vtxt = "放量" if v_ratio >= 1.3 else ("缩量" if v_ratio <= 0.7 else "量平")
    line = "【AI因子研判】综合得分%d/%s。趋势%s，动量%s，%s。区间位置%.2f。" % (
        int(composite*100), verdict, t_label, m_label, vtxt, pos)
    if verdict != "观望":
        line += "建议%s：入场 %.4f，止损 %.4f，目标 %.4f，盈亏比 %.2f。" % (
            verdict, rec["entry"], rec["stop"], rec["target"], rr)
        line += "风险：跌破止损宜离场；%s级波动，仓位建议轻仓。" % ("高" if atr/c > 0.03 else "中低")
    else:
        line += "当前多空因素交错，建议观望，等待趋势确认后择机介入。"
    return line
