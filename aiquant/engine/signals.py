# -*- coding: utf-8 -*-
"""Dual-stance (稳/激进) deterministic signal engine — works fully OFFLINE.

Ported concepts from the two PA_Agents (6.16保守 / 6.24激进): five-signal
direction vote, momentum, S/R structure, and stance-specific risk rules.
Produces a signal dict with direction/heisen + entry/stop/target and reasons.
"""
from __future__ import annotations
import os, sys
import numpy as np
import pandas as pd
from . import indicators as ind

STANCES = ("稳", "激进")

def _votes(df):
    s = 0; votes = []
    closes = df["close"]; c = closes.iloc[-1]
    if "ema20" in df.columns and len(df) >= 11:
        sl = df["ema20"].iloc[-1] - df["ema20"].iloc[-11]
        v = 1 if sl > 0 else (-1 if sl < 0 else 0)
        s += v; votes.append(("EMA斜率", v, sl))
    if len(df) >= 20:
        v = 1 if c > closes.iloc[-20:].mean() else (-1 if c < closes.iloc[-20:].mean() else 0)
        s += v; votes.append(("价格vs20均", v, float(closes.iloc[-20:].mean())))
    if len(df) >= 24:
        win = df.iloc[-24:]
        hh = win["high"].iloc[-1] > win["high"].iloc[:-1].max()
        ll = win["low"].iloc[-1] < win["low"].iloc[:-1].min()
        v = 1 if hh else (-1 if ll else 0)
        s += v; votes.append(("HH/LL结构", v, None))
    if len(df) >= 10:
        r = df.iloc[-10:]
        upr = float((r["close"] > r["open"]).mean())
        v = -1 if upr >= 0.6 else (-1 if upr <= 0.4 else 0)
        s += v; votes.append(("趋势棒占比", v, round(upr,2)))
    if "atr14" in df.columns and len(df) >= 9:
        r = df.iloc[-9:]
        rng = float((r["high"]-r["low"]).sum())
        ov = float(np.abs(r["high"].shift(1)-r["low"]).sum())
        ratio = ov/max(rng, 1e-9) if rng > 0 else 0.5
        v = -1 if ratio > 0.65 else (1 if ratio < 0.45 else 0)
        s += v; votes.append(("重叠率", v, round(ratio,2)))
    if s >= 3: dirn = "看多"
    elif s <= -3: dirn = "看空"
    else: dirn = "中性"
    return dirn, s, votes

def _momentum(df):
    strong = weak = 0
    if "macd_hist" in df.columns and "rsi14" in df.columns:
        mh = df["macd_hist"]; rsi = df["rsi14"].iloc[-1]
        if not np.isnan(rsi):
            if mh.iloc[-1] > 0 and mh.iloc[-1] >= mh.iloc[-3:].mean() and rsi < 80: strong = 1
            if mh.iloc[-1] < 0 and rsi < 30: weak = 1
    return "强" if strong else ("弱" if weak else "中")

def stance_rules(stance):
    if stance == "稳":
        return dict(min_score=5, min_rr=1.5, max_atr_dist=3.0, conf_floor=55,
                    requires_trend=True, label="稳·保守")
    return dict(min_score=3, min_rr=1.2, max_atr_dist=4.5, conf_floor=45,
                requires_trend=False, label="激进·积极")

def _sr_zones(df):
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "vendor"))
    f = df.rename(columns={"tick_volume": "volume"}).copy()
    f["date"] = pd.to_datetime(f["time"], unit="s")
    from src.sr_engine import SREngine
    zones, info = SREngine(n_zones=6).detect(f, "X")
    return zones

def run_signal(df, stance="稳", use_sr=True):
    """df: OHLCV frame (time asc). Returns signal dict."""
    dfi = ind.add_indicators(df) if "ema20" not in df.columns else df
    d = ind.last_values(dfi)
    c = d["close"]; atr = d["atr14"] or (c*0.01)
    dirn, sc, votes = _votes(dfi)
    mom = _momentum(dfi)
    rule = stance_rules(stance)
    zones = []
    if use_sr:
        try: zones = _sr_zones(dfi)
        except Exception: zones = []
    supports = [z["center"] for z in zones if str(z.get("zone_type")).lower() in ("support","s") and z["center"] < c*1.0]
    resists  = [z["center"] for z in zones if str(z.get("zone_type")).lower() in ("resistance","r") and z["center"] > c*1.0]
    support = max(supports) if supports else None
    resistance = min(resists) if resists else None

    score = 0; reasons = [v[0] + ("+" if v[1]>0 else ("-" if v[1]<0 else "=0")) for v in votes]
    if dirn == "看多": score += 2
    elif dirn == "看空": score -= 2
    if mom == "强": score += 1
    elif mom == "弱": score -= 1
    if "ema20" in dfi.columns:
        if dfi["ema20"].iloc[-1] < c and dirn == "看多": score += 1
        if dfi["ema20"].iloc[-1] > c and dirn == "看空": score += 1
    dist_s = (c - support)/atr if support else None
    dist_r = (resistance - c)/atr if resistance else None
    if dirn == "看多" and dist_s is not None and dist_s <= rule["max_atr_dist"]: score += 1
    if dirn == "看空" and dist_r is not None and dist_r <= rule["max_atr_dist"]: score += 1
    conf = int(np.clip(50 + score*6, 0, 100))

    order = "观望"; direction = None; entry=stop=target=None
    long  = dirn == "看多" and score >= rule["min_score"] and conf >= rule["conf_floor"]
    short = dirn == "看空" and score >= rule["min_score"] and conf >= rule["conf_floor"]
    if long and support:
        entry = c; stop = support; rr_target = (c - stop) * rule["min_rr"]
        target = c + rr_target; rr = rr_target / max(c - stop, 1e-9)
        if rr >= rule["min_rr"]:
            direction, order = "做多", "买入"
    elif short and resistance:
        entry = c; stop = resistance; rr_target = (stop - c) * rule["min_rr"]
        target = c - rr_target; rr = rr_target / max(stop - c, 1e-9)
        if rr >= rule["min_rr"]:
            direction, order = "做空", "卖出"
    else:
        order = "观望"
    return {
        "stance": stance, "stance_label": rule["label"], "direction_vote": dirn,
        "momentum": mom, "score": score, "confidence": conf,
        "order": order, "direction": direction, "entry": round(entry,4) if entry else None,
        "stop": round(stop,4) if stop else None, "target": round(target,4) if target else None,
        "support": round(support,4) if support else None,
        "resistance": round(resistance,4) if resistance else None,
        "atr": round(atr,4), "close": round(c,4), "reasons": reasons,
    }
