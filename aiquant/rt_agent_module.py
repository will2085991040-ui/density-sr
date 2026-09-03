# -*- coding: utf-8 -*-
"""Real-time AI monitoring agent for DENSITY-SR (实时盯盘)。
Feeds the LATEST live kline + quote into the dual PA_Agent real-AI reasoning.
"""
from __future__ import annotations
import time

def live_pa_json(symbol, market='A股', stance='6.24', n=160, timeout=110):
    import pandas as pd
    from aiquant.live_connector import live_kline
    from aiquant.pa_llm import run_agent
    from aiquant.market import load
    bars = None
    try:
        bars = live_kline(symbol, days=n)
    except Exception:
        bars = None
    df = None
    if bars and len(bars) >= 20:
        try:
            df = pd.DataFrame(bars)
            df['time'] = pd.to_datetime(df['date']).astype(int) // 10**9
        except Exception:
            df = None
    live = bool(df is not None and len(df) >= 20)
    if df is None or len(df) < 20:
        df = load(_catalog(), market, symbol, 'daily')
    if df is None or len(df) < 20:
        return {'symbol': symbol, 'market': market, 'error': '数据不足', 'live': False}
    res = run_agent(df, symbol, market, stance, timeout=timeout)
    res['live'] = live
    res['asof'] = int(time.time())
    return res

_CAT = [None]
def _catalog():
    from aiquant.market import MarketCatalog
    if _CAT[0] is None:
        _CAT[0] = MarketCatalog()
    return _CAT[0]
