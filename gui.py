# -*- coding: utf-8 -*-
"""aiquant — AI 量化盯盘交易系统 (tkinter, 无 PyQt)。

主界面: AI 盯盘可视化终端（左侧 AI 判读面板 + 中央真实 K 线 + 右侧明细）。
子页: 情绪/盯盘 · 完整HTML报告 · 6策略回测 · 全市场扫荡。
全程可离线：双智能体+离线AI因子给出 AI 级判读；配置 api_key 后自动追加 LLM 解读。
"""
from __future__ import annotations
import os, sys, threading, webbrowser, io

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

MARKETS = ("A股", "MT5", "OKX", "指数")
TFS = ("daily", "60min", "15min", "5min")

# ---- 暗色终端配色（贴合参考终端九成） ----
BG      = "#0d1117"   # 主背景
BG_PANEL= "#161b22"   # 面板
BG_CARD = "#1c2129"   # 卡片
BORDER  = "#30363d"
ACCENT  = "#58a6ff"   # 蓝
ACCENT2 = "#e3b341"   # 琥珀
UP      = "#3fb950"   # 涨(绿)
DOWN    = "#f85149"   # 跌(红)
TXT     = "#e6edf3"
TXT_DIM = "#8b949e"
CHART_BG= "#0d1117"

def _today():
    import datetime
    return datetime.date.today().strftime("%Y-%m-%d")

def _apply_dark_theme():
    import tkinter.ttk as _ttk
    st = _ttk.Style()
    try: st.theme_use("clam")
    except Exception: pass
    for w, bg, fg in (("TFrame", BG, TXT), ("TLabel", BG, TXT),
                      ("TButton", BG_PANEL, TXT), ("TCheckbutton", BG, TXT),
                      ("TCombobox", BG_PANEL, TXT), ("TEntry", BG_PANEL, TXT)):
        st.configure(w, background=bg, foreground=fg, fieldbackground=BG_PANEL)
    st.configure("TButton", padding=6, bordercolor=BORDER, focusthickness=0)
    st.map("TButton", background=[("active", "#1f2733"), ("pressed", "#1b2734")])
    st.configure("Title.TLabel", background=BG, foreground=TXT, font=("Microsoft YaHei", 12, "bold"))
    st.configure("Dim.TLabel", background=BG, foreground=TXT_DIM, font=("Microsoft YaHei", 8))
    st.configure("Accent.TButton", background=ACCENT, foreground="#0d1117", font=("Microsoft YaHei", 9, "bold"))
    st.map("Accent.TButton", background=[("active", "#79c0ff")])
    st.configure("Sidebar.TButton", background=BG, foreground=TXT_DIM, anchor="w", font=("Microsoft YaHei", 10))
    st.map("Sidebar.TButton", background=[("active", BG_PANEL)], foreground=[("active", TXT)])
    st.configure("TNotebook", background=BG, borderwidth=0)
    st.configure("TNotebook.Tab", background=BG_PANEL, foreground=TXT_DIM, padding=(10,5))
    st.map("TNotebook.Tab", background=[("selected", ACCENT)], foreground=[("selected", "#0d1117")])
    st.configure("TTreeview", background=BG_CARD, fieldbackground=BG_CARD, foreground=TXT, bordercolor=BORDER)
    st.map("TTreeview", background=[("selected", ACCENT)])
    st.configure("TTreeview.Heading", background=BG_PANEL, foreground=TXT, relief="flat")


class AiquantApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("aiquant · 量化监控终端  V3.2 · MULTI-ASSET · 多模块")
        self.geometry("1360x820")
        self.minsize(1080, 700)
        self.configure(bg=BG)
        self._cat = None
        self._sent = {}
        self._img_ref = None
        _apply_dark_theme()
        topbar = ttk.Frame(self); topbar.pack(side="top", fill="x")
        ttk.Label(topbar, text="AIQUANT  RESEARCH", style="Title.TLabel").pack(side="left", padx=14, pady=8)
        ttk.Label(topbar, text="量化监控终端 · 离线AI引擎 · 双智能体", style="Dim.TLabel").pack(side="left", padx=4)
        ttk.Label(topbar, text="● 本地数据已装载 · 4273 品种可扫", style="Dim.TLabel").pack(side="right", padx=14)
        ttk.Label(topbar, text="数据截至 " + _today(), style="Dim.TLabel").pack(side="right")
        body = ttk.Frame(self); body.pack(fill="both", expand=True)
        nav = ttk.Frame(body, width=180); nav.pack(side="left", fill="y"); nav.pack_propagate(False)
        ttk.Label(nav, text="MODULES", style="Dim.TLabel").pack(anchor="w", padx=12, pady=(10,4))
        nb = ttk.Notebook(body); nb.pack(side="left", fill="both", expand=True)
        self.nb = nb
        mods = (("AI盯盘·可视化","AI盯盘终端"),("情绪·盯盘","情绪/热评"),("完整HTML分析","HTML报告"),("策略解析回测","严谨回测"),("全市场支撑/阻力","批量识别"))
        self._tab_home = ttk.Frame(nb); nb.add(self._tab_home, text=mods[0][1])
        self._tab_news = ttk.Frame(nb); nb.add(self._tab_news, text=mods[1][1])
        self._tab_rep  = ttk.Frame(nb); nb.add(self._tab_rep, text=mods[2][1])
        self._tab_bt   = ttk.Frame(nb); nb.add(self._tab_bt, text=mods[3][1])
        self._tab_scan = ttk.Frame(nb); nb.add(self._tab_scan, text=mods[4][1])
        for idx, (name, _) in enumerate(mods):
            ttk.Button(nav, text=name, style="Sidebar.TButton", command=lambda x=idx: self._goto(x)).pack(fill="x", padx=8, pady=2)
        self._build_home()
        self._build_news(); self._build_report(); self._build_bt(); self._build_scan()
        self.status = tk.Label(self, text="就绪 · 数据源: 大A量化监控系统 · 全离线", bg=BG_PANEL, fg=TXT_DIM, anchor="w")
        self.status.pack(side="bottom", fill="x", ipady=3)
        self.after(600, self.do_viz)

    def _goto(self, idx):
        try:
            self.nb.select(idx)
        except Exception:
            pass
    # ---------- helpers ----------
    def cat(self):
        if self._cat is None:
            from aiquant.market import MarketCatalog
            self._cat = MarketCatalog()
        return self._cat

    def _resolve_sym(self, market, query):
        q = (query or "").strip()
        if not q: return q
        if market != "A股": return q.upper()
        import re
        if re.fullmatch(r"\d{6}", q): return q
        try:
            from aiquant.market import names
            hits = names.find_by(q)
            if hits: return hits[0][0]
        except Exception:
            pass
        return q

    def _load(self, market, sym, tf):
        from aiquant.market import load
        return load(self.cat(), market, sym, tf)

    # ============ 🔔 主界面 : AI 盯盘可视化终端 ============
    def _build_home(self):
        f = self._tab_home
        top = ttk.Frame(f); top.pack(fill="x", padx=8, pady=6)
        ttk.Label(top, text="市场:").pack(side="left")
        self.v_mkt = ttk.Combobox(top, values=MARKETS, width=7); self.v_mkt.set("A股")
        self.v_mkt.pack(side="left")
        ttk.Label(top, text="代码/名称:").pack(side="left", padx=(8,0))
        self.v_sym = ttk.Entry(top, width=13); self.v_sym.insert(0, "贵州茅台")
        self.v_sym.pack(side="left", padx=4)
        ttk.Label(top, text="周期:").pack(side="left")
        self.v_tf = ttk.Combobox(top, values=TFS, width=7); self.v_tf.set("daily")
        self.v_tf.pack(side="left", padx=4)
        ttk.Button(top, text="AI一键研判 (K线+双智能体)", command=self.do_viz).pack(side="left", padx=6)
        ttk.Button(top, text="HTML完整分析", command=self.do_viz_html).pack(side="left", padx=4)
        ttk.Button(top, text="抓最新新闻", command=self.easy_news).pack(side="left", padx=4)

        body = ttk.Frame(f); body.pack(fill="both", expand=True, padx=8, pady=4)
        self.panel = ttk.LabelFrame(body, text="🤖 AI 自动盯盘判读", width=250)
        self.panel.pack(side="left", fill="y", padx=(0,6)); self.panel.pack_propagate(False)
        self.agent_txt = tk.Label(self.panel, text="正在加载并分析...", justify="left",
                                  font=("Microsoft YaHei", 10), anchor="nw",
                                  wraplength=230, bg="#f7f9fc", pady=2)
        self.agent_txt.pack(fill="both", expand=True, padx=6, pady=4)
        ttk.Label(self.panel, text="支撑/阻力带 (杠杆带叠加K线)", font=("Microsoft YaHei", 9, "bold")).pack(anchor="w", padx=6)
        self.sr_tree2 = ttk.Treeview(self.panel, columns=("t", "d"), show="headings", height=5)
        self.sr_tree2.heading("t", text="类型"); self.sr_tree2.heading("d", text="中心价")
        self.sr_tree2.column("t", width=80, anchor="center"); self.sr_tree2.column("d", width=80, anchor="center")
        self.sr_tree2.pack(fill="x", padx=6, pady=2)
        self.sr_tree = self.sr_tree2

        mid = ttk.Frame(body); mid.pack(side="left", fill="both", expand=True)
        ct = ttk.Frame(mid); ct.pack(fill="x")
        ttk.Button(ct, text="选择查看日期", command=self.watch_date_pick).pack(side="left", padx=4, pady=2)
        ttk.Label(ct, text="滚轮缩放 · 拖动平移 · 日期切换时段 · 下部=每时刻情绪", foreground="#8b949e").pack(side="left")
        self.k_canvas = tk.Frame(mid, bg="#0d1117")
        self.k_canvas.pack(fill="both", expand=True)

        self.v_box = scrolledtext.ScrolledText(body, width=30, wrap="word")
        self.v_box.pack(side="right", fill="y", padx=(4,0))

        ttk.Label(f, text="支持鼠标滚轮页面缩放（画布自适应） · AI 自动判读市场情绪，无需手工紧盯",
                  foreground="#666").pack(side="bottom", pady=2)

    def do_viz(self):
        mkt = self.v_mkt.get() or "A股"
        sym = self._resolve_sym(mkt, self.v_sym.get())
        tf = self.v_tf.get() or "daily"
        if not sym: return
        self.status.config(text="AI 盯盘中: %s %s (%s) ..." % (mkt, sym, tf))
        threading.Thread(target=self._viz_worker, args=(mkt, sym, tf), daemon=True).start()

    def _viz_worker(self, mkt, sym, tf):
        try:
            from aiquant.report.report import _apply_font
            _apply_font()
            # 研判
            u = self._unify(mkt, sym, tf)
            s = None
            try:
                from aiquant.features.sentiment import sentiment
                s = sentiment(symbol=sym)
            except Exception:
                s = None
            df = self._load(mkt, sym, tf)
            zones = self._sr_zones_for(df)
            self.after(0, lambda: self._viz_done(mkt, sym, tf, u, s, df, zones))
        except Exception as e:
            import traceback; traceback.print_exc()
            self.after(0, lambda: messagebox.showerror("盯盘", str(e)))

    def _sr_zones_for(self, df):
        """用 vendored SREngine 识别支撑/阻力带。"""
        import pandas as _pd
        from src.sr_engine import SREngine
        try:
            f = df.rename(columns={"tick_volume": "volume"}).copy()
            f["date"] = _pd.to_datetime(f["time"], unit="s")
            zones, _ = SREngine(n_zones=8).detect(f, "sym")
            return zones or []
        except Exception:
            return []

    def _unify(self, mkt, sym, tf):
        from aiquant.agents.integrate import unify
        from aiquant.market import load
        df = self._load(mkt, sym, tf)
        if df is None or len(df) < 30:
            raise RuntimeError("数据不足")
        return unify(df, stance="稳")

    def _viz_done(self, mkt, sym, tf, u, s, df, zones):
        from aiquant.ui.watch import WatchChart
        if getattr(self, "_wc", None) is not None:
            try: self._wc.canvas.get_tk_widget().destroy()
            except Exception: pass
        self._sr_list_zones = zones
        d = df.copy()
        wd = getattr(self, "w_date", None)
        if wd is not None:
            lo, hi = wd
            dt = pd.to_datetime(d["time"], unit="s")
            d = d[(dt >= lo) & (dt <= hi)].reset_index(drop=True)
            if len(d) < 15: d = df.copy()
        self._wc = WatchChart(self.k_canvas, d, zones,
                              title="%s %s (%s) · 支撑/阻力 + 每时刻情绪" % (sym, mkt, tf))
        self.agent_txt.config(text=self._panel_text(u, s) if s else (u.get("narrative") or "已载入"))
        self.v_box.delete("1.0", "end")
        self.v_box.insert("end", "%s · %s · %s\n" % (mkt, sym, tf))
        self.v_box.insert("end", "双智能体研判: " + (u.get("narrative") or "") + "\n")
        if s:
            for i, n in enumerate(s.get("news", [])[:6], 1):
                self.v_box.insert("end", "%d. %s\n" % (i, n))
        if u.get("llm"):
            self.v_box.insert("end", "\n[LLM] " + u["llm"] + "\n")
        self.sr_tree.delete(*self.sr_tree.get_children())
        for z in zones[:6]:
            self.sr_tree.insert("", "end", values=(str(z.get("zone_type")), "%.4f" % z.get("center")))
        self.status.config(text="✅ 交互看盘完成: %s %s (%s) · 滚轮缩放/拖动/日期" % (mkt, sym, tf))

    def watch_date_pick(self):
        from tkinter import simpledialog
        ans = simpledialog.askstring("查看指定日期", "输入范围(逗号分隔) 例: 2026-01-01,2026-08-20 \\n留空=全部", parent=self)
        if not ans: return
        try:
            import datetime as _d
            a, b = [x.strip() for x in ans.split(",")]
            lo = _d.datetime.strptime(a, "%Y-%m-%d")
            hi = _d.datetime.strptime(b, "%Y-%m-%d") if b else lo
        except Exception:
            messagebox.showwarning("日期", "格式: YYYY-MM-DD,YYYY-MM-DD"); return
        self.w_date = (lo, hi)
        self.status.config(text="已选日期窗口 %s ~ %s · 重新绘制" % (lo.date(), hi.date()))
        if self.v_sym.get():
            self.do_viz()

    def _panel_text(self, u, s):
        c = u["consensus"]; sig = u["signal"]; fac = u["factor"]
        L = []
        L.append("（AI 自动盯盘结论）")
        L.append("◆ 方向: %s  %s" % (c.get("direction") or "中性", c.get("order")))
        L.append("◆ 置信: %s%%" % c.get("confidence"))
        L.append("◆ 情绪: %s%s" % (s.get("label") if s else "—",
                (" " + str(s.get("score"))) if s else ""))
        L.append("◆ 双智能体:")
        L.append("    稳: %s %s" % (sig.get("order"), sig.get("direction") or "-"))
        L.append("◆ 离线AI因子: %s(%s)" % (fac.get("verdict"), fac.get("composite")))
        L.append("◆ 支撑: %s" % (("%.4f" % sig["support"]) if sig.get("support") else "—"))
        L.append("◆ 阻力: %s" % (("%.4f" % sig["resistance"]) if sig.get("resistance") else "—"))
        if fac.get("recommendation"):
            r = fac["recommendation"]
            L.append("◆ 参考: 入%s 停%s 标%s" % (r.get("entry"), r.get("stop"), r.get("target")))
        if s and s.get("top"):
            L.append("◆ 词云: %s" % "、".join(s["top"][:6]))
        return "\n".join(L)

    def do_viz_html(self):
        mkt = self.v_mkt.get() or "A股"; sym = self._resolve_sym(mkt, self.v_sym.get())
        tf = self.v_tf.get() or "daily"
        threading.Thread(target=self._html_worker, args=(mkt, sym, tf), daemon=True).start()

    def easy_news(self):
        mkt = "A股"; sym = self._resolve_sym(mkt, self.v_sym.get()) or "600519"
        threading.Thread(target=self._sent_worker, args=(sym,), daemon=True).start()

    def _html_worker(self, mkt, sym, tf):
        try:
            from aiquant.engine.indicators import add_indicators
            from aiquant.engine.signals import run_signal
            from aiquant.backtest.strategies import compare
            from aiquant.features.sentiment import sentiment
            from aiquant.report import report as R
            df = self._load(mkt, sym, tf)
            if df is None: return self.after(0, lambda: messagebox.showwarning("HTML", "无数据"))
            df = add_indicators(df)
            sig = run_signal(df, "稳"); strat = compare(df)
            s = None
            try: s = sentiment(symbol=sym)
            except Exception: s = None
            path = os.path.join(ROOT, "out", "report_%s_%s.html" % (sym, tf))
            os.makedirs(os.path.dirname(path), exist_ok=True)
            R.build_report(df, sig, s, strat, path, symbol="%s %s" % (mkt, sym))
            self.after(0, lambda: webbrowser.open("file:///" + path))
            self.after(0, lambda: self.status.config(text="HTML报告: %s" % path))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("HTML", str(e)))

    # ============ ① 情绪 / 盯盘 ============
    def _build_news(self):
        f = self._tab_news
        top = ttk.Frame(f); top.pack(fill="x", padx=8, pady=6)
        ttk.Label(top, text="市场:").pack(side="left")
        self.sy_mkt1 = ttk.Combobox(top, values=MARKETS, width=8); self.sy_mkt1.set("A股")
        self.sy_mkt1.pack(side="left")
        ttk.Label(top, text="代码/名称:").pack(side="left", padx=(10,0))
        self.e_code = ttk.Entry(top, width=12); self.e_code.insert(0, "贵州茅台")
        self.e_code.pack(side="left", padx=4)
        ttk.Button(top, text="爬新闻 + AI情绪打分", command=self.do_sentiment).pack(side="left", padx=4)
        ttk.Button(top, text="生成情绪HTML", command=self.sent_report).pack(side="left", padx=4)
        self.news_box = scrolledtext.ScrolledText(f, height=22, wrap="word")
        self.news_box.pack(fill="both", expand=True, padx=8, pady=4)
        self.sent_lbl = ttk.Label(f, text="情绪: --", font=("Microsoft YaHei", 11, "bold"))
        self.sent_lbl.pack(pady=4)

    def do_sentiment(self):
        mkt = self.sy_mkt1.get() or "A股"
        code = self._resolve_sym(mkt, self.e_code.get())
        if not code: return
        threading.Thread(target=self._sent_worker, args=(code,), daemon=True).start()

    def _sent_worker(self, code):
        try:
            from aiquant.features.sentiment import sentiment
            s = sentiment(symbol=code)
            self._sent[code] = s
            self.after(0, lambda: self._render_sent(code, s))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("情绪", str(e)))

    def _render_sent(self, code, s):
        self.news_box.delete("1.0", "end")
        self.news_box.insert("end", "【%s】 情绪: %s (%.3f · %s)\n" % (code, s.get("label"), s.get("score",0), s.get("source","")))
        self.news_box.insert("end", "-"*60 + "\n")
        for i, n in enumerate(s.get("news", [])[:15], 1):
            self.news_box.insert("end", "%2d. %s\n" % (i, n))
        self.sent_lbl.config(text="情绪: %s (%.3f)" % (s.get("label"), s.get("score",0)))

    def sent_report(self):
        mkt = self.sy_mkt1.get() or "A股"
        code = self._resolve_sym(mkt, self.e_code.get()) or "600519"
        s = self._sent.get(code)
        if s is None:
            from aiquant.features.sentiment import sentiment
            s = sentiment(symbol=code)
        try:
            from aiquant.report.sentiment_html import render
            path = os.path.join(ROOT, "out", "sentiment_%s.html" % code)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            render(s, code, path)
            webbrowser.open("file:///" + path)
        except Exception as e:
            messagebox.showerror("情绪HTML", str(e))

    # ============ ② 完整 HTML 报告 ============
    def _build_report(self):
        f = self._tab_rep
        top = ttk.Frame(f); top.pack(fill="x", padx=8, pady=6)
        ttk.Label(top, text="市场:").pack(side="left")
        self.cmb_mkt = ttk.Combobox(top, values=MARKETS, width=8); self.cmb_mkt.set("A股")
        self.cmb_mkt.pack(side="left")
        ttk.Label(top, text="代码/名称:").pack(side="left", padx=(8,0))
        self.e_rep_sym = ttk.Entry(top, width=12); self.e_rep_sym.insert(0, "600519")
        self.e_rep_sym.pack(side="left", padx=4)
        ttk.Label(top, text="周期:").pack(side="left")
        self.cmb_tf = ttk.Combobox(top, values=TFS, width=7); self.cmb_tf.set("daily")
        self.cmb_tf.pack(side="left", padx=4)
        ttk.Label(top, text="风格:").pack(side="left")
        self.cmb_s = ttk.Combobox(top, values=["稳","激进"], width=5); self.cmb_s.set("稳")
        self.cmb_s.pack(side="left", padx=4)
        ttk.Button(top, text="生成完整HTML报告", command=self.full_report).pack(side="left", padx=6)
        self.out_box = scrolledtext.ScrolledText(f, height=20, wrap="word")
        self.out_box.pack(fill="both", expand=True, padx=8, pady=4)

    def full_report(self):
        threading.Thread(target=self._html_worker,
                         args=(self.cmb_mkt.get() or "A股",
                               self._resolve_sym(self.cmb_mkt.get(), self.e_rep_sym.get()),
                               self.cmb_tf.get() or "daily"),
                         daemon=True).start()

    # ============ ③ 6 策略回测 ============
    def _build_bt(self):
        f = self._tab_bt
        top = ttk.Frame(f); top.pack(fill="x", padx=8, pady=6)
        ttk.Label(top, text="市场:").pack(side="left")
        self.cmb_bt = ttk.Combobox(top, values=MARKETS, width=9); self.cmb_bt.set("A股")
        self.cmb_bt.pack(side="left")
        ttk.Label(top, text="代码/名称:").pack(side="left", padx=(8,0))
        self.e_bt = ttk.Entry(top, width=12); self.e_bt.insert(0, "600519")
        self.e_bt.pack(side="left", padx=4)
        ttk.Label(top, text="周期:").pack(side="left")
        self.cmb_bt_tf = ttk.Combobox(top, values=TFS, width=7); self.cmb_bt_tf.set("daily")
        self.cmb_bt_tf.pack(side="left", padx=4)
        ttk.Button(top, text="严谨竹测(止损/胜率/盈亏比/OOS)", command=self.do_bt).pack(side="left", padx=6)
        ttk.Label(top, text="成本bp:").pack(side="left", padx=(8,0))
        self.e_cost = ttk.Entry(top, width=6); self.e_cost.insert(0, "5")
        self.e_cost.pack(side="left", padx=4)
        self.cb_oos = tk.BooleanVar(value=True)
        ttk.Checkbutton(top, text="样本外OOS验证", variable=self.cb_oos).pack(side="left", padx=6)
        self.bt_tree = ttk.Treeview(f, columns=("name","win","pf","payoff","n","return","mdd","lossp"), show="headings", height=15)
        for c_, t_, w in (("name","策略",90),("win","胜率%",70),("pf","盈利因子",80),("payoff","盈亏比",70),
                          ("n","交易数",60),("return","累计收益%",90),("mdd","最大回撤%",90),("lossp","亏损概率%",90)):
            self.bt_tree.heading(c_, text=t_); self.bt_tree.column(c_, width=w, anchor="center")
        self.bt_tree.pack(fill="both", expand=True, padx=8, pady=4)
        self.bt_note = ttk.Label(f, text="", foreground="#555")
        self.bt_note.pack(anchor="w", padx=10, pady=2)

    def do_bt(self):
        threading.Thread(target=self._bt_worker, daemon=True).start()

    def _bt_worker(self):
        mkt = self.cmb_bt.get(); sym = self._resolve_sym(mkt, self.e_bt.get())
        tf = self.cmb_bt_tf.get() or "daily"
        try:
            cost = float(self.e_cost.get() or 5)
            from aiquant.backtest.engine import run_engine, walkforward
            df = self._load(mkt, sym, tf)
            if df is None: return self.after(0, lambda: messagebox.showwarning("回测", "无数据"))
            rows = run_engine(df, cost_bps=cost)
            oos = walkforward(df, cost_bps=cost) if self.cb_oos.get() else None
            self.after(0, lambda: self._render_bt(rows, oos))
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("回测", str(e)))

    def _render_bt(self, rows, oos=None):
        for it in self.bt_tree.get_children():
            self.bt_tree.delete(it)
        for r in rows:
            if "error" in r:
                self.bt_tree.insert("", "end", values=(r["strategy"], "ERR", "", "", "", "", "", ""))
            else:
                self.bt_tree.insert("", "end", values=(r["strategy"], r["胜率%"], r["盈利因子"], r["盈亏比"],
                    r["交易数"], r["累计收益%"], r["最大回撤%"], r["亏损概率%"]))
        if oos:
            t = " | ".join("%s: OOS胜率%s %% PF%s 收益%s%%" % (x["strategy"], x["OOS胜率%"], x["OOS-PF"], x["OOS收益%"])
                           for x in oos if "error" not in x)
            self.bt_note.config(text="样本外(OOS)验证: " + t[:200])

    # ============ ④ 全市场扫荡 ============
    def _build_scan(self):
        f = self._tab_scan
        top = ttk.Frame(f); top.pack(fill="x", padx=8, pady=6)
        ttk.Label(top, text="扫描市场:").pack(side="left")
        self.cmb_sc = ttk.Combobox(top, values=("A股","MT5","OKX"), width=9); self.cmb_sc.set("A股")
        self.cmb_sc.pack(side="left")
        ttk.Label(top, text="风格:").pack(side="left", padx=(8,0))
        self.cmb_sc_s = ttk.Combobox(top, values=("激进","稳"), width=5); self.cmb_sc_s.set("激进")
        self.cmb_sc_s.pack(side="left", padx=4)
        self.btn_scan = ttk.Button(top, text="批量识别全市场支撑/阻力位", command=self.do_scan)
        self.btn_scan.pack(side="left", padx=6)
        ttk.Button(top, text="导出CSV", command=self.export_sr_csv).pack(side="left", padx=4)
        ttk.Button(top, text="导出HTML报告", command=self.export_sr_html).pack(side="left", padx=4)
        self.scan_box = scrolledtext.ScrolledText(f, height=24, wrap="word")
        self.scan_box.pack(fill="both", expand=True, padx=8, pady=4)
        self._sr_rows = []

    def do_scan(self):
        self.btn_scan.config(state="disabled")
        self.scan_box.delete("1.0", "end")
        threading.Thread(target=self._scan_worker, daemon=True).start()

    def _scan_worker(self):
        mkt = self.cmb_sc.get()
        try:
            from aiquant.market.batch_sr import scan_market
            rows, errs = scan_market(self.cat(), mkt, "daily", "long", 6, limit=4000,
                                     on_progress=lambda d,t,nr: self.after(0, lambda: self._set_scan_prog(d, t, nr)))
            self._sr_rows = rows
            self.after(0, lambda: self._render_scan(rows))
        except Exception as e:
            import traceback; traceback.print_exc()
            self.after(0, lambda: (self.btn_scan.config(state="normal"), messagebox.showerror("批量识别", str(e))))

    def _set_scan_prog(self, d, t, nr):
        self.scan_box.delete("1.0", "end")
        self.scan_box.insert("end", "扫描中 ... %d/%d   已识别 %d 只" % (d, t, nr))

    def _render_scan(self, rows):
        self.scan_box.delete("1.0", "end")
        if not rows:
            self.scan_box.insert("end", "未识别到支撑/阻力位(数据不足或概率模型异常)")
            self.btn_scan.config(state="normal"); return
        self.scan_box.insert("end", "全市场支撑/阻力位批量识别完成(按有效概率=触及x守住 降序):\n\n")
        hdr = "%-8s %-8s %-7s %-9s %-9s %-6s %-6s %-6s %-4s %s" % ("代码","现价","涨跌%","最近支撑","最近压力","触及%","守住%","有效%","事件","趋势")
        self.scan_box.insert("end", hdr + "\n" + "-"*72 + "\n")
        for r in rows[:400]:
            line = "%-8s %-8.2f %+7.2f %-10s %-10s %-6s %-6s %-6s %-4d %s" % (
                r["symbol"], r["current_price"], r["change_pct"],
                ("%.4f"%r["nearest_support"]) if r["nearest_support"] is not None else "-",
                ("%.4f"%r["nearest_resistance"]) if r["nearest_resistance"] is not None else "-",
                ("%.0f"%(r["p_touch"]*100)) if r["p_touch"] is not None else "-",
                ("%.0f"%(r["p_hold"]*100)) if r["p_hold"] is not None else "-",
                ("%.0f"%(r["p_effective"]*100)) if r["p_effective"] is not None else "-",
                r["n_events"] or 0, r["trend_label"])
            self.scan_box.insert("end", line + "\n")
        self.scan_box.insert("end", "\n共 %d 只 · 概率来自 130训练/130互斥 走查回测模型" % len(rows))
        self.btn_scan.config(state="normal")
        self.status.config(text="批量支撑/阻力位识别完成: %d 只" % len(rows))

    def export_sr_csv(self):
        if not self._sr_rows:
            messagebox.showinfo("导出", "请先执行批量识别"); return
        try:
            from aiquant.market.batch_sr import to_csv
            path = os.path.join(ROOT, "out", "batch_sr.csv")
            os.makedirs(os.path.dirname(path), exist_ok=True)
            to_csv(self._sr_rows, path)
            self.status.config(text="CSV已导出: %s (%d 行)" % (path, len(self._sr_rows)))
        except Exception as e:
            messagebox.showerror("CSV", str(e))

    def export_sr_html(self):
        if not self._sr_rows:
            messagebox.showwarning("导出", "请先执行批量识别"); return
        try:
            from aiquant.market.batch_sr import to_html
            path = os.path.join(ROOT, "out", "batch_sr.html")
            os.makedirs(os.path.dirname(path), exist_ok=True)
            to_html(self._sr_rows, path, "全市场支撑/阻力批量识别")
            import webbrowser; webbrowser.open("file:///" + path)
            self.status.config(text="HTML已导出: " + path)
        except Exception as e:
            messagebox.showerror("HTML", str(e))


def main():
    app = AiquantApp()
    return app


def run():
    app = AiquantApp()
    app.mainloop()


if __name__ == "__main__":
    run()

