const http=require('http');
function g(base,p){return new Promise(res=>{http.get(base+p,r=>{const c=[];r.on('data',d=>c.push(d));r.on('end',()=>res({code:r.statusCode,len:Buffer.concat(c).length}));}).on('error',e=>res('ERR'+e.message));});}
(async()=>{
  const base='http://127.0.0.1:54341/';
  for(const p of ['','index.html','sentiment_panel.js','app.js','styles.css']){
    const r=await g(base,p); console.log('/'+p, r.code, r.len);
  }
})();
