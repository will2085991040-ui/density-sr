# -*- coding: utf-8 -*-
import sys, time, json, urllib.request
sys.path.insert(0, r"C:\Users\mine\Downloads\quant_research")
import server
srv = server.Server(port=8716).start()
url = srv.url()
def get(u):
    with urllib.request.urlopen(url+u, timeout=20) as r:
        return r.read()
res = []
html = get("index.html")
res.append("index:"+str(len(html))+" bytes")
init_ = get("api/init")
init_ = json.loads(init_); res.append("init n="+str(init_["n"]))
det = get("api/detail?symbol=000001&n=90&levels=4"); det=json.loads(det)
res.append("detail cur="+str(det.get("current_price"))+" k="+str(len(det.get("k",[])))+" bands="+str(len(det.get("bands",[]))))
sc = get("api/scan?limit=20"); sc=json.loads(sc)
res.append("scan rows="+str(len(sc.get("rows",[]))))
open(r"C:\Users\mine\Downloads\quant_research\srv_test.txt","w",encoding="utf-8").write("\n".join(res))
srv.stop()
import os; os._exit(0)