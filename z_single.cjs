const http=require('http');
function g(p){return new Promise(res=>{http.get('http://127.0.0.1:49523/'+p,r=>{let d='';r.on('data',c=>d+=c);r.on('end',()=>res(d));}).on('error',e=>res('ERR'+e.message));});}
(async()=>{
  console.log('alive:', (await g('index.html')).slice(0,15));
  const rt=await g('api/rt/realtime?symbol=601318&tf=60');
  console.log('601318 len', rt.length, rt.slice(0,120));
})();
