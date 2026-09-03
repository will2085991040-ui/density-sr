# -*- coding: utf-8 -*-
"""Feature 2 — self-contained interactive HTML report (K线+MACD, 雷达图, 词云, 信号&策略表)."""
from __future__ import annotations
import io, base64, os, datetime
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")

BG_DARK = "#0d1117"

def _dark():
    """暗色图表主题（贴合暗色量化终端截图）。"""
    import matplotlib.pyplot as plt
    plt.rcParams["axes.facecolor"] = BG_DARK
    plt.rcParams["figure.facecolor"] = BG_DARK
    plt.rcParams["savefig.facecolor"] = BG_DARK
    plt.rcParams["axes.edgecolor"] = "#30363d"
    plt.rcParams["text.color"] = "#e6edf3"
    plt.rcParams["axes.labelcolor"] = "#e6edf3"
    plt.rcParams["xtick.color"] = "#8b949e"
    plt.rcParams["ytick.color"] = "#8b949e"
    plt.rcParams["grid.color"] = "#21262d"
    plt.rcParams["legend.facecolor"] = BG_DARK
    plt.rcParams["legend.edgecolor"] = "#30363d"

def _apply_font():
    import matplotlib.pyplot as plt
    from matplotlib import font_manager as fm
    names = {f.name for f in fm.fontManager.ttflist}
    for fam in ("Microsoft YaHei", "SimHei", "SimSun", "Noto Sans CJK SC", "PingFang SC"):
        if fam in names:
            plt.rcParams["font.sans-serif"] = [fam]
            plt.rcParams["axes.unicode_minus"] = False
            return
    plt.rcParams["axes.unicode_minus"] = False

def _b64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=110, bbox_inches="tight")
    import matplotlib.pyplot as plt
    plt.close(fig)
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()

def kline_macd(df, title="", tail=200):
    """Candlestick + EMA20 + MACD subplot -> base64 PNG."""
    import matplotlib.pyplot as plt
    _apply_font()
    d = df.tail(tail).reset_index(drop=True)
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(11, 6.2), gridspec_kw={"height_ratios": [3.1, 1.0]})
    for i in range(len(d)):
        o, c, h, l = d["open"][i], d["close"][i], d["high"][i], d["low"][i]
        col = "#de4437" if c >= o else "#17955f"
        a1.vlines(i, l, h, color=col, lw=0.9)
        a1.bar(i, max(abs(o - c), 1e-6), 0.6, bottom=min(o, c), color=col if c >= o else "none", edgecolor=col, lw=0.9)
    if "ema20" in d.columns:
        a1.plot(d.index, d["ema20"], color="#f5a623", lw=1.3, label="EMA20")
    a1.set_title(title or "K线 + MACD", fontsize=12)
    a1.legend(loc="upper left", fontsize=8); a1.grid(alpha=0.2)
    if "date" in d.columns:
        dd = pd.to_datetime(d["date"]); step = max(1, len(d) // 10)
        ticks = list(range(0, len(d), step)); lab = [str(dd.iloc[t])[:10] for t in ticks]
        a1.set_xticks(ticks); a1.set_xticklabels(lab, rotation=45, fontsize=7, ha="right")
        a2.set_xticks(ticks); a2.set_xticklabels(lab, rotation=45, fontsize=7, ha="right")
    if {"macd", "macd_signal", "macd_hist"}.issubset(d.columns):
        cols = ["#c0392b" if v >= 0 else "#16a085" for v in d["macd_hist"]]
        a2.bar(d.index, d["macd_hist"], color=cols, width=0.6)
        a2.plot(d.index, d["macd"], color="#1167b1", lw=1.0, label="DIF")
        a2.plot(d.index, d["macd_signal"], color="#e8630a", lw=1.0, label="DEA")
        a2.legend(loc="upper left", fontsize=7); a2.grid(alpha=0.3)
    return _b64(fig)

def kline_macd_bytes(df, title="", tail=200, figsize=(11, 6.2)):
    """返回 K线+MACD 图的原始 PNG bytes（供 GUI 直接显示，不走 base64）。"""
    import matplotlib.pyplot as plt
    _apply_font()
    _dark()
    d = df.tail(tail).reset_index(drop=True).copy()
    if "date" not in d.columns:
        d["date"] = pd.to_datetime(d["time"], unit="s")
    fig = plt.figure(figsize=figsize, facecolor=BG_DARK)
    gs = fig.add_gridspec(2, 1, height_ratios=[3.1, 1.0], hspace=0.12)
    a1 = fig.add_subplot(gs[0]); a2 = fig.add_subplot(gs[1], sharex=a1)
    for a in (a1, a2):
        a.set_facecolor(BG_DARK); a.tick_params(colors="#8b949e", labelsize=8)
        for s in ("top", "right"): a.spines[s].set_visible(False)
        for s in ("left", "bottom"): a.spines[s].set_color("#30363d")
    for i in range(len(d)):
        o, c, h, l = d["open"][i], d["close"][i], d["high"][i], d["low"][i]
        col = "#de4437" if c >= o else "#17955f"
        a1.vlines(i, l, h, color=col, lw=0.9)
        a1.bar(i, max(abs(o - c), 1e-6), 0.6, bottom=min(o, c),
               color=col if c >= o else "none", edgecolor=col, lw=0.9)
    for col, name in (("ema20", "EMA20"), ("sma10", "MA10"), ("sma20", "MA20")):
        if col in d.columns:
            a1.plot(d.index, d[col], lw=1.1, label=name)
    # 支撑/阻力横线 + 买卖点标记（若传入）
    for i, row in d.iterrows():
        if "sig_point" in d.columns and row.get("sig_point") == 1:
            a1.scatter(i, row["low"] * 0.997, marker="^", color="#c0392b", s=70)
        if "sig_point" in d.columns and row.get("sig_point") == -1:
            a1.scatter(i, row["high"] * 1.003, marker="v", color="#16a085", s=70)
    a1.set_title(title or "K线 + MACD", fontsize=12)
    a1.legend(loc="upper left", fontsize=8); a1.grid(alpha=0.2)
    step = max(1, len(d) // 10)
    ticks = list(range(0, len(d), step))
    dd = pd.to_datetime(d["date"])
    lab = [str(dd.iloc[t])[:10] for t in ticks]
    a1.set_xticks(ticks); a1.set_xticklabels(lab, rotation=45, fontsize=7, ha="right")
    a2.set_xticks(ticks); a2.set_xticklabels(lab, rotation=45, fontsize=7, ha="right")
    if {"macd", "macd_signal", "macd_hist"}.issubset(d.columns):
        cols = ["#c0392b" if v >= 0 else "#16a085" for v in d["macd_hist"]]
        a2.bar(d.index, d["macd_hist"], color=cols, width=0.6)
        a2.plot(d.index, d["macd"], color="#1167b1", lw=1.0, label="DIF")
        a2.plot(d.index, d["macd_signal"], color="#e8630a", lw=1.0, label="DEA")
        a2.legend(loc="upper left", fontsize=7); a2.grid(alpha=0.3)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120, bbox_inches="tight")
    import matplotlib.pyplot as _plt
    _plt.close(fig)
    return buf.getvalue()

def make_radar(metrics, title="综合评分雷达"):
    dims = list(metrics.keys()); vals = [float(v) for v in metrics.values()]
    if not dims:
        return ""
    import matplotlib.pyplot as plt
    _apply_font()
    n = len(dims); ang = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
    fig, ax = plt.subplots(figsize=(5.6, 5.6), subplot_kw={"projection": "polar"})
    a = ang + ang[:1]; v = vals + vals[:1]
    ax.plot(a, v, color="#1167b1", lw=2); ax.fill(a, v, color="#1167b1", alpha=0.25)
    ax.set_xticks(ang); ax.set_xticklabels(dims, fontsize=10)
    ax.set_ylim(0, 1); ax.set_title(title, pad=16, fontsize=12)
    return _b64(fig)

def make_wordcloud(words):
    if not words:
        return ""
    from wordcloud import WordCloud
    import matplotlib.pyplot as plt
    _apply_font()
    fp = _wc_font()
    try:
        wc = WordCloud(font_path=fp, width=700, height=380, background_color="white", collocations=False)
        wc.generate_from_frequencies({w: max(1, c) for w, c in words.items()})
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.imshow(wc, interpolation="bilinear"); ax.axis("off"); ax.set_title("新闻词云")
        return _b64(fig)
    except Exception:
        return ""

def _wc_font():
    for c in (r"C:\Windows\Fonts\msyh.ttc", r"C:\Windows\Fonts\simhei.ttf", r"C:\Windows\Fonts\simsun.ttc"):
        if os.path.exists(c):
            return c
    return None

def _tbl(headers, rows, cap):
    h = "".join("<th>%s</th>" % x for x in headers)
    body = "".join("<tr>" + "".join("<td>%s</td>" % ("" if x is None else x) for x in r) + "</tr>" for r in rows)
    return "<h3>%s</h3><table><thead><tr>%s</tr></thead><tbody>%s</tbody></table>" % (cap, h, body)

def _sig_table(sig):
    if not sig:
        return ""
    f = lambda x: "" if x is None else ("%.4f" % x if isinstance(x, float) else str(x))
    rows = [("智能体", sig.get("stance_label", "")),("方向投票", sig.get("direction_vote", "")),
            ("动量", sig.get("momentum", "")),("评分/置信度", "%s/%s" % (sig.get("score", 0), sig.get("confidence", 0))),
            ("建议", "%s %s" % (sig.get("order", ""), sig.get("direction", ""))),
            ("入场", f(sig.get("entry"))),("止损", f(sig.get("stop"))),("目标", f(sig.get("target"))),
            ("支撑/阻力", "%s / %s" % (f(sig.get("support")), f(sig.get("resistance")))),
            ("ATR/现价", "%s / %s" % (f(sig.get("atr")), f(sig.get("close"))))]
    return _tbl(["指标", "值"], rows, "双智能体融合信号")

def _strat_table(strategies):
    if not strategies:
        return ""
    rows = [[s.get("strategy", ""), "%.2f%%" % ((s.get("total_return") or 0) * 100),
             "%.2f" % (s.get("sharpe") or 0), "%.2f%%" % ((s.get("max_drawdown") or 0) * 100), s.get("trades", 0)]
            for s in strategies if "error" not in s]
    return _tbl(["策略", "累计收益", "夏普", "最大回撤", "交易次数"], rows, "6 种策略一键对比")

def default_metrics(sig, sent):
    score = (sig or {}).get("score", 0) or 0; conf = (sig or {}).get("confidence", 50) / 100.0 or 0.5
    mom = 0.5 if (sig or {}).get("momentum") == "强" else (0.3 if (sig or {}).get("momentum") == "弱" else 0.5)
    sentv = (sent or {}).get("score", 0) or 0
    return {"价格": 0.5, "趋势": conf, "动量": mom, "量能": 0.5, "支撑": 0.5, "情绪": (sentv + 1) / 2}

def build_report(df, signal, sentiment, strategies, out_path, symbol="", title=None, extra_metrics=None):
    km = ""
    try: km = kline_macd(df, title or (symbol + " 走势"), 220)
    except Exception as e: km = "<p>K线生成失败:%s</p>" % str(e)[:120]
    metrics = extra_metrics or default_metrics(signal, sentiment)
    rdr = make_radar(metrics) if metrics else ""
    wc = ""
    if sentiment and sentiment.get("top"):
        wc = make_wordcloud({w: 1 for w in sentiment["top"]})
    sT = _sig_table(signal); st = _strat_table(strategies)
    news = ""
    if sentiment and sentiment.get("news"):
        lis = "".join("<li>%s</li>" % n for n in sentiment["news"][:12])
        news = "<h3>新闻（AI 情绪打分 %s）</h3><ul>%s</ul>" % (sentiment.get("label", ""), lis)
    gen = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    html = "<!DOCTYPE html>"
    html += "<html><head><meta charset='utf-8'><title>%s</title><style>" % (title or symbol)
    html += "body{font-family:SimHei,Arial;background:#f4f6f9;color:#222;margin:0}"
    html += ".wrap{max-width:1000px;margin:0 auto;padding:20px} h1{font-size:22px} img{max-width:100%;border:1px solid #ccc;border-radius:6px;background:#fff}"
    html += "table{border-collapse:collapse;width:100%;background:#fff;margin:8px 0} th,td{border:1px solid #dde2e8;padding:6px 9px;font-size:13px} th{background:#0b3d6b;color:#fff}"
    html += ".banner{padding:12px 16px;font-size:19px;font-weight:bold;background:#fff;border-radius:6px;border-left:6px solid #0b3d6b;margin:10px 0}"
    html += "</style></head><body><div class='wrap'>"
    html += "<h1>%s 量化分析报告</h1><p>生成:%s | 数据源:本地parquet | 情绪源:%s</p>" % (title or symbol, gen, (sentiment or {}).get("source", "无"))
    if signal:
        html += "<div class='banner'>%s %s</div>" % (signal.get("order", "观望"), signal.get("direction", ""))
    html += "<div style='display:flex;gap:14px;flex-wrap:wrap'><div style='flex:1;min-width:380px'>%s</div><div style='flex:1;min-width:260px'>%s</div></div>" % (km, rdr)
    html += wc + news + sT + st
    html += "</div></body></html>"
    with open(out_path, "w", encoding="utf-8") as fh: fh.write(html)
    return out_path
