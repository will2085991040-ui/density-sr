# -*- coding: utf-8 -*-
"""DENSITY·SR 策略信号引擎 (Strategy Signal Engine)
把支撑/阻力 + 均线趋势 + 市场情绪 合成可执行的交易信号:
  - 触发位 / 现价位置
  - 方向(多/空/观望) + 入场/止损/目标/风控
  - 情绪过滤(冰点/偏空 自动降多), 给出何时开仓/平仓/观望
供前端看板与量化盯盘使用; 纯本地+尽力实时, 永不抛异常。
"""
from __future__ import annotations

def signals_for(symbol, market="A股", tf="daily", price=None, sr_bands=None,
                ema5=None, ema10=None, ema20=None, sentiment=None):
    out = {"symbol": symbol, "tf": tf, "signal": "观望", "direction": "观望",
           "entry": None, "stop": None, "target": None, "rr": None,
           "sup": None, "res": None, "heat": 0, "reason": "数据不足"}
    if price is None or not sr_bands:
        return out

    sup = None; res = None
    for b in sr_bands:
        c = b.get("center")
        if c is None: continue
        zt = str(b.get("zone_type") or "").lower()
        if ("sup" in zt) and c < price:
            if sup is None or (price - c) < (price - sup): sup = c
        elif ("res" in zt) and c > price:
            if res is None or (c - price) < (res - price): res = c

    trend = 0
    if ema5 and ema10 and ema20:
        trend = (1 if ema5 > ema10 else -1) + (1 if ema10 > ema20 else -1)

    s_score = (sentiment or {}).get("score", 50)
    s_label = (sentiment or {}).get("label", "中性")

    direction = "观望"; entry = None; stop = None; target = None; rr = None
    reason = []; heat = 0

    if sup is not None and res is not None:
        dist_sup = (price - sup) / price * 100
        dist_res = (res - price) / price * 100
        risk = 0.4

        if dist_sup <= 2.0 and trend >= 0 and s_score >= 42:
            direction = "做多(回踩支撑)"
            entry = round(price, 2); stop = round(sup * 0.995, 2); target = round(res, 2)
            rr = round((target - entry) / max(entry - stop, 0.0001), 2)
            risk = max(0.3, min(0.9, (2.0 - dist_sup) / 2.0 + trend * 0.1))
            reason.append("回踩支撑%.2f且均线多头" % sup)
        elif dist_res <= 2.0 and trend >= 0 and s_score >= 55:
            direction = "持有(接近压力·减仓)"
            entry = round(price, 2); stop = round(ema10 or price * 0.97, 2); target = round(res, 2)
            rr = (target - entry) / max(entry - stop, 0.0001)
            heat = 0.7
            reason.append("接近压力%s,情绪偏暖,可持有并逢高减仓保盈" % res)
        elif price <= sup * 1.01 and trend < 0:
            direction = "做空(跌破支撑)"
            entry = round(price, 2); stop = round(res, 2); target = round(sup, 2)
            rr = (entry - target) / max(stop - entry, 0.0001)
            heat = 0.6
            reason.append("跌破支撑%s,顺势短空" % sup)
        else:
            direction = "观望"
            reason.append("夹在支撑%s与压力%s之间,等触发" % (sup, res))

        if s_score >= 78 and direction == "做多(回踩支撑)":
            direction = "减多(过热)"
            heat = max(0.0, heat - 0.2)
            reason.append("情绪过热(%s),减仓控回撤" % s_label)
        if s_score <= 40 and direction == "做多(回踩支撑)":
            direction = "观望(情绪冷)"
            reason.append("市场弱(%s),暂不追多" % s_label)

        out.update({
            "signal": direction,
            "direction": "多" if "多" in direction.replace("减多", "多") else ("空" if "空" in direction else "观望"),
            "entry": entry, "stop": stop, "target": target,
            "sup": sup, "res": res,
            "rr": round(float(rr), 2) if rr and rr > 0 else None,
            "trend": trend, "s_score": round(float(s_score), 1),
            "heat": round(heat, 2), "reason": " · ".join(reason),
        })
    return out
