# -*- coding: utf-8 -*-
import requests, json
h={'User-Agent':'Mozilla/5.0','Referer':'http://www.10jqka.com.cn/','Host':'d.10jqka.com.cn'}
r=requests.get('http://d.10jqka.com.cn/v6/line/hs_600519/01/last.js',headers=h,timeout=8)
txt=r.text
i=txt.find('{'); j=txt.rfind('}')
obj=None
try:
    obj=json.loads(txt[i:j+1])
except Exception as e:
    print("parse err", e)
    # try removing trailing ;xxx
    for cut in (2,3,5,8):
        try:
            obj=json.loads(txt[i:j+1-cut]); break
        except Exception: continue
if obj:
    print("keys:", list(obj.keys()))
    d=obj.get('data')
    print("data type:", type(d).__name__, "len:", len(d) if isinstance(d,(list,str)) else '-')
    if isinstance(d,str): print("data head:", repr(d[:80]))
    print("info:", (obj.get('info') or '')[:120])
    # 尝试找 '7' (close) / '1' (open) 等
    if isinstance(d, dict):
        print("data dict keys:", list(d.keys()))
