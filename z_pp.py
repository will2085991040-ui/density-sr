# -*- coding: utf-8 -*-
p = r"C:/Users/mine/Downloads/quant_research/server.py"
t = open(p, encoding="utf-8").read()
# after out['closes'] = d['closes'] in the realtime block, add out['src']
anchor = "            out['closes'] = d['closes']\n            bands = d.get('bands') or []"
repl = "            out['closes'] = d['closes']\n            out['src'] = d.get('src') or ('同花顺' if (d or {}).get('src') else None)\n            bands = d.get('bands') or []"
assert anchor in t, "a2"
t = t.replace(anchor, repl, 1)
open(p,"w",encoding="utf-8").write(t)