# -*- coding: utf-8 -*-
import urllib.request, json
def try_fs(fs, pn=1, pz=200):
    u = ("http://push2.eastmoney.com/api/qt/clist/get?pn=%d&pz=%d&po=1&np=1"
         "&fltt=2&invt=2&fid=f12&fs=%s") % (pn, pz, fs)
    try:
        d = json.load(urllib.request.urlopen(u, timeout=25))
        diff = (d.get("data") or {}).get("diff") or []
        return len(diff)
    except Exception as e:
        return "ERR " + str(e)[:60]

filters = [
  "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23",
  "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23,m:0+t:81+s:2048",
  "m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23,m:0+t:81+s:2048,m:0+t:81+s:2048",
]
for f in filters:
    print("rows:", try_fs(f), "| fs=", f)
