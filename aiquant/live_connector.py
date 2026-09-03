# -*- coding: utf-8 -*-
"""联网实时数据连接器: 腾讯行情 API 为主, akshare 为辅, 本地 parquet 兜底。"""
import os, sys, re, socket
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import requests

_UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

def online(timeout=2.0) -> bool:
    try:
        r = requests.get("https://qt.gtimg.cn/q=sh600000", timeout=timeout, headers=_UA)
        return bool(r.status_code == 200)
    except Exception:
        return False

def code_to_tx(symbol) -> str:
    s = str(symbol).zfill(6)[-6:]
    if s.startswith("4") or s.startswith("8"): return "bj" + s
    if s[0] in "569" or s.startswith("688") or s.startswith("689"): return "sh" + s
    return "sz" + s

def tx_to_code(tx) -> str:
    s = str(tx)
    for pre in ("sh", "sz", "bj", "us"):
        if s.startswith(pre): return s[len(pre):]
    return s

def quotes(symbols) -> dict:
    """批量实时报价。Tencent 字段: 0=v,1=name,2=code,3=price,4=preclose,5=open,32=chg%,33=high,34=low,36=vol,37=amt"""
    out = {}
    if not symbols: return out
    tx = [code_to_tx(s) for s in symbols]
    for i in range(0, len(tx), 50):
        chunk = tx[i:i+50]
        try:
            r = requests.get("https://qt.gtimg.cn/q=" + ",".join(chunk), timeout=12, headers=_UA)
            r.encoding = "gbk"
            for line in r.text.split(";"):
                if "~" not in line: continue
                f = line.split("~")
                if len(f) < 38: continue
                sym = tx_to_code(f[2])
                try:
                    out[sym] = {
                        "code": sym, "name": f[1],
                        "price": float(f[3]), "preclose": float(f[4]), "open": float(f[5]),
                        "high": float(f[33]), "low": float(f[34]), "chg_pct": float(f[32]),
                        "volume": int(float(f[36])), "amount": float(f[37]),
                    }
                except Exception:
                    continue
        except Exception:
            continue
    return out

def live_kline(symbol, days=120):
    """拉取腾讯日K(后复权/不复权 简单版), 返回 [(date, open, close, high, low, volume), ...] 或 None"""
    tx = code_to_tx(symbol)
    try:
        r = requests.get(f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param={tx},day,,,{days},qfq",
                         timeout=12, headers=_UA)
        j = r.json()
        data = j["data"][tx]
        key = "qfqday" if "qfqday" in data else "day"
        rows = data[key]
        out = []
        for it in rows:
            # [date, open, close, high, low, volume, ...]
            out.append({"date": it[0], "open": float(it[1]), "close": float(it[2]),
                       "high": float(it[3]), "low": float(it[4]), "volume": float(it[5])})
        return out
    except Exception:
        return None

def market_snapshot(limit=50):
    """实时全市场快照(akshare 优先, 失败返回空)"""
    try:
        import akshare as ak
        df = ak.stock_zh_a_spot_em()
        df = df.head(limit)
        return [{ "code": str(r["代码"]), "name": str(r["名称"]),
                 "price": float(r["最新价"]), "chg_pct": float(r["涨跌幅"]) }
               for _, r in df.iterrows()]
    except Exception:
        return []
