# -*- coding: utf-8 -*-
import sys, threading, time, urllib.request, json
sys.path.insert(0, r"C:/Users/mine/Downloads/quant_research")
import server
sv = server.Server(0)
t = threading.Thread(target=sv.serve_forever, daemon=True); t.start()
base = "http://127.0.0.1:%d/" % sv.port
time.sleep(0.8)
def get(path):
    try:
        with urllib.request.urlopen(base+path, timeout=15) as r:
            return r.status, r.read(400).decode("utf-8","replace")
    except Exception as e:
        return "ERR", repr(e)
print("static index:", get("")[0])
print("js:", get("app.js")[0], "| sentiment_panel:", get("sentiment_panel.js")[0])
print("init:", get("api/init")[0])
st, rt = get("api/rt/realtime?symbol=600519")
print("realtime:", st)
try:
    o = json.loads(rt)
    print("  src", o.get("source"), "bars", len(o.get("kline") or []))
    print("  signal", (o.get("signal") or {}).get("signal"), "sent", (o.get("sentiment") or {}).get("label"))
except Exception as e:
    print("  parse", e, rt[:120])
st2, stj = get("api/rt/sentiment")
print("sentiment:", st2, stj[:90])
sv.shutdown()
