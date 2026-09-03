# -*- coding: utf-8 -*-
"""aiquant —— 端到端全自动量化工具 · 命令行入口.

用法:
  python -m aiquant.app --market A股 --symbol 600519 --tf daily [--stance 稳|激进] [--report]
  python -m aiquant.app scan --market A股 [--top 20]        # 全市场扫描
"""
from __future__ import annotations
import argparse, os, sys, time, datetime
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path: sys.path.insert(0, ROOT)

def analyze(market, symbol, tf, stance="稳", use_report=True, use_news=True):
    from aiquant.market import MarketCatalog, load
    from aiquant.engine.indicators import add_indicators
    from aiquant.engine.signals import run_signal
    from aiquant.backtest.strategies import compare
    from aiquant.features.sentiment import sentiment
    import aiquant.report.report as rep
    from aiquant.api.deepseek import summarize_offline
    cat = MarketCatalog()
    df = load(cat, market, symbol, tf)
    if df is None or len(df) < 60:
        print("数据不足:", market, symbol); return None
    df = add_indicators(df)
    sig = run_signal(df, stance)
    strat = compare(df)
    ss = None
    if use_news:
        try: ss = sentiment(symbol=symbol)
        except Exception: ss = None
    print(summarize_offline(symbol, sig, ss, strat))
    if use_report:
        out = os.path.join(ROOT, "out", "report_%s_%s.html" % (symbol, tf))
        os.makedirs(os.path.dirname(out), exist_ok=True)
        rep.build_report(df, sig, ss, strat, out, symbol="%s %s" % (market, symbol))
        print("HTML 报告:", out)
    return {"signal": sig, "sentiment": ss, "backtest": strat}

def scan(market, top=20, stance="激进"):
    from aiquant.market import MarketCatalog, load, list_symbols
    from aiquant.engine.indicators import add_indicators
    from aiquant.engine.signals import run_signal
    cat = MarketCatalog()
    syms = list_symbols(cat, market)
    rows = []
    for s in syms[:400]:
        try:
            df = load(cat, market, s, "daily")
            if df is None or len(df) < 60: continue
            df = add_indicators(df)
            sig = run_signal(df, stance)
            if sig["order"] != "观望":
                rows.append((sig["confidence"], s, sig["direction"], round(sig["close"],3)))
        except Exception:
            continue
    rows.sort(key=lambda x: -x[0])
    print("市场: %s  扫描出信号 %d 条" % (market, len(rows)))
    for conf, s_, d, c_ in rows[:top]:
        line = "  %-10s %-4s conf=%d close=%s" % (s_, d, conf, c_)
        print(line)
    return rows

def main():
    ap = argparse.ArgumentParser(prog="aiquant")
    sub = ap.add_subparsers(dest="cmd")
    p1 = sub.add_parser("analyze"); p1.add_argument("--symbol", required=True); p1.add_argument("--market", default="A股")
    p1.add_argument("--tf", default="daily"); p1.add_argument("--stance", default="稳", choices=["稳","激进"])
    p1.add_argument("--no-report", action="store_true")
    p2 = sub.add_parser("scan"); p2.add_argument("--market", default="A股"); p2.add_argument("--top", type=int, default=15)
    args = ap.parse_args()
    if args.cmd == "analyze":
        analyze(args.market, args.symbol, args.tf, args.stance, use_report=not args.no_report)
    elif args.cmd == "scan":
        scan(args.market, args.top)
    else:
        ap.print_help()

if __name__ == "__main__":
    main()
