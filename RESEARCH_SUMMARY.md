# 四项目源码研究总结 + 批量全市场支撑阻力位工具构建规划

> 生成时间：由 AI agent 基于对 4 个 GitHub 项目的实际源码研读完成
> 工作目录：C:\Users\mine\Downloads\quant_research\

## 一、4 个项目的定位与本任务的关系

| 项目 | 定位 | 支撑/阻力算法 | 与任务关系 |
|------|------|--------------|-----------|
| **Detect_support_and_resistance_levels** (rosemarycox5334-debug) | 本地化 S/R 检测 Web 工具，V3 融合算法 | ✅ **核心算法**（V3Fusion，回测验证过） | **直接采用**：批量扫描全市场 |
| **AlphaMaster** (rosemarycox5334-debug) | RL 因子挖掘中心（MT5/OKX/通达信/天勤） | ❌ 无 | **数据层复用**：MT5/Parquet/A股批量取数 |
| **vnpy/VeighNa** | 开源量化框架（事件驱动+插件化） | ❌ 无 | **数据抽象借鉴**：BarData 契约、AlphaLab 全市场长表 |
| **abupy/阿布量化** (bbfamily) | 综合量化框架 | ⚠️ TLineBu 趋势线 S/R（多项式拟合+BFGS+KMeans） | **算法对照**：经典水平价位 S/R 才是主目标 |

关键结论：**唯一带"批量识别全市场支撑阻力位"现成实现的只有 Detect_support 项目**，而它恰好支持用户给的三种数据：A股(000001_daily.parquet)、期货主连(螺纹钢主连_D1)、MT5(EURUSD_H1)。

---

## 二、Detect_support 项目核心算法（主引擎，V3Fusion）

源码：src/srlab/{base,pivots,profile,detectors,data,probability,walkforward}.py + src/sr_engine.py + app.py

### 算法路径（V3 融合）
1. **因果 ATR**：src/srlab/data.py 的 atr_series(high,low,close,14)，Wilder 平滑简化版
2. **ATR 阈值 ZigZag 枢轴**（pivots.py）：k_atr=2.0 反向确认，记录 confirm_idx 保证无未来信息
3. **体积守恒成交量-价格剖面**（profile.py）：分箱宽=max(tick, 0.25*ATR)，50% 半衰期时间衰减
4. **V3Fusion 检测器**（detectors.py）：融合 成交量剖面/枢轴堆积/收盘堆积/历史触及事件/陈旧度重估 多证据 → NMS 非极大值抑制 → 置信度
5. **概率模型**（probability.py）：逻辑回归（Newton-Raphson+L2），双概率"触及概率+守住概率"，特征 8 个
6. **标定表**（score_calibration.json）+ **复权因子**（adj_factors.parquet，A股）

### 对外生产接口 src/sr_engine.py
- SREngine.detect(df, symbol) → zones + info
- build_summary / attach_mtf（多周期共振）

### 批量扫描入口 app.py: /api/analyze_all
- 遍历 data_dir 下所有 parquet → 每标的 V3Fusion 检测 → 汇总按"有效概率(触及×守住)"降序排序
- 文件命名识别（local_data_loader.py）：{品种}主连_{D1|W1|H1..}.parquet / MT5 {symbol}_{tf}.parquet / A股 {6位代码}_{daily|60min|15min|5min}.parquet

### 关键阈值（回测验证过）
- MIN_DIST_ATR=0.5, MAX_DIST_ATR=5.0, 区间宽窄钳入[0.3,1.2]*ATR
- 回看窗口：volume lookback=250, hist=750, pivot lookback=500
- 分箱宽 = max(tick, 0.25*ATR)，默认 60 根半衰期

---

## 三、各项目可复用组件清单（对本任务构建）

### 直接复用 detect_support 的完整算法链（推荐主路径）
- SREngine / V3Fusion / profile / pivots / probability 全部拿来直接用

### 从 AlphaMaster 复用（数据接入）
- DataSource 抽象 + Bar(ts,OHLC,vol) 统一结构
- MT5Source.fetch_bars（MetaTrader5 库，copy_rates_from_pos，服务端时区偏移修正，drop_forming）
- KlineCache（Parquet 优先，全量/增量）
- ParquetManager（parquet 读取/排序/去重/时间戳修复）
- 通达信/通达信 pytdx A股 接入、tqsdk 国内期货接入

### 从 vnpy 借鉴（规范）
- BarData/vt_symbol 唯一键约定
- AlphaLab.load_bar_df 全市场长表/归一化/停牌转NaN
- ts_max(high,N)/ts_min(low,N) 时序因子（支撑阻的几何约束）

### 从 abu 借鉴（辅助/对照）
- ABuTLExecute：demean + search_best_poly + Chebyshev 拟合 + BFGS 局部极值 + KMeans 定数量 → 趋势线 S/R
- 但这是"趋势线"范式；经典水平价位需在 low/high 摆动拐点上做 Kafka-means

结论：**以 detectSupport 的 V3Fusion 为主引擎（水平价位式 S/R），可选叠加 abu 趋势线范式对照；数据层用 AlphaMaster 的多源接入；输出层借鉴 vnpy 的全市场长表组织。**

---

## 四、Python 环境（已就绪）
- Python 3.11.2（已配置 pip 走腾讯镜像）
- 已装：flask 3.1.3 / pandas 3.0.5 / numpy 2.4.6 / scipy 1.17.1 / pyarrow 25.0.1
- 环境验证：detect_support 引擎已用合成数据跑通（输出 5 个 S/R 位）

## 五、待办（需用户提供）
- [ ] **飞书文档无法直接访问**（my.feishu.cn 需要登录），需用户贴正文或导出
- [ ] 用户提供 k几数据集 / A股数据（建议 parquet 或 CSV）、MT5 数据/接入方式
- [ ] 确认数据存放路径与格式后，正式构建并运行"批量全市场支撑阻力扫描"

## 六、复现路径建议（等数据到位）
1. 把 A 股数据按 {6位代码}_{D1|H1|M15|M5}.parquet 落到一个目录（Detect_support 直接支持本地读，且有复权处理）
2. 把 MT5/外盘数据按 {symbol}_{D1|H1...}.parquet 落同目录或另目录
3. 复用 detectSupport 的 V3Fusion + analyze_all 逻辑，写一个批量 CLI/脚本遍历全市场 → 输出按有效概率排序的支撑/阻力汇总表
