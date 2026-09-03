# -*- coding: utf-8 -*-
import os, sys, json, requests
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
_UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
_TX = {"User-Agent": "Mozilla/5.0", "Referer": "https://gu.qq.com/"}
_SINA = {"User-Agent": "Mozilla/5.0", "Referer": "https://finance.sina.com.cn"}

def online(timeout=3.0):
    try: return requests.get("https://qt.gtimg.cn/q=sh600000", timeout=timeout, headers=_UA).status_code == 200
    except Exception: return False

def prefix_of(market, symbol):
    if market not in ("A股", "指数"): return None
    s = str(symbol).zfill(6)[-6:]
    if s.startswith(('4','8','9')): return 'bj'+s
    if s[0] in '569' or s.startswith(('688','689')): return 'sh'+s
    if market == '指数':
        return 'sh'+s if s in ('000001','000016','000300','000905','000688') else 'sz'+s
    return 'sz'+s

def _get(url, headers, timeout=12, enc=None):
    try:
        r = requests.get(url, timeout=timeout, headers=headers)
        if enc: r.encoding = enc
        return r.text
    except Exception: return None

def quote(symbol, market):
    pre = prefix_of(market, symbol)
    if not pre: return None
    txt = _get('https://qt.gtimg.cn/q='+pre, _UA, enc='gbk')
    if not txt: return None
    for line in txt.split(';'):
        if '~' not in line: continue
        f = line.split('~')
        if len(f) < 38: continue
        try:
            return {'code':f[2],'name':f[1],'price':float(f[3]),'preclose':float(f[4]),'open':float(f[5]),'high':float(f[33]),'low':float(f[34]),'chg_pct':float(f[32]),'volume':int(float(f[36])),'amount':float(f[37]),'date':f[30] if len(f)>30 else ''}
        except Exception: return None
    return None

def minute(symbol, market):
        pre = prefix_of(market, symbol)
        if not pre: return None
        txt = _get('https://web.ifzq.gtimg.cn/appstock/app/minute/query?code='+pre, _TX)
        if not txt: return None
        try:
            j = json.loads(txt)
            arr = j['data'][pre]['data']['data']
        except Exception: return None
        out = []
        for row in arr:
            parts = row.replace(',', ' ').split()
            if len(parts) < 3: continue
            try:
                hm = parts[0]; p = float(parts[1]); cv = float(parts[2]); ca = float(parts[3]) if len(parts) > 3 else p*cv
                if hm.isdigit() and len(hm) == 4: hm = hm[:2] + ':' + hm[2:]
                avg = round(ca / (cv * 100.0), 3) if cv > 0 else p
                out.append({'t': hm, 'p': round(p,3), 'avg': avg})
            except Exception: continue
        return out if out else None


def mkline(symbol, market, scale=60, n=160):
    pre = prefix_of(market, symbol)
    if not pre: return None
    url = ('https://quotes.sina.cn/cn/api/json_v2.php/CN_MarketDataService.getKLineData?symbol=%s&scale=%d&ma=no&datalen=%d' % (pre, scale, n))
    txt = _get(url, _SINA)
    if not txt: return None
    try: arr = json.loads(txt)
    except Exception: return None
    out = []
    for r in arr:
        try:
            out.append({'t': str(r.get('day',''))[5:16] if str(r.get('day',''))[11:16] else str(r.get('day',''))[5:11],'dt': str(r.get('day','')),'open':float(r['open']),'close':float(r['close']),'high':float(r['high']),'low':float(r['low']),'vol':float(r.get('volume',0))})
        except Exception: continue
    return out if out else None


def mkline5(symbol, market, n=96):
    pre = prefix_of(market, symbol)
    if not pre: return None
    url = ('https://quotes.sina.cn/cn/api/json_v2.php/CN_MarketDataService.getKLineData?symbol=%s&scale=5&ma=no&datalen=%d' % (pre, n))
    txt = _get(url, _SINA)
    if not txt: return None
    try: arr = json.loads(txt)
    except Exception: return None
    out = []
    for r in arr:
        try:
            out.append({'t': str(r.get('day',''))[11:16],'dt': str(r.get('day','')),'open':float(r['open']),'close':float(r['close']),'high':float(r['high']),'low':float(r['low']),'vol':float(r.get('volume',0))})
        except Exception: continue
    return out if out else None