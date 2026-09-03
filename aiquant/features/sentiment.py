# -*- coding: utf-8 -*-
"""Feature 1 — news crawling + sentiment scoring (offline-first).

crawl_news(symbol): best-effort fetch of finance headlines (东方财富 search),
                  never raises (returns [] on network failure).
lexicon_score(headlines): deterministic zh-finance sentiment in [-1, 1], works offline.
sentiment(): high-level API returning {score,label,headlines,top_words,source}.
Optionally an LLM call upgrades scoring when api_key is supplied (functions.llm).
"""
from __future__ import annotations
import re, json, numpy as np

_POS = set("利好 超预期 增长 突破 反弹 增持 买入 中标 签约 盈利 分红 回购 创新高 涨停 净流入 扭亏 预增 上调 强势 活跃 亮眼 赢得 市占率 提升 放量 放量大涨 业绩增长 净利润增长".split())
_NEG = set("利空 跌破 减持 亏损 下调 预亏 违约 违规 立案 停牌 跌停 净流出 退市 风险 质押 爆雷 业绩下滑 不及预期 净减持 罚款 被查 低迷 回落 风险提示 商誉减值 扭亏为盈转亏".split())

def crawl_news(symbol, limit=10):
    """Return up to {limit} headlines for the symbol. Empty list on any network failure."""
    if not symbol:
        return []
    try:
        import requests
        param = {"uid":"","keyword":symbol,"type":["cmsArticleWebOld"],"client":"web",
                 "clientType":"web","clientVersion":"curr",
                 "param":{"cmsArticleWebOld":{"searchScope":"default","sort":"time","pageIndex":1,
                                              "pageSize":limit,"preTag":"","postTag":""}}}
        url = "https://search-api-web.eastmoney.com/search/jsonp?cb=x&param=" + json.dumps(param, ensure_ascii=False)
        headers = {"User-Agent":"Mozilla/5.0","Referer":"https://so.eastmoney.com/"}
        r = requests.get(url, headers=headers, timeout=6)
        titles = []
        for m in re.finditer(r'"title"\s*:\s*"((?:[^"\\\\]|\\\\.)*)"', r.text):
            t = m.group(1)
            try:
                t = json.loads('"' + t + '"')
            except Exception:
                pass
            t = re.sub(r"<[^>]+>", "", t).strip()
            if t: titles.append(t)
        return titles[:limit]
    except Exception:
        return []

def lex_sentiment(titles):
    if not titles:
        return 0.0
    s = 0.0
    for t in titles:
        for w in _POS:
            if w in t: s += 1.0
        for w in _NEG:
            if w in t: s -= 1.0
    return float(np.tanh(s / max(len(titles), 1)))

def top_words(titles, k=12):
    from collections import Counter
    c = Counter()
    for t in titles:
        for w in _POS | _NEG:
            if w in t: c[w] += 1
    return [w for w, _ in c.most_common(k)]

def sentiment(headlines=None, symbol="", llm_fn=None):
    """headlines: optional list. If None, crawl for symbol.
    Returns dict. When llm_fn provided (callable(title)->LOAT in [-1,1]), blend it.
    """
    if not headlines and symbol:
        headlines = crawl_news(symbol)
    if not headlines:
        return {"score": 0.0, "label": "信息不足", "news": [], "top": [], "source": "none"}
    lex = lex_sentiment(headlines)
    if llm_fn:
        try:
            llms = [float(llm_fn(t)) for t in headlines]
            llm_avg = float(np.mean(llms))
            score = 0.5 * lex + 0.5 * llm_avg
            src = "lexicon+llm"
        except Exception:
            score = lex; src = "lexicon"
    else:
        score = lex; src = "lexicon"
    label = ("强烈看多" if score > 0.6 else ("看多" if score > 0.15 else
             ("中性" if score > -0.15 else ("看空" if score > -0.6 else "强烈看空"))))
    return {"score": round(float(score), 4), "label": label, "news": headlines[:15],
            "top": top_words(headlines), "source": src}
