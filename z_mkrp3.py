# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r"C:/Users/mine/Downloads/quant_research")
import server, json
ech  = open(r"C:/Users/mine/Downloads/quant_research/webui/echarts.min.js", encoding="utf-8").read()
cr   = open(r"C:/Users/mine/Downloads/quant_research/webui/chart_realtime.js", encoding="utf-8").read()
def safe(s): return s.replace("<", "u003c") if False else s
run_tpl = """window.__renderRealtime(PAYLOAD);
var ch=window.__rtChart; var opt=ch.getOption();
var S=(opt.series||[]).map(function(s){return s.name+"("+((s.data||[]).length)+")";}).join(" , ");
var c0=((opt.xAxis||[])[0]||{}).data||[];
var el=document.getElementById("R");
el.textContent = "MODE="+MODE+" | SERIES: "+S+" | CATS="+c0.length+" | first="+JSON.stringify(c0.slice(0,3))+" | last="+JSON.stringify(c0.slice(-2));"""
for mode in ("kline","minute"):
    d = server.realtime_json("600519","A股","daily")
    pd = dict(d); pd["mode"]=mode; pd["showM5"]=False; pd["showMacd"]=False
    run = run_tpl.replace("PAY", json.dumps(pd,ensure_ascii=False)).replace("MODE", mode)
    html = ('<!doctype html><body style="margin:0;background:#0a0e14;color:#fff;font:12px monospace">'
            '<div id="kline" style="width:760px;height:520px"></div><pre id="R"></pre>'
            '<script>'+ech+'</script>'
            '<script>'+cr+'</script>'
            '<script>'+run+'</script></body>')
    open(r"C:/Users/mine/Downloads/quant_research/_rp_%s.html" % mode, "w", encoding="utf-8").write(html)
print("ok")
