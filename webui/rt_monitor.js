/* DENSITY·SR 实时盯盘 + 多图层实时盘图引擎 */
"use strict";
(function(){
  var $=function(s){return document.querySelector(s);};
  var API="/api";
  function wget(u){return fetch(u).then(function(r){if(!r.ok)throw new Error(u+" "+r.status);return r.json();});}
  var jget=window.jget||wget;
  function fmt(x){return (x===null||x===undefined||isNaN(+x))?"-":(+x).toFixed(2);}
  function esc(s){return String(s==null?"":s).replace(/[&<>]/g,function(c){return ({"&":"&amp;","<":"&lt;",">":"&gt;"})[c];});}
  var rtState={mode:"minute",showM5:false,showMacd:false};
  var lastRt=null, monRunning=false, monTimer=null, monCount=0;
  function setStatus(v){var d=$("#net-dot"),t=$("#net-tag");if(d)d.className=v?"live-dot on":"live-dot";if(t)t.textContent=v?"实时盯盘运行中":"实时盯盘已停止";}
  function setMeta(q,live){var m=$("#rt-meta");if(!m)return;if(!q){m.innerHTML="<span>实时盘不可用 - 使用本地数据(离线)</span>";return;}var c=q.chg_pct||0,cls=c>=0?"up":"down";
    m.innerHTML="<b>"+esc(q.name||"")+" "+(q.code||"")+"</b><span> 现价 <b class=\""+cls+"\">"+fmt(q.price)+"</b> "+(c>=0?"+":"")+c.toFixed(2)+"%</span><span> 开 "+fmt(q.open)+" 高 "+fmt(q.high)+" 低 "+fmt(q.low)+" 昨收 "+fmt(q.preclose)+"</span><span> 量 "+(q.volume!=null?Math.round(q.volume).toLocaleString():"-")+"</span>"+(live?"<span style=\"color:#22c0b0\"> 实时</span>":"<span> 本地</span>");}
  function loadRealtime(){
    var sym=$("#sel-symbol")?$("#sel-symbol").value:""; if(!sym)return;
    var mk=$("#sel-market")?$("#sel-market").value:"A股";
    var tfs=$('#sel-tf')?$('#sel-tf').value:'日线 (D1)';
    var tf = tfs.indexOf('60')>=0?'60':(tfs.indexOf('15')>=0?'15':'daily');
    wget(API+'/rt/realtime?symbol='+encodeURIComponent(sym)+'&market='+encodeURIComponent(mk)+'&tf='+tf).then(function(d){
      if(!d||d.error){var m=$("#rt-meta");if(m)m.innerHTML="<span>实时盘加载失败: "+esc((d&&d.error)||"网络错误")+"</span>";return;}
      lastRt=d; d.mode=rtState.mode; d.showM5=rtState.showM5; d.showMacd=rtState.showMacd;
      if(window.__renderRealtime)window.__renderRealtime(d);
      setMeta(d.quote,d.live);
      var ct=$('#chart-title');if(ct){var tfn=d.tf==='60'?'60分':(d.tf==='15'?'15分':'日线');ct.textContent='价格走势 · 支撑/阻力叠加 · '+tfn+' · '+(d.live?'实时':'本地');}
      var p=$("#d-price");if(p&&d.quote)p.textContent=fmt(d.quote.price);
      var cg=$("#d-chg");if(cg&&d.quote){var cc=d.quote.chg_pct||0;cg.textContent=(cc>=0?"+":"")+cc.toFixed(2)+"%";cg.className=cc>=0?"up":"down";}
    },function(){var m=$("#rt-meta");if(m)m.innerHTML="<span>实时盘加载失败(网络)</span>";});
  }
  function setMode(mode){
    rtState.mode=mode;
    var a=$("#mode-min"),b=$("#mode-k"),md=$("#mode-macd");
    if(a)a.className="ct-btn "+(mode==="minute"?"on":"");
    if(b)b.className="ct-btn "+(mode==="kline"?"on":"");
    if(md)md.className="ct-btn "+(rtState.showMacd?"on":"")+" ct-tiny";
    if(lastRt){lastRt.mode=mode;lastRt.showM5=rtState.showM5;lastRt.showMacd=rtState.showMacd;if(window.__renderRealtime)window.__renderRealtime(lastRt);}
  }
  function monitorTick(){
    var sym=$("#sel-symbol")?$("#sel-symbol").value:""; if(!sym){if(monRunning){monRunning=false;setStatus(false);}return;}
    var mk=$("#sel-market")?$("#sel-market").value:"A股";
    loadRealtime();
    return;
  }
  var recBtn=$("#btn-rec");
  if(recBtn)recBtn.addEventListener("click",function(){
    monRunning=!monRunning;setStatus(monRunning);
    var sym=$("#sel-symbol")?$("#sel-symbol").value:"";
    recBtn.innerHTML=monRunning?"● 实时盯盘中…":"阿尔法量化价格行为";recBtn.classList.toggle("rec-on",monRunning);
    if(monRunning){monCount=0;if(!sym){var m=$("#ai-result");if(m)m.innerHTML='<div style="padding:6px 10px;background:rgba(240,192,75,.12);border:1px solid #f0c04b;border-radius:6px;font-size:12px;color:#f0c04b">实时盯盘: 请先选 SYMBOL/标的</div>';return;}monitorTick();if(!monTimer)monTimer=setInterval(monitorTick,15000);}
    else{if(monTimer){clearInterval(monTimer);monTimer=null;}}
  });
  var mA=$("#mode-min"),mB=$("#mode-k"),mM=$("#mode-macd"),mR=$("#btn-rt-load");
  if(mA)mA.addEventListener("click",function(){setMode("minute");});
  if(mB)mB.addEventListener("click",function(){setMode("kline");});
  if(mM)mM.addEventListener("click",function(){rtState.showMacd=!rtState.showMacd;setMode(rtState.mode);});
  if(mR)mR.addEventListener("click",function(){loadRealtime();});
  var ss=$("#sel-symbol");if(ss)ss.addEventListener("change",function(){loadRealtime();});
  var stf=$("#sel-tf");if(stf)stf.addEventListener("change",function(){setMode("kline");loadRealtime();});
  var smk=$("#sel-market");if(smk)smk.addEventListener("change",function(){loadRealtime();});
})();