# -*- coding: utf-8 -*-
"""全市场支撑/阻力位批量识别（对齐 Detect_support_and_resistance_levels / analyze_all）。

对每只股票跑 SREngine（V3Fusion: density+pivots+ATR），输出:
  symbol, current_price, change_pct, n_zones, nearest_support(+dist_pct),
  nearest_resistance(+dist_pct), p_touch, p_hold, p_effective, edge_score,
  n_events, width_atr, trend_label, direction, data_bars, atr_pct
按 p_effective(触及×守住)降序。支持 CSV + 自包含 HTML 汇总。全离线。
"""
import os, sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
_VENDOR = os.path.join(os.path.dirname(__file__), "..", "engine", "vendor")
if _VENDOR not in sys.path:
    sys.path.insert(0, _VENDOR)


def _engine():
    from src.sr_engine import SREngine, build_summary
    return SREngine, build_summary


def analyze_symbol(df, symbol, direction="long", n_zones=6, tf="daily"):
    """单标的总风阻数据行；失败返回 (None, reason)。"""
    SREngine, build_summary = _engine()
    if df is None or len(df) < 60:
        return None, "数据不足"
    try:
        current = float(df["close"].iloc[-1])
        chg = float((df["close"].iloc[-1] / df["close"].iloc[-2] - 1) * 100) if len(df) > 1 else 0.0
        import pandas as _pd
        f = df.rename(columns={"tick_volume": "volume"}).copy()
        if "date" not in f.columns:
            f["date"] = _pd.to_datetime(f["time"], unit="s")
        eng = SREngine(n_zones=n_zones * 2)
        zones, info = eng.detect(f, symbol)
        if info.get("error"):
            return None, info["error"]
        summary = build_summary(zones, df, direction, info)
        sups = [z for z in zones if z["zone_type"] == "support"]
        ress = [z for z in zones if z["zone_type"] == "resistance"]
        ns = min(sups, key=lambda z: abs(z["distance_atr"])) if sups else None
        nr = min(ress, key=lambda z: abs(z["distance_atr"])) if ress else None
        near = summary.get("nearest")
        row = {
            "symbol": symbol, "tf": tf,
            "current_price": round(current, 4),
            "change_pct": round(chg, 2),
            "n_zones": len(zones),
            "nearest_support": ns["center"] if ns else None,
            "nearest_support_dist_pct": ns["distance_pct"] if ns else None,
            "nearest_resistance": nr["center"] if nr else None,
            "nearest_resistance_dist_pct": nr["distance_pct"] if nr else None,
            "p_touch": near.get("p_touch") if near else None,
            "p_hold": near.get("p_hold") if near else None,
            "p_effective": near.get("p_effective") if near else None,
            "edge_score": near["edge_score"] if near else None,
            "n_events": near["n_events"] if near else None,
            "width_atr": near["width_atr"] if near else None,
            "trend_label": summary["trend_label"],
            "direction": direction,
            "data_bars": len(df),
            "atr_pct": info.get("atr_pct"),
        }
        return row, None
    except Exception as e:
        return None, str(e)[:80]


def scan_market(cat, market="A股", tf="daily", direction="long", n_zones=6, limit=4000, on_progress=None):
    """扫全市场，返回 (rows, errors)。rows 按 p_effective 降序。"""
    from aiquant.market import list_symbols, load
    syms = list_symbols(cat, market)
    if limit:
        syms = syms[:limit]
    rows, errors = [], []
    total = len(syms)
    for idx, s in enumerate(syms):
        try:
            df = load(cat, market, s, tf)
        except Exception:
            df = None
        row, reason = analyze_symbol(df, s, direction=direction, tf=tf)
        if row:
            rows.append(row)
        elif reason:
            errors.append({"symbol": s, "reason": reason})
        if on_progress and (idx % 100 == 0 or idx == total - 1):
            on_progress(idx + 1, total, len(rows))
    _sort(rows)
    return rows, errors


def _sort(rows):
    def key(r):
        if r.get("p_effective") is not None:
            return -r["p_effective"]
        if r.get("edge_score") is not None:
            return -(r["edge_score"] or 0)
        return 1e9
    rows.sort(key=key)


CSV_COLS = ["symbol","current_price","change_pct","n_zones","nearest_support",
            "nearest_support_dist_pct","nearest_resistance","nearest_resistance_dist_pct",
            "p_touch","p_hold","p_effective","edge_score","n_events","width_atr",
            "trend_label","direction","data_bars","atr_pct"]


def to_csv(rows, path):
    import csv
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=CSV_COLS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k) for k in CSV_COLS})
    return path


def to_html(rows, path, title="全市场支撑/阻力位批量识别结果"):
    n = len(rows)
    hi_touch = sum(1 for r in rows if (r.get("p_touch") or 0) >= 0.6)
    hi_hold = sum(1 for r in rows if (r.get("p_hold") or 0) >= 0.7)
    heads = "<td>代码</td><td>现价</td><td>涨跌%</td><td>最近支撑</td><td>最近压力</td>"\
            "<td>触及%</td><td>守住%</td><td>有效%</td><td>被测试</td><td>趋势</td></thead><tbody>"
    body = []
    for r in rows[:3000]:
        chg = r.get("change_pct") or 0
        cls = "up" if chg > 0 else ("down" if chg < 0 else "")
        pfmt = lambda x: ("%.0f" % (x * 100)) if x is not None else "—"
        body.append(("<tr class='%s'><td>%s</td><td>%.2f</td><td>%+.2f</td><td>%s</td><td>%s</td>"
                    "<td>%s</td><td>%s</td><td>%s</td><td>%d</td><td>%s</td></tr>" % (
                        cls, r["symbol"], r["current_price"], r["change_pct"],
                        ("%.4f" % r["nearest_support"]) if r["nearest_support"] is not None else "—",
                        ("%.4f" % r["nearest_resistance"]) if r["nearest_resistance"] is not None else "—",
                        pfmt(r.get("p_touch")), pfmt(r.get("p_hold")), pfmt(r.get("p_effective")),
                        int(r.get("n_events") or 0), r.get("trend_label"))))
    css = ("body{{font-family:'Microsoft YaHei';margin:20px}}"
           "table{{border-collapse:collapse;width:96%}}"
           "th,td{{border:1px solid #ddd;padding:4px 8px;font-size:12px;text-align:right}}"
           "th{{background:#1167b1;color:#fff}}tr.up td{{color:#c0392b}}tr.down td{{color:#0e8a5f}}"
           "tr:nth-child(even){{background:#f6f8fa}}.st{{background:#eef4ff;padding:10px;border-radius:6px;margin-bottom:12px}}")
    html = ("<!DOCTYPE html><html><head><meta charset='utf-8'><title>{t}</title>"
           "<style>{c}</style></head><body>"
           "<h2>{t}</h2>"
           "<div class='st'>共识别 <b>{n}</b> 只 &middot; 高触及(&gt;=60%): <b>{ht}</b> &middot; 高守住(&gt;=70%): <b>{hh}</b> &middot; 按有效概率(触及x守住)排序 &middot; 全离线本地数据</div>"
           "<table><thead><tr>{thead}</tr></thead><tbody>{tbody}</tbody></table></body></html>").format(
        t=title, c=css, n=n, ht=hi_touch, hh=hi_hold, thead=heads, tbody="".join(body))
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    return path
