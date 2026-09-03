# -*- coding: utf-8 -*-
import py_compile
f=r"C:/Users/mine/Downloads/quant_research/server.py"
t=open(f,encoding="utf-8").read()
# add knowledge_json function before _esc
anchor = 'def _esc(s):'
fn = '''def knowledge_list():
    try:
        import glob as _gl
        kdir = os.path.join(_ROOT, "knowledge", "ep004")
        out = []
        for p in sorted(_gl.glob(os.path.join(kdir, "*.md"))):
            out.append({"name": os.path.basename(p), "size": os.path.getsize(p),
                        "text": open(p, encoding="utf-8").read()})
        return {"ok": True, "dir": "knowledge/ep004", "source": "frank-quant/ai-trading-videos (EP004 四LLM量化基准)",
                "files": out, "count": len(out)}
    except Exception as e:
        return {"ok": False, "error": str(e)}


'''
assert anchor in t
t=t.replace(anchor, fn+anchor, 1)
# add route
old = '''    if path == "/api/rt/sentiment":
        return 200, json.dumps(emotion_json()), "application/json"'''
new = '''    if path == "/api/rt/sentiment":
        return 200, json.dumps(emotion_json()), "application/json"
    if path == "/api/knowledge/ep004":
        return 200, json.dumps(knowledge_json()), "application/json"'''
assert old in t
t=t.replace(old,new,1)
open(f,"w",encoding="utf-8").write(t)
py_compile.compile(f,doraise=True)
print("knowledge route added")
