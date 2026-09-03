# -*- coding: utf-8 -*-
import os
k=r"C:/Users/mine/Downloads/quant_research/knowledge/ep004"
ess = """# EP004 实证量化策略知识库 (frank-quant/ai-trading-videos)
> 数据来源: EP004_four-llm-quant-benchmark 独立复现评测报告(样本外 2025-07~2026-07, 大盘 -45%)。

## 一、实证结论(最重要)
1. 真正有效的因子是「横截面相对强弱, 不是单资产的空势」。
2. Fable 5 是唯一有正 alpha(+7.9%)的模型: 用「风险调整动量」, 选股对了但仓位(34%净多头)在熊市亏。
3. DeepSeek V4 Flash 绝对收益最好(-7.1%)、回撤最小(14%); 空单+15.3%最强。
4. 验证集夏普 1.24~1.93, 样本外全部转负 -> 验证集污染 / 市场变天是主因, 不是调参。
5. 有效风控: 每仓灾难止损 -30%, 排名退出+滞回缓冲降换手, mini_hold 最短持有。

## 二、两个实证有效的因子(已内置进 factor_mine)
### A. DeepSeekMomentumXS
factor_score = close[t] / close[t-mom_window] - 1   (N日简单动量)
- mom_window 10~28d, 甜点区 10~18d, 默认 13; 横截面排序多top/空bottom

### B. XSRiskMomentum(Fable 正alpha)
score = ( close[t-skip]/close[t-skip-W] - 1 ) / realized_vol_W
- skip 前几天避开短反转, realized_vol_W = 同窗口log收益滚动std
- 把动量变 t 统计量, 偏向沉稳趋势, 避开单根 pump 大阳线

## 三、组合与风控(可复用经验)
- 排序: 横截面 rank; 不按个币z评分
- 换手: exit_buffer 滞回带 + mini_hold, 降双边 6bps 成本
- 下行风控: 每仓灾难止损 -30%; mini_hold 不阻断止损/爆仓
- 杠杆固定 1x

## 四、诚实局限
- 样本外熊市(-45%)/训练验证牛市: 最诚实压力测试非中性样本
- 幸存者偏差: 20 币 2026 回看选; 滑点乐观(扁6bps无冲击模型)
"""
open(os.path.join(k,"STRATEGY_ESSENCE.md"),"w",encoding="utf-8").write(ess)
print("essence written", len(ess))
