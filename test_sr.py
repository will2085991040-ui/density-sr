import sys, os
sys.path.insert(0, r"C:\Users\mine\Downloads\quant_research\detect_support_resistance_extract\Detect_support_and_resistance_levels-main")
import numpy as np
from src.srlab.data import atr_series, tick_size_guess
from src.srlab.pivots import zigzag
from src.srlab.detectors import V3Fusion
from src.srlab.base import Ctx

rng = np.random.default_rng(42)
n = 800
open_ = 100 * (1 + 0.001*np.cumsum(rng.standard_normal(n)))
close = open_ * (1 + 0.0005*rng.standard_normal(n))
high = np.maximum(open_, close) * (1 + 0.005*np.abs(rng.standard_normal(n)))
low = np.minimum(open_, close) * (1 - 0.005*np.abs(rng.standard_normal(n)))
vol = rng.integers(1000, 100000, n).astype(float)
atr = atr_series(high, low, close, 14)
det = V3Fusion()
ctx = Ctx(code="TEST", t=n-1, open_=open, high=high, low=low, close=close,
          volume=vol, atr=float(atr[-1]), tick=0.01, atr_arr=atr,
          pivots=zigzag(high, low, atr))
levels = det.detect(ctx)
print("n levels detected:", len(levels))
for l in levels[:6]:
    print(round(l.center,2), l.kind, "score=%.4f"%l.score, "width_atr=%.2f"%l.width_atr, "dist_atr=%.2f"%l.dist_atr)
print()
print("SUCCESS: detect_support engine imports and runs with current pandas/numpy/scipy")
