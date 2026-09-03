# -*- coding: utf-8 -*-
"""情绪看板 HTML（词云 + 情绪雷达）。独立于主报告，供 Tab1 单独生成。"""
from __future__ import annotations
import os, datetime
from . import report as R

def render(sent, symbol, out_path):
    sent = sent or {"score": 0.0, "label": "无", "news": [], "top": [], "source": "无"}
    wc = ""
    if sent.get("top"):
        wc = R.make_wordcloud({w: 1 for w in sent["top"]})
    radar = R.make_radar(R.default_metrics(None, sent))
    gen = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    news = "".join("<li>%s</li>" % n for n in sent.get("news", [])[:20])
    html = "<!DOCTYPE html><html><head><meta charset='utf-8'><title>%s 情绪看板</title><style>" % symbol
    html += "body{font-family:SimHei,Arial;background:#f4f6f9;margin:0;color:#222}"
    html += ".wrap{max-width:900px;margin:0 auto;padding:20px} .big{font-size:30px;margin:10px 0}"
    html += "img{max-width:100%;border:1px solid #ccc;border-radius:6px;background:#fff}"
    html += "li{margin:6px 0}</style></head><body><div class='wrap'>"
    html += "<h1>%s 新闻情绪看板</h1><div class='big'>情绪 %s (%.3f)</div>" % (symbol, sent.get("label"), sent.get("score", 0))
    html += "<div style='display:flex'><div style='flex:1'>%s</div><div style='flex:1'>%s</div></div>" % (wc, radar)
    html += "<h3>新闻列表</h3><ul>%s</ul>" % news
    html += "<p>生成:%s · 来源:%s</p></div></body></html>" % (gen, sent.get("source", ""))
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    return out_path
