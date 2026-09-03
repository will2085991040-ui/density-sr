"use strict";
/* DENSITY-SR interactive行情图: hover OHLC, click bar卡, click 支撑/阻力卡, 缩放平移, 十字准线 */
(function(){
  function $(s){return document.querySelector(s);}
  function fmt(x,d){d=(d==null?2:d);return (x==null||x===''||x==='—')?'—':(+x).toFixed(d);}
  function esc(s){return String(s==null?'':s).replace(/[&<>]/g,function(c){return ({'&':'&amp;','<':'&lt;','>':'&gt;'})[c];});}

  window.__renderInteractive = function(d){
    if(!d || !d.k || !d.dates) return;
    var el=$('#kline'); if(!el) return;
    var chart=window.__chart || (window.__chart=echarts.init(el,'dark'));
    var kk=d.k, dates=d.dates, closes=d.closes||[], bands=d.bands||[];
    var flat=function(price){return kk.map(function(){return price;});};
    var bandSeries=bands.map(function(b,i){
      var col=b.zone_type==='support'?'#16c784':'#ea3943';
      var tb=b.zone_type==='support'?'支撑':'压力';
      return {
        type:'line', symbol:'none', name:'SR'+(i+1)+'·'+tb,
        data:flat(b.center),
        lineStyle:{color:col,width:1.6,type:'dashed'}, z:20,
        tooltip:{trigger:'item',formatter:function(){
          return '<b>'+tb+'位 #'+(i+1)+'</b><br/>中心价 <b>'+fmt(b.center,3)+'</b><br/>带宽 '+(b.width_atr!=null?b.width_atr:0)+' ATR<br/>距现价 '+(b.distance_pct!=null?b.distance_pct.toFixed(2):'-')+'%<br/>触及 '+(b.p_touch!=null?(b.p_touch*100).toFixed(1):'-')+'%<br/>守住 '+(b.p_hold!=null?(b.p_hold*100).toFixed(1):'-')+'%';
        }},
        label:{show:true,position:'end',color:col,fontSize:10,offset:[6,0],
               formatter:function(){return '  '+fmt(b.center,3);}},
        emphasis:{disabled:false}
      };
    });
    var ema=[];
    (function(){var p=Math.min(20,closes.length);var sum=0;var m=[];for(var i=0;i<closes.length;i++){sum=closes[i]+(p?p:1)*((i?m[i-1]:closes[i])||closes[i])*0;m[i]=closes[i];} /* EMA20 approx */;var k=2/(20+1);var e=closes[0]||0;ema=[];for(var j=0;j<closes.length;j++){e=(j===0)?closes[j]:((closes[j]-e)*k+e);ema.push(e);}})();
    chart.setOption({
      backgroundColor:'#0a0e14', animation:true, animationDuration:350,
      tooltip:{trigger:'axis',confine:true,backgroundColor:'#151b25',borderColor:'#2a3441',textStyle:{color:'#e6e6e6',fontSize:12},
        axisPointer:{type:'cross',crossStyle:{color:'#f0c04b',width:1},label:{backgroundColor:'#2a3441',color:'#e6e6e6'}},
        formatter:function(ps){
          if(!ps||!ps.length) return '';
          var p=ps[0];
          if(p.seriesType==='candlestick' && p.dataIndex!=null){
            var ci=p.dataIndex, dd=kk[ci], st=dates[ci]||'';
            var up=dd.close>=dd.open;
            var chg=dd.open>0?((dd.close/dd.open-1)*100):0;
            var col=up?'#ea3943':'#16c784';
            var html='<div style="min-width:150px;font-size:12px;line-height:1.7">';
            html+='<b>'+st+'</b><br/>';
            html+='开 <span style="color:'+col+'">'+fmt(dd.open,2)+'</span> '+(dd.volume!=null?'量 '+Math.round(dd.volume).toLocaleString():'')+'<br/>';
            html+='高 '+fmt(dd.high,2)+'　低 '+fmt(dd.low,2)+'<br/>';
            html+='收 <b>'+fmt(dd.close,2)+'</b>　涨跌 <b style="color:'+col+'">'+(chg>=0?'+':'')+chg.toFixed(2)+'%</b><br/>';
            html+='<span style="color:#8b949e;font-size:11px">提示: 点击该K线可看时点快照 · 点击虚线=支撑/阻力详情</span>';
            return html;
          }
          return '';
        }},
      grid:{left:56,right:128,top:30,bottom:34},
      xAxis:{type:'category',data:dates.map(function(s){return String(s).slice(5);}),boundaryGap:true,
        axisLabel:{color:'#8b949e'},axisLine:{lineStyle:{color:'#2a3441'}},
        axisPointer:{label:{formatter:function(p){var dd=dates[p.value];return dd||'';}}}},
      yAxis:{scale:true,axisLabel:{color:'#8b949e'},splitLine:{lineStyle:{color:'#141a22'}},
        axisPointer:{label:{backgroundColor:'#2a3441',color:'#fff',formatter:function(p){return '¥ '+p.value.toFixed(2);}}}},
      dataZoom:[
        {type:'inside',xAxisIndex:0,zoomOnMouseWheel:true,moveOnMouseMove:true,throttle:30,start:0,end:100},
        {type:'slider',xAxisIndex:0,height:16,bottom:4,start:0,end:100,borderColor:'#2a3441',textStyle:{color:'#8b949e'}}
      ],
      series:[
        {type:'candlestick',name:'K线',data:kk,
         itemStyle:{color:'#ea3943',color0:'#16c784',borderColor:'#ea3943',borderColor0:'#16c784'},
         tooltip:{trigger:'item'}},
        {type:'line',name:'EMA20',symbol:'none',data:ema,lineStyle:{color:'#f0c04b',width:1.3},z:10}
      ].concat(bandSeries)
    },true);
    chart.off('click');
    chart.on('click',function(pr){
      if(!pr) return;
      if(pr.seriesType==='line' && (pr.seriesName||'').indexOf('SR')===0){
        var n=parseInt((pr.seriesName||'').split('#')[1],10)-1;
        if(bands[n]) showBandCard(bands[n]);
        return;
      }
      if(pr.seriesType==='candlestick' && pr.dataIndex!=null){
        showBarCard(pr.dataIndex,d);
      }
    });
    window.__lastChartData=d;
  };

  function showBandCard(b){
    var m=$('#ai-result'); if(!m) return;
    var st=b.zone_type==='support'?'支撑':'压力';
    m.innerHTML='<div class="bandCardBox"><div class="bandTitle">'+st+'位详情</div>'
      +'<table class="pa-kv" style="width:100%"><tbody>'
      +'<tr><td>中心价</td><td><b>'+fmt(b.center,3)+'</b></td><td>带宽</td><td>'+(b.width_atr!=null?b.width_atr:'-')+' ATR</td></tr>'
      +'<tr><td>区间</td><td>'+fmt(b.lo,3)+' ~ '+fmt(b.hi,3)+'</td><td>距现价</td><td>'+(b.distance_pct!=null?b.distance_pct.toFixed(2):'-')+'%</td></tr>'
      +'<tr><td>触及概率</td><td>'+(b.p_touch!=null?(b.p_touch*100).toFixed(1):'-')+'%</td><td>守住概率</td><td>'+(b.p_hold!=null?(b.p_hold*100).toFixed(1):'-')+'%</td></tr>'
      +'</tbody></table>'
      +'<div style="margin-top:7px;font-size:11px;color:var(--dim)">'+esc('图中虚线即'+st+'位(每条可点)。点K线看单条快照。')+'</div>'
      +'</div>';
  }
  function showBarCard(i,d){
    var dd=d.k[i]; if(!dd) return; var st=(d.dates&&d.dates[i])||'';
    var chg=dd.open>0?((dd.close/dd.open-1)*100):0;
    var box=document.createElement('div'); box.className='barCard';
    box.innerHTML='<div class="bsTitle">'+st+' · K线快照</div>'
      +'<table class="bs-kv" style="width:100%"><tbody>'
      +'<tr><td>开</td><td>'+fmt(dd.open,2)+'</td><td>收</td><td>'+fmt(dd.close,2)+'</td></tr>'
      +'<tr><td>高</td><td>'+fmt(dd.high,2)+'</td><td>低</td><td>'+fmt(dd.low,2)+'</td></tr>'
      +'<tr><td>涨跌</td><td>'+(chg>=0?'+':'')+chg.toFixed(2)+'%</td><td>量</td><td>'+(dd.volume!=null?Math.round(dd.volume).toLocaleString():'-')+'</td></tr>'
      +'</tbody></table>'
      +'<div style="font-size:11px;color:#888;margin-top:5px">点AI查看该股趋势研判</div>';
    var m=$('#ai-result'); if(m){ m.innerHTML=''; m.appendChild(box); }
  }
  // override loadDetail's renderChart to the interactive one
  function hijack(){
    if(window.__hijackedChart) return;
    if(window.renderChart && window.__origRenderChart) { window.__origRenderChart=window.renderChart; }
    window.renderChart=function(d){ try{ window.__renderInteractive(d);}catch(e){ window.dispatchEvent(new Event('dsrchartfail')); } };
    window.__hijackedChart=true;
  }
  if(window.addEventListener){ window.addEventListener('load',hijack); hijack(); }
  // re-render whenever detail reloaded (app.js calls loadDetail->renderChart)
  var orig=window.renderChart;
  hijack();
})();
