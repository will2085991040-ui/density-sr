/* DENSITY·SR 下跌宽通道 AI 分析面板 */
"use strict";
(function(){
  var API="/api";
  function wget(u){return fetch(u).then(function(r){if(!r.ok)throw new Error(u+" "+r.status);return r.json();});}
  var g$=function(s){return document.querySelector(s);};
  function esc(s){return String(s==null?"":s).replace(/[&<>]/g,function(c){return({"&":"&amp;","<":"&lt;",">":"&gt;"})[c];});}
  function fmt(x){return (x===null||x===undefined||isNaN(+x))?"-":(+x).toFixed(2);}
  var lastR=null;
  function render(){
    var el=document.getElementById("ch-body"); if(!el)return;
    if(!lastR){el.innerHTML='<span class="muted">选择品种后点击「下跌宽通道分析」。</span>';return;}
    var r=lastR;
    var dirTxt=r.direction==="down"?"下降通道":(r.direction==="up"?"上升通道":"横盘通道");
    var badge=(r.direction==="down"&&r.is_wide)?
       '<span class="chip" style="background:rgba(234,57,67,.16);color:#ea3943;border:1px solid #ea3943">下跌宽通道</span>'
      :'<span class="chip" style="background:rgba(139,148,158,.14);color:#8b949e;border:1px solid #2a3441">'+esc(dirTxt)+'</span>';
    var dirTxt2=r.direction;
    el.innerHTML='<div class="agent"><div class="atop"><div><div class="aname">下跌宽通道分析 · '+esc(r.symbol||"")+'</div>'
      +'<div class="atone">'+badge+' 现价 <b>'+fmt(r.price)+'</b> · 宽度 '+(r.width_pct!=null?r.width_pct.toFixed(1)+'%':'–')
      +' · 斜率 '+fmt(r.slope)+' · 通道内位置 '+fmt(r.position_pct)+'%</div></div>'
      +'<span class="abat '+(r.direction==="down"?"dn":(r.direction==="up"?"up":""))+'">'+esc(r.direction==="down"?"空头区间":(r.direction==="up"?"多头区间":"震荡"))+'</span></div>'
      +'<div class="aact">'+esc(r.read_note||"")+'</div>'
      +'<div class="lns">'
      +'<div class="ln">上轨 <b>'+fmt(r.upper)+'</b></div>'
      +'<div class="ln">下轨 <b>'+fmt(r.lower)+'</b></div>'
      +'<div class="ln">中轨 <b>'+fmt(r.mid)+'</b></div>'
      +'<div class="ln">ATR <b>'+fmt(r.atr)+'</b>('+(r.atr_pct!=null?r.atr_pct.toFixed(1):'–')+'%) · 宽 x'+fmt(r.width_atr_mult)+'ATR · R² '+fmt(r.r2)+'</div></div>'
      +'<div class="anote">AI解读: '+esc(r.read_note||'')+'</div></div>';
  }
  async function runChannel(){
    var symEl=document.getElementById("sel-symbol"); var sym=symEl?symEl.value:"";
    var mk=window.currentMarket||"A股";
    var body=document.getElementById("ch-body"); if(body)body.innerHTML='<span class="muted">分析下跌宽通道…</span>';
    try{
      lastR=await wget("/api/channel?symbol="+encodeURIComponent(sym)+"&market="+encodeURIComponent(mk));
      render();
    }catch(e){ if(body)body.innerHTML='<span class="muted">通道分析失败:'+esc(e.message)+'</span>'; }
  }
  // 若按钮已存在则直接绑定; 否则由 index 静态结构承载
  function bind(){
    var b=document.getElementById("btn-channel");
    if(b){ b.removeEventListener("click",window.__oldCh||function(){}); b.addEventListener("click",runChannel); }
  }
  if(window.addEventListener){ try{ bind(); }catch(e){} }
  if(document.readyState==="complete"||document.readyState==="interactive"){ setTimeout(bind,0);}
})();
