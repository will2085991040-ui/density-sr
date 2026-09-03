# -*- coding: utf-8 -*-
"因子 + AI K线分析 + 因子挖掘 (sklearn/随机森林)。"
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path: sys.path.insert(0, HERE)
import numpy as np
import pandas as pd

FACTOR_NAMES = ["mom5","mom10","mom20","mom60","rsi14","macd","macd_dist","atr_pct",
"vol_ratio","ma20_dist","ma60_dist","volatility20","skew20","kurt20",
"ret_ratio","vol20_trend","close_pos","ema_ratio","obv_slope",
"mom_ds","mom_t","mom_som"]

def factor_df(df):
    d = df.copy()
    volc = "volume" if "volume" in d.columns else "tick_volume"
    close = d["close"].astype(float)
    hi = d["high"].astype(float); lo = d["low"].astype(float); vol = d[volc].astype(float)
    o = pd.DataFrame(index=d.index)
    for kk in (5,10,20,60):
        o["mom"+str(kk)] = (close / close.shift(kk) - 1).fillna(0)
    delta = close.diff()
    gain = delta.clip(lower=0).ewm(alpha=1/14, adjust=True).mean()
    loss = -delta.clip(upper=0).ewm(alpha=1/14, adjust=True).mean()
    rs = gain / loss.replace(0, np.nan)
    o["rsi14"] = (100 - 100/(1 + rs)).fillna(50)
    dif = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean()
    dea = dif.ewm(span=9, adjust=False).mean()
    o["macd"] = dif - dea
    o["macd_dist"] = ((dif - dea) / (close + 1e-9)).fillna(0)
    tr = pd.concat([hi-lo, (hi-close.shift()).abs(), (lo-close.shift()).abs()], axis=1).max(axis=1)
    atr = tr.ewm(span=14, adjust=False).mean()
    o["atr_pct"] = (atr / close).fillna(0)
    vma20 = vol.rolling(20).mean()
    o["vol_ratio"] = (vol / vma20.replace(0, np.nan)).fillna(0)
    ma20 = close.rolling(20).mean(); ma60 = close.rolling(60).mean()
    o["ma20_dist"] = (close/ma20 - 1).fillna(0)
    o["ma60_dist"] = (close/ma60 - 1).fillna(0)
    pc = close.pct_change()
    o["volatility20"] = pc.rolling(20).std().fillna(0)
    o["skew20"] = pc.rolling(20).skew().fillna(0)
    o["kurt20"] = pc.rolling(20).kurt().fillna(0)
    o["ret_ratio"] = (o["mom20"] / (o["mom10"].abs().add(o["volatility20"].add(1e-9)))).fillna(0)
    # ---- GitHub EP004 实证因子 (frank-quant/ai-trading-videos) ----
    # 1) DeepSeekMomentumXS: N 日动量(默认窗口13), 横截面区分度最强的原始动量
    dsw = 13
    o["mom_ds"] = (close / close.shift(dsw) - 1).fillna(0)
    # 2) XSRiskMomentum(Fable 正alpha): 风险调整动量=动量/实现波动 (t统计量式), 跳过快进反转
    skip = 1; W = 20
    logr = np.log(close / close.shift(1))
    m = close.shift(skip) / close.shift(skip + W) - 1.0
    v = logr.rolling(W, min_periods=W).std()
    o["mom_t"] = (m / (v + 1e-9)).fillna(0)
    # 3) 归一化动量(除以自身20日波动, 供横截面排序用)
    o["mom_som"] = (close / close.shift(12) - 1) / (logr.rolling(20, min_periods=5).std() + 1e-9)
    o["mom_som"] = o["mom_som"].fillna(0)
    lo20 = close.rolling(20).min(); hi20 = close.rolling(20).max()
    o["close_pos"] = ((close - lo20) / (hi20 - lo20).replace(0, np.nan)).fillna(0.5)
    o["vol20_trend"] = (vol.rolling(20).mean() / vol.rolling(60).mean() - 1).fillna(0)
    o["ema_ratio"] = (close.ewm(span=5).mean() / close.ewm(span=20).mean() - 1).fillna(0)
    obv = (np.sign(close.diff().fillna(0)) * vol).cumsum()
    o["obv_slope"] = (obv.diff(5) / (vol.mean() + 1e-9)).fillna(0)
    return o[list(FACTOR_NAMES)]

def label(df, horizon=5, thr=0.0):
    close = df["close"].astype(float)
    fut = close.shift(-horizon) / close - 1
    return pd.Series(np.where(fut > thr, 1, np.where(fut < -thr, -1, 0)), index=df.index)

def train(df, horizon=5):
    from sklearn.ensemble import RandomForestClassifier
    X = factor_df(df); y = label(df, horizon)
    m = (y != -1).values
    Xm, ym = X[m], y[m]
    if len(Xm) < 40: return None
    idx = np.random.RandomState(7).permutation(len(Xm))
    cut = int(len(Xm)*0.7)
    clf = RandomForestClassifier(n_estimators=140, min_samples_leaf=4, random_state=7, n_jobs=1)
    clf.fit(Xm.iloc[idx[:cut]], ym.iloc[idx[:cut]])
    pred = clf.predict(Xm.iloc[idx[cut:]])
    acc = float((pred == ym.iloc[idx[cut:]].values).mean())
    imp = pd.Series(clf.feature_importances_, index=FACTOR_NAMES).sort_values(ascending=False).to_dict()
    return clf, {"acc": acc, "samples": int(len(Xm)), "test": int(len(Xm)-cut), "horizon": horizon}, imp

def ai_analyze(df, symbol, n=120):
    nn = max(40, min(n, len(df)-6))
    F = factor_df(df.tail(nn)); last = F.iloc[-1]
    res = train(df.tail(nn), horizon=5)
    if res is None:
        return {"symbol": symbol, "signal": "数据不足", "confidence": 0.0, "factors": [], "metrics": None, "reason": "历史样本不足, 无法建模"}
    clf, metrics, imp = res
    probs = clf.predict_proba([last.values])[0]
    pm = {int(c): float(p) for c, p in zip(clf.classes_, probs)}
    up = pm.get(1, 0.0); fl = pm.get(0, 0.0); dn = pm.get(-1, 0.0)
    if up > dn and up > fl and up - fl > 0.02: signal, conf = "看多", up
    elif dn > up and dn > fl and dn - fl > 0.02: signal, conf = "看空", dn
    else: signal, conf = "观望", max(up, dn, fl)
    top = sorted(imp.items(), key=lambda kv: kv[1], reverse=True)[:6]
    factors = [{"name": k, "weight": float(v), "value": round(float(last[k]), 4)} for k, v in top]
    tops = ", ".join(str(k)+"(值"+format(last[k],".3f")+", 重要性"+str(int(v*100))+"%)" for k, v in top[:4])
    reason = "随机森林模型在 "+str(metrics["samples"])+" 条样本上训练(测试集准确率 "+str(int(metrics["acc"]*100))+"%), 未来 5 日方向判定为 "+signal+" , 置信度 "+str(int(conf*100))+"%。主要驱动因子: "+tops
    return {"symbol": symbol, "signal": signal, "confidence": round(float(conf), 3), "factors": factors, "metrics": metrics, "reason": reason}

def mine(pairs, horizon=5, topk=6):
    from sklearn.ensemble import RandomForestClassifier
    Xs = []; ys = []
    for df, sym in pairs:
        f = factor_df(df); y = label(df, horizon)
        m = (y != -1).values
        if len(np.where(m)[0]) < 10: continue
        Xs.append(f[m].values); ys.append(y[m].values)
    if not Xs: return {"rows": [], "ok": False, "note": "无有效样本"}
    X = np.vstack(Xs); y = np.concatenate(ys)
    # 提速: 采样上限控制训练体量, 保证 UI 秒出
    if len(X) > 26000:
        idx = np.random.RandomState(3).choice(len(X), 26000, replace=False)
        X, y = X[idx], y[idx]
    clf = RandomForestClassifier(n_estimators=70, min_samples_leaf=16, random_state=7)
    clf.fit(X, np.where(y > 0, 1, 0))
    imp = np.argsort(clf.feature_importances_)[::-1]
    rows = [{"rank": i+1, "factor": FACTOR_NAMES[int(idx)], "importance": round(float(clf.feature_importances_[int(idx)]), 4)} for i, idx in enumerate(imp[:topk])]
    return {"rows": rows, "ok": True, "samples": int(len(X))}