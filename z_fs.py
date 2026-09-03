# -*- coding: utf-8 -*-
import urllib.request
BASE="http://127.0.0.1:55105/"
for p in ["index.html","channel_panel.js"]:
    try:
        r=urllib.request.urlopen(BASE+p,timeout=30)
        b=r.read()
        ct=r.headers.get("Content-Type","")
        print(f"{p}: {r.status} bytes={len(b)} ct={ct}")
        if p=="index.html":
            s=b.decode("utf-8","replace")
            print("   has btn-channel:", 'id="btn-channel"' in s, "| has script:", "channel_panel.js" in s)
        if p=="channel_panel.js":
            print("   js head:", b[:60].decode("utf-8","replace").replace("\n"," "))
    except Exception as e:
        print(p, "ERR", str(e)[:100])
