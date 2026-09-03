# -*- coding: utf-8 -*-
"""DENSITY-SR 离线 API + 静态文件服务 (给 pywebview 加载 web 界面)。"""
import os, sys, json, time, threading, re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

_ROOT = os.path.dirname(os.path.abspath(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

def _webui_dir():
    base = getattr(sys, "_MEIPASS", _ROOT)
    return os.path.join(base, "webui")
WEB = _webui()

from aiquant.market import MarketCatalog, load, list_symbols, list_markets  # noqa'

def _cat():
    return MarketCatalog()

def _name_of(symbol):
    try:
        from aiquant import names
        n = names.name_of(symbol)
        return n or ""
    except Exception:
        return ""

def _ema_list(a, period):
    if not a:
        return None
    k = 2.0 / (period + 1)
    e = a[0]
    out = [e]
    for x in a[1:]:
        e = (x - e) * k + e
        out.append(e)
    return out[-1]

# ---------------- 行情: 实时 + 同花顺日K + SR带 ----------------
def rt_engine(symbol, market="A股", tf="daily"):
    from aiquant import realtime_sina as RS
    out = {"symbol": symbol, "market": market, "tf": tf, "live": False,
           "error": None, "source": None}
    live = False
    try:
        live = RS.online(timeout=2.5)
    except Exception:
        live = False
    if live:
        try:
            q = RS.quote(symbol, market)
            if q:
                out["live"] = True
                out["quote"] = q
                out["source"] = "腾讯/同花顺"
        except Exception:
            pass
    bars = None
    clos = []
    if tf in ("60", "15", "5"):
        try:
            bars = RS.mkline(symbol, market, int(tf), 160)
        except Exception:
            bars = None
    elif tf == "daily":
        # 同花顺日K优先
        try:
            from aiquant import realtime_ths
            ths_bars = realtime_ths.ths_kline(symbol, market, "01", 140)
            if ths_bars:
                bars = ths_bars
                out["source"] = "同花顺"
        except Exception:
            bars = None
    if bars:
        k = [{"open": x.get("open"), "close": x.get("close"),
              "low": x.get("low"), "high": x.get("high"),
              "volume": x.get("volume")} for x in bars]
        dates = [str(x.get("date"))[-8:] for x in bars]
        clos = [float(x["close"]) for x in bars]
        hi = max(x["high"] for x in bars)
        lo = min(x["low"] for x in bars)
        span = (hi - lo) or 1.0
        bands = []
        for lv in (0.618, 0.5, 0.382, 0.236):
            c0 = lo + span * lv
            bands.append({"zone_type": "support", "center": round(c0, 2),
                          "lo": round(c0 * 0.997, 2), "hi": round(c0 * 1.003, 2),
                          "level": lv, "width_atr": 0.5, "p_touch": 0.45, "p_hold": 0.5})
            c1 = hi - span * lv
            bands.append({"zone_type": "resist", "center": round(c1, 2),
                          "lo": round(c1 * 0.997, 2), "hi": round(c1 * 1.003, 2),
                          "level": lv, "width_atr": 0.5, "p_touch": 0.45, "p_hold": 0.5})
        out["kline"] = kline
        out["dates"] = dates
        out["closes"] = closes
        out["bands"] = bands[:8]

    # ---------------- 策略信号 + 情绪 ----------------
    try:
        from aiquant.signal_engine import signals_for
        from aiquant.market_sentiment import sentiment_market
        try:
            sent = sentiment_market()
            out["sentiment"] = {"score": sent.get("score"), "label": sent.get("label"),
                                "suggest": sent.get("suggest")}
        except Exception:
            sent = {}
        px = None
        if out.get("quote") and out["quote"].get("price"):
            px = out["quote"]["price"]
        elif closes:
            px = closes[-1]
        # EMA warmers
        e5 = _ema_list(closes, 5) if len(closes) >= 5 else None
        e10 = _ema_list(closes, 10) if len(closes) >= 10 else None
        e20 = _ema_list(closes, 20) if len(closes) >= 20 else None
        sig = signals_for(symbol, market, tf, price=px, sr_bands=out.get("bands"),
                          ema5=e5, ema10=e10, ema20=e20, sentiment=sent)
        out["signal"] = sig
    except Exception:
        pass
    if not out.get("kline") and not out.get("quote"):
        out["error"] = "实时与本地数据均不可用"
    return out


def sentiment_json():
    try:
        from aiquant.market_sentiment import sentiment_market
        return sentiment_market()
    except Exception:
        return {"score": 0, "label": "离线", "suggest": "", "breadth": {},
                "indices": {}, "zt_count": None, "max_lb": None, "source": "error"}
