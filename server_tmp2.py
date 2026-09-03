# -*- coding: utf-8 -*-
"""DENSITY-SR 离线 API + 静态文件服务 (pywebview web 界面 + 市场情绪 + 策略信号 + 同花顺行情)。"""
import os, sys, json, time, threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

_ROOT = os.path.dirname(os.path.abspath(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)


def _webui_dir():
    base = getattr(sys, "_MEIPASS", _ROOT)
    return os.path.join(base, "webui")


WEB = _webui_dir()

_CTYPE = {".html": "text/html; charset=utf-8", ".js": "application/javascript; charset=utf-8",
          ".css": "text/css; charset=utf-8", ".png": "image/png", ".svg": "image/svg+xml",
          ".ico": "image/x-icon", ".woff2": "font/woff2", ".json": "application/json"}


def _cat():
    return MarketCatalog_()


def _name_of(symbol):
    try:
        from aiquant import names
        return names.name_of(symbol) or ""
    except Exception:
        return ""


def _ema_last(a, period):
    if not a or len(a) < period:
        return None
    k = 2.0 / (period + 1)
    e = a[0]
    for x in a[1:]:
        e = (x - e) * k + e
    return e


# ---------------- 市场情绪 / 策略信号 ----------------
def sentiment_json():
    try:
        from aiquant.market_sentiment import sentiment_market
        return sentiment_market()
    except Exception:
        return {"score": 0, "label": "离线", "suggest": "数据暂不可用",
                "breadth": {}, "indices": {}, "zt_count": None, "max_lb": None,
                "source": "error"}


def _signal_for(quote_price, closes, bands, symbol, market, tf, sent):
    try:
        from aiquant.signal_engine import signals_for
        e5 = _ema_last(closes, 5); e10 = _ema_last(closes, 10); e20 = _ema_last(closes, 20)
        px = quote_price
        if px is None and closes:
            px = closes[-1]
        return signals_for(symbol, market, tf, price=px, sr_bands=bands,
                           ema5=e5, ema10=e10, ema20=e20, sentiment=sent)
    except Exception:
        return None


def _ema_last(a, p):
    return _ema(a, p)


def _ema(a, period):
    if not a or len(a) < period:
        return None
    k = 2.0 / (period + 1)
    e = a[0]
    for x in a[1:]:
        e = (x - e) * k + e
    return e


def _make_bands(bars):
    hi = max(x["high"] for x in bars) or 1.0
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
    return bands[:8]


# ===================================== API handlers =====================================
def realtime_json(symbol, market="A股", tf="daily"):
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
        except Exception:
            q = None
    bars = None
    if tf in ("60", "15", "5"):
        try:
            bars = RS.mkline(symbol, market, int(tf), 160)
        except Exception:
            bars = None
    elif tf == "daily":
        try:
            from aiquant import realtime_ths
            _t = realtime_ths.ths_kline(symbol, market, "01", 140)
            if _t:
                bars = _t
                out["source"] = "同花顺"
        except Exception:
            bars = None
        if bars is None:
            try:
                bars = RS.mkline(symbol, market, 60, 140)  # 兜底用半小时近似
                bars = None  # 不做错误兜底, 保持实时分时
            except Exception:
                bars = None
    if bars:
        k = [{"open": x["open"], "close": x["close"], "low": x["low"],
              "high": x["high"], "volume": x.get("volume")} for x in bars]
        dates = [str(x["date"])[-8:] for x in bars]
        closes = [float(x["close"]) for x in bars]
        out["kline"] = k
        out["dates"] = dates
        out["closes"] = closes
        out["bands"] = _make_bands(bars)
        if not out.get("source"):
            out["source"] = "同花顺/新浪"

    # 策略信号 + 情绪
    try:
        from aiquant.market_sentiment import sentiment_market
        try:
            sent = sentiment_market()
        except Exception:
            sent = {}
        out["sentiment"] = {"score": sent.get("score"), "label": sent.get("label"),
                            "suggest": sent.get("suggest")}
        px = (out.get("quote") or {}).get("price")
        if px is None and out.get("closes"):
            px = out["closes"][-1]
        from aiquant.signal_engine import signals_for
        sig = signals_for(symbol, market, tf, price=px, sr_bands=out.get("bands"),
                          ema5=_ema(out.get("closes"), 5), ema10=_ema(out.get("closes"), 10),
                          ema20=_ema(out.get("closes"), 20), sentiment=sent)
        out["signal"] = sig
    except Exception:
        pass
    if not out.get("kline") and not out.get("quote"):
        out["error"] = "实时与本地数据均不可用"
    return out
