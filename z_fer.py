# -*- coding: utf-8 -*-
import os, sys, time, subprocess, urllib.request, urllib.parse, json
exe=r"C:/Users/mine/Downloads/quant_research/dist_v92/dsr_sr.exe"
boot=os.path.expanduser("~/_dsr_sr_boot.txt")
try: os.remove(boot)
except Exception: pass
p=subprocess.Popen([exe], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
url=None
for _ in range(150):
    if os.path.exists(boot):
        try: url=open(boot).read().strip(); break
        except Exception: pass
    if p.poll() is not None:
        print("EXE_EXITED", p.returncode); break
    time.sleep(1)
print("boot:", url)
if not url:
    p.kill(); sys.exit(1)
mk=urllib.parse.quote("A股")
def get(path):
    try:
        r=urllib.request.urlopen(url+path, timeout=90); return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()
    except Exception as e:
        return "ERR", str(e)[:160].encode()
checks=[("index",""),("app.js","app.js"),("rt_monitor","rt_monitor.js"),
 ("sentiment_panel","sentiment_panel.js"),("chart_interactive","chart_interactive.js"),
 ("detail","api/detail?symbol=600519&n=120&levels=4&market="+mk),
 ("realtime","api/rt/realtime?symbol=600519&tf=daily&market="+mk),
 ("sentiment","api/rt/sentiment"),
 ("init","api/init?market="+mk),
 ("scan","api/scan?limit=260"),
 ("live","api/live/quotes?symbols=600519%2C000001"),
 ("ai","api/ai/analyze?symbol=600519&n=120"),
 ("factor","api/factor/mine?limit=8"),
 ("pa","api/pa/llm?symbol=600519&stance=6.16"),
 ("export_csv","api/export?type=csv"),
 ("export_html","api/export?type=html")]
allok=True
for name,path in checks:
    st,b=get(path)
    ok=st==200
    if not ok: allok=False
    print(("PASS" if ok else "FAIL"), name, st, (str(len(b)) if ok else b.decode('utf-8','replace')[:120]))
print("ALL_PASS" if allok else "SOME_FAIL")
p.kill()
