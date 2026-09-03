
/* DENSITY-SR · 市场情绪 + 策略信号 + 使用说明 面板 */
"use strict";
(function(){
  function $(s){ return document.querySelector(s); }
  function esc(s){ return String(s==null?"":s).replace(/[&<>]/g,function(c){return ({"&":"&amp;","<":"&lt;",">":"&gt;"})[c];}); }
  function fmt(x,n){ n=n||2; return (x===null||x===undefined||isNaN(+x))?"–":(+x).toFixed(n); }
  function tempColor(s){ return s>=75?"#ea3943":(s>=52?"#ff9e3d":(s>=40?"#f0c04b":(s>=26?"#7bd88f":"#3ecf8e"))); }
  function currentTf(){
    var tfs=$('#sel-tf'), v=tfs?tfs.value:'日线 (D1)';
    return (v.indexOf('60')>=0)?'60':((v.indexOf('15')>=0)?'15':'daily');
  }
  function renderSentiment(se){
    var body=$('#sent-body'); if(!body) return;
    if(!se||se.error){ body.innerHTML='<span class="muted">情绪数据暂不可用</span>'; return; }
    var sc=+se.score||0, col=tempColor(sc), br=se.breadth||{};
    var ra=br.total?Math.round((br.ratio||0)*100)+"%":"–";
    var h='<div style="display:flex;align-items:center;gap:12px;padding:8px 0 2px">';
    h+='<div style="min-width:62px;font-size:30px;font-weight:700;line-height:1;color:'+col+'">'+sc+'<span style="font-size:12px">°</span></div>';
    h+='<div style="flex:1"><div style="font-size:14px;font-weight:600;color:'+col+'">'+esc(se.label||"")+'</div>';
    h+='<div class="hband" style="background:#1c2431;border-radius:4px;height:8px;margin-top:4px"><div style="width:'+Math.max(4,Math.min(100,sc))+'%;height:8px;border-radius:4px;background:'+col+'"></div></div></div></div>';
    h+='<table class="sent-kv"><tbody>';
    if(se.indices){
      var sy=se.indices.sh, cyb=se.indices.cyb;
      h+='<tr><td>上证指数</td><td>'+(sy==null?"–":(sy>=0?'+':'')+fmt(sy)+"%")+'</td><td>创业板</td><td>'+(cyb==null?"–":(cyb>=0?'+':'')+fmt(cyb)+"%")+'</td></tr>';
    }
    h+='<tr><td>上涨家数</td><td>'+(br.up||0)+'</td><td>下跌家数</td><td>'+(br.down||0)+'</td></tr>';
    h+='<tr><td>涨跌比</td><td>'+ratio+'</td><td>涨停家数</td><td>'+(se.zt_count==null?"–":se.zt_count)+'</td></tr>';
    h+='<tr><td>最高连板</td><td>'+(se.max_lb?se.max_lb+"板":"–")+'</td><td>数据源</td><td>'+(se.source==="realtime"?"实时":"本地")+'</td></tr>';
    h+='</tbody></table>';
    h+='<div class="muted small" style="color:'+col+';padding-top:4px">'+esc(se.suggest||"")+'</div>';
    if(se.reasons&&se.reasons.length) h+='<div class="muted small">'+se.reasons.map(esc).join(' · ')+'</div>';
    body.innerHTML=h;
    var src=$('#sent-src'); if(src) src.textContent=(se.source==="realtime"?"· 实时":"· 离线");
  }
  var __sigSrc='';
  function renderSignal(sig){
    var body=$('#sig-body'); if(!body) return;
    if(!sig||sig.reason==="数据不足"){ body.innerHTML='<span class="muted">该品种尚无触发信号(等触位 / 数据不足)</span>'; return; }
    var cls=sig.direction==="多"?"up":(sig.direction==="空"?"down":"flat");
    var _s=esc(__sigSrc||'');
    var h='<div class="sig-top"><span class="sig-tag '+cls+'">'+esc(sig.signal||sig.direction||"-")+'</span><span class="muted small" style="margin-left:8px">'+(__sigSrc?'数据源 '+_s+'':'')+'</span><span class="muted small">'+(sig.rr?'风比 1:'+fmt(sig.rr,2):'')+'</span></div>';
    h+='<table class="sent-kv"><tbody>';
    h+='<tr><td>方向</td><td>'+esc(sig.direction||"-")+'</td><td>触发位 撑/压</td><td>'+fmt(sig.sup)+' / '+fmt(sig.res)+'</td></tr>';
    h+='<tr><td>入场</td><td>'+fmt(sig.entry)+'</td><td>止损</td><td>'+fmt(sig.stop)+'</td></tr>';
    h+='<tr><td>目标</td><td>'+fmt(sig.target)+'</td><td>情绪分</td><td>'+fmt(sig.s_score,1)+'</td></tr>';
    h+='</tbody></table>';
    h+='<div class="muted small">'+esc(sig.reason||"")+'</div>';
    body.innerHTML=h;
  }
  function loadSentiment(){
    fetch('/api/rt/sentiment').then(function(r){return r.json();}).then(renderSentiment).catch(function(){renderSentiment(null);});
  }
  function loadSignalInner(){
    var im=$('#sel-symbol'), sym=im?im.value:''; if(!sym) return;
    var sel=$('#sel-market'), mk=sel?sel.value:'A股';
    fetch('/api/rt/realtime?symbol='+encodeURIComponent(sym)+'&market='+encodeURIComponent(mk)+'&tf='+currentTf())
      .then(function(r){return r.json();}).then(function(d){ __sigSrc=d.source||''; renderSignal(d.signal); })
      .catch(function(){ renderSignal(null); });
  }
  window.__refreshSentimentPanel=function(){ if(window.__renderSentiment) {} loadSentiment(); loadSignalInner(); };
  window.__renderSentiment=renderSentiment;
  window.__renderSignal=renderSignal;
  var sb=$('#btn-sig-refresh'); if(sb) sb.onclick=loadSignalInner;
  var sb2=$('#btn-rt-load'); if(sb2) sb2.addEventListener('click',loadSignalInner);
  // 使用说明浮层
  var HELP=[], BT='<div style="width:min(680px,92vw);position:fixed;top:6%;left:50%;transform:translateX(-50%);background:#12161f;border:1px solid #2b3546;border-radius:10px;z-index:9999;padding:16px 22px;color:#d7dee8;box-shadow:0 12px 40px #000">';
  var hb=$('#btn-help');
  if(hb) hb.onclick=function(){
    if(document.getElementById('dshelp')) return;
    var box=document.createElement('div'); box.id='dshelp'; box.style.cssText='position:fixed;inset:0;background:rgba(0,0,0,.6);z-index:9998;display:flex;align-items:center;justify-content:center;';
    var card=document.createElement('div'); card.style.cssText='width:min(700px,90vw);max-height:80vh;overflow:auto;background:#12161f;border:1px solid #2b3546;border-radius:12px;padding:18px 24px;color:#d7dee8;box-shadow:0 14px 50px #000';
    card.innerHTML='<div style="display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #2b3546;padding-bottom:8px;margin-bottom:12px"><b style="color:#f0c04b;font-size:16px">DENSITY·SR 使用说明 · 量化交易指南</b><button class="btn mini" id="htc">关闭</button></div>'+
      '<h3 style="margin:8px 0 4px">一、图表怎么读</h3><ul>'+
      '<li>分时：白线=现价、黄线=当日均价、灰虚线=昨收；红虚线=涨停、绿虚线=跌停。</li>'+
      '<li>K线：红涨绿跌；MA5黄橙 / MA10黄 / MA20蓝 / MA60绿。</li>'+
      '<li>绿色虚线=支撑位(易企稳)，紫红虚线=压力位(易受阻)；悬停查看区间。</li>'+
      '<li>MACD(黄DIF/蓝DEA)：金叉偏多、死叉偏空；灰色点线=昨收/开/高/低/现价。</li>'+
      '<li>顶部按钮切换 分时 / K线 / MACD / 刷新实时盘。</li></ul>'+
      '<h3 style="margin:8px 0 4px">二、怎么用它做量化择时</h3><ul>'+
      '<li>左上选 品种 ＋ 周期(日线/60分/15分)→ 图表+策略信号自动刷新。</li>'+
      '<li><b>策略信号卡</b>：只在该品种触及支撑/压力、且形态与情绪允许时，给 方向·入场·止损·目标·盈亏比·情绪分。</li>'+
      '<li><b>市场情绪卡</b>(0-100°)：冰点/偏空/中性/偏多/亢奋，指导仓位与攻守；情绪冰点自动过滤追多。</li>'+
      '<li>点"阿尔法量化价格行为"开启 <b>实时盯盘</b>：每15秒刷新行情/分时/K线/信号。</li></ul>'+
      '<h3 style="margin:8px 0 4px">三、风险提示</h3><p class="muted" style="margin:0">程序输出为量化参考，不构成买卖承诺；突发事件、主力洗盘可能击穿止损。务必预先设好止损并控制单笔风险。</p>';
    card.addEventListener('click',function(e){ if(e.target&&e.target.id==='htc') box.remove(); });
    box.appendChild(card); document.body.appendChild(box);
    box.addEventListener('click',function(e){ if(e.target===box) box.remove(); });
  };
  // 初载
  loadSentiment();
  loadSignalInner();
})();
