# -*- coding: utf-8 -*-
"""· 下跌宽通道 AI 分析 (Wide Descending Channel).
识别近期价格下降通道(上轨/下轨=近端波段极值线性回归), 量化通道宽度(相对ATR)
与斜率, 判定是否「宽通道」并给出 AI 解读。纯本地, 永不抛异常。"""
from __future__ import annotations


def _linreg(x, y):
    import numpy as np
    x = np.array(x, float); y = np.array(y, float)
    if len(x) < 2:
        return None, None, None
    den = len(x) * (x * x).sum() - x.sum() ** 2 + 1e-9
    k = (len(x) * (x * y).sum() - x.sum() * y.sum()) / den
    b = (y.sum() - k * x.sum()) / len(x)
    yhat = k * x + b
    ss = ((y - yhat) ** 2).sum(); st = ((y - y.mean()) ** 2).sum() + 1e-9
    return float(k), float(b), 1 - ss / st


def channel_wide_analysis(df, price=None, lookback=140, channel_lookback=60):
    import numpy as np
    out = {"detected": False, "is_wide": False, "direction": None, "slope": 0,
           "width_pct": 0, "width_atr_mult": 0, "upper": None, "lower": None,
           "mid": None, "price": price, "atr": 0, "atr_pct": 0, "r2": 0,
           "position_pct": 50.0, "read_note": "数据不足", "reason": "数据不足"}
    try:
        if df is None or len(df) < channel_lookback + 6:
            return out
        d = df.tail(lookback)
        close = d["close"].astype(float).values
        high = d["high"].astype(float).values
        low = d["low"].astype(float).values
        n = len(close)
        if price is None:
            price = float(close[-1])
        tr = np.maximum(high[1:] - low[1:],
                        np.maximum(np.abs(high[1:] - close[:-1]),
                                   np.abs(low[1:] - close[:-1])))
        m = min(14, len(tr))
        atr = float(np.mean(tr[-m:])) or (price * 0.02)
        h = high[-channel_lookback:]; l = low[-channel_lookback:]
        idx = np.arange(len(h))
        kh, bh, r2u = _linreg(idx, h)
        kl, bl, _ = _linreg(idx, l)
        if kh is None or kl is None:
            out["read_note"] = "通道拟合失败"
            return out
        slope = (kh + kl) / 2
        upper = kh * (len(h) - 1) + bh
        lower = kl * (len(l) - 1) + bl
        width_px = upper - lower + 1e-12
        width_pct = (width_px / price * 100.0) if price else 0.0
        is_wide = (width_px > 3.2 * atr) or (width_pct > 7.5)
        direction = "down" if slope < -0.015 else ("up" if slope > 0.015 else "flat")
        pos = min(1.0, max(0.0, (price - lower) / width_px))
        note = []
        wm = width_px / max(atr, 1e-9)
        if is_wide and direction == "down":
            note.append("下跌宽通道: 上下沿均下行, 通道较宽(%.1f倍ATR / 跨价%s%%)。宽通道=大区间震荡或深回调, 单根反弹难破上沿。" % (wm, round(width_pct, 1)))
            mid = (upper + lower) / 2
            if pos < 0.35:
                note.append("价贴下沿, 短线易反抽; 下行未破, 反弹到中轨(%.2f)即先减。" % mid)
            elif pos > 0.8:
                note.append("价贴上沿, 未真突破前不追多; 放量破上轨再介入。")
            else:
                note.append("价处通道中部, 无边界机会, 等触上下沿。")
        else:
            note.append("未形成明确下跌宽通道(斜率%s, 宽度%.1f%%)。" % (round(slope, 3), width_pct))
        out.update({
            "detected": True, "is_wide": bool(is_wide), "direction": direction,
            "slope": round(slope, 4), "width_pct": round(width_pct, 2),
            "width_atr_mult": round(wm, 2),
            "upper": round(float(upper), 2), "lower": round(float(lower), 2),
            "mid": round(float((upper + lower) / 2), 2), "price": round(float(price), 2),
            "atr": round(float(atr), 2), "atr_pct": round(atr / price * 100.0, 2),
            "r2": round(float(r2u), 3) if r2u is not None else 0,
            "position_pct": round(pos * 100.0, 1),
            "read_note": "".join(note), "reason": "近%d根高/低点回归" % channel_lookback,
        })
        return out
    except Exception as e:
        out["read_note"] = "通道分析异常: %s" % e
        return out


def analyze_ai(df, symbol="", market="A股", price=None, lookback=120, channel_lookback=60):
    r = channel_wide_analysis(df, price=price, lookback=lookback, channel_lookback=channel_lookback)
    r["symbol"] = symbol
    r["market"] = market
    if r.get("detected") and r.get("is_wide") and r.get("direction") == "down":
        r["ai_direction"] = "空头区间·下沿反抽做T"
        r["ai_level"] = r.get("mid")
    else:
        r["ai_direction"] = "观望(非下跌宽通道)"
        r["ai_level"] = r.get("price")
    return r
