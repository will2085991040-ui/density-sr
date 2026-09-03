# -*- coding: utf-8 -*-
"""PA Agent 融合代理 —— 把 大A量化监控系统 里的两个价格行为智能体(稳/激进)融入 DENSITY·SR。

基于 PA_Agent 的价格行为(Price Action)几何特征栈,在本地 OHLCV 上直接计算确定性特征,
再按 6.16「稳(保守)」 与 6.24「激进」两种决策倾向,产出可落地的双智能体研判。
无需 API Key、与现有数据同源、纯计算(确定性),保证在打包 EXE 中稳定运行。
"""
from __future__ import annotations


def _ema(values, period):
    n = len(values); out = [None]*n
    if n < period: return out
    alpha = 2.0/(period+1)
    seed = sum(values[:period])/period
    out[period-1] = seed; prev = seed
    for i in range(period, n):
        prev = values[i]*alpha + prev*(1-alpha); out[i] = prev
    return out


def _atr(high, low, close, period=14):
    n = len(close); tr = [0.0]*n; prevc = close[0]
    for i in range(n):
        h = high[i]; l = low[i]
        a = h-l; b = abs(h-prevc) if i else a; c2 = abs(l-prevc) if i else a
        tr[i] = max(a, b, c2); prevc = close[i]
    out = [None]*n
    if n >= period:
        seed = sum(tr[:period])/period; out[period-1] = seed; prev = seed
        for i in range(period, n):
            prev = (prev*(period-1)+tr[i])/period; out[i] = prev
    return out


def price_action_features(df):
    """对(旧->新)OHLCV 计算最新已收盘棒(K1)的价格行为几何特征。"""
    o = [float(x) for x in df["open"]]; h = [float(x) for x in df["high"]]
    l = [float(x) for x in df["low"]];   c = [float(x) for x in df["close"]]
    ema = _ema(c, 20); atr = _atr(h, l, c, 14)
    i = len(c)-1
    e = ema[i] if ema[i] is not None else c[i]
    a = atr[i] if (i < len(atr) and atr[i] is not None) else max((h[i]-l[i])*1.4, 1e-9)
    spread = (h[i]-l[i]) or 1e-9
    body = abs(c[i]-o[i])
    body_ratio = body/spread
    upper = (h[i]-max(o[i], c[i]))/spread
    lower = (min(o[i], c[i])-l[i])/spread
    close_pos = (c[i]-l[i])/spread
    inside = (h[i] <= h[i-1] and l[i] >= l[i-1]) if i >= 1 else False
    ema_dist_pct = (c[i]/e - 1)*100 if e else 0.0
    atr_dist = (c[i]-e)/a if a else 0.0
    near_ema = abs(atr_dist) < 0.5
    return {
        "close": c[i], "ema20": round(e, 4), "atr": round(a, 4),
        "body_ratio": round(body_ratio, 3), "upper_wick": round(upper, 3),
        "lower_wick": round(lower, 3), "close_pos": round(close_pos, 3),
        "is_bull": c[i] > o[i], "inside": bool(inside),
        "ema_dist_pct": round(ema_dist_pct, 2), "atr_dist": round(atr_dist, 2),
        "near_ema": bool(near_ema),
    }


def _directional(f):
    """返回 1=多, 0=空, 2=中性 (确定性初判)。"""
    if f["is_bull"] and f["close_pos"] > 0.55 and not (f["upper_wick"] > f["lower_wick"] + 0.15):
        if f["ema_dist_pct"] > 0 or f["atr_dist"] > -0.4:
            return 1
    if (not f["is_bull"]) and f["close_pos"] < 0.45 and f["lower_wick"] < f["upper_wick"] + 0.05:
        if f["ema_dist_pct"] < 0.2 or f["atr_dist"] < 0.4:
            return 0
    return 2


def _strength(f, bullish):
    s = f["body_ratio"]*5.0
    if (f["lower_wick"] > 0.2) if bullish else (f["upper_wick"] > 0.2): s += 1.5
    s += (f["close_pos"]) if bullish else (1 - f["close_pos"])
    if f["near_ema"]: s += 0.8
    if f["inside"]: s -= 0.6
    return max(0.0, min(1.0, s/4.0))


def _verdict(direction, strength, stance):
    """按 stance 把 方向+强度 映射为 动作/价位策略。 return (action,信心,summary)"""
    bullish = direction == 1; bearish = direction == 0
    if stance == "conservative":   # 6.16 稳但机会少
        if bullish and strength >= 0.62:
            return "做多(突破/回踩确认)", "强", "顺势且实体/收盘强,符合保守确认线"
        if bearish   and strength >= 0.62:
            return "做空(跌破/反抽确认)", "强", "空头信号且实体确认充分"
        if bullish and strength >= 0.5:
            return "观察做多(等确认)", "中", "有偏多迹象但未达保守确认,等待K线跟进"
        if bearish and strength >= 0.5:
            return "观察做空(等确认)", "中", "有偏空迹象但未达保守确认,等待跟进"
        return "观望/等待", "低", "无满足保守(6.16)条件的方向信号,保持空仓等待"
    # aggressive 6.24 激进但多
    if bullish:
        if strength >= 0.45:
            return "做多(轻仓/突破)", "强" if strength >= 0.6 else "中", "偏多信号即试图,更多机会但需严格止损"
        return "关注做多", "低", "轻度偏多,激进聊试探后仍需方向确认"
    if bearish:
        if strength >= 0.45:
            return "做空(轻仓/反抽)", "强" if strength >= 0.6 else "中", "偏空信号即试图,利润目标更近"
        return "关注做空", "低", "轻度偏空,激进聊试探"
    if abs(f["atr_dist"]) < 0.5 and f["inside"]:
        return "区间蓄势", "中", "窄幅内包蓄势,等待突破方向"
    return "观望", "低", "无明显偏多偏空结构"


def analyze(df, symbol="", market="A股"):
    f = price_action_features(df)
    direction = _directional(f)
    bullish = direction == 1; bearish = direction == 0
    strength = _strength(f, bullish) if (bullish or bearish) else 0.0
    action_c, conf_c, note_c = _verdict(direction, strength, "conservative")
    action_a, conf_a, note_a = _verdict(direction, strength, "aggressive")
    dir_label = "多头" if bullish else ("空头" if bearish else "中性震荡")
    return {
        "symbol": symbol, "market": market,
        "direction": dir_label, "strength": round(strength*100, 1),
        "features": f,
        "agents": [
            {"id": "agent-6.16", "label": "稳健 Agent · 6.16", "tone": "稳但机会少",
             "stance": "conservative", "action": action_c, "confidence": conf_c, "note": note_c,
             "color": "#39d98a"},
            {"id": "agent-6.24", "label": "激进 Agent · 6.24", "tone": "激进但机会多",
             "stance": "aggressive",  "action": action_a, "confidence": conf_a, "note": note_a,
             "color": "#f0a032"},
        ],
    }
