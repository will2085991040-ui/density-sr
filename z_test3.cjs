const http=require('http');
const base='http://127.0.0.1:64618/';
function g(p){return new Promise(res=>{http.get(base+p,r=>{let d='';r.on('data',c=>d+=c);r.on('end',()=>res(d));}).on('error',e=>res('ERR'+e.message));});}
(async()=>{
  const rt=JSON.parse(await g('api/rt/realtime?symbol=600519&tf=daily'));
  console.log('signal:', JSON.stringify(rt.signal));
  console.log('sentiment:', JSON.stringify(rt.sentiment));
  console.log('quote_price:', rt.quote&&rt.quote.price, 'bands:', rt.bands&&rt.bands.length);
  const rt60=JSON.parse(await g('api/rt/realtime?symbol=600519&tf=60'));
  console.log('60min signal:', JSON.stringify(rt60.signal));
})();
