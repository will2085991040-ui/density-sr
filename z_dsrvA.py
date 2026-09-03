# -*- coding: utf-8 -*-
import sys, threading, os, time
sys.path.insert(0, r'C:/Users/mine/Downloads/quant_research')
import server, aiquant.ensure_data as ED
os.environ['DSRS_DATA_ROOT']=ED.existing_root() or ''
srv=server.Server(0)
threading.Thread(target=srv.httpd.serve_forever,daemon=True).start()
open(r'C:/Users/mine/_dsr_dev_boot.txt','w').write('http://127.0.0.1:%d/' % srv.port)
while True: time.sleep(3600)
