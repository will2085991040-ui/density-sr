# -*- coding: utf-8 -*-
p = r"C:/Users/mine/Downloads/quant_research/server.py"
t = open(p, encoding="utf-8").read()
old = "        else:\n            d = detail_json(symbol, 'daily', 140, 4, market)"
blk = ("        else:\n"
"            # 主同花顺日K(同花顺); 失败回退本地 detail_json\n"
"            d = None\n"
"            try:\n"
"                from aiquant import realtime_ths\n"
"                _ths = realtime_ths.ths_kline(symbol, market, '01', 140)\n"
"                if _ths:\n"
"                    _hi = max(x['high'] for x in _ths); _lo = min(x['low'] for x in _ths)\n"
"                    _sp = (_hi - _lo) or 1.0\n"
"                    _bt = []\n"
"                    for _lv in (0.618, 0.5, 0.382, 0.236):\n"
"                        _c0 = round(_lo + _sp*_lv, 2)\n"
"                        _bt.append({'zone_type':'support','center':_c0,'lo':round(_c0*0.997,2),'hi':round(_c0*1.003,2),'level':_lv,'width_atr':0.5,'p_touch':0.45,'p_hold':0.5})\n"
"                        _c1 = round(_hi - _sp*_lv, 2)\n"
"                        _bt.append({'zone_type':'resist','center':_c1,'lo':round(_c1*0.997,2),'hi':round(_c1*1.003,2),'level':_lv,'width_atr':0.5,'p_touch':0.45,'p_hold':0.5})\n"
"                    _k = [{'open':x['open'],'close':x['close'],'low':x['low'],'high':x['high'],'volume':x['volume']} for x in _ths]\n"
"                    _dates = [str(x['date'])[-8:] for x in _ths]\n"
"                    _cks = [x['close'] for x in _ths]\n"
"                    d = {'k': _k, 'dates': _dates, 'closes': _cks, 'bands': _bt[:8], 'src': '同花顺'}\n"
"            except Exception:\n"
"                d = None\n"
"            if not d:\n"
"                d = detail_json(symbol, 'daily', 140, 4, market)")
assert old in t, "anchor missing"
t = t.replace(old, blk, 1)
open(p, "w", encoding="utf-8").write(t)
import py_compile
py_compile.compile(p, doraise=True)
print("THS integrated OK")
