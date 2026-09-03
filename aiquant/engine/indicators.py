# -*- coding: utf-8 -*-
"""Technical indicators on OHLCV DataFrames (time asc). Pure pandas/numpy, no TA-Lib."""
from __future__ import annotations
import numpy as np
import pandas as pd

def ema(series: pd.Series, span: int) -> pd.Series:
    return series.ewm(span=span, adjust=False).mean()

def sma(series: pd.Series, window: int) -> pd.Series:
    return series.rolling(window).mean()

def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    h, l, c = df["high"], df["low"], df["close"]
    pc = c.shift(1)
    tr = pd.concat([h - l, (h - pc).abs(), (l - pc).abs()], axis=1).max(axis=1)
    return tr.ewm(alpha=1.0 / period, adjust=False, min_periods=period).mean()

def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    d = series.diff()
    up = d.clip(lower=0.0)
    dn = (-d).clip(lower=0.0)
    ru = up.ewm(alpha=1.0 / period, adjust=False).mean()
    rd = dn.ewm(alpha=1.0 / period, adjust=False).mean()
    rs = ru / rd.replace(0, np.nan)
    return 100 - 100 / (1 + rs)

def macd_series(series: pd.Series, fast=12, slow=26, signal=9):
    dif = ema(series, fast) - ema(series, slow)
    dea = ema(dif, signal)
    hist = (dif - dea) * 2.0
    return dif, dea, hist

def bollinger(series: pd.Series, window=20, k=2.0):
    mid = sma(series, window)
    sd = series.rolling(window).std(ddof=0)
    return mid + k * sd, mid, mid - k * sd

def swing_highs_lows(df: pd.DataFrame, left=2, right=2):
    """Return list of (idx, 'H'|'L', price) swing points over recent window."""
    h = df["high"].values; l = df["low"].values; n = len(df)
    out = []
    for i in range(left, n - right):
        seg_h = h[i - left:i + right + 1]; seg_l = l[i - left:i + right + 1]
        if h[i] == seg_h.max() and (np.nanargmax(seg_h) == left):
            out.append((i, "H", h[i]))
        if l[i] == seg_l.min() and (np.nanargmin(seg_l) == left):
            out.append((i, "L", l[i]))
    return out

def pivot_support_resistance(df: pd.DataFrame, lookback: int = 30):
    """Simple swing-based current support/resistance from recent pivots + key EMA."""
    closes = df["close"]
    sw = swing_highs_lows(df, left=2, right=2)
    if not sw:
        return None, None
    cur = closes.iloc[-1]
    supps = [p for (_, t, p) in sw if t == "L" and p < cur]
    resis = [p for (_, t, p) in sw if t == "H" and p > cur]
    support = max(supps) if supps else None
    resistance = min(resis) if resis else None
    return support, resistance

def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Return df with ema20, atr14, macd dif/dea/hist, rsi14, boll mid/up/lo appended."""
    out = df.copy()
    c = out["close"]
    out["ema20"] = ema(c, 20)
    out["atr14"] = atr(out, 14)
    dif, dea, hist = macd_series(c)
    out["macd"] = dif; out["macd_signal"] = dea; out["macd_hist"] = hist
    out["rsi14"] = rsi(c, 14)
    up, mid, lo = bollinger(c)
    out["boll_up"] = up; out["boll_mid"] = mid; out["boll_lo"] = lo
    return out

def last_values(df: pd.DataFrame) -> dict:
    """Return a dict of latest indicator values for reporting."""
    d = add_indicators(df)
    last = d.iloc[-1]
    return {
        "close": float(last["close"]),
        "ema20": float(last["ema20"]),
        "atr14": float(last["atr14"]),
        "macd": float(last["macd"]),
        "macd_signal": float(last["macd_signal"]),
        "macd_hist": float(last["macd_hist"]),
        "rsi14": float(last["rsi14"]) if not np.isnan(last["rsi14"]) else None,
        "boll_up": float(last["boll_up"]),
        "boll_mid": float(last["boll_mid"]),
        "boll_lo": float(last["boll_lo"]),
    }
