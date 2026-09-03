# -*- coding: utf-8 -*-
import sys, os, threading, time, urllib.request, json
sys.path.insert(0, r"C:\Users\mine\Downloads\quant_research")
import server
srv = server.Server(port=0).start()
u = srv.url()
def hit(tag):
    try:
        with urllib.request.urlopen(u+"api/init", timeout=12) as r:
            d=json.loads(r.read().decode())
            open(r"C:\Users\mine\Downloads\quant_research\probe.txt","a",encoding="utf-8").write(tag+" OK n="+str(d.get("n"))+"\n")
    except Exception as e:
        open(r"C:\Users\mine\Downloads\quant_research\probe.txt","a",encoding="utf-8").write(tag+" ERR "+str(e)+"\n")
threading.Thread(target=lambda: hit("BEFORE"), daemon=True).start()
time.sleep(3)
def after():
    time.sleep(4)
    hit("AFTER")
    os._exit(0)
threading.Thread(target=after, daemon=True).start()
import webview
open(r"C:\Users\mine\Downloads\quant_research\probe.txt","a").write("PORT "+str(srv.port)+"\n")
webview.create_window("t", u, width=500, height=350)
webview.start()