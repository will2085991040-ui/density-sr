# -*- coding: utf-8 -*-
"""Self-contained pivot-based support/resistance detection (ATR-influenced pivots + volume merge).

Produces a ranked list of {price, kind:support|resistance, strength, n_touches, dist_atr}.
Self-contained (numpy/pandas only) so it has no external deps beyond those for the EXE.
"""
from __future__ import annotations
import numpy as np
import pandas as pd

def _atr(df, period=14):
    h,l,c = df["high"].values, df["low"].values, df["close"].values
    pc = np.concatenate([[c[0]], c[:-1]])
    tr = np.maximum(h-l, np.maximum(np.abs(h-pc), np.abs(l-pc)))
    return pd.Series(tr).ewm(alpha=1.0/period, adjust=False, min_periods=period).mean().values

def _zigzag_pivots(h, l, atr, max_steps=3):
    """Return arrays of pivot highs/lows indices using ATR reversal threshold."""
    n = len(h); piv = []
    last_type = None; last_ext = 0.0; last_i = 0
    for i in range(2, n):
        big_pull = (h[i] - l[i]) 
        # simple: track a candidate 'last extreme'
        cur_h = h[i]; cur_l = l[i]
        if last_type is None:
            if cur_h >= max(h[last_i: i+1]): last_type="H"; last_pv=cur_h; last_i=i
            if cur_l <= min(l[last_i: i+1]): last_type="L"; last_pv=cur_l; last_i=i
            continue
        if last_type=="H":
            if cur_l <= last_pv - atr_s[i]:
                piv.append((last_i,"H",last_pv))
                last_type="L"; last_pv=cur_l; last_i=i
            elif cur_h > last_pv:
                last_pv=cur_h; last_i=i
        else:
            if cur_h >= last_pv + atr_s[i]:
                piv.append((last_i,"L",last_pv))
                last_type="H"; last_pv=cur_h; last_i=i
            elif cur_l < last_pv:
                last_pv=cur_l; last_i=i
    return piv
