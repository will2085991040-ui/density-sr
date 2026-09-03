# -*- coding: utf-8 -*-
import os, sys, time, subprocess, urllib.request, json
exe = "C:/Users/mine/Downloads/quant_research/dist_v92/dsr_sr.exe"
print("exe bytes:", os.path.getsize(exe))
boot = os.path.expanduser("~/_dsr_sr_boot.txt")
try: os.remove(boot)
except Exception: pass
p = subprocess.Popen([exe], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
url = None
for _ in range(90):
    if os.path.exists(boot):
        try: url = open(boot).read().strip(); break
        except Exception: pass
    time.sleep(1)
print("boot:", url)
if not url:
    print("NO_BOOT"); p.kill(); sys.exit(1)
def get(path):
    try:
        with urllib.request.urlopen(url+path, timeout=15) as r:
            return r.status, r.read()
    except Exception as e:
        return "ERR", repr(e)[:200]
st, idx = get("")
print("index:", st, len(idx), "idx bytes")
st, js = get("sentiment_panel.js")
print("panel js:", st, len(js), "hasSrcBadge:", ("\\u6570\\u636e\\u6e90".encode('latin1') if False else ("\xe6\x95\xb0\xe6\x8d\xae\xe6\xba\x90" in js)))
st, rt = get("api/rt/realtime?symbol=600519&tf=daily")
print("realtime:", st)
try:
    o = json.loads(rt)
    print("  src:", o.get("source"), "bars:", len(o.get("kline") or []), "signal:", (o.get("signal") or {}).get("signal"))
except Exception as e:
    print("  parse err", e, rt[:100])
st, se = get("api/rt/sentiment")
print("sentiment:", st, (json.loads(se).get("label") if st==200 else se[:80]))
p.kill()
