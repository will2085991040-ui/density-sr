
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