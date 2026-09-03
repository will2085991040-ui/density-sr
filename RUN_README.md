# 批量全市场支撑/阻力位扫描工具 —— 使用说明

## 文件
- batch_sr_scan.py ：主入口（独立 CLI，复用 detectSupport 的 V3Fusion 引擎）

## 用法
  python batch_sr_scan.py --data-dir <K线parquet目录> \
      [--tf D1|H1|W1|M15|M5] [--direction long|short|both] [--n-zones 4] \
      [--out out/sr_scan] [--symbols A B C]

## 能力
- 自动识别三类数据：
  - A股  : 000001_daily / 60min / 15min / 5min.parquet（自动前复权，缺因子则降级<不复权>+告警）
  - 期货主连 : 螺纹钢主连_D1.parquet
  - MT5/外盘: EURUSD_H1.parquet
- 复用 detect_support 的 V3Fusion 引擎 + 触及/守住双概率模型 + 历史分位档标定
- 输出 CSV(utf-8-sig) + JSON，按"有效概率(触及x守住)"降序排序
- 每标的给出最近支撑/阻力价、触及概率、守住概率、有效概率、历史测试次数、趋势

## 验证状态
已在合成测试集（4只A股 + EURUSD/XAUUSD/US30外盘 + 螺纹钢/沪金/原油/铁矿石，
覆盖 D1 与 H1）上端到端验证：均成功检测、0 失败、概率与标定加载正常。

## 数据到位后
把真实数据（A股/MT5/期货）parquet 放入任一目录，运行：
  python batch_sr_scan.py --data-dir <真实数据目录> --out <输出前缀>
得到按有效概率排序的全市场支撑/阻力位汇总。
