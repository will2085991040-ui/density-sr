const http=require('http');
const base='http://127.0.0.1:60070/';
function g(p){return new Promise(res=>{http.get(base+p,r=>{let d='';r.on('data',c=>d+=c);r.on('end',()=>res(d));}).on('error',e=>res('ERR '+e.message));});}
(async()=>{
  const s=await g('api/rt/sentiment');
  console.log('SENTIMENT:', s.slice(0,700));
  const rt=await g('api/rt/realtime?symbol=600519&tf=daily');
  const j=JSON.parse(rt);
  console.log('REALTIME has signal:', !!j.signal, '| signal:', JSON.stringify(j.signal));
  console.log('sentiment:', JSON.stringify(j.sentiment));
  console.log('bands:', j.bands?j.bands.length:0);
})();
