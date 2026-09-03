# -*- coding: utf-8 -*-
import sys; sys.path.insert(0, r"C:/Users/mine/Downloads/quant_research")
src = open(r"C:/Users/mine/Downloads/quant_research/server.py", encoding="utf-8").read()
for sym in ("def run_pa","def _api","class Handler","class Server","def detail_json","def scan_rows","def realtime_json","def live_quotes","def ai_analyze","def factor_mine","def export_csv","def export_html","def init_json","def emotion_json"):
    print(sym, "count=", src.count(sym))
