# 市场情绪量化分析 & 全市场扫荡量化系统

> **DENSITY-SR — 阿尔法量化价格行为引擎 v3.2**
> 支撑/阻力智能识别 + 双智能体（PA_Agent 稳健/激进）实时判定 + 全市场扫荡 + 6 策略回测

一个端到端全自动量化工具（非 demo）。读入本地「大A量化监控系统」全部数据
（A股个股 / 指数 / MT5 / OKX K线），并融合文件夹内两个 PA_Agent（稳健/激进双风格）
判定逻辑，完成：AI 情绪打分 → 交互式 HTML 报告 → 6 策略回测对比 → API 高强度分析。

![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6)
![License](https://img.shields.io/github/license/will2085991040-ui/density-sr)
![Repo Size](https://img.shields.io/github/repo-size/will2085991040-ui/density-sr)

---

## 📸 产品截图 / Screenshots

> 桌面端 (Windows 单文件 EXE) 实际运行截图。完整 4 张说明见 [docs/screenshots/README.md](docs/screenshots/README.md)。

| **全市场扫描 + 因子挖掘** | **K线 + 实时盯盘** | **分时 + 双 Agent 研判** | **实时盯盘 + 自动量化建议** |
| :---: | :---: | :---: | :---: |
| ![](docs/screenshots/01-market-scan-factor-mining.png) | ![](docs/screenshots/02-kline-realtime-monitor.png) | ![](docs/screenshots/03-intraday-dual-agent.png) | ![](docs/screenshots/04-realtime-auto-signal.png) |
| 扫描 260 只 + Top 6 因子 | 000670 日线 + MA5/10/20/60 | 000543 分时 + 微盟/激流双 Agent | 600127 实时 + 自动量化建议 |

## 🧭 项目解读 / What is this

**DENSITY-SR** 解决"个人量化交易者面对 4000+ 只 A 股 / 100+ MT5 品种时，怎么把 AI 和价格行为学（Price Action）结合起来做决策"的问题——

- **数据层**：本地 Parquet 仓库存了 A 股 4273 只、MT5 167 品种、OKX 19 币对的历史 K 线（5min / 15min / 60min / daily 四周期），全部离线可用；
- **指标层**：自动补全 EMA20 / ATR / MACD / RSI / BOLL 五大族，再用 srlab 做支撑/阻力关键位检测（"密度支撑阻力" = DENSITY-SR 名字来源）；
- **决策层**：把两个 PA_Agent（Al Brooks 价格行为引擎）的"稳 / 激进"两套判定阈值实现为本地 `aiquant/engine/signals.py`，不依赖 GUI/外部服务；
- **智能体层**：双 LLM Agent（微盟/激流）独立打分，可切换风格，输出 倾向/方向/入场/止损/目标/置信度；
- **交付层**：单文件 `dist/aiquant.exe`（PyInstaller 打包，含 ffmpeg），双击启动；同一后端也能 Web 部署。

【主程序 = 双击可用的 Windows 可执行文件】
- 图形界面:  dist/aiquant.exe  (114 MB, 单文件, 免安装, 双击启动)
- 命令行  :  dist/aiquant.exe --cli analyze --symbol 600519

## 四项功能
1. 输入股票代码 → 自动爬新闻 → AI 情感打分（① 情绪盯盘）
   实时抓取东方财富新闻流并做中英情感词典打分(-1~+1)，同时生成「情绪看板」HTML。
2. 生成交互式 HTML 报告（② HTML 量化报告）
   单文件自包含：蜡烛图 + EMA20 叠加 + MACD 副图、六维评分雷达图、新闻词云、
   双智能体融合信号表、6 策略绩效对比。图均以 base64 内嵌，不联网也可查看。
3. 6 种回测策略一键对比（③ 6 策略回测）
   双均线交叉 / MACD 金叉 / RSI 均值回归 / RSI 超买卖出 / 唐奇安突破 / 布林带回归，
   统一比较 累计收益·夏普·最大回撤·交易次数，自动选最优。
4. 接入 API 高强度分析（④ 全市场扫描 + API 深度研判）
   从 4000+ 只 A 股全市场扫荡，输出非「观望」的可交易信号；如需 DeepSeek 大模型深度
   研判，配置密钥即可；未配置则自动使用本地离线研判，全流程不联网也能跑通。

## 数据源（读入磁盘现存数据，无需联网下载）
| 市场 | 目录 | 规模 |
|------|------|------|
| A股个股 | A股数据/parquet/stocks | 4273 只 x {5min,15min,60min,daily} |
| 指数   | A股/parquet/indices   | 215 个 / 4 周期 |
| MT5    | MT5_K线数据/MT5_K线数据 | 167 品种 / {D1,H1,M15,M5} |
| OKX    | OKX_K线数据/OKX_K线数据 | 19 加密币对 |
统一清洗为 [time,open,high,low,close,tick_volume,code]；指标层自动补
EMA20/ATR/MACD/RSI/BOLL，并调用原生支撑/阻力检测获取关键位。

## 双智能体融合说明
两个 PA_Agent 为 Al Brooks 价行动作交易判定引擎，区别仅在决策心态（稳/激进）。
源码唯一配置差异 general.decision_stance = 稳 | 激进。本项目不重复 PyQt6 GUI，
而把其确定性判定移植为本机离线信号引擎 aiquant/engine/signals.py：
- 5 票方向票 → 方向投票 → 双风格阈值（稳: 起评≥5+RR≥1.5 等；激进: 更宽松）
- 输出 {倾向, 方向, 入场, 止损, 目标, 支撑, 阻力, 置信度, ATR}
- 在 GUI/CLI 中可随时切换「稳 / 激进」两种风格。

## 命令行用法
```bash
# 单只全流程分析 + 生成HTML报告（含情绪/回测）
python -m aiquant.app analyze --symbol 600519 --market A股 --tf daily

# 全市场扫荡（激进风格）
python -m aiquant.app scan --market A股 --top 15

# 源码启动图形界面（推荐方式之一）
python app.py
```

## 运行依赖
- Python 3.11+
- `pandas`, `pyarrow`, `matplotlib`, `wordcloud`, `openai`, `scikit-learn`, `pyinstaller`（构建 EXE 时用）
- DeepSeek / 自定义 LLM 密钥（可选）：复制 `config/ai_gateway.example.json` 为 `config/ai_gateway.json` 并填入自己的 key
- 未配置 LLM key 时自动降级为本地多因子离线研判，核心功能不因缺 key 失效

## 目录结构
aiquant/market/data.py          数据目录挂载与统一加载
aiquant/engine/indicators.py    指标
aiquant/engine/signals.py       双风格融合信号引擎（并入两 agent 逻辑）
aiquant/features/sentiment.py   新闻抓取 + AI 情感打分
aiquant/report/report.py        HTML 报告生成器（K线/MACD/雷达/词云）
aiquant/report/sentiment_html.py 情绪看板
aiquant/backtest/strategies.py  6 策略回测对比
aiquant/api/deepseek.py         DeepSeek API 高强度分析（离线降级）
aiquant/engine/vendor/src       支撑阻力引擎(srlab)
app.py / gui.py / main.py       CLI / GUI / 入口
dist/aiquant.exe                已打包可执行文件

## 备注
- 运行依赖: pip install pandas pyarrow matplotlib wordcloud openai scikit-learn pyinstaller
- DeepSeek 密钥（可选）：设置环境变量 PA_API_KEY 或 aiquant/api_key.json 写 {"api_key":"sk-..."}
- LLM 无法连接时自动降级为本地多因子离线研判，核心功能不因缺 Key 失效。
