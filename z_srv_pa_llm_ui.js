
function dirColorOf(d){ if(!d) return "#8b949e"; if(d.indexOf("多")>=0) return "#16c784"; if(d.indexOf("空")>=0) return "#ea3943"; return "#8b949e"; }
function paLine(k,v,opt){ return (v==null||v==="") ? "" : ('<div class="ln '+(opt||"")+'">'+k+' <b>'+v+'</b></div>'); }
function paCard(a){
  var lvs=(a.llm&&Array.isArray(a.llm.key_levels)&&a.llm.key_levels.length)?('<div class="pa-feats">'+a.llm.key_levels.map(function(x){return '<span class="chip">关键 <b>'+x+'</b></span>';}).join("")+'</div>'):"";
  var cls = (a.direction&&a.direction.indexOf("多")>=0)?"up":((a.direction&&a.direction.indexOf("空")>=0)?"dn":"");
  return '<div class="agent"><div class="atop"><div><div class="aname">'+(a.label||"")+'</div>'
    +'<div class="atone">'+(a.tone||"")+'</div></div>'
    +'<span class="abat" style="background:'+dirColorOf(a.direction)+'">'+(a.direction||"观望")+'</span></div>'
    +'<div class="aact '+cls+'">'+(a.action||"")+'</div>'
    +'<div class="lns">'+paLine("入场",a.entry)+paLine("止损",a.stop)+paLine("目标",a.target)
      +'<div class="ln">盈亏比 <b>'+(a.rr!=null?a.rr:"–")+'</b> · 风险 '+(a.risk_pct!=null?a.risk_pct+"/10":"–")+'</div></div>'
    +'<div class="anote">'+(a.reason||"")+'</div>'+lvs+'</div>';
}
async function runPA(){
  const mk=currentMarket||"A股", sym=$("#sel-symbol").value||"", tf=$("#sel-tf").value;
  const body=$("#pa-body");
  body.innerHTML='<span class="muted">正在调用真实AI · 双Agent研判…</span>';
  try{
    function url(st){ return API+"/pa/llm?market="+encodeURIComponent(mk)+"&symbol="+encodeURIComponent(sym)+"&tf="+encodeURIComponent(tf)+"&stance="+st; }
    const res=await Promise.all([jget(url("6.16")),jget(url("6.24"))]);
    body.innerHTML='<div style="margin-bottom:8px;font-size:11px;color:var(--dim)">真实大模型 DeepSeek-v4-flash · Tencent TokenHub 云网关 · 6.16 稳(机会少) / 6.24 激进(机会多)</div>'
      + (res[0].error?('<div class="agent"><div class="anote">6.16: '+res[0].error+'</div></div>'):paCard(res[0]))
      + (res[1].error?('<div class="agent"><div class="anote">6.24: '+res[1].error+'</div></div>'):paCard(res[1]));
  }catch(e){ body.innerHTML='<span class="muted">研判失败:'+e.message+'</span>'; }
}
// 重新绑定按钮到真实AI 双Agent
if(window.addEventListener){ try{ var _b=document.getElementById("btn-pa"); if(_b){ _b.removeEventListener("click", window.__oldRunPA||function(){}); _b.addEventListener("click", runPA); } }catch(e){} }
