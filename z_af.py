# -*- coding: utf-8 -*-
import py_compile, re
f=r"C:/Users/mine/Downloads/quant_research/aiquant/factor_mine.py"
t=open(f,encoding="utf-8").read()
# 1) extend FACTOR_NAMES
old_names = """FACTOR_NAMES = ["mom5","mom10","mom20","mom60","rsi14","macd","macd_dist","atr_pct",
"vol_ratio","ma20_dist","ma60_dist","volatility20","skew20","kurt20",
"ret_ratio","vol20_trend","close_pos","ema_ratio","obv_slope"]"""
new_names = '''FACTOR_NAMES = ["mom5","mom10","mom20","mom60","rsi14","macd","macd_dist","atr_pct",
"vol_ratio","ma20_dist","ma60_dist","volatility20","skew20","kurt20",
"ret_ratio","vol20_trend","close_pos","ema_ratio","obv_slope",
"mom13_ds","risk_t","mom13_norm"]'''
assert old_names in t, "names"
t=t.replace(old_names,new_names,1)
# 2) add the new factor computations in factor_df (before return)
old_ret = '''    o["ret_ratio"] = (o["mom20"] / (o["mom10"].abs().add(o["volatility20"].add(1e-9)))).fillna(0)'''
new_block = old_ret + '''
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
    o["mom_som"] = o["mom_som"].fillna(0)'''
assert old_ret in t, "ret"
t=t.replace(old_ret,new_block,1)
# 3) fix thresh reference (add a rollover alias is not needed; label uses thr explicitly)
open(f,"w",encoding="utf-8").write(t)
py_compile.compile(f, doraise=True)
print("factors added")
# smoke test
