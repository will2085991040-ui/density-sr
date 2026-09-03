# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r"C:/Users/mine/Downloads/quant_research")
import server, json
ech  = open(r"C:/Users/mine/Downloads/quant_research/webui/echarts.min.js", encoding="utf-8").read()
cr   = open(r"C:/Users/mine/Downloads/quant_research/webui/chart_realtime.js", encoding="utf-8").read()
def ejs(s): return s.replace("</script>", "<\\/script>")
report_js = '''
var ch = window.__rtChart; var opt = ch.getOption();
var series = (opt.series||[]).map(function(s){return s.name+"("+((s.data||[]).length)+")";});
var c0 = ((opt.xAxis||[])[0]||{}).data||[];
window.__REPORT = JSON.stringify({series:series, cats:c0.length, first:c0.slice(0,2), last:c0.slice(-1)});
document.title = window.__REPORT; document.body.setAttribute("data-r", window.__REPORT);
'''
for mode in ("kline","minute"):
    d = server.realtime_json("600519","A股","daily")
    pd = dict(d); pd["mode"]=mode; pd["showM5"]=False; pd["showMacd"]=False
    html = ('<!doctype html><body style="margin:0"><div id="kline" style="width:760px;height:520px"></div>'
            '<script>' + ejs(ech) + '</script><script>' + ejs(cr) + '</script>'
            '<script>window.__renderRealtime(' + json.dumps(pd, ensure_ascii=False) + ');'
            'setTimeout(function(){' + report_js + '},800);</script></body>')
    open(r"C:/Users/mine/Downloads/quant_research/_rp_%s.html" % mode, "w", encoding="utf-8").write(html)
print("ok")
