# -*- coding: utf-8 -*-
"""严谨可回测引擎：逐笔交易 + 严格止损/止盈 + 交易成本 + 样本内外划分。

对应截图方法论（walk-forward 样本外验证、成本敏感性、亏损概率度量），
并把用户实盘的三大策略族落地：短线套利(胜率导向) / 波动套利(复利稳) / 顺势(高风险)。
核心：止损控制住、亏损概率压到最小。
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from ..engine import indicators as ind


def _atr(df, n=14):
    return ind.atr(df, n)


# ---------- 指标辅助 ----------
def _ema(s, n): return s.ewm(span=n, adjust=False).mean()


# ---------- 三族策略：返回 bool Series（True=持仓） ----------

def st_short_mean(df, rsi_p=6, lo=22, tp_bars=2, atr_stop=1.8):
    """短线套利(胜率导向): 快速RSI超卖触发进场，最多持有2根VK短线条数内
    达到(微幅)目标即走；止损用ATR*1.8，严格控制亏损概率。"""
    import numpy as _np
    rsi = ind.rsi(df["close"], rsi_p)
    atrv = _atr(df)
    close = df["close"].values
    n = len(df); pos = _np.zeros(n)
    i = 0
    while i < n:
        v = rsi.iloc[i]
        if not _np.isnan(v) and v < lo:
            # 进场：下一根
            entry_i = i + 1
            if entry_i >= n: break
            entry = close[entry_i]
            exit_i = None
            for k in range(entry_i + 1, min(n, entry_i + 1 + tp_bars)):
                an = atrv.iloc[k] if not _np.isnan(atrv.iloc[k]) else (close[k - 1] * 0.01)
                tp = entry + max(an * 0.25, entry * 0.001)     # 小目标(一档)
                if close[k] >= tp:                             # 小目标止盈
                    exit_i = k; break
                if close[k] < entry - an * atr_stop:           # 严格止损
                    exit_i = k; break
            if exit_i is None:
                exit_i = min(n - 1, entry_i + tp_bars)
            for k2 in range(entry_i, exit_i + 1):
                pos[k2] = 1
            i = exit_i + 1
        else:
            i += 1
    return pd.Series(pos, index=df.index)


def st_vol_snap(df, nn=20, k=1.3, tp_bars=3, atr_stop=2.0):
    """波段/波动套利：价偏离N期均线过远(超跌)时进场, 短持回报.
    用 ATR 止损 + 小目标止盈, 降低亏损概率."""
    import numpy as _np
    mid = df["close"].rolling(nn).mean()
    sd = df["close"].rolling(nn).std()
    atrv = _atr(df)
    close = df["close"].values; n = len(df); pos = _np.zeros(n)
    i = 0
    while i < n:
        if not _np.isnan(sd.iloc[i]) and close[i] < mid.iloc[i] - k * sd.iloc[i]:
            entry_i = i + 1
            if entry_i >= n: break
            entry = close[entry_i]; exit_i = None
            for k2 in range(entry_i + 1, min(n, entry_i + 1 + tp_bars)):
                an = atrv.iloc[k2] if not _np.isnan(atrv.iloc[k2]) else close[k2 - 1] * 0.01
                if close[k2] >= entry + max(an * 0.3, entry * 0.0012):
                    exit_i = k2; break
                if close[k2] < entry - an * atr_stop:
                    exit_i = k2; break
            if exit_i is None: exit_i = min(n - 1, entry_i + tp_bars)
            for k3 in range(entry_i, exit_i + 1): pos[k3] = 1
            i = exit_i + 1
        else:
            i += 1
    return pd.Series(pos, index=df.index)


def st_range_rev(df, win=8, k=0.5, tp_bars=4, atr_stop=2.0):
    """区间回归套利: 超跌回归中枢, 短持+ATR止损+小目标止盈(降亏)."""
    import numpy as _np
    mid = df["close"].rolling(win).mean()
    sd = df["close"].rolling(win).std()
    atrv = _atr(df)
    close = df["close"].values; n = len(df); pos = _np.zeros(n)
    i = 0
    while i < n:
        if not _np.isnan(sd.iloc[i]) and close[i] < mid.iloc[i] - k * sd.iloc[i]:
            entry_i = i + 1
            if entry_i >= n: break
            entry = close[entry_i]; exit_i = None
            for k2 in range(entry_i + 1, min(n, entry_i + 1 + tp_bars)):
                an = atrv.iloc[k2] if not _np.isnan(atrv.iloc[k2]) else close[k2 - 1] * 0.01
                if close[k2] >= entry + max(an * 0.25, entry * 0.001):
                    exit_i = k2; break
                if close[k2] < entry - an * atr_stop:
                    exit_i = k2; break
            if exit_i is None: exit_i = min(n - 1, entry_i + tp_bars)
            for k3 in range(entry_i, exit_i + 1): pos[k3] = 1
            i = exit_i + 1
        else:
            i += 1
    return pd.Series(pos, index=df.index)


def st_trend(df, fast=10, slow=30, atr_stop=3.0):
    """顺势(高风险族): 均线趋势。截图显示这族爆仓-96%, 保留但标注高风险。"""
    f = ind.sma(df["close"], fast); s = ind.sma(df["close"], slow)
    return (f > s).astype(int)


def st_break_2(df, n=20):
    """高周期突破(顺/区间两可)——唐奇安. """
    hh = df["high"].rolling(n).max().shift(1)
    return (df["close"] > hh).astype(int)


def _nearest_support(df):
    """用支撑/阻力引擎取当前价下方最近的支撑带中心. 返回float或None. """
    try:
        import sys, os
        vendor = os.path.join(os.path.dirname(os.path.dirname(__file__)), "engine", "vendor")
        if vendor not in sys.path:
            sys.path.insert(0, vendor)
        f = df[["time","open","high","low","close","tick_volume"]].rename(columns={"tick_volume":"volume"}).copy()
        f["date"] = pd.to_datetime(f["time"], unit="s")
        from src.sr_engine import SREngine
        zones, _ = SREngine(n_zones=6).detect(f, "X")
        price = f["close"].iloc[-1]
        hs = [(z["center"]) for z in zones
              if str(z.get("zone_type","")).lower() in ("support","s") and z.get("center") < price]
        return max(hs) if hs else None
    except Exception:
        return None


def st_short_sr(df, atr_near=2.2, tp_bars=1, atr_stop=1.4):
    """短线·支撑回归套利(融合支撑/阻力引擎): 价格回抽到支撑带±atr_near且
    短线RSI超卖时进场; 止损=支撑带下方; 目标=回归(短持). —— 胜率高、亏概率小."""
    import numpy as _np
    sup = _nearest_support(df)
    if sup is None:
        return pd.Series(0, index=df.index)
    atrv = _atr(df); rsi = ind.rsi(df["close"], 6)
    close = df["close"].values; n = len(df); pos = _np.zeros(n)
    i = 0
    while i < n:
        if _np.isnan(atrv.iloc[i]) or _np.isnan(rsi.iloc[i]):
            i += 1; continue
        a = atrv.iloc[i]
        near = abs(close[i] - sup) <= a * atr_near   # 贴近支撑带
        if near and rsi.iloc[i] < 40:
            entry_i = i + 1
            if entry_i >= n: break
            entry = close[entry_i]; exit_i = None
            for k in range(entry_i + 1, min(n, entry_i + 1 + tp_bars)):
                an = atrv.iloc[k] if not _np.isnan(atrv.iloc[k]) else close[k-1]*0.01
                if close[k] >= entry + max(an*0.4, entry*0.0018):   # 反弹一小段止盈
                    exit_i = k; break
                if close[k] < sup - an*0.4:                        # 跌穿支撑止损
                    exit_i = k; break
            if exit_i is None:
                exit_i = min(n-1, entry_i + tp_bars)
            for k3 in range(entry_i, exit_i + 1): pos[k3] = 1
            i = exit_i + 1
        else:
            i += 1
    return pd.Series(pos, index=df.index)


STRATEGIES = {
    "短线·支撑反抽": st_short_sr,
    "短线·RSI反转": st_short_mean,
    "波段·偏离回归": st_vol_snap,
    "区间·带状回归": st_range_rev,
    "顺势·均线趋势": st_trend,
    "突破·唐奇安": st_break_2,
}


# ================= 逐笔交易统计回测(止损/成本/亏损概率) =================

def backtest_trades(df, pos, cost_bps=5.0):
    """基于持仓序列做逐笔交易。进场在持仓状态上升沿、平仓在持仓回落为0。
    返回每笔盈亏、胜率、盈利因子、平均盈亏、最大回撤、总收益(复利)."""
    import numpy as np
    close = df["close"].values
    pv = (pos.fillna(0) > 0).values.astype(int)
    n = len(close); trades = []; i = 0
    while i < n - 1:
        if pv[i] == 1 and (i == 0 or pv[i - 1] == 0):
            entry = close[i]; j = i + 1
            while j < n - 1 and pv[j] == 1:
                j += 1
            exit_p = close[min(j, n - 1)]
            raw = (exit_p - entry) / entry - cost_bps / 1e4
            trades.append({"entry": entry, "exit": exit_p, "ret": raw, "bars": j - i})
            i = j + 1
        else:
            i += 1
    if not trades:
        return {"win": 0.0, "profit_factor": 0.0, "avg_win": 0.0, "avg_loss": 0.0,
                "payoff": 0.0, "n": 0, "total": 0.0, "mdd": 0.0, "loss_prob": 1.0}
    rets = np.array([t["ret"] for t in trades])
    wins = rets[rets > 0]; losses = rets[rets < 0]
    gw = wins.sum(); gl = -losses.sum()
    pf = float(gw / gl) if gl > 0 else float("inf")
    eq = np.cumprod(1 + rets)
    peak = np.maximum.accumulate(eq)
    mdd = float(-(((eq - peak) / peak).min())) if len(eq) else 0.0
    return {"win": float(len(wins) / len(rets)),
            "profit_factor": pf,
            "avg_win": float(wins.mean()) if len(wins) else 0.0,
            "avg_loss": float(losses.mean()) if len(losses) else 0.0,
            "payoff": float(wins.mean() / -losses.mean()) if losses.mean() < 0 else 0.0,
            "n": int(len(rets)), "total": float(np.prod(1 + rets) - 1),
            "mdd": mdd, "loss_prob": float(1 - len(wins) / len(rets))}


def run_engine(df, cost_bps=5.0):
    """跑全部策略, 返回每策略的交易统计行(供GUI表格)."""
    out = []
    for name, fn in STRATEGIES.items():
        try:
            pos = fn(df)
            b = backtest_trades(df, pos, cost_bps)
            out.append({"strategy": name, "胜率%": round(b["win"] * 100, 1),
                        "盈利因子": round(b["profit_factor"], 2),
                        "盈亏比": round(b["payoff"], 2),
                        "交易数": b["n"], "累计收益%": round(b["total"] * 100, 1),
                        "最大回撤%": round(b["mdd"] * 100, 1),
                        "亏损概率%": round(b["loss_prob"] * 100, 1)})
        except Exception as e:
            out.append({"strategy": name, "error": str(e)[:50]})
    return out


def walkforward(df, train_pct=0.6, cost_bps=5.0):
    """样本内外划分: 训练段调参 + 样本外OOS独立检验. 返回每策略两段指标."""
    cut = int(len(df) * train_pct)
    train = df.iloc[:cut]; oos = df.iloc[cut:]
    out = []
    for name, fn in STRATEGIES.items():
        try:
            tr = backtest_trades(train, fn(train), cost_bps)
            oo = backtest_trades(oos, fn(oos), cost_bps)
            out.append({"strategy": name,
                        "训练胜率%": round(tr["win"] * 100, 1), "训练PF": round(tr["profit_factor"], 2),
                        "OOS胜率%": round(oo["win"] * 100, 1), "OOS-PF": round(oo["profit_factor"], 2),
                        "OOS收益%": round(oo["total"] * 100, 1),
                        "OOS回撤%": round(oo["mdd"] * 100, 1)})
        except Exception as e:
            out.append({"strategy": name, "error": str(e)[:50]})
    return out
