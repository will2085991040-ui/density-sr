# -*- coding: utf-8 -*-
"""Unified market data layer for 大A量化监控系统.
Loads the uniform OHLCV parquet schema across A股 / MT5 / OKX universes.
"""
from __future__ import annotations
import os, re
from dataclasses import dataclass, field
from typing import Optional
import pandas as pd

def _find_root():
    """Auto-locate the 大A量化监控系统 data root:
    1) DSRS_DATA_ROOT env, 2) sibling folder next to the EXE (portable),
    3) 'data' next to the EXE, 4) original Desktop path."""
    import sys
    cands = []
    env = os.environ.get("DSRS_DATA_ROOT", "").strip()
    if env:
        cands.append(env)
    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
        cands += [base, os.path.join(base, "大A量化监控系统"),
                  os.path.join(base, "data"),
                  os.path.join(os.path.dirname(base), "大A量化监控系统")]
    else:
        base = os.path.dirname(os.path.abspath(__file__))
        cands.append(os.path.normpath(os.path.join(base, "..", "..")))  # workspace root
        cands.append(os.path.normpath(os.path.join(base, "..", "..", "..", "Desktop", "大A量化监控系统")))
    cands += [r"C:\Users\mine\Desktop\大A量化监控系统"]
    for c in cands:
        try:
            if c and os.path.isdir(c) and os.path.isdir(os.path.join(c, "A股数据")):
                return c
        except Exception:
            continue
    return r"C:\Users\mine\Desktop\大A量化监控系统"

DEFAULT_ROOT = _find_root()

# timeframe aliases -> canonical
_TF = {
    "daily":"daily","D1":"daily","1d":"daily","d":"daily","日":"daily",
    "60min":"60min","60m":"60min","H1":"60min","h1":"60min","1h":"60min","时":"60min",
    "15min":"15min","15m":"15min","M15":"15min",
    "5min":"5min","5m":"5min","M5":"5min","m5":"5min",
}

def norm_tf(t: str) -> str:
    if not t: return "daily"
    key = t.strip().lstrip(".").replace(".parquet","").lower()
    if key in _TF: return _TF[key]
    # allow M15 -> 15min style
    up = key.upper()
    if up == "M5": return "5min"
    if up == "M15": return "15min"
    if up in ("H1","H60","60"): return "60min"
    if up in ("D1","D"): return "daily"
    return key

@dataclass
class MarketCatalog:
    root: str = DEFAULT_ROOT
    stocks_dir: str = os.path.join("A股数据","parquet","stocks")
    index_dir:  str = os.path.join("A股数据","parquet","indices")
    mt5_dir:  Optional[str] = os.path.join("MT5_K线数据(1)", "MT5_K线数据")
    okx_dir:  Optional[str] = os.path.join("OKX_K线数据(1)", "OKX_K线数据")
    _stock: dict = field(default_factory=dict, repr=False)
    _index: dict = field(default_factory=dict, repr=False)
    _mt5:   dict = field(default_factory=dict, repr=False)
    _okx:   dict = field(default_factory=dict, repr=False)
    _stock_scanned = False
    _index_scanned = False

def _scan_dir(root, sub, prefix=None):
    """Return {symbol: {tf: abspath}}; filenames {prefix?}{sym}_{tf}.parquet"""
    out = {}
    base = os.path.join(root, sub)
    if not os.path.isdir(base): return out
    for fn in os.listdir(base):
        if not fn.endswith(".parquet"): continue
        stem = fn[:-8]
        m = re.match(r"^(.*)_(\w+)$", stem)
        if not m: continue
        sym, tf = m.group(1), m.group(2)
        if prefix and stem.startswith(prefix):
            sym = sym[len(prefix):]
        nf = norm_tf(tf)
        out.setdefault(sym, {})[nf] = os.path.join(base, fn)
    return out

def _scan_stocks(catalog):
    if catalog._stock_scanned and catalog._stock: return catalog._stock
    catalog._stock = _scan_dir(catalog.root, catalog.stocks_dir)
    catalog._stock_scanned = True
    return catalog._stock

def _scan_index(catalog):
    idx = _scan_dir(catalog.root, catalog.index_dir, prefix="idx_")
    catalog._index = { ("IDX_"+k if not k.startswith("IDX_") else k): v for k,v in idx.items() }
    catalog._index_scanned = True
    return catalog._index

def list_markets():
    return ["A股","指数","MT5","OKX"]

def list_symbols(catalog, market="A股"):
    if market=="A股": return sorted(_scan_stocks(catalog).keys())
    if market=="指数": return sorted(_scan_index(catalog).keys())
    if market=="MT5":
        if not catalog._mt5: catalog._mt5 = _scan_dir(catalog.root, catalog.mt5_dir)
        return sorted(catalog._mt5.keys())
    if market=="OKX":
        if not catalog._okx: catalog._okx = _scan_dir(catalog.root, catalog.okx_dir)
        return sorted(catalog._okx.keys())
    return []

def resolve(catalog, market, symbol, tf="daily"):
    """Return abspath for (market,symbol,tf). tf may be wildcard for first avail."""
    d = None
    if market=="A股": d = _scan_stocks(catalog).get(symbol)
    elif market=="指数": d = _scan_index(catalog).get(symbol)
    elif market=="MT5":
        if not catalog._mt5: catalog._mt5 = _scan_dir(catalog.root, catalog.mt5_dir)
        d = catalog._mt5.get(symbol)
    elif market=="OKX":
        if not catalog._okx: catalog._okx = _scan_dir(catalog.root, catalog.okx_dir)
        d = catalog._okx.get(symbol)
    if not d: return None, []
    nf = norm_tf(tf)
    if nf in d: return d[nf], list(d.keys())
    # fallback: return canonical daily + available list
    for pref in ("daily","60min","15min","5min"):
        if pref in d: return d[pref], list(d.keys())
    return None, list(d.keys())

def load(catalog, market, symbol, tf="daily", n=None):
    """Load bars -> DataFrame[time,open,high,low,close,tick_volume] sorted asc."""
    path, avail = resolve(catalog, market, symbol, tf)
    if path is None:
        return None
    df = pd.read_parquet(path)
    for col in ("time","open","high","low","close","tick_volume"):
        if col in df.columns and df[col].dtype == object:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    if "tick_volume" not in df.columns and "vol" in df.columns:
        df["tick_volume"] = pd.to_numeric(df["vol"], errors="coerce")
    df = df[["time","open","high","low","close","tick_volume"]].dropna()
    df = df.sort_values("time").reset_index(drop=True)
    df["code"] = symbol
    if n: df = df.tail(n).reset_index(drop=True)
    return df
