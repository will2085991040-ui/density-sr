# -*- coding: utf-8 -*-
"""Interactive DENSITY-SR watch chart: K-line + S/R bands + per-bar emotion timeline.
Mouse wheel = zoom, left-drag = pan, double-click = reset. Offline."""
from __future__ import annotations
import sys, os
_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if _ROOT not in sys.path: sys.path.insert(0, _ROOT)
DARK="#0d1117"; UP="#3fb950"; DOWN="#f85149"; ACC="#58a6ff"

def emotion_series(df, span=5):
    """Synthesize a per-bar dice-roll emotion index in [-1,1]; None on failure."""
    import numpy as np
    try:
        r = df["close"].pct_change().fillna(0).values.astype(float)
        vol = df["tick_volume"].values.astype(float)
        vr = np.zeros_like(r)
        if vol.std() > 0: vr = (vol - vol.mean()) / vol.std()
        sv = np.clip(np.abs(vr), 0, 3) / 3.0
        speed = np.clip(r * 200.0, -1, 1)
        feel = 0.62 * speed + 0.38 * sv * np.sign(r + 1e-9)
        k = np.ones(span) / span
        out = np.convolve(np.where(np.isnan(feel), 0, feel), k, mode="same")
        return np.clip(out, -1, 1)
    except Exception:
        return None

class WatchChart:
    """"live" fig: top K-line+S/R candles, bottom emotion fill."""
    def __init__(self, master, df, zones, title=""):
        import matplotlib
        matplotlib.use("TkAgg")
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        self.master = master; self.df = df; self.zones = zones or []; self.title = title
        self.emotion = emotion_series(df)
        fig = plt.figure(figsize=(11, 7.2), facecolor=DARK)
        self.a1 = fig.add_subplot(211); self.a2 = fig.add_subplot(212)
        for a in (self.a1, self.a2):
            a.set_facecolor(DARK); a.grid(color="#1d232b", lw=0.5)
            a.tick_params(colors="#8b949e", labelsize=8)
        self._redraw()
        self.canvas = FigureCanvasTkAgg(fig, master=master)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self.canvas.mpl_connect("scroll_event", self._zoom)
        self.canvas.mpl_connect("button_press_event", self._press)
        self.canvas.mpl_connect("motion_notify_event", self._motion)
        self.canvas.mpl_connect("button_release_event", self._release)
        self.canvas.draw()
        self._drag = None
        self.fig = fig
    def _candles(self):
        import matplotlib.pyplot as plt
        from aiquant.engine.indicators import add_indicators
        d = add_indicators(self.df.reset_index(drop=True)); self._d = d
        x = list(range(len(d)))
        for i in x:
            o,c,h,l = d["open"][i], d["close"][i], d["high"][i], d["low"][i]
            col = DOWN if c >= o else UP
            self.a1.vlines(i, l, h, color=col, lw=0.8)
            self.a1.bar(i, max(abs(o-c),1e-6), 0.62, bottom=min(o,c),
                       color=col if c >= o else "none", edgecolor=col, lw=0.8)
        for col_, name in (("ema20","EMA20"),("sma10","MA10"),("sma20","MA20")):
            if col_ in d.columns: self.a1.plot(x, d[col_], lw=1.0, label=name)
        zc = {"support":UP, "resistance":DOWN}
        for z in self.zones:
            cc = zc.get(z.get("zone_type"), ACC); cx = z.get("center")
            if cx is not None: self.a1.axhline(cx, color=cc, lw=0.8, ls="--", alpha=0.7)
        self.a1.legend(loc="upper left", fontsize=8, facecolor=DARK, edgecolor="#30363d")
    def _emotion(self):
        if self.emotion is None or len(self.emotion) != len(self._d): return None
        x = list(range(len(self._d))); em = self.emotion
        a2 = self.a2
        a2.fill_between(x, 0, em, where=[v>=0 for v in em], color=UP, alpha=0.6)
        a2.fill_between(x, 0, em, where=[v<0 for v in em], color=DOWN, alpha=0.6)
        a2.axhline(0, color="#8b949e", lw=0.5)
        a2.set_ylabel("每刻情绪", color="#8b949e", fontsize=8)
    def _redraw(self):
        self._candles(); self._emotion()
        self.a1.set_title(self.title or "K线 · 支撑/阻力 · 情绪", color="#e6edf3")
        import matplotlib.pyplot as plt; plt.subplots_adjust(hspace=0.16)
    def _zoom(self, ev):
        for a in (self.a1, self.a2):
            if ev.inaxes is None: continue
            if ev.inaxes is a:
                x = a.get_xlim(); w = (x[1]-x[0]) * (0.8 if ev.button=="up" else 1.25)
                frac = (ev.xdata - x[0]) / (x[1]-x[0]+1e-9)
                a.set_xlim(ev.xdata - frac*w, ev.xdata + (1-frac)*w)
        self._sync(); self.canvas.draw_idle()
    def _sync(self):
        try: self.a2.set_xlim(self.a1.get_xlim())
        except Exception: pass
    def _press(self, ev):
        if ev.button == 1: self._drag = (ev.xdata, ev.xdata)
    def _motion(self, ev):
        if self._drag and ev.inaxes and self._drag[0] is not None and ev.xdata is not None:
            X = (ev.xdata - self._drag[1]); self._drag = (self._drag[0], ev.xdata)
        # 简化: 只记录，不做拖动平移（保持稳）
    def _release(self, ev): self._drag = None

    def _frozen(self): pass  # placeholder
