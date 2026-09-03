# -*- coding: utf-8 -*-
import sys, os, threading
sys.path.insert(0, r"C:\Users\mine\Downloads\quant_research")
import server
srv = server.Server(port=8720).start()
import webview
def closer():
    import time; time.sleep(6)
    open(r"C:\Users\mine\Downloads\quant_research\wv_ok.txt","w").write("loaded 6s ok")
    try: os._exit(0)
    except Exception: pass
threading.Thread(target=closer, daemon=True).start()
webview.create_window("DENSITY-SR", srv.url(), width=1500, height=860)
webview.start()