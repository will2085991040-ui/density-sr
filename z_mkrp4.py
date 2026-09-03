# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r"C:/Users/mine/Downloads/quant_research")
import server, json
ech  = open(r"C:/Users/mine/Downloads/quant_research/webui/echarts.min.js", encoding="utf-8").read()
cr   = open(r"C:/Users/mine/Downloads/quant_research/webui/chart_realtime.js", encoding="utf-8").read()
run_tpl = """try{ window.__renderRealtime(PAYL); var ch=window.__rtChart;
if(!ch){document.getElementById('R').textContent='NO__rtChart typeof render=',typeof window.__renderRealtime; }
var opt=ch.getOption();
var S=(opt.series||[]).map(function(s){return s.name+'('+((s.data||[]).length)+')';}).join(' , ');
var c0=((opt.xAxis||[])[0]||{}).data||[];
document.getElementById('R').textContent = 'MODE='+wd+' | SERIES: '+S+' | CATS='+c0.length+' | first='+JSON.stringify(c0.slice(0,3))+' | last='+JSON.stringify(c0.slice(-2)); }
catch(e){document.getElementById('R').textContent='ERR '+e.message+' '+e.stack; document.getElementById('R').textContent= document.getElementById('R').textContent.slice(0,500);}"""
run = run_t.replace("PAYR", json.dumps(dict(server.realtime_json("600519","A股","daily"), mode="kline", showM5=False, showMacd=False), ensure_ascii=False)).replace("wd=","render")
for mode in ("kline","minute"):
    pd = server.realtime_json("600519","A股","daily"); pd["mode"]=mode; pd["showM5"]=False; pd["showMacd"]=False
    run = ("try{window.__renderRealtime("+json.dumps(pd,ensure_ascii=False)+");var ch=window.__rtChart;"
           "var opt=ch.getOption();var S=(opt.series||[]).map(function(s){return s.name+'( '+((s.data||[]).length)+')';}).join(' , ');"
           "var c0=((opt.xAxis||[])[0]||{}).data||[];"
           "document.getElementById('R').textContent='MODE="+mode+" SERIES='+S+' CATS='+c0.length+' first='+JSON.stringify(c0.slice(0,3))+' last='+JSON.stringify(c0.slice(-2));"
           "}catch(e){document.getElementById('R').textContent='ERR '+e.message+' / t='+typeof window.__renderRealtime;}")
    html = ('<!doctype html><body style="margin:0;background:#0a0e14;color:#fff;font:12px monospace">'
            '<div id="kline" style="width:760px;height:520px"></div><pre id="R"></pre>'
            '<script>'+ech+'</script><script>'+cr+'</script><script>'+run+'</script></body>')
    open(r"C:/Users/mine/Downloads/quant_research/_rp_%s.html" % mode, "w", encoding="utf-8").write(html)
print("ok")
