# -*- coding: utf-8 -*-
"""A股 名称<=>代码 映射。抓取一次并缓存到 names.json，之后离线可用（EXE 已内置）。"""
from __future__ import annotations
import os, json, re

_CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "names.json")

def _board(code):
    if code.startswith(("688", "689")): return "科创板"
    if code.startswith(("300", "301", "302")): return "创业板"
    if code.startswith(("8", "4", "92")): return "北交所"
    return "沪深主板"

def _url(pn):
    g = "fs=m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23,m:0+t:81+s:2048"
    base = "http://push2.eastmoney.com/api/qt/clist/get?pn=%d&pz=200&po=1&np=1"
    base += "&fltt=2&invt=2&fid=f12&fs=%s"
    return base % (pn, g)

def _get(pn, timeout=25):
    import urllib.request
    req = urllib.request.Request(_url(pn), headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://quote.eastmoney.com/"})
    return urllib.request.urlopen(req, timeout=timeout)

def fetch_all(timeout=25):
    import json as _j, time
    out = {}
    for pn in range(1, 61):
        try:
            d = _j.load(_get(pn, timeout))
            diff = (d.get("data") or {}).get("diff") or []
            if not diff: break
            for it in diff:
                code = str(it.get("f12", "")).strip()
                name = (it.get("f14") or "").strip()
                if code and name:
                    out[code] = {"name": name, "board": _board(code)}
            time.sleep(0.2)
        except Exception:
            time.sleep(0.5)
            try:
                d = _j.load(_get(pn, timeout))
                diff = (d.get("data") or {}).get("diff") or []
                for it in diff:
                    code = str(it.get("f12", "")).strip(); name = (it.get("f14") or "").strip()
                    if code and name: out[code] = {"name": name, "board": _board(code)}
            except Exception:
                break
    return out

def _read_cache():
    try:
        m = json.load(open(_CACHE, encoding="utf-8"))
        return m if isinstance(m, dict) else {}
    except Exception:
        return {}

def get_mapping(force_refresh=False):
    if not force_refresh and os.path.exists(_CACHE):
        c = _read_cache()
        if c: return c
    m = fetch_all()
    if m:
        try:
            with open(_CACHE, "w", encoding="utf-8") as fh:
                json.dump(m, fh, ensure_ascii=False)
        except Exception:
            pass
    return _read_cache() or m

def find_by(query):
    m = get_mapping(); q = (query or "").strip().lower()
    if not q: return []
    hits = []
    if re.fullmatch(r"d{5,6}", q) and q in m:
        d = m[q]; hits.append((q, d["name"], d.get("board", "")))
    else:
        for c, d in m.items():
            if q in d["name"].lower():
                hits.append((c, d["name"], d.get("board", "")))
                if len(hits) >= 100: break
    hits.sort(key=lambda x: len(x[1]))
    return hits

def name_of(code):
    m = get_mapping()
    d = m.get(str(code))
    return d["name"] if d else str(code)
