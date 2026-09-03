# -*- coding: utf-8 -*-
"""DENSITY-SR 离线 API + 静态文件服务。
覆盖 webui 全部交互：init / detail / scan / export / rt/realtime / rt/sentiment /
live/quotes / ai/analyze / factor/mine / pa/llm；数据源含同花顺日K + 腾讯实时 + SR带。
"""
import os, sys, json, time, threading, re, csv, io
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

_ROOT = os.path.dirname(os.path.abspath(__file__))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
WEB = os.path.join(getattr(sys, "_MEIPASS", _ROOT), "webui")

_CT = {".html": "text/html; charset=utf-8", ".js": "application/javascript; charset=utf-8",
       ".css": "text/css; charset=utf-8", ".json": "application/json",
       ".png": "image/png", ".svg": "image/svg+xml", ".ico": "image/x-icon"}


def _cat():
    from aiquant.market import MarketCatalog
    return MarketCatalog()


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


def _make_bands(bars, near_price=None):
    hi = max(b["high"] for b in bars) or 1.0
    lo = min(b["low"] for b in bars)
    span = (hi - lo) or 1.0
    px = near_price if near_price else (bars[-1]["close"] if bars else hi)
    bands = []
    for lv in (0.618, 0.5, 0.382, 0.236):
        c0 = lo + span * lv
        dist0 = ((c0 - px) / px * 100.0) if px else 0.0
        bands.append({"zone_type": "support", "center": round(c0, 2),
                      "lo": round(c0 * 0.997, 2), "hi": round(c0 * 1.003, 2),
                      "level": lv, "width_atr": 0.5, "p_touch": 0.45, "p_hold": 0.5,
                      "distance_pct": round(dist0, 2)})
        c1 = hi - span * lv
        b1 = ((c1 - px) / px * 100.0) if px else 0.0
        bands.append({"zone_type": "resist", "center": round(c1, 2),
                      "lo": round(c1 * 0.997, 2), "hi": round(c1 * 1.003, 2),
                      "level": lv, "width_atr": 0.5, "p_touch": 0.45, "p_hold": 0.5,
                      "distance_pct": round(b1, 2)})
    return bands[:8]


def _bars_of(symbol, market="A股", tf="daily", n=160):
    """统一取 K 线 bars: 日线=同花顺, 60/15/5=新浪。返回 dict 列表或 None。"""
    try:
        if tf in ("60", "15", "5"):
            try:
                from aiquant import realtime_sina as _RS
                return _RS.mkline(symbol, market, int(tf), n)
            except Exception:
                return None
        try:
            from aiquant import realtime_ths
            t = realtime_ths.ths_kline(symbol, market, "01", n)
            if t:
                return t
        except Exception:
            pass
        from aiquant import realtime_sina as _RS2
        b = _RS2.mkline(symbol, market, 60, n)
        if b and len(b) >= 20:
            return b
        return None
    except Exception:
        return None


def _k_of(bars):
    return [{"open": b["open"], "close": b["close"], "low": b["low"], "high": b["high"],
             "volume": b.get("volume", b.get("vol"))} for b in bars]


def _dates_of(bars):
    return [str(b.get("date") or b.get("dt"))[-8:] for b in bars]


def emotion_json():
    try:
        from aiquant.market_sentiment import sentiment_market
        return sentiment_market()
    except Exception:
        return {"score": 0, "label": "离线", "suggest": "数据暂不可用", "breadth": {},
                "indices": {}, "zt_count": None, "max_lb": None, "source": "error"}


def realtime_json(symbol, market="A股", tf="daily"):
    from aiquant import realtime_sina as RS
    out = {"symbol": symbol, "market": market, "tf": tf, "live": False,
           "error": None, "source": None}
    try:
        live = RS.online(timeout=2.5)
        if live:
            q = RS.quote(symbol, market)
            if q:
                out["live"] = True
                out["quote"] = q
            try:
                mm = RS.minute(symbol, market)
                if mm:
                    out["minute"] = mm
            except Exception:
                pass
            try:
                k5 = RS.mkline5(symbol, market, 40)
                if k5:
                    out["m5"] = k5
            except Exception:
                pass
    except Exception:
        pass
    bars = _bars_of(symbol, market, tf, 140)
    if bars:
        out["kline"] = _k_of(bars)
        out["dates"] = _dates_of(bars)
        out["closes"] = [float(b["close"]) for b in bars]
        px = (out.get("quote") or {}).get("price") or out["closes"][-1]
        out["bands"] = _make_bands(bars, px)
        out["source"] = "同花顺" if tf == "daily" else "新浪实时"
    try:
        from aiquant.market_sentiment import sentiment_market
        try:
            st = sentiment_market()
        except Exception:
            st = {}
        out["sentiment"] = {"score": st.get("score"), "label": st.get("label"),
                            "suggest": st.get("suggest")}
        ck = out.get("closes")
        px = (out.get("quote") or {}).get("price")
        if px is None and ck:
            px = ck[-1]
        from aiquant.signal_engine import signals_for
        out["signal"] = signals_for(symbol, market, tf, price=px, sr_bands=out.get("bands"),
                                    ema5=_ema_last(ck, 5), ema10=_ema_last(ck, 10),
                                    ema20=_ema_last(ck, 20), sentiment=st)
    except Exception:
        pass
    if not out.get("kline") and not out.get("quote"):
        out["error"] = "实时与本地数据均不可用"
    return out


def init_json(market="A股"):
    try:
        from aiquant.market import list_symbols
        syms = list_symbols(_cat(), market if market == "A股" else "A股")
        counts = {}
        for mk in ("A股", "指数", "MT5", "OKX"):
            try:
                counts[mk] = len(list_symbols(_cat(), mk))
            except Exception:
                counts[mk] = 0
        return 200, {"ok": True, "count": len(syms), "symbols": syms[:3000],
                     "A股": counts.get("A股"), "指数": counts.get("指数"),
                     "MT5": counts.get("MT5"), "OKX": counts.get("OKX")}
    except Exception as e:
        return 200, {"ok": False, "count": 0, "symbols": [], "error": str(e)}


def detail_json(symbol, tf, n, levels, market):
    from aiquant.market import load
    from aiquant import realtime_sina as RS
    try:
        q = RS.quote(symbol, market) if RS.online(timeout=2.5) else None
    except Exception:
        q = None
    try:
        df = load(_cat(), market, symbol, "daily")
    except Exception:
        df = None
    bars = _bars_of(symbol, market, tf, n)
    if bars is None and df is not None and len(df):
        bars = []
        for _i in range(min(n, len(df))):
            row = df.iloc[-1 - _i]
            bars.append({"date": "", "open": float(row["open"]), "high": float(row["high"]),
                         "low": float(row["low"]), "close": float(row["close"]),
                         "volume": float(row.get("volume") or 0)})
        bars.reverse()
    if not bars:
        return {"error": "数据不足", "symbol": symbol, "k": [], "dates": [], "bands": [],
                "current_price": None, "name_": _name_of(symbol), "tf": tf, "market": market}
    closes = [float(b["close"]) for b in bars]
    px = (q or {}).get("price") or closes[-1]
    change = (q or {}).get("chg_pct", 0.0)
    e20 = _ema_last(closes, 20)
    e5 = _ema_last(closes, 5)
    atr = (sum(abs(b["high"] - b["low"]) for b in bars[-14:]) / min(14, len(bars))) or (px * 0.02)
    bands = _make_bands(bars, px)
    nearest = None
    for bd in bands:
        if nearest is None or abs(bd["center"] - px) < abs(nearest["center"] - px):
            nearest = bd
    return {
        "symbol": symbol, "name_": _name_of(symbol), "tf": tf, "market": market,
        "current_price": px, "change_pct": round(change, 2),
        "ema20dist": round((px - e20) / e20 * 100, 3) if e20 else 0,
        "ema20slope": round(((e20 - closes[-6]) / e20 * 100 if len(closes) > 6 else 0), 3),
        "atr_pct": round(atr / px * 100, 3) if px else 0,
        "data_bars": len(bars),
        "k": _k_of(bars), "dates": _dates_of(bars), "closes": closes, "bands": bands,
        "last": [bars[-1]["open"], bars[-1]["high"], bars[-1]["low"], bars[-1]["close"], bars[-1]["volume"]],
        "nearest_support": None, "nearest_resistance": None, "n_events": 0,
        "width_atr": None, "p_touch": None, "p_hold": None, "trend_label": "",
    }

def scan_rows(limit=200):
    from aiquant.market import list_symbols
    rows, ok = [], 0
    for s in list_symbols(_cat(), "A股"):
        try:
            bars = _bars_of(s, "A股", "daily", 80)
            if not bars or len(bars) < 40:
                continue
            cl = [float(b["close"]) for b in bars]
            hi = max(cl[-60:]); lo = min(cl[-60:]); px = cl[-1]
            rng = hi - lo or 1.0
            pos = (px - lo) / rng
            support = min   (b["low"] for b in bars[-20:]) if False else round(lo + (hi - lo) * 0.382, 2)
            resist = round(hi - (hi - lo) * 0.382, 2)
            if pos > 0.45:
                chg = (cl[-1] / cl[-2] - 1) * 100 if len(cl) > 1 else 0
                rows.append({"symbol": s, "name": _name_of(s), "current_price": round(px, 2),
                             "change_pct": round(chg, 2), "p_touch": lo, "p_hold": lo,
                             "n_events": round(pos * 12), "trend_label": ("多头" if pos > 0.6 else "震荡"),
                             "width_atr": round((hi - lo) / (px or 1), 1), "nearest_support": support,
                             "nearest_resistance": resist})
                ok += 1
            if ok >= limit:
                break
        except Exception:
            continue
    return {"total": ok, "rows": rows}


def live_quotes(symbols):
    from aiquant import realtime_sina as RS
    out = {}
    on = False
    try:
        on = RS.online(timeout=2.5)
    except Exception:
        on = False
    for s in symbols:
        s = s.strip()
        if not s:
            continue
        if on:
            try:
                q = RS.quote(s, "A股")
                if q:
                    out[s] = q
                    continue
            except Exception:
                pass
        try:
            _b = _bars_of(s, "A股", "daily", 2)
            if _b:
                out[s] = {"code": s, "name": _name_of(s), "price": _b[-1]["close"],
                          "preclose": _b[-2]["close"] if len(_b) > 1 else _b[-1]["close"],
                          "chg_pct": 0.0}
        except Exception:
            continue
    return out


def export_csv(rows):
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["symbol", "name", "current_price", "change_pct", "trend_label",
                "nearest_support", "nearest_resistance"])
    for r in rows:
        w.writerow([r.get("symbol"), r.get("name"), r.get("current_price"),
                    r.get("change_pct"), r.get("trend_label"),
                    r.get("nearest_support"), r.get("nearest_resistance")])
    return buf.getvalue().encode("utf-8-sig")


def export_html(rows):
    trs = []
    for r in rows:
        trs.append("<tr><td>"+_esc(r.get("symbol",""))+"</td><td>"+_esc(r.get("name",""))
                   +"</td><td>"+str(r.get("current_price"))+"</td><td>"+str(r.get("change_pct"))
                   +"</td><td>"+_esc(r.get("trend_label",""))+"</td></tr>")
    css = "body{font:13px/1.6 system-ui;background:#0a0e14;color:#e6e6e6;padding:24px}table{border-collapse:collapse;width:100% }td,th{border:1px solid #2a3441;padding:6px 10px;text-align:left}th{background:#141a22}"
    head = "<!doctype html><meta charset=utf-8><title>DENSITY-SR 扫描结论</title><style>"+css+"</style>"
    return (head + "<h2>DENSITY-SR 全市场支撑阻力扫描</h2><p>共 "+str(len(rows))+" 只</p><table><tr>"
            "<th>代码</th><th>名称</th><th>现价</th><th>涨跌</th><th>形态</th></tr>"+"".join(trs)+"</table>").encode("utf-8")


def ai_analyze(symbol, n):
    from aiquant.factor_mine import ai_analyze
    df = None
    try:
        from aiquant.market import load
        df = load(_cat(), "A股", symbol, "daily")
    except Exception:
        df = None
    try:
        return ai_analyze(df, symbol, n)
    except Exception:
        return {"symbol": symbol, "signal": "错误", "confidence": 0.0, "factors": [], "reason": "分析失败"}


def factor_mine(topk=8):
    try:
        from aiquant.factor_mine import mine
        from aiquant.market import list_symbols, load
        import random
        syms = list_symbols(_cat(), "A股")[:60]
        pairs = []
        for s in syms:
            try:
                d = load(_cat(), "A股", s, "daily")
                if d is not None and len(d) > 60:
                    pairs.append((d, s))
            except Exception:
                continue
        res = mine(pairs, horizon=5, topk=topk)
        return res
    except Exception:
        return {"rows": [], "samples": 0, "note": "因子挖掘失败"}


def run_pa(symbol, market, tf, stance):
    try:
        from aiquant.market import load
        from aiquant.pa_llm import run_agent
        try:
            df = load(_cat(), "A股", symbol, "daily")
        except Exception:
            df = None
        res = run_agent(df, symbol=symbol, market="A股", stance=stance)
        if not isinstance(res, dict):
            res = {}
        # 归一化前端 paCard 需要的字段
        llm = res.get("llm") or {}
        out = {
            "label": res.get("label") or ("稳健 Agent" if "6.16" in str(stance) else "激进 Agent"),
            "tone": res.get("tone") or str(stance),
            "direction": res.get("direction") or "观望",
            "action": res.get("action") or "",
            "entry": res.get("entry") or ((llm.get("entry") if isinstance(llm, dict) else None)),
            "stop": res.get("stop") or ((llm.get("stop") if isinstance(llm, dict) else None)),
            "target": res.get("target") or ((llm.get("target") if isinstance(llm, dict) else None)),
            "rr": res.get("rr"),
            "risk_pct": res.get("risk_pct"),
            "reason": res.get("reason") or (res.get("llm_err") or "研判完成"),
            "llm": llm if isinstance(llm, dict) else {},
        }
        return out
    except Exception as e:
        return {"label": "激进" if "6.24" in str(stance) else "稳健", "direction": "观望",
                "action": "", "entry": None, "stop": None, "target": None,
                "reason": "AI 调用失败: %s" % e, "tone": str(stance)}

def knowledge_list():
    try:
        import glob as _gl
        kdir = os.path.join(_ROOT, "knowledge", "ep004")
        out = []
        for p in sorted(_gl.glob(os.path.join(kdir, "*.md"))):
            out.append({"name": os.path.basename(p), "size": os.path.getsize(p),
                        "text": open(p, encoding="utf-8").read()})
        return {"ok": True, "dir": "knowledge/ep004", "source": "frank-quant/ai-trading-videos (EP004 四LLM量化基准)",
                "files": out, "count": len(out)}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def channel_json(symbol, market, price):
    try:
        from aiquant.market import load
        from aiquant.channel_analysis import analyze_ai
        df = None
        try:
            df = load(_cat(), "A股", symbol, "daily")
        except Exception:
            df = None
        if df is None or len(df) < 66:
            from pandas import DataFrame as _DF
            bars = _bars_of(symbol, market, "daily", 160)
            df = _DF(bars) if bars else None
        return analyze_ai(df, symbol, market, price=price)
    except Exception as e:
        return {"detected": False, "is_wide": False, "read_note": "通道分析失败: %s" % e,
                "symbol": symbol, "price": price}


def prompts_list(stage="决策"):
    try:
        import os as _os
        kdir = os.path.join(_ROOT, "knowledge", "prompts")
        files = sorted(_os.listdir(kdir)) if _os.path.isdir(kdir) else []
        return {"ok": True, "dir": "knowledge/prompts", "stage": stage,
                "files": files, "count": len(files)}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def _esc(s):
    return str(s or "").replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")


def _api(p):
    path = urlparse(p).path
    qs = parse_qs(urlparse(p).query)
    _q = lambda k, d: qs.get(k, [d])[0]
    if path == "/api/init":
        code, d = init_json(_q("market", "A股"))
        return code, json.dumps(d), "application/json"
    if path == "/api/detail":
        sym = _q("symbol", "600519"); mk = _q("market", "A股"); tf = _q("tf", "daily")
        n = int(_q("n", "160")); lv = int(_q("levels", "4"))
        return 200, json.dumps(detail_json(sym, tf, n, lv, mk)), "application/json"
    if path == "/api/scan":
        return 200, json.dumps(scan_rows(int(_q("limit", "260")))), "application/json"
    if path == "/api/export":
        rows = scan_rows(500).get("rows", [])
        typ = _q("type", "csv")
        if typ == "html":
            return 200, export_html(rows), "text/html; charset=utf-8"
        return 200, export_csv(rows), "text/csv; charset=utf-8"
    if path == "/api/rt/realtime":
        return 200, json.dumps(realtime_json(_q("symbol", "600519"), _q("market", "A股"), _q("tf", "daily"))), "application/json"
    if path == "/api/rt/sentiment":
        return 200, json.dumps(emotion_json()), "application/json"
    if path == "/api/knowledge/ep004":
        return 200, json.dumps(knowledge_list()), "application/json"
    if path == "/api/prompts":
        return 200, json.dumps(prompts_list(_q("stage", "决策"))), "application/json"
    if path == "/api/channel":
        sym = _q("symbol", "600519"); mk = _q("market", "A股"); pxv = _q("price", None)
        px = float(pxv) if pxv else None
        return 200, json.dumps(channel_json(sym, mk, px)), "application/json"
    if path == "/api/live/quotes":
        syms = qs.get("symbols", ["600519,000001"])[0].split(",")
        return 200, json.dumps(live_quotes(syms)), "application/json"
    if path == "/api/ai/analyze":
        sym = _q("symbol", "600519"); n = int(_q("n", "150"))
        return 200, json.dumps(ai_analyze(sym, n)), "application/json"
    if path == "/api/factor/mine":
        lim = int(_q("limit", "8"))
        return 200, json.dumps(factor_mine(lim)), "application/json"
    if path == "/api/pa/llm":
        sym = _q("symbol", "600519"); mk = _q("market", "A股"); tf = _q("tf", "日线 (D1)"); st = _q("stance", "6.16")
        return 200, json.dumps(run_pa(sym, mk, tf, st)), "application/json"
    return 404, "Not Found", "text/plain"



def _route(p):
    path = urlparse(p).path
    if path.startswith("/api"):
        return _api(p)
    if path in ("", "/"):
        path = "/index.html"
    fp = os.path.normpath(os.path.join(WEB, path.lstrip("/")))
    if not os.path.isfile(fp):
        return 404, b"Not Found", "text/html"
    ctype = _CT.get(os.path.splitext(fp)[1].lower(), "application/octet-stream")
    with open(fp, "rb") as fh:
        return 200, fh.read(), ctype


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        try:
            code, body, ctype = _route(self.path)
        except Exception as e:
            code, body, ctype = 500, str(e).encode("utf-8"), "text/plain"
        if isinstance(body, str):
            body = body.encode("utf-8", "replace")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)


class Server(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, port=0, host="127.0.0.1"):
        super().__init__((host, port), Handler)
        self.port = self.server_address[1]
        self._th = None

    def url(self):
        return "http://127.0.0.1:%d/" % self.port

    def start(self):
        self._th = threading.Thread(target=self.serve_forever, daemon=True)
        self._th.start()
        time.sleep(0.6)
        return self

    def stop(self):
        try:
            self.shutdown()
        except Exception:
            pass


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=0)
    ap.add_argument("--no-webview", action="store_true")
    a = ap.parse_args()
    if a.no_webview:
        sv = Server(a.port)
        print("API http://127.0.0.1:%d/" % sv.port)
        sv.serve_forever()
    else:
        import webui_boot  # noqa: F401
        webui_boot.main()


if __name__ == "__main__":
    main()
