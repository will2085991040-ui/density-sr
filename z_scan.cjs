const http=require('http');
function g(u,p){return new Promise(res=>{http.get(u+'/'+p,r=>{let d='';r.on('data',c=>d+=c);r.on('end',()=>res(d));}).on('error',e=>res('ERR'+e.message));});}
(async()=>{
  const base='http://127.0.0.1:49523/';
  // scan a few well-known stocks to find one with an actionable signal
  for(const s of ['600519','000858','601318','000001','002594','600036','000333']){
    try{
      const rt=JSON.parse(await g('api/rt/realtime?symbol='+s+'&tf=60'));
      const sig=rt.signal||{};
      if(sig.signal && sig.signal!=='观望'){ console.log(s, '=>', sig.signal, 'entry', sig.entry, 'op', sig.stop, 'target', sig.target, 'reason', sig.reason); }
      else console.log(s, '=>观望', sig.reason||'');
    }catch(e){ console.log(s,'ERR');
    }
  }
})();
