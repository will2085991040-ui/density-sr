# -*- coding: utf-8 -*-
import sys; sys.path.insert(0, r"C:/Users/mine/Downloads/quant_research")
import server, time, urllib.request
srv = server.Server(0).start()
url = srv.url()
print("url:", url)
with urllib.request.urlopen(url+"api/rt/sentiment", timeout=15) as r:
    print("sentiment status:", r.status, r.read(60).decode("utf-8","replace"))
srv.stop()
print("static check:")
