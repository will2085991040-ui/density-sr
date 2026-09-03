# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r"C:/Users/mine/Downloads/quant_research")
import server, json
d = server.realtime_json("600519", "A股", "daily")
ech  = open(r"C:/Users/mine/Downloads/quant_research/webui/echarts.min.js", encoding="utf-8").read()
cr   = open(r"C:/Users/mine/Downloads/quant_research/webui/chart_realtime.js", encoding="utf-8").read()
payload = json.dumps(d, ensure_ascii=False)
for mode in ("kline","minute"):
    pd = dict(d); pd["mode"]=mode; pd["showM5"]=False; pd["showMacd"]=False
    html = ('<!doctype html><html><head><meta charset="utf-8"><style>html,body{margin:0}'
            '#kline{width:760px;height:520px;background:#0a0e14}</style></head><body>'
            '<div id="kline"></div>'
            '<script>' + ech.replace("</script>","<\\/script>") + '</script>'
            '<script>' + cr.replace("</script>","<\\/script>") + '</script>'
            '<script>var __PAYLOAD=' + json.dumps(pd, ensure_ascii=False) + ';'
            '__renderRealtime(__PAYLOAD);'
            'setTimeout(function(){document.body.setAttribute("data-done","1");},800);'
            '</script></body></html>')
    open(r"C:/Users/mine/Downloads/quant_research/_har_%s.html" % mode, "w", encoding="utf-8").write(html)
print("harness html written")
