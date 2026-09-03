# -*- coding: utf-8 -*-
p = "C:/Users/mine/Downloads/quant_research/webui/sentiment_panel.js"
t = open(p, encoding="utf-8").read()
old1 = "  function renderSignal(sig){\n    var body=$('#sig-body'); if(!body) return;"
new1 = "  var __sigSrc='';\n  function renderSignal(sig){\n    var body=$('#sig-body'); if(!body) return;"
assert old1 in t, "r1"
t = t.replace(old1, new1, 1)
old2 = "    var cls=sig.direction===\"多\"?\"up\":(sig.direction===\"空\"?\"down\":\"flat\");\n    var h='<div class=\"sig-top\"><span class=\"sig-tag '+cls+'\">'+esc(sig.signal||sig.direction||\"-\")+'</span><span class=\"muted small\">'+(sig.rr?'风比 1:'+fmt(sig.rr,2):'')+'</span></div>';"
new2 = "    var cls=sig.direction===\"多\"?\"up\":(sig.direction===\"空\"?\"down\":\"flat\");\n    var _s=esc(__sigSrc||'');\n    var h='<div class=\"sig-top\"><span class=\"sig-tag '+cls+'\">'+esc(sig.signal||sig.direction||\"-\")+'</span><span class=\"muted small\" style=\"margin-left:8px\">'+(__sigSrc?'数据源 '+_s+'':'')+'</span><span class=\"muted small\">'+(sig.rr?'风比 1:'+fmt(sig.rr,2):'')+'</span></div>';"
assert old2 in t, "r2"
t = t.replace(old2, new2, 1)
old3 = ".then(function(d){ renderSignal(d.signal); })"
new3 = ".then(function(d){ __sigSrc=d.source||''; renderSignal(d.signal); })"
assert old3 in t, "r3"
t = t.replace(old3, new3, 1)
open(p,"w",encoding="utf-8").write(t)
import subprocess
print("patched sentiment_panel.js")
