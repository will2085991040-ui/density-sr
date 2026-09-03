# -*- coding: utf-8 -*-
import py_compile
f = r"C:/Users/mine/Downloads/quant_research/server.py"
t = open(f, encoding="utf-8").read()
old = '''def export_html(rows):
    trs = []
    for r in rows:
        trs.append("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (
            _esc(r.get("symbol", "")), _esc(r.get("name", "")), r.get("current_price"),
            r.get("change_pct"), _esc(r.get("trend_label", ""))))
    return (("<!doctype html><meta charset=utf-8><title>DENSITY-SR 扫描导出</title>"
             "<style>body{font:13px/1.6 system-ui;background:#0a0e14;color:#e6e6e6;padding:24px}"
             "table{border-collapse:collapse;width:100%}td,th{border:1px solid #2a3441;padding:6px 10px;text-align:left}"
             "th{background:#141a22}.pos{color:#16c784}.neg{color:#ea3943}</style>"
             "<h2>DENSITY-SR 全市场支撑阻力扫描</h2><p>共 %d 只</p><table><tr>"
             "<th>代码</th><th>名称</th><th>现价</th><th>涨跌%</th><th>形态</th></tr>%s</table>")
            % (len(rows), "".join(trs))).encode("utf-8")'''
new = '''def export_html(rows):
    trs = []
    for r in rows:
        trs.append("<tr><td>"+_esc(r.get("symbol",""))+"</td><td>"+_esc(r.get("name",""))
                   +"</td><td>"+str(r.get("current_price"))+"</td><td>"+str(r.get("change_pct"))
                   +"</td><td>"+_esc(r.get("trend_label",""))+"</td></tr>")
    css = "body{font:13px/1.6 system-ui;background:#0a0e14;color:#e6e6e6;padding:24px}table{border-collapse:collapse;width:100% }td,th{border:1px solid #2a3441;padding:6px 10px;text-align:left}th{background:#141a22}"
    head = "<!doctype html><meta charset=utf-8><title>DENSITY-SR 扫描结论</title><style>"+css+"</style>"
    return (head + "<h2>DENSITY-SR 全市场支撑阻力扫描</h2><p>共 "+str(len(rows))+" 只</p><table><tr>"
            "<th>代码</th><th>名称</th><th>现价</th><th>涨跌</th><th>形态</th></tr>"+"".join(trs)+"</table>").encode("utf-8")'''
if old in t:
    t = t.replace(old, new, 1); print("export_html patched")
else:
    print("pattern not found")
open(f,"w",encoding="utf-8").write(t)
py_compile.compile(f, doraise=True)
