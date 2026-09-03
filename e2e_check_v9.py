# -*- coding: utf-8 -*-
"""V9 冻结 EXE 端到端校验:
1. 等待 ~/_dsr_sr_boot.txt 出现并读到 URL
2. 检查 /sentiment_panel.js /index.html 等静态资源 200
3. 检查 /api/rt/sentiment 返回情绪JSON
4. 检查 /api/rt/realtime?symbol=600519 返回 signal + sentiment
"""
import os, time, sys, json
try:
    import requests
except Exception:
    sys.exit("no requests")
host = os.path.join(os.path.expanduser("~"), "_dsr_sr_boot.txt")
url = None
for _ in range(90):
    if os.path.exists(host):
        try:
            u = open(host).read().strip()
            if u: url = u; break
        except Exception: pass
    time.sleep(1)
if not url:
    print("E2E_FAIL no_boot_file"); sys.exit(1)
url = url.rstrip("/")
print("URL", url)
def get(p):
    try:
        r = requests.get(url + "/" + p, timeout=20)
        return r.status_code, r.text[:60]
    except Exception as e:
        return "ERR", repr(e)
for p in ("sentiment_panel.js","index.html","styles.css","app.js"):
    code, txt = get(p)
    print("GET", p, code, txt[:40])
c, s = get("api/rt/sentiment")
print("SENTIMENT", c, s)
try:
    j = requests.get(url + "/api/rt/realtime?symbol=600519&tf=daily", timeout=30).json()
    print("REALTIME signal:", j.get("signal", {}).get("signal") if isinstance(j.get("signal"), dict) else j.get("signal"))
    print("REALTIME sentiment:", j.get("sentiment"))
    print("REALTIME bands:", len(j.get("bands") or []))
except Exception as e:
    print("REALTIME ERR", repr(e))
print("E2E_DONE")
