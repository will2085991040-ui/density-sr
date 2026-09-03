/* DENSITY·SR 实时盘多图层引擎: 分时 / K线 / 量能 / 均线MA / 支撑阻力 / MACD */
"use strict";
window.__renderRealtime=function(d){
  if(!d) return;
  var el=document.getElementById("kline"); if(!el) return;
  var chart=window.__rtChart||(window.__rtChart=window.__chart||echarts.init(el,"dark"));
  window.__chart=chart;
  var UP="#ea3943",DN="#16c784",YELLOW="#f0c04b",DIM="#8b949e",GRID="#141a22",AXIS="#2a3441";
  var mode=d.mode||"kline", q=d.quote||null, mm=d.minute||[], k5=d.m5||[], kk=d.kline||[], dates=d.dates||[], bands=d.bands||[];
  var isMin=(mode==="minute" && mm.length);
  var src, cats=[], closes=[];
  if(isMin){ src=mm; for(var i=0;i<mm.length;i++){cats.push(mm[i].t);closes.push(mm[i].p);} }
  else { var use5=(d.showM5&&k5.length)||(!kk.length&&k5.length); src=use5?k5:kk;
    for(var j=0;j<src.length;j++){ var _lbl=(src[j].t||(dates&&dates[j])||(""+j)); cats.push(_lbl); closes.push(src[j].close);}
    if(!use5 && (!src[0]||!src[0].t) && dates && dates.length===src.length){
      // K-K线用真实日期刻度(修复v9.2日期轴为空)
      cats=dates.slice();
    } }
  function sma(a,p){var o=[],s=0;for(var z=0;z<a.length;z++){s+=a[z];if(z>=p)s-=a[z-p];o.push(z>=p-1?Math.round(s/p*100)/100:null);}return o;}
  function ema(a,p){var k=2/(p+1),e=a[0]||0,o=[];for(var z=0;z<a.length;z++){e=(z===0)?a[z]:((a[z]-e)*k+e);o.push(Math.round(e*100)/100);}return o;}
  var series=[];
  var vols=[];
  // ===== 分时图层 =====
  var isMinute=(mode==="minute"&&mm.length);
  if(isMinute){
    var priceY=mm.map(function(m){return m.p;}),avgY=mm.map(function(m){return m.avg;});
    series.push({type:"line",name:"价格",showSymbol:false,smooth:true,data:priceY,lineStyle:{color:"#ffffff",width:1.8},z:12});
    series.push({type:"line",name:"均价",showSymbol:false,smooth:true,data:avgY,lineStyle:{color:YELLOW,width:1.4},z:11});
    if(d.quote){var pre=d.quote.preclose; series.push({type:"line",name:"昨收",symbol:"none",data:cats.length?cats.map(function(){return pre;}):[],lineStyle:{color:"#ffffff",width:1,type:"dotted"},z:3});}
  }
  // ===== K线图层 =====
  if(!isMinute){
    var candles=src.map(function(b){return [b.open,b.close,b.low,b.high];});
    series.push({type:"candlestick",name:"K",data:candles,itemStyle:{color:UP,color0:DN,borderColor:UP,borderColor0:DN},z:10});
    series.push({type:"line",name:"MA5",symbol:"none",data:sma(closes,5),lineStyle:{color:"#ffe24d",width:1.2},z:6});
    series.push({type:"line",name:"MA10",symbol:"none",data:sma(closes,10),lineStyle:{color:YELLOW,width:1.2},z:6});
    series.push({type:"line",name:"MA20",symbol:"none",data:sma(closes,20),lineStyle:{color:"#7b9bf2",width:1.2},z:6});
    series.push({type:"line",name:"MA60",symbol:"none",data:sma(closes,60),lineStyle:{color:DN,width:1.2},z:6});
  }
  // ===== 量能 =====
  if(src.length){
    var b0=src[0]; if(b0.vol!==undefined){vols=src.map(function(b){return Math.round(b.vol);});}
    else {for(var v=0;v<src.length;v++){var dx=v?(src[v].p-src[v-1].p):0;vols.push(Math.max(1,Math.round(Math.abs(dx)* (d.quote?Math.round(d.quote.volume/(src.length||1)):10)/40)));}}
    series.push({type:"bar",name:"量",xAxisIndex:1,yAxisIndex:1,data:vols,itemStyle:{color:function(p){var pi=p.dataIndex;var pr=pi>0?vols[pi-1]:p.value;return (p.value>=pr?UP:DN);}},z:2,barGap:"0%"});
  }
  // ===== 支撑/阻力带 + 今日参考线 =====
  var maxY=Math.max.apply(null,(isMinute?closes:closes||[1]).filter(function(x){return x!=null;}));
  bands.forEach(function(b,i){var col=b.zone_type==="support"?DN:UP;var tb=b.zone_type==="support"?"支撑":"压力";series.push({type:"line",name:"SR"+(i+1)+"."+tb,symbol:"none",data:cats.map(function(){return b.center;}),lineStyle:{color:col,width:1.5,type:"dashed"},z:30,label:{show:true,position:"end",formatter:function(){return " "+fmt(b.center);},color:col,fontSize:10},tooltip:{trigger:"item",formatter:function(){return "<b>"+tb+"</b> "+(b.lo!=null?fmt(b.lo):"-")+" ~ "+(b.hi!=null?fmt(b.hi):"-");}}});});
  function fmt(x){return x==null?"-":(+x).toFixed(2);}
  if(d.quote){var Q=d.quote; [[["昨日",Q.preclose],["今日",Q.open],["最高",Q.high],["最低",Q.low],["现价",Q.price]]].forEach(function(arr){arr.forEach(function(ln){if(ln[1]==null)return;series.push({type:"line",name:"r:"+ln[0],symbol:"none",data:cats.map(function(){return ln[1];}),lineStyle:{color:DIM,width:1,type:"dotted"},z:4,label:{show:true,position:"start",formatter:ln[0]+" "+fmt(ln[1]),color:DIM,fontSize:9}});});});}
  // ===== 涨/跌停参考线(按板块) =====
  if(d.quote && d.quote.code){
    var ccode=String(d.quote.code);
    var limPct = (ccode.charAt(0)==='3' || ccode.indexOf('688')===0 || ccode.indexOf('689')===0) ? 0.20
              : (ccode.charAt(0)==='4' || ccode.charAt(0)==='8' || ccode.charAt(0)==='9') ? 0.30 : 0.10;
    var ul=(d.quote.preclose||0)*(1+limPct), dl=(d.quote.preclose||0)*(1-limPct);
    if(d.quote.preclose){
      series.push({type:'line',name:'l涨停'+limPct,['symbol']:'none',data:cats.map(function(){return ul;}),lineStyle:{color:'#ff7b8a',width:1.2,type:'dashed'},z:7,label:{show:true,position:'start',formatter:'涨停 '+fmt(ul),color:'#ff7b8a',fontSize:9}});
      series.push({type:'line',name:'跌停',symbol:'none',data:cats.map(function(){return dl;}),lineStyle:{color:'#3ecf8e',width:1.2,type:'dashed'},z:7,label:{show:true,position:'start',formatter:'跌停 '+fmt(dl),color:'#3ecf8e',fontSize:9}});
    }
  }
  // ===== MACD 副图(可选) =====
  var macdS=[], macdIdx=-1;
  function mema(a,per){var k=2/(per+1),e=(a[0]||0),o=[];for(var z=0;z<a.length;z++){e=(z===0)?a[z]:((a[z]-e)*k+e);o.push(Math.round(e*1000)/1000);}return o;}
  if(d.showMacd && closes.length>=26){
    var e12=mema(closes,12),e26=mema(closes,26),diff=[],z2;
    for(z2=0;z2<closes.length;z2++){var aa=e12[z2],bb=e26[z2];diff.push((aa!=null&&bb!=null)?(aa-bb):null);}
    var dea=mema(diff,9),hist=[];
    for(z2=0;z2<diff.length;z2++){hist.push((diff[z2]!=null&&dea[z2]!=null)?((diff[z2]-dea[z2])*100):null);}
    macdS.push({type:'bar',name:'MACD',xAxisIndex:2,yAxisIndex:2,data:hist,itemStyle:{color:function(p){return p.value>=0?UP:DN;}},barGap:'0%',z:2});
    macdS.push({type:'line',name:'DIF',xAxisIndex:2,yAxisIndex:2,symbol:'none',data:diff,lineStyle:{color:'#fbe54d',width:1.2},z:5});
    macdS.push({type:'line',name:'DEA',xAxisIndex:2,yAxisIndex:2,symbol:'none',data:dea,lineStyle:{color:'#a78bf0',width:1.2},z:5});
    macdIdx=2;
  }

  chart.setOption({
    backgroundColor:'#0a0e14',animation:true,animationDuration:300,
    tooltip:{trigger:'axis',confine:true,backgroundColor:'#151b25',borderColor:GRID,textStyle:{color:'#fff'},axisPointer:{type:'cross',crossStyle:{color:YELLOW,width:1}}},
    grid:[{left:56,right:116,top:24,height:macdIdx>=0?'56%':'72%'},{left:56,right:116,top:'72%',height:'13%'},{left:56,right:116,top:'87%',height:'9%'}],
    xAxis:[{type:'category',data:cats,axisLabel:{color:DIM},axisLine:{lineStyle:{color:GRID}},gridIndex:0},{type:'category',gridIndex:1,data:cats,axisLabel:{show:false}},{type:'category',gridIndex:2,data:cats,axisLabel:{show:false}}],
    yAxis:[{scale:true,gridIndex:0,splitLine:{lineStyle:{color:GRID}},axisLabel:{color:DIM}},{gridIndex:1,axisLabel:{show:false},splitLine:{show:false}},{gridIndex:2,axisLabel:{show:false},splitLine:{show:false}}],
    dataZoom:[{type:'inside',xAxisIndex:[0,1,2],start:0,end:100},{type:'slider',xAxisIndex:[0,1,2],height:15,bottom:4,start:0,end:100}],
    series: macdIdx>=0 ? series.concat(macdS) : series
  },true);

  window.__lastRealtime=d;
};