# -*- coding: utf-8 -*-
"""DENSITY·SR 市场情绪引擎
聚合市场"温度 / 赚钱效应 / 涨跌结构 / 龙头连板梯队", 供量化交易做情绪择时与题材热度判断。
数据源(实时尽力而为, 失败自动回退本地):
  - 涨停池/连板梯队 : 东方财富 push2ex getTopicZTPool
  - 核心指数涨跌    : 东方财富 push2 ulist (上证/深成/创业板/沪深300)
  - 涨跌家数        : 本地 A股 parquet 最新两根日K统计(离线可靠)
所有网络访问均为 best-effort, 永不抛异常。
"""
from __future__ import annotations
import os, sys, json, time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

_EM = {"User-Agent": "Mozilla/5.0", "Referer": "https://data.eastmoney.com/", "Connection": "close"}

def _get(url, maxtry=3, timeout=12):
    import requests
    for _ in range(maxtry):
        try:
            r = requests.get(url, headers=_EM, timeout=timeout)
            if r.status_code == 200 and len(r.text) > 12:
                return r.text
        except Exception:
            pass
        time.sleep(0.9)
    return None

def _index_quotes():
    url = ("https://push2.eastmoney.com/api/qt/ulist.get?fltt=2&secids=1.000001,0.399001,1.000300,0.399006"
           "&fields=f2,f3,f4,f6,f12,f14")
    txt = _get(url)
    if not txt:
        # 回退: 腾讯行情(s_sh000001 等) 上证/创业板指
        try:
            import requests
            r = requests.get('https://qt.gtimg.cn/q=s_sh000001,s_sz399001,s_sz399006', timeout=8, headers={'User-Agent': 'Mozilla/5.0'})
            r.encoding = 'gbk'
            out = {}
            for line in r.text.split(';'):
                if '~' not in line: continue
                f = line.split('~')
                if len(f) < 6: continue
                code = str(f[2])
                out[code] = {'name': f[1], 'pct': float(f[5]) if f[5] else None, 'close': float(f[3]) if f[3] else None}
            return out or None
        except Exception:
            return None

    try:
        diff = json.loads(txt).get("data", {}).get("diff", [])
        return dict((str(d.get("f12", "")), {"name": d.get("f14", ""), "pct": d.get("f3"),
                                              "close": d.get("f2"), "chg": d.get("f4"),
                                              "amount": d.get("f6")}) for d in diff)
    except Exception:
        return None

def _zt_pool():
    try:
        import requests
        url = ("https://push2ex.eastmoney.com/getTopicZTPool?ut=7eea3edcaed734bea9cbfc24409ed989"
               "&dpt=wz.ztzt&Pageindex=0&pagesize=8&sort=fbt%3Aasc")
        r = requests.get(url, headers=_EM, timeout=6)
        data = json.loads(r.text).get("data") or {}
        tc = int(data.get("tc", 0))
        pool = data.get("pool") or []
        max_lb = max((int(p.get("lbc", 1)) for p in pool), default=0)
        sample = [{"code": p.get("c"), "name": p.get("n"), "lb": int(p.get("lbc", 1)),
                   "pct": float(p.get("zdp", 0))} for p in pool[:10]]
        return {"zt_count": tc, "max_lb": max_lb, "pool": sample, "online": True}
    except Exception:
        return {"zt_count": None, "max_lb": None, "pool": [], "online": False}

_BREAD_CACHE = [None, 0.0]

def _local_breadth(max_stocks=2200):
    import time as _t
    if _BREAD_CACHE[0] is not None and _t.time() - _BREAD_CACHE[1] < 900.0:
        return _BREAD_CACHE[0]
    ups = downs = total = 0
    try:
        from aiquant.market import MarketCatalog, list_symbols, load
        cat = MarketCatalog()
        syms = list_symbols(cat, "A股")
        if not syms:
            return None
        used = syms if len(syms) <= max_stocks else syms[:max_stocks]
        for s in used:
            try:
                df = load(cat, "A股", s, "daily")
                if df is None or len(df) < 2:
                    continue
                c = float(df['close'].iloc[-1]); pre = float(df['close'].iloc[-2])
                total += 1
                if c >= pre: ups += 1
                else: downs += 1
            except Exception:
                continue
        res = {"up": ups, "down": downs, "total": total}
        _BREAD_CACHE[0] = res; _BREAD_CACHE[1] = _t.time()
        return res
    except Exception:
        return None

def sentiment_market():
    """主入口: 返回市场情绪结构 dict(含温度/情绪/连板/涨跌结构/量化建议)。"""
    zt = _index_quotes()
    zty = _zt_pool()
    breadth = _local_breadth()

    idx = zt or {}
    sh = idx.get("000001") or {}
    cyb = idx.get("399006") or {}
    try:
        sh_pct = float(sh.get("pct")); cyb_pct = float(cyb.get("pct"))
    except Exception:
        sh_pct = cyb_pct = None

    zt_c = zty.get("zt_count"); max_lb = zty.get("max_lb"); zt_online = zty.get("online", False)
    up = down = total = 0; ratio = None
    if breadth:
        up, down, total = breadth.get("up", 0), breadth.get("down", 0), breadth.get("total", 0)
        ratio = round(min(1.0, max(0.0, (up / total if total else 0.0))), 4)

    # --- 情绪分数合成 ---
    score = 50.0
    reasons = []
    if sh_pct is not None and cyb_pct is not None:
        d = max(-20, min(20, sh_pct * 9 + cyb_pct * 6))
        score += d
        reasons.append("指数%+.2f%% 创业板%+.2f%% (贡献%+.1f)" % (sh_pct, cyb_pct, d))
    if zt_c is not None:
        d = max(0.0, min(20.0, (zt_c - 18) * 0.25))
        score += d
        reasons.append("涨停%d家 (贡献%+.1f)" % (zt_c, d))
    if max_lb:
        d = max(0.0, min(14.0, max_lb * 2.5))
        score += d
        reasons.append("最高%d连板 (贡献%+.1f)" % (max_lb, d))
    if total:
        d = (ratio - 0.5) * 40
        score += max(-18, min(18, d))
        reasons.append("涨跌比%.0f%% (贡献%+.1f)" % ((ratio or 0) * 100, d))

    score = max(0.0, min(100.0, score))
    if score >= 80: label = "亢奋·过热"
    elif score >= 65: label = "强势多头"
    elif score >= 52: label = "偏多"
    elif score >= 40: label = "中性震荡"
    elif score >= 26: label = "偏空"
    else: label = "低迷·冰点"

    if score >= 75:
        suggest = "情绪亢奋: 谨防高位分歧退潮, 兑现为主/不追最后一棒, 注意控制回撤"
    elif score >= 55:
        suggest = "情绪偏暖: 可积极做多强势主线, 顺势而为, 严守止损"
    elif score >= 42:
        suggest = "中性: 高抛低吸, 轻仓试错, 待右侧放量信号再加仓"
    elif score >= 26:
        suggest = "情绪偏冷: 防守为主, 降仓位, 只做超跌反弹并快进快出"
    else:
        suggest = "情绪冰点: 观望为主或分批左侧埋伏, 等待情绪与赚钱效应修复"

    return {
        "score": round(score, 2), "label": label, "suggest": suggest,
        "temperature": round(score, 1),
        "indices": {"sh": sh_pct, "cyb": cyb_pct},
        "zt_count": zt_c, "max_lb": max_lb, "zt_online": zt_online,
        "zt_pool": zty.get("pool", []),
        "breadth": {"up": up, "down": down, "total": total, "ratio": ratio},
        "reasons": reasons,
        "source": "realtime" if (zt_online or sh_pct is not None) else "local",
    }

if __name__ == "__main__":
    r = sentiment_market()
    print(json.dumps(r, ensure_ascii=False, indent=2))
