const http=require('http');
function g(p){return new Promise(res=>{http.get('http://127.0.0.1:54341/'+p,r=>{let d='';r.on('data',c=>d+=c);r.on('end',()=>res(d));}).on('error',e=>res('ERR'+e.message));});}
(async()=>{
  const s=await g('api/rt/sentiment');
  const j=JSON.parse(s);
  console.log('温度', j.score, j.label, '| 涨跌', j.breadth&&j.breadth.up+'/'+j.breadth.down, '| 涨停', j.zt_count, '| 连板', j.max_lb, '| 上证', j.indices&&j.indices.sh);
  console.log('建议:', j.suggest);
  const rt=JSON.parse(await g('api/rt/realtime?symbol=600519&tf=60'));
  const sig=rt.signal;
  console.log('60分信号:', sig.signal, '| 方向', sig.direction, '| 入场', sig.entry, '| 止损', sig.stop, '| 目标', sig.target, '| 风比', sig.rr);
})();
