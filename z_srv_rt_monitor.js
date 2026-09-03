/* DENSITY-SR · 实时盯盘 + 全按钮功能补强 */
"use strict";
(function(){
  var $=function(s){return document.querySelector(s);};
  var API='/api';
  var jget=window.jget||wget; function wget(u){return fetch(u).then(function(r){if(!r.ok)throw new Error(u+' '+r.status);return r.json();});}
  function fmt(x){ return (x===null||x===undefined) ? '—' : (+x).toFixed(2); }
  function esc(s){ return String(s==null?'':s).replace(/[&<>]/g,function(c){return({'&':'&amp;','<':'&lt;','>':'&gt;'})[c];}); }
  var renderChart=window.renderChart;
  var monTimer=null, monRunning=false, monCount=0, monLastSym=null;

  function setStatus(v){ var d=$('#net-dot'),t=$('#net-tag'); if(d)d.className=v?'live-dot on':'live-dot'; if(t)t.textContent=v?'实时盯盘运行中':'实时盯盘已停止'; }

  function runLive(sym,mk){
    var box=$('#pa-body'); if(!box) return;
    var dir=$('#sel-dir')?$('#sel-dir').value:'只做多';
    var stances=(dir==='只做空')?['6.24']:((dir==='双向')?['6.16','6.24']:['6.16']);
    box.innerHTML='<span class="muted">实时盯盘 AI 研判中… '+esc(sym)+'</span>';
    stances.forEach(function(st){
      jget(API+'/rt/pa?symbol='+encodeURIComponent(sym)+'&market='+encodeURIComponent(mk)+'&stance='+st+'&n=160').then(function(r){
        if(!r||r.error) return;
        var dirr=r.direction, cls=(dirr==='多')?'up':((dirr==='空')?'down':'flat');
        var card=document.createElement('div'); card.className='pa-card';
        var h='<div class="pa-card-head"><b>'+esc(r.label||st)+'</b><span class="live-dot on"></span><em>'+(r.live?'实时':'本地')+'</em></div>';
        h+='<div class="pa-decision '+cls+'">方向 <b>'+esc(dirr||'-')+'</b> · 动作 '+esc(r.action||'-')+'</div>';
        h+='<table class="pa-kv"><tbody><tr><td>入场</td><td>'+fmt(r.entry)+'</td><td>止损</td><td>'+fmt(r.stop)+'</td></tr>';
        h+='<tr><td>目标</td><td>'+fmt(r.target)+'</td><td>风比</td><td>'+(r.rr!=null?r.rr.toFixed(2):'-')+'</td></tr></tbody></table>';
        h+='<div class="muted">'+esc(r.reason||'')+'</div>';
        if(r.llm_err) h+='<div class="llm-err">AI错误: '+esc(r.llm_err)+'</div>';
        card.innerHTML=h; box.appendChild(card);
      },function(){});
    });
  }

  function monitorTick(){
    var sym=$('#sel-symbol')?$('#sel-symbol').value:''; if(!sym){ if(monRunning){monRunning=false; setStatus(false);} return; }
    var mk=$('#sel-market')?$('#sel-market').value:'A股';
    jget('/api/live/quotes?symbols='+encodeURIComponent(sym)).then(function(q){
      var lv=q&&q[sym]; if(lv&&$('#d-price')){ $('#d-price').textContent=fmt(lv.price); var c=lv.chg_pct||0; $('#d-chg').textContent=(c>=0?'+':'')+c.toFixed(2)+'%'; $('#d-chg').className=c>=0?'up':'down'; }
    },function(){});
    monCount=(monCount||0)+1;
    if(monLastSym!==sym||(monCount%3)===0){
      monLastSym=sym;
      jget('/api/live/kline?symbol='+encodeURIComponent(sym)+'&n=120').then(function(d){ if(d&&d.k&&renderChart) renderChart({dates:d.dates||[],k:d.k||[],closes:d.closes||[],bands:[]}); },function(){});
      runLive(sym,mk);
    }
  }

  var recBtn=$('#btn-rec');
  if(recBtn) recBtn.addEventListener('click',function(){
    monRunning=!monRunning; setStatus(monRunning);
    recBtn.textContent=monRunning?'● 实时盯盘中…':'阿尔法量化价格行为'; recBtn.classList.toggle('rec-on',monRunning);
    if(monRunning){ monCount=0; monLastSym=null; monitorTick(); if(!monTimer) monTimer=setInterval(monitorTick,15000); }
    else if(monTimer){ clearInterval(monTimer); monTimer=null; }
  });

  var dr=$('#sel-dir'); if(dr) dr.addEventListener('change',function(){ var sym=$('#sel-symbol')?$('#sel-symbol').value:''; if(sym) runLive(sym,$('#sel-market').value); });

  var rf=$('#btn-refresh'); if(rf) rf.addEventListener('click',function(){
    var sym=$('#sel-symbol')?$('#sel-symbol').value:''; if(!sym) return;
    var info=$('#ai-result'); if(info) info.innerHTML='<span class="muted">刷新实时数据…</span>';
    jget('/api/live/quotes?symbols='+encodeURIComponent(sym)).then(function(q){
      var lv=q&&q[sym]; if(lv&&info) info.innerHTML='<span class="muted">已获取最新实时报价 '+esc(lv.name||sym)+' '+fmt(lv.price)+' ('+(lv.chg_pct>=0?'+':'')+lv.chg_pct.toFixed(2)+'%)</span>';
      var s=$('#sel-symbol'); if(s) s.dispatchEvent(new Event('change'));
    },function(){ if(info) info.innerHTML='<span class="muted">实时获取失败,已回退本地数据</span>'; });
  });
})();
