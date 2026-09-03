"use strict";
const $=(s)=>document.querySelector(s);
let chart=null, allRows=[], symbols=[], current=null, currentMarket="A股";
const API="/api";
const fmt=(x,d=2)=>x==null?"—":(+x).toFixed(d);
const pctf=(x)=>x==null?"—":(x*100).toFixed(1);
async function jget(u){const r=await fetch(u);if(!r.ok)throw new Error(u+" "+r.status);return r.json();}
async function loadScan(){
  try{
    const d=await jget(API+"/scan?limit=260");
    allRows=d.rows||[]; renderScan(allRows);
    $("#data-count").textContent="品种数：扫描 "+allRows.length+" 只";
  }catch(e){console.error("scan",e);}
}
async function loadDetail(sym){
  try{
    const tf=$("#sel-tf").value,n=+$("#sel-lookback").value,lv=+$("#sel-levels").value;
    const mk=$("#sel-market").value; currentMarket=mk; current={symbol:sym,market:mk};
    const d=await jget(API+"/detail?market="+encodeURIComponent(mk)+"&symbol="+encodeURIComponent(sym)+"&tf="+encodeURIComponent(tf)+"&n="+n+"&levels="+lv);
    renderDetail(d); renderChart(d);
  }catch(e){console.error("detail",e);}
}
function renderScan(rows){
  const tb=$("#scan-body"); tb.innerHTML="";
  rows.forEach(r=>{
    const chg=r.change_pct||0, ccls=chg>0?"up":(chg<0?"down":"flat");
    const tr=document.createElement("tr");
    tr.innerHTML=`<td>${r.symbol}</td><td>${fmt(r.current_price)}</td><td class="${ccls}">${fmt(chg)}</td><td>${pctf(r.p_touch)}</td><td>${pctf(r.p_hold)}</td><td>${r.n_events||0}</td><td>${r.trend_label}</td><td>${r.width_atr==null?"-":r.width_atr+"A"}</td><td>${fmt(r.nearest_support)}</td><td>${fmt(r.nearest_resistance)}</td>`;
    tr.onclick=()=>{$("#sel-symbol").value=r.symbol; loadDetail(r.symbol);};
    tb.appendChild(tr);
  });
  $("#pager").textContent="显示 1-"+rows.length+" / "+allRows.length;
}
function renderDetail(d){
  $("#d-title").textContent="["+(d.market||"A股")+"] "+(d.name_||"")+" "+d.symbol+" · "+d.tf;
  $("#d-price").textContent=fmt(d.current_price);
  const c=Number(d.change_pct)||0; $("#d-chg").textContent=(c>=0?"+":"")+c.toFixed(2)+"%";
  $("#d-chg").className=c>=0?"up":"down";
  $("#d-summary").textContent=`现价vs EMA20 ${fmt(d.ema20dist,2)}% · EMA20斜率 ${fmt(d.ema20slope,2)}% · ATR/价格 ${fmt(d.atr_pct,2)}% · 样本 ${d.data_bars}`;
  const tb=$("#d-bands tbody"); tb.innerHTML="";
  (d.bands||[]).forEach(b=>{
    const tr=document.createElement("tr");
    tr.innerHTML=`<td class="${b.zone_type==="support"?"sup":"res"}">${b.zone_type==="support"?"支撑":"压力"}</td><td>${fmt(b.center)}</td><td>${b.width_atr}A</td><td>${fmt(b.distance_pct,2)}%</td><td>${pctf(b.p_touch)}</td><td>${pctf(b.p_hold)}</td>`;
    tb.appendChild(tr);
  });
  const L=d.last||[];
  $("#d-ohlc").textContent=`最新 OHLC: O ${fmt(L[0])} H ${fmt(L[1])} L ${fmt(L[2])} C ${fmt(L[3])} · 量 ${L[4]}`;
}
function renderChart(d){
  if(!chart) chart=echarts.init($("#kline"),"dark");
  const kk=(d.k||[]).map(c=>[c.open,c.close,c.low,c.high]);
  const cross_sr=(d.bands||[]).map(b=>({yAxis:b.center,name:b.zone_type+" "+fmt(b.center,3),lineStyle:{color:b.zone_type==="support"?"#16c784":"#ea3943",type:"dashed",opacity:0.85}}));
  chart.setOption({backgroundColor:"#0a0e14",animation:false,
    tooltip:{trigger:"axis",axisPointer:{type:"cross"}},
    grid:{left:52,right:14,top:30,bottom:8},
    xAxis:{type:"category",data:(d.dates||[]).map(s=>s.slice(5)),boundaryGap:true,axisLabel:{color:"#8b949e"},axisLine:{lineStyle:{color:"#2a3441"}}},
    yAxis:{scale:true,axisLabel:{color:"#8b949e"},splitLine:{lineStyle:{color:"#1b222c"}}},
    dataZoom:[{type:"inside",xAxisIndex:0,zoomOnMouseWheel:true,moveOnMouseMove:true},{type:"inside",start:55,end:100}],
    series:[
      {type:"candlestick",data:kk,itemStyle:{color:"#ea3943",color0:"#16c784",borderColor:"#ea3943",borderColor0:"#16c784"}},
      {type:"line",data:(d.closes||[]),symbol:"none",lineStyle:{width:1.4,color:"#f0c04b"},markLine:{silent:true,symbol:"none",data:cross_sr||[]}},
    ]
  });
}
function debounce(fn,ms){let t;return(...a)=>{clearTimeout(t);t=setTimeout(()=>fn(...a),ms);};}
$("#btn-analyze").addEventListener("click",()=>loadDetail($("#sel-symbol").value));
$("#sel-symbol").addEventListener("change",()=>loadDetail($("#sel-symbol").value));
$("#sel-tf").addEventListener("change",()=>current&&loadDetail(current.symbol));
$("#sel-lookback").addEventListener("change",()=>current&&loadDetail(current.symbol));
$("#btn-scan").addEventListener("click",loadScan);
$("#btn-all").addEventListener("click",loadScan);
$("#fltr").addEventListener("input",debounce(()=>{
  const q=$("#fltr").value.toLowerCase();
  const rows=allRows.filter(r=>!q||r.symbol.toLowerCase().includes(q)||(r.trend_label||"").includes(q));
  renderScan(rows);
},250));
$("#btn-csv").addEventListener("click",()=>{location.href="/api/export?type=csv";});
$("#btn-html").addEventListener("click",()=>{location.href="/api/export?type=html";});
window.addEventListener("resize",()=>chart&&chart.resize());
init();
async function init(){
  await loadSymbols("A股");
  loadDetail($("#sel-symbol").value);
  loadScan();
}
async function loadSymbols(){  // build symbol datalist for the selected market
  const mk=$("#sel-market").value; currentMarket=mk;
  try{
    const base=await jget(API+"/init?market="+encodeURIComponent(mk));
    symbols=base.symbols||[]; symbols=Array.isArray(symbols)?symbols:[];
    const dl=$("#sym-list"); dl.innerHTML="";
    symbols.slice(0,2500).forEach(s=>{const o=document.createElement("option");o.value=s;dl.appendChild(o);});
    $("#data-count").textContent=["A股 "+base["A股"]+"  ·  指数 "+base["指数"]+"  ·  MT5 "+base["MT5"]+"  ·  OKX "+base["OKX"]].join("");
    // choose a sensible default symbol per market
    const pick = symbols[0] || (mk==="A股"?"000001":"");
    $("#sel-symbol").value=pick;
  }catch(e){console.error("loadSymbols",e);symbols=[];}
}
$("#sel-market").addEventListener("change",()=>{ loadSymbols().then(()=>{ if($("#sel-symbol").value) loadDetail($("#sel-symbol").value); }); });

// ===== AI/联网研判 =====
async function netStatus(){
  try{ await jget(API+"/live/quotes?symbols=600519"); $("#net-dot").className="live-dot on"; $("#net-tag").textContent="云端行情已连接"; }
  catch(e){ $("#net-dot").className="live-dot"; $("#net-tag").textContent="离线模式 · 本地数据"; }
}
async function doLive(){
  const sym=$("#sel-symbol").value;
  $("#ai-result").innerHTML=`<span class="muted">实时拉取 ${sym} …</span>`;
  try{
    const q=await jget(API+"/live/quotes?symbols="+encodeURIComponent(sym));
    const lv=q[sym]||null;
    if(lv){ $("#d-price").textContent=fmt(lv.price); $("#d-chg").textContent=(lv.chg_pct>=0?"+":"")+lv.chg_pct.toFixed(2)+"%"; $("#d-chg").className=lv.chg_pct>=0?"up":"down"; $("#d-title").textContent=(lv.name||"")+" "+sym+" · LIVE"; }
    const chips=Object.entries(q).map(([k,v])=>`<span class="qchip ${v.chg_pct>=0?"up":"down"}">${v.name||k} ${fmt(v.price)} ${(v.chg_pct>=0?"+":"")+v.chg_pct.toFixed(2)}%</span>`).join(" ");
    $("#ai-result").innerHTML=`<div class="live-grid">${chips}</div><div class="muted">实时报价 · 腾讯行情API · ${lv?("现价 "+fmt(lv.price)+" · 涨跌 "+(lv.chg_pct>=0?"+":"")+lv.chg_pct.toFixed(2)+"%"):"仅本地兜底"}</div>`;
  }catch(e){ $("#ai-result").innerHTML=`<span class="muted">实时获取失败, 已回退本地数据</span>`; }
}
async function doAI(){
  const sym=$("#sel-symbol").value,n=+$("#sel-lookback").value||150;
  $("#ai-result").innerHTML=`<span class="muted">AI 训练中… (${sym})</span>`;
  try{
    const d=await jget(API+"/ai/analyze?symbol="+encodeURIComponent(sym)+"&n="+n);
    const cls=d.signal==="看多"?"up":(d.signal==="看空"?"down":"flat");
    const bars=(d.factors||[]).map(f=>`<div class="fbar"><span>${f.name}</span><div class="bar"><i style="width:${Math.min(100,Math.round((f.weight||0)*400))}%"></i></div><b>${(f.weight||0).toFixed(3)}</b></div>`).join("");
    $("#ai-result").innerHTML=`<div class="sig"><span class="sig-label">AI 未来5日方向</span><b class="sig-val ${cls}">${d.signal}</b><span class="conf">置信度 ${Math.round((d.confidence||0)*100)}%</span></div><div class="muted">${d.reason||""}</div><div class="fbars">${bars}</div>`;
  }catch(e){ $("#ai-result").innerHTML=`<span class="muted">AI 分析失败: ${e.message}</span>`; }
}
async function doFactor(){
  $("#ai-result").innerHTML=`<span class="muted">跨市场因子挖掘中… (随机森林特征重要度)</span>`;
  try{
    const d=await jget("/api/factor/mine?limit=8");
    const rows=(d.rows||[]).map((r,i)=>`<div class="frank"><span>#${r.rank}</span><b>${r.factor}</b><i style="width:${Math.min(100,Math.round(r.importance*600))}%"></i><em>${(r.importance*100).toFixed(1)}%</em></div>`).join("");
    $("#ai-result").innerHTML=`<div class="fh">全市场因子挖掘 · 随机森林特征重要度 · 样本 ${d.samples||0}</div><div class="frank-list">${rows||"无样本"}</div>`;
  }catch(e){ $("#ai-result").innerHTML=`<span class="muted">因子挖掘失败: ${e.message}</span>`; }
}
$("#btn-live").addEventListener("click",doLive);
$("#btn-ai").addEventListener("click",doAI);
$("#btn-factor").addEventListener("click",doFactor);
netStatus();

// ===== 双价格行为智能体 (PA_Agent 稳/激进) =====
$("#sel-market").addEventListener("change",()=>{ $("#pa-body").innerHTML='<span class="muted">市场切换,重新运行双Agent研判</span>'; });