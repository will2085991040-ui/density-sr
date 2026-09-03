# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, r"C:/Users/mine/Downloads/quant_research")
import pandas as pd
import numpy as np
from aiquant import pa_llm

rng = np.random.default_rng(7)
n = 120
price = 100.0
opens, highs, lows, closes = [], [], [], []
for i in range(n):
    o = price
    c = o + rng.normal(0, 0.8)
    h = max(o, c) + abs(rng.normal(0, 0.4))
    l = min(o, c) - abs(rng.normal(0, 0.4))
    opens.append(o); highs.append(h); lows.append(l); closes.append(c)
    price = c
df = pd.DataFrame({"open": opens, "high": highs, "low": lows, "close": closes,
                   "tick_volume": list(rng.integers(1000, 5000, n))})

for stance in ["6.16", "6.24"]:
    r = pa_llm.run_agent(df, symbol="SYNTH", market="TEST", stance=stance,
                         timeout=150, max_tokens=2400)
    print("STANCE=", stance, "LABEL=", r.get("label"), "TONE=", r.get("tone"))
    print("  llm_parsed=", r.get("llm") is not None, "llm_err=", r.get("llm_err"))
    print("  has_flat_direction=", "direction" in r)
    if r.get("llm") is not None:
        print("  direction=", r.get("direction"), "| action=", r.get("action"))
        print("  entry=", r.get("entry"), "stop=", r.get("stop"), "target=", r.get("target"))
        print("  risk_pct=", r.get("risk_pct"), "rr=", r.get("rr"))
        print("  key_levels=", r.get("llm").get("key_levels"))
        rr = r.get("reason")
        print("  reason=", (rr[:120] + "...") if rr else None)
print("DONE")
