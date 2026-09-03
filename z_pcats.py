# -*- coding: utf-8 -*-
f="C:/Users/mine/Downloads/quant_research/webui/chart_realtime.js"
t=open(f,encoding="utf-8").read()
old = """  else { var use5=(d.showM5&&k5.length)||(!kk.length&&k5.length); src=use5?k5:kk; for(var j=0;j<src.length;j++){cats.push(src[j].t||(""+j));closes.push(src[j].close);} }"""
new = """  else { var use5=(d.showM5&&k5.length)||(!kk.length&&k5.length); src=use5?k5:kk;
    for(var j=0;j<src.length;j++){ var _lbl=(src[j].t||(dates&&dates[j])||(""+j)); cats.push(_lbl); closes.push(src[j].close);}
    if(!use5 && (!src[0]||!src[0].t) && dates && dates.length===src.length){
      // K-K线用真实日期刻度(修复v9.2日期轴为空)
      cats=dates.slice();
    } }"""
assert old in t, "pattern"
t=t.replace(old,new,1)
open(f,"w",encoding="utf-8").write(t)
print("patched today axis")
