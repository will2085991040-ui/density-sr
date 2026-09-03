# -*- coding: utf-8 -*-
"""批量识别全市场支撑/阻力位 —— 独立命令行工具

复用 Detect_support_and_resistance_levels 项目的 V3Fusion 引擎与本地数据加载器，
与 app.py 的 /api/analyze_all 逻辑保持一致，但作为无 Web 依赖的 CLI 运行，
便于批量跑全市场并输出 CSV / JSON 结果。

支持三类数据（按文件名自动识别）：
  - A股   : 000001_daily.parquet （自动前复权，缺失因子时降级<不复权+告警>）
  - 期货主连: 螺纹钢主连_D1.parquet
  - MT5/外盘: EURUSD_H1.parquet

用法:
  python batch_sr_scan.py --data-dir D:\A股_K线数据\parquet\stocks
  python batch_sr_scan.py --data-dir D:\MT5_K线数据 --tf H1 --direction both --out out/sr_scan
  python batch_sr_scan.py --data-dir D:\K线数据 --symbols EURUSD XAUUSD
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time

import pandas as pd

_BASE = os.path.dirname(os.path.abspath(__file__))
SR_ROOT = os.path.join(_BASE, "detect_support_resistance_extract",
                       "Detect_support_and_resistance_levels-main")
sys.path.insert(0, SR_ROOT)

from src.local_data_loader import (          # noqa: E402
    TIMEFRAME_LABELS, list_instruments, load_kline,
)
from src.sr_engine import (                  # noqa: E402
    DIRECTION_LABELS, SREngine, build_summary, get_calibration, get_prob_models,
)


def scan_all(data_dir, tf, n_zones, direction, symbols=None):
    instruments = list_instruments(data_dir)
    target = symbols if symbols else list(instruments.keys())
    rows, errors = [], []

    for symbol in target:
        available_tfs = instruments.get(symbol, [])
        if tf not in available_tfs:
            continue
        try:
            df = load_kline(data_dir, symbol, tf)
            if len(df) < 60:
                errors.append({"symbol": symbol, "reason": f"数据不足({len(df)}条)"})
                continue

            current_price = float(df["close"].iloc[-1])
            latest_pct = float(df["pct_chg"].iloc[-1]) if "pct_chg" in df.columns else 0.0

            zones, info = SREngine(n_zones=n_zones * 2).detect(df, symbol)
            if info.get("error"):
                errors.append({"symbol": symbol, "reason": info["error"]})
                continue

            summary = build_summary(zones, df, direction, info)
            sups = [z for z in zones if z["zone_type"] == "support"]
            ress = [z for z in zones if z["zone_type"] == "resistance"]
            n_sup = min(sups, key=lambda z: abs(z["distance_atr"])) if sups else None
            n_res = min(ress, key=lambda z: abs(z["distance_atr"])) if ress else None
            nearest = summary.get("nearest")

            rows.append({
                "symbol": symbol,
                "tf": tf,
                "tf_label": TIMEFRAME_LABELS.get(tf, tf),
                "current_price": round(current_price, 4),
                "change_pct": round(latest_pct, 2),
                "n_zones": len(zones),
                "nearest_support": n_sup["center"] if n_sup else None,
                "nearest_support_dist_pct": n_sup["distance_pct"] if n_sup else None,
                "nearest_resistance": n_res["center"] if n_res else None,
                "nearest_resistance_dist_pct": n_res["distance_pct"] if n_res else None,
                "p_touch": nearest.get("p_touch") if nearest else None,
                "p_hold": nearest.get("p_hold") if nearest else None,
                "p_effective": nearest.get("p_effective") if nearest else None,
                "edge_score": nearest["edge_score"] if nearest else None,
                "n_events": nearest["n_events"] if nearest else None,
                "width_atr": nearest["width_atr"] if nearest else None,
                "nearest_distance_pct": nearest["distance_pct"] if nearest else None,
                "nearest_distance_atr": nearest["distance_atr"] if nearest else None,
                "trend_label": summary["trend_label"],
                "direction": direction,
                "data_bars": len(df),
                "atr_pct": info.get("atr_pct"),
                "adjusted": info.get("adjust_source") == "factor_cache",
                "adjust_source": info.get("adjust_source"),
            })
        except Exception as e:
            errors.append({"symbol": symbol, "reason": str(e)})
            continue

    def _sort_key(r):
        if r.get("p_effective") is not None:
            return -r["p_effective"]
        if r.get("edge_score") is not None:
            return -r["edge_score"] / 1e6
        return 1e9

    rows.sort(key=_sort_key)
    return rows, errors


def main():
    ap = argparse.ArgumentParser(description="批量识别市场支撑/阻力位")
    ap.add_argument("--data-dir", required=True, help="K线 parquet 文件目录")
    ap.add_argument("--tf", default="D1", help="周期: D1/W1/H1/M15/M5 等")
    ap.add_argument("--n-zones", type=int, default=4, help="每侧最大关键位数")
    ap.add_argument("--direction", default="long",
                    choices=["long", "short", "both"], help="方向偏好")
    ap.add_argument("--out", default="out/sr_scan",
                    help="输出前缀（生成 {out}.csv 与 {out}.json）")
    ap.add_argument("--symbols", nargs="*", help="限定品种列表")
    args = ap.parse_args()

    if not os.path.isdir(args.data_dir):
        print(f"数据目录不存在: {args.data_dir}")
        sys.exit(1)

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    t0 = time.time()

    print(f"[scan] data_dir={args.data_dir} tf={args.tf} "
          f"n_zones={args.n_zones} direction={args.direction}")

    rows, errors = scan_all(args.data_dir, args.tf, args.n_zones, args.direction,
                            args.symbols)

    df = pd.DataFrame(rows)
    if not df.empty:
        df.to_csv(f"{args.out}.csv", index=False, encoding="utf-8-sig")
    else:
        print("[warn] 无结果行（检查数据目录格式）")

    calib = get_calibration()
    probs = get_prob_models()
    n_adj = sum(1 for r in rows if r.get("adjusted"))
    report = {
        "data_dir": args.data_dir,
        "tf": args.tf,
        "n_zones": args.n_zones,
        "direction": args.direction,
        "direction_label": DIRECTION_LABELS.get(args.direction, args.direction),
        "total": len(rows) + len(errors),
        "analyzed": len(rows),
        "failed": len(errors),
        "n_adjusted": n_adj,
        "n_unadjusted": len(rows) - n_adj,
        "calibrated": calib.ok,
        "prob_ready": probs.ok,
        "top_rows": rows[:50],
        "errors": errors,
        "elapsed_s": round(time.time() - t0, 2),
    }
    with open(f"{args.out}.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"完成：分析 {len(rows)} 只，失败 {len(errors)} 只，"
          f"用时 {report['elapsed_s']:.1f}s")
    print(f"输出: {args.out}.csv  /  {args.out}.json")
    if errors:
        print("失败明细:")
        for e in errors[:15]:
            print(f"  - {e['symbol']}: {e['reason']}")


if __name__ == "__main__":
    main()
