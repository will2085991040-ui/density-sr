# -*- coding: utf-8 -*-
"""同花顺(10jqka)行情适配器。

免费接口 d.10jqka.com.cn/v6/line/hs_<code>/<period>/last.js 返回 JSONP:
  data 为分号分隔字符串, 每行 = 日期,开,高,低,收,量,额,...
提供同花顺日线/分钟级 K 线, 与腾讯实时融合。
实时现价/分时若同花顺受限, 由腾讯 qt.gtimg.cn 负责(本机已验证可用)。
"""
import json
import requests

_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Referer": "http://www.10jqka.com.cn/",
    "Host": "d.10jqka.com.cn",
}
BASE = "http://d.10jqka.com.cn/v6/line/"

def _ths_code(symbol):
    c = str(symbol)
    if c[:1] in ("5", "6", "9", "2"):
        return "hs_" + c
    return "sz_" + c

def ths_kline(symbol, market="A股", period="01", n=None):
    """获取同花顺K线(period: 01日线 / 02周线等), 返回归一化 bars 或 None。

    bars: [ {date:'20260130', open, high, low, close, volume, amount}, ... ](由旧到新)
    """
    try:
        url = BASE + _ths_code(symbol) + "/" + period + "/last.js"
        r = requests.get(url, headers=_HEADERS, timeout=8)
        if r.status_code != 200:
            return None
        txt = r.text
        i = txt.find("{")
        j = txt.rfind("}")
        if i < 0 or j < i:
            return None
        import json
        obj = json.loads(txt[i:j + 1])
        data = obj.get("data")
        if not isinstance(data, str):
            return None
        bars = []
        for row in data.split(";"):
            p = row.split(",")
            if len(p) < 6:
                continue
            try:
                dt = p[0].strip()
                o = float(p[1]); hi = float(p[2]); lo = float(p[3]); cl = float(p[4])
                vol = float(p[5]); amt = float(p[6]) if len(p) > 6 and p[6] else 0.0
            except Exception:
                continue
            if not dt or not (o and hi and lo and cl):
                continue
            bars.append({"date": dt, "open": o, "high": hi, "low": lo,
                         "close": cl, "volume": vol, "amount": amt})
        if n and len(bars) > n:
            bars = bars[-n:]
        return bars if bars else None
    except Exception:
        return None

if __name__ == "__main__":
    bs = ths_kline("600519")
    print("bars:", len(bs) if bs else None)
    if bs:
        print("first", bs[0])
        print("last ", bs[-1])
