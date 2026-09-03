# -*- coding: utf-8 -*-
import sys, threading, time, urllib.request, urllib.parse, json
sys.path.insert(0, r"C:/Users/mine/Downloads/quant_research")
import server
sv = server.Server(0).start(); base=sv.url(); time.sleep(0.8)
mk = urllib.parse.quote("A股")
def get(path):
    try:
        r = urllib.request.urlopen(base+path, timeout=60); return r.status, r.read()
    except Exception as e: return "ERR", str(e)[:160]
checks=[
 ("静态 index",""),("app.js","app.js"),("rt_monitor.js","rt_monitor.js"),
 ("sentiment_panel","sentiment_panel.js"),("chart_interactive","chart_interactive.js"),
 ("图表引擎实盘","/api/rt/realtime?symbol=600519&tf=daily&market="+mk),
 ("情绪","api/rt/sentiment"),
 ("品种-TABLE","api/init?market="+mk),
 ("README分析","api/detail?symbol=600519&n=120&levels=4&market="+mk),
 ("扫描","api/scan?limit=260"),
 ("实时","api/live/quotes?symbols=600519%2C000001"),
 ("AI","api/ai/analyze?symbol=600519&n=120"),
 ("因子","api/factor/mine?limit=8"),
 ("PA","api/pa/llm?symbol=600519&tf=日线%20(D1)&stance=6.16"),
 ("导出CSV","api/export?type=csv"),
 ("导出HTML","api/export?type=html"),
]
allok=True
for name,p in checks:
    st,b=get(p)
    ok = st==200
    if not ok: allok=False
    print(("PASS" if ok else "FAIL"), name, st, (str(len(b)) if ok else b))
print("ALL_PASS" if allok else "SOME_FAIL")
sv.stop()
