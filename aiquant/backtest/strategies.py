# -*- coding: utf-8 -*-
"""6 backtest strategies one-click comparison on a symbol's OHLCV frame.

Each strategy is a vectorized signal function returning a boolean 'position'
Series. Backtester computes equity from long-only signals on the close.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from ..engine import indicators as ind

def s_ma_cross(df, fast=5, slow=20):
    """双均线交叉多头."""
    f = ind.sma(df["close"], fast); s = ind.sma(df["close"], slow)
    pos = (f > s).astype(int)
    return pos

def s_macd(df):
    dif, dea, h = ind.macd_series(df["close"])
    pos = (dif > dea).astype(int)
    return pos

def s_rsi_mean(df, period=14):
    rsi = ind.rsi(df["close"], period)
    pos = (rsi < 50).astype(int)  # 均值回归：RSI<50 持有
    return pos

def s_rsi_band(df, period=14, lo=30, hi=70):
    rsi = ind.rsi(df["close"], period)
    pos = np.zeros(len(df)); hold = 0
    for i in range(len(df)):
        v = rsi.iloc[i]
        if np.isnan(v):
            pos[i] = hold
        elif v < lo:
            hold = 1
        elif v > hi:
            hold = 0
        pos[i] = hold
    return pd.Series(pos, index=df.index)

def s_breakout(df, n=20):
    """唐奇安通道突破：价格破前n日高点做多."""
    hh = df["high"].rolling(n).max().shift(1)
    close = df["close"]
    pos = (close > hh).astype(int)
    return pos

def s_momentum_macd(df):
    dif, dea, h = ind.macd_series(df["close"])
    pos = (h > 0).astype(int)
    return pos

def s_boll_rev(df, window=20, k=2.0):
    up, mid, lo = ind.bollinger(df["close"], window, k)
    pos = np.zeros(len(df)); hold = 0
    for i in range(len(df)):
        if np.isnan(mid.iloc[i]):
            pos[i] = hold
        else:
            if df["close"].iloc[i] < lo.iloc[i]: hold = 1
            elif df["close"].iloc[i] > up.iloc[i]: hold = 0
        pos[i] = hold
    return pd.Series(pos, index=df.index)

STRATEGIES = {
    "双均线交叉": s_ma_cross,
    "MACD金叉": s_macd,
    "RSI均值回归": s_rsi_mean,
    "RSI超买超卖": s_rsi_band,
    "唐奇安突破": s_breakout,
    "布林回归": s_boll_rev,
}

def backtest(df, strategy_fn, cost_bps=0.0):
    """Long-only vectorized backtest. Returns dict of metrics + equity."""
    c = df["close"].values
    pos = strategy_fn(df).values  # 1 = in market
    # assume entering at signal bar close, exit when pos flips to 0
    ret = np.diff(c) / c[:-1]
    pos_shifted = pos[:-1]
    strat_ret = np.where(pos_shifted > 0, ret, 0.0)
    if cost_bps:
        turn = np.abs(np.diff(pos, prepend=pos[0]))
        strat_ret = strat_ret - turn.astype(np.float64) * (cost_bps / 1e4)
    equity = np.cumprod(1 + strat_ret)
    total = equity[-1] - 1
    n = len(strat_ret)
    years = max(n / 250, 1e-6)
    cagr = (1 + total) ** (1 / years) - 1 if total > -1 else -1
    ann_vol = np.std(strat_ret, ddof=1) * np.sqrt(250) if n > 1 else 0
    sharpe = cagr / ann_vol if ann_vol > 0 else 0
    mdd = _max_drawdown(equity)
    trades = int((np.diff(pos, prepend=0) > 0).sum())
    in_market = pos[:-1] > 0
    win = float((ret[in_market] > 0).mean()) if in_market.any() and (in_market.sum() > 0) else 0
    return {
        "total_return": float(total), "cagr": float(cagr), "sharpe": float(sharpe),
        "max_drawdown": float(mdd), "win_rate": win, "trades": trades,
        "equity": equity.tolist(), "periods": int(n),
    }

def _max_drawdown(equity):
    peak = np.maximum.accumulate(equity)
    dd = (equity - peak) / peak
    return float(-dd.min()) if len(dd) else 0.0

def compare(df, cost_bps=0.0):
    """Run all 6 strategies, return list sorted by sharpe desc."""
    out = []
    for name, fn in STRATEGIES.items():
        try:
            res = backtest(df, fn, cost_bps=cost_bps)
            res["strategy"] = name
            res.pop("equity", None)
            out.append(res)
        except Exception as e:
            out.append({"strategy": name, "error": str(e)[:60]})
    out.sort(key=lambda r: r.get("sharpe", -9), reverse=True)
    return out
