# vnpy(VeighNa) v4.4.0 源码深度分析报告

> 目的：为批量识别全市场支撑阻力位工具建设提供 vnpy 可复用组件分析。

**实际源码路径**：C:\\Users\\mine\\Downloads\\quant_research\\vnpy_extract\\vnpy-master
（注：题目写的 npy_extract\\npy-master 路径不存在，实际目录名是 vnpy_extract\\vnpy-master。）

---

## 1. 项目定位、架构、设计思想

定位（README.md，版本 4.4.0，MIT）：VeighNa 是基于 Python 的开源量化交易系统开发框架，定位为交易平台/框架底座。本仓库(vnpy 包)只是核心框架，不含任何行情/交易接口实现.所有 gateway / database / datafeed / CTA策略 / MT5 都是独立的 vnpy_ 插件（GitHub 单独仓库）。已在本仓库核实：核心包内无任何 CTP/XTP/MT5/tushare 等接口实现。

架构三层：
1. vnpy/event -- 事件驱动引擎（平台通信总线）
2. vnpy/trader -- 交易核心（MainEngine/BaseEngine, BaseGateway/BaseDatabase/BaseDatafeed, 数据对象, 工具类）
3. vnpy/alpha（4.0新增）/ vnpy/chart / vnpy/rpc -- 上层功能包

设计思想：插件化 + 事件驱动 + 接口抽象(ABC) + 配置驱动（vnpy/trader/setting.py 的 SETTINGS dict + vt_setting.json）。

---

## 2. vnpy/trader 核心

### 2.1 事件驱动（vnpy/event/engine.py）
- Event(type, data)：type 字符串 + data 对象；EventEngine = 一个 queue.Queue + 处理线程 _run + 定时线程 _run_timer（默认每秒投递 EVENT_TIMER=eTimer）。
- register(type, handler) 按事件类型注册；register_general 注册全局。分发是同步、逐 handler 顺序调用，单一消费者线程串行消费，天然线程安全。
- 事件常量（vnpy/trader/event.py）：EVENT_TICK=eTick. / EVENT_TRADE / EVENT_ORDER / EVENT_POSITION / EVENT_ACCOUNT / EVENT_QUOTE / EVENT_CONTRACT / EVENT_LOG=eLog。
- 关键：算法/回测侧不依赖 EventEngine（alpha 回测即纯函数化）。

### 2.2 MainEngine / BaseEngine / OmsEngine（vnpy/trader/engine.py）
- BaseEngine(main_engine, event_engine, engine_name) 抽象类，注册进 MainEngine.engines[name]。
- init_engines() 内置 LogEngine、OmsEngine、EmailEngine、WechatEngine。
- OmsEngine 是平台实时对象中心（内存字典缓存）：ticks/orders/trades/positions/accounts/contracts/quotes 各 dict，key=vt_symbol/vt_orderid，保存最新快照；还管 OffsetConverter。

### 2.3 数据库适配（vnpy/trader/database.py）
- 重点：DB_TZ=ZoneInfo(SETTINGS[database.timezone]) 与 convert_tz()：入库前 datetime 转库时区并去除 tzinfo。
- BarOverview/TickOverview；BaseDatabase 抽象：save_bar_data / load_bar_data / delete_bar_data / get_bar_overview 等；get_database() 按 SETTINGS[database.name] 动态加载 vnpy_<name>（默认 sqlite，支持 mysql/postgresql/QuestDB/TDengine/MongoDB 等）。

### 2.4 数据服务（vnpy/trader/datafeed.py）
- BaseDatafeed：query_bar_history(HistoryRequest)->list[BarData]；get_datafeed() 按配置加载（rqdata/xt/tushare/wind/gm 等）。

### 2.5 资金回测与 CTA
- CTA 策略引擎（cta_strategy/cta_backtester）不在本仓库（外部插件 vnpy_ctastrategy）。本仓储带回测的是 vnpy/alpha/strategy/backtesting.py。
- 用户提到资金回测(fn)：本仓库无名为 fn 的模块；对应 alpha 回测的资金/账户处理。

---

## 3. 数据对象结构 + K线/Bar 合成

全部 dataclass，继承 BaseData（含 gateway_name + extra），路径 vnpy/trader/object.py。

BarData: symbol, exchange, datetime, interval, OHLC, volume, turnover, open_interest; vt_symbol=symbol.exchange
TickData: 五档买卖价量, last_price, OHLC, pre_close, limit_up/down
OrderData/TradeData/PositionData/AccountData/ContractData/QuoteData: 委托/成交/持仓/账户/合约/报价
HistoryRequest: symbol, exchange, start, end, interval（历史K线统一入参）
SubscribeRequest/OrderRequest/CancelRequest: 订阅/下单/撤单

Exchange 枚举覆盖 A/股/期/港/美/全球 + LOCAL（本地生成数据），非常适合标注支撑阻力工具的本地结果。

### K线合成（vnpy/trader/utility.py）
- BarGenerator (L166)：Tick→1min→Nmin（N 整除60）/H/D。
- ArrayManager (L495)：numpy 滚动滑窗（size 默认 100），提供 60+ 个 TA-Lib 指标：sma/ema/kama/mom/roc/std/obv/cci/atr/natr/rsi/macd/adx/willr/ultosc/boll/keltner/donchian/aroon/mfi/stoch/sar 等。

---

## 4. vnpy/alpha：Alpha 多因子模块（与本任务关系最紧密）

4.0 亮点，受 Qlib 启发，数据流用 Polars 数据框流水线，不依赖 EventEngine。公共 API：AlphaLab / AlphaDataset / AlphaModel / AlphaStrategy / BacktestingEngine / Segment / register_functions。

### 4.1 AlphaLab（vnpy/alpha/lab.py）
- 本地目录：lab_path/{daily,minute,component,dataset,model,signal,contract.json}。
- K线落地：save_bar_data(list[BarData]) 按 vt_symbol 写 Parquet 分区合并去重；load_bar_data() 读回 BarData。
- load_bar_df(vt_symbols, interval, start, end, extended_days)（重点）：批量读多标 → 长表(datetime,OHLC,vol,turnover,OI,vwap,vt_symbol)，价格归一化（首日 close 相除）、全零价视为停牌转 NaN。
- 成分股管理：load_component_symbols / load_component_filters；数据集/模型/信号 pkl/parquet 存储；合约参数 json。

### 4.2 AlphaDataset（vnpy/alpha/dataset/template.py）
- 表达式因子引擎：add_feature(name, expression) 字符串因子 → polars expr / DataProxy 重载求值；register_functions 可注册扩展。
- 因子命名空间：ts_（时序 23个：delay/min/max/rank/sum/std/slope/rsquare/resi/corr/log 等）、cs_（截面：rank/mean/std/sum/scale）、ta_（rsi/atr）、math_（less/greater/log/abs/sign 等）。
- 内置 Alpha158 / Alpha101；label = ts_delay(close,-3)/ts_delay(close,-1)-1（未来 3 日收益）。
- 流程 prepare_data(<filters>) + process_data（drop_na/fill_na/cs_norm/robust_zscore/ts_norm/replace_inf/drop_feature/cs_rank_norm）；分 TRAIN/VALID/TEST 三段；alphalens 绘绩效。

### 4.3 模型（vnpy/alpha/model/）
AlphaModel：fit(dataset)+predict(dataset,segment)；内置 LassoModel/LgbModel/L lpModel(PyTorch MLP)。

### 4.4 回测（vnpy/alpha/strategy/backtesting.py）
- BacktestEngine(lab)：set_parameters(vt_symbols, interval, start/end, capital, risk_free, annual_days)；add_strategy(cls, setting, signal_df)。
- load_data()：history_data[(datetime, vt_symbol)]=bar + dts 时间戳集合。
- run_backtesting()：先 on_init，再按时间逐 dt 回放 new_bars(dt)（时间切片→全市场 on_bars 回调）。
- calculate_result()：每日盯市 PortfolioDailyResult（date/trade_count/turnover/commission/trading_pnl/holding_pnl/net_pnl）；calculate_statistics()：年化/最大回撤/Sharpe/回撤比/爆仓检测。
- 策略模板 AlphaStrategy + set_target 目标持仓；示例 EquityDemoStrategy 按信号 top-K 调仓，是多标的截面切片批量调仓的现成范例。

---

## 5. 数据源/gateway 如何提供行情

核心仓库不含任何具体网关（已核实），对接模式 = BaseGateway 接口 + 独立 vnpy_* 插件：
- 需实现 connect/close/subscribe/send_order/cancel_order/query_account/query_position；回调 on_tick/on_trade/on_order/on_position/on_account/on_contract/on_quote（包装为 Event 入队，对具体 vt_symbol 再发一次）。
- query_history(HistoryRequest)->list[BarData] 历史K线统一口（默认空）。
- A股：rqdata/xt/tushare/gm 等数据服务 + XTP/TSP 证券网关；期货：CTP 系；外盘：InteractiveBrokers；MT5：外部 vnpy_mt5 插件（不在此仓库）。

---

## 6. 支持/阻力位算法？ —— grep 结论（重点）

全仓库 grep support|resistance|pivot|支撑|阻力：并没有任何真正的支撑/阻力/枢轴(Pivot) 算法实现。命中的仅为 pandas DataFrame.pivot()（alpha/template.py 把长表 reshape 为宽表给 alphalens）、英文注释/支持词。

结论：vnpy 没有内置支撑/阻力/枢轴计算器，需自行实现。可参考/借用：ArrayManager 的 donchian（MAX(high)/MIN(low) 通道阻/撑）、boll、keltner 通道；以及因子中的 ts_max(high,N)/ts_min(low,N)（Alpha158 已含 max_N/min_N）。

---

## 7. 与批量识别全市场支撑阻力可复用组件

直接复用的标准契约:
1. BarData / Exchange / Interval（object.py/constant.py）+ vt_symbol 唯一 key，用 LOCAL 标记本地结果。
2. database.py 的 convert_tz + get_database 统一时区落地。
3. HistoryRequest + query_bar_history 统一历史查询口。

Alpha 模块的批量全标的流水线（最值得借鉴）:
4. AlphaLab.load_bar_df 批量读全市场→长表（含 vwap/停牌NaN/归一化）：是批量识别全市场支撑阻力的直接数据起点。
5. AlphaLab 的 parquet 分标地落盘/合并/去重：可做批处理多层数据缓存。
6. BacktestEngine 的 (time, vt_symbol) 双索引+逐时间切片遍历：可改造为按时间点扫描全市场支撑阻力的骨架。
7. ts_min/ts_max/ma/corr 等时序因子：可直接构造近N日高低/均价型支撑阻力（N日高压顶=ts_max(high,N)、N日低位=ts_min(low,N)）。
8. ArrayManager 的 donchian/boll/keltner 通道 & 60+ 指标：复用为相似支撑阻力。
9. AlphaStrategy + set_target 批量调仓回调：若把支撑阻力做成可择时信号可直接安装。

明确不可复用:
- CTA 策略引擎、任意具体网关（CTP/XTP/MT5）均在 vnpy_* 插件，本仓库只有抽象接口。
- 无现成支撑阻力算法，需要自建（建议基于 ts_max/ts_min + donchian + 价格分桶/聚类叠加）。

---
**一句话总结**：vnpy 最大的复用价值在于 (1) 统一规范 K线数据抽象、批量加载全市场长表、逐时间切片批量回测；(2) 提供 Polars 全市场批处理 + 因子引擎 + 多标的切片回测完整样板；(3) 支撑/阻力算法本身需自建，但 ts_max/ts_min/donchian 等素材已具备。