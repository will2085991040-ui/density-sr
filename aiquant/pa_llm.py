# -*- coding: utf-8 -*-
"""pa_llm.py -- LLM 双交易 Agent (稳 6.16 / 激进 6.24) 驱动模块.

ThroughView OpenAI compatible gateway, 复用 aiquant.pa_proxy.price_action_features
计算最新已收盘价的几何特征, 构造价格行为 prompt, 让模型返回结构化 JSON 决策.
"""
from __future__ import annotations

import json
import threading
from typing import Any, Dict, Optional

# 复用既有价格行为特征函数 (同一 aiquant 包内), 不重复定义.
from aiquant.pa_proxy import price_action_features  # noqa: E402


# 历史固定路径兜底（项目目录曾被命名为 quant_research，后改名导致读不到配置）。
CONFIG_PATH = "C:/Users/mine/Downloads/quant_research/config/ai_gateway.json"
DEFAULT_BASE_URL = "https://tokenhub.tencentmaas.com/v1"
DEFAULT_MODEL = "glm-5.3-flash"


def _candidate_gateway_configs():
    """按序返回可能的 ai_gateway.json 位置, 取第一个真实存在的读取.

    顺序: 当前工作目录 config/ -> exe/_MEIPASS 旁 config/ -> 本模块上层 config/
    -> 历史硬编码路径(兜底)。
    """
    import os as _os
    import sys as _sys

    here = _os.path.dirname(_os.path.abspath(__file__))
    root = getattr(_sys, "_MEIPASS", None) or here
    cands = [
        _os.path.join(_os.getcwd(), "config", "ai_gateway.json"),
        _os.path.join(root, "config", "ai_gateway.json"),
        _os.path.join(_os.path.dirname(here), "config", "ai_gateway.json"),
        CONFIG_PATH,
    ]
    return cands


def _load_gateway_config() -> Dict[str, Any]:
    """读取 AI 网关 JSON 配置, 失败/缺键时回退默认值."""
    cfg = {"base_url": DEFAULT_BASE_URL, "model": DEFAULT_MODEL, "api_key": ""}
    for p in _candidate_gateway_configs():
        try:
            with open(p, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            if isinstance(data, dict):
                for k in ("base_url", "model", "api_key"):
                    v = data.get(k)
                    if isinstance(v, str) and v.strip():
                        cfg[k] = v.strip()
                cfg["_config_path"] = p
            return cfg
        except Exception as exc:
            cfg["_load_err"] = repr(exc)
    return cfg


def _calc_rsi(closes, period: int = 14):
    """滚动 14 周期 RSI 辅助, 返回最新值."""
    if len(closes) < period + 1:
        return None
    avg_gain, avg_loss = 0.0, 0.0
    for i in range(1, period + 1):
        chg = closes[i] - closes[i - 1]
        if chg >= 0:
            avg_gain += chg
        else:
            avg_loss += -chg
    avg_gain /= period
    avg_loss /= period
    for i in range(period + 1, len(closes)):
        chg = closes[i] - closes[i - 1]
        g = chg if chg > 0 else 0.0
        lo = -chg if chg < 0 else 0.0
        avg_gain = (avg_gain * (period - 1) + g) / period
        avg_loss = (avg_loss * (period - 1) + lo) / period
    if avg_loss == 0.0:
        return 100.0 if avg_gain > 0 else 50.0
    rs = avg_gain / avg_loss
    return 100.0 - 100.0 / (1.0 + rs)


def _resolve_stance(stance: str) -> str:
    """把 stance 输入映射为 mode: conservative / aggressive."""
    s = (stance or "").strip()
    if (s == "6.16") or ("稳" in s) or ("保守" in s):
        return "conservative"
    return "aggressive"


def _prompt_files(stage):
    import os, glob
    here = os.path.dirname(os.path.abspath(__file__))
    kdir = os.path.join(here, "..", "knowledge", "prompts")
    order = (["1-提示词大纲","2-二元决策","3-市场诊断框架","4-文件16"] if stage=="诊断" else
              ["1-提示词大纲","2-二元决策","5-震荡区间分析","6-震荡区间交易","7-二次入场","8-文件19","文件18-突破","10-铁丝网","11-磁力位","12-逐棒","4-文件16","13-文件17","文件23"])
    pool = sorted(glob.glob(os.path.join(kdir, "*.txt")))
    picked, out = [], []
    for key in order:
        for p in pool:
            if key in os.path.basename(p) and p not in picked:
                picked.append(p); out.append(open(p, encoding="utf-8").read().strip()); break
    return out

def _system_prompt(stage="决策"):
    try:
        return (chr(10)*2).join(_prompt_files(stage))
    except Exception:
        return ""
def _sys_payload():
    """两阶段系统提示词组·决策套件注入 system 角色。"""
    try:
        return _system_prompt("决策")
    except Exception:
        return ""


def _build_prompt(df, symbol: str, market: str, stance: str, f: Dict[str, Any]) -> str:
    """构造价格行为 Prompt (最新收盘几何 + 近50根文本表 + 姿态指引)."""
    mode = _resolve_stance(stance)
    closes = [float(x) for x in df["close"]]
    rsi = _calc_rsi(closes, 14)

    geom = [
        "最新已收盘K线几何:",
        "  close=%.4f  ema20=%.4f  atr=%.4f" % (f["close"], f["ema20"], f["atr"]),
        "  body_ratio=%.3f  upper_wick=%.3f  lower_wick=%.3f  close_pos=%.3f" % (
            f["body_ratio"], f["upper_wick"], f["lower_wick"], f["close_pos"]),
        "  is_bull=%s  inside=%s  ema_dist_pct=%.2f%%  atr_dist=%.2f" % (
            f["is_bull"], f["inside"], f["ema_dist_pct"], f["atr_dist"]),
    ]
    geom.append("  RSI(14)=%.2f" % rsi if rsi is not None else "  RSI(14)=N/A")
    geom_text = chr(10).join(geom)

    rows = ["#N   O        H        L        C"]
    n = len(closes)
    start = max(0, n - 50)
    for i in range(start, n):
        o = float(df["open"].iloc[i])
        h = float(df["high"].iloc[i])
        lo = float(df["low"].iloc[i])
        c = float(df["close"].iloc[i])
        rows.append("#%-3d %-8.3f %-8.3f %-8.3f %-8.3f" % (i, o, h, lo, c))
    table = chr(10).join(rows)

    tone = (
        "稳(保守 6.16): 只做高置信度确认形态"
        if mode == "conservative"
        else "激进(6.24): 回调/早信号试探, 但须带止损+目标"
    )
    if mode == "conservative":
        guidance = (
            "你姿态: 保守 6.16。仅在高置信度确认形态时出手"
            "(顺势 + 实体收盘 + 突破/回踩确认), 未确认一律观望, 不赌反抽。"
        )
    else:
        guidance = (
            "你姿态: 激进 6.24。允许轻仓试探回调/早期信号以博取更大弹性, "
            "但任何出手必须伴随明确止损价与目标价, 控制单笔风险。"
        )

    prompt = (
        "你是资深价格行为量化交易助手。标的: " + symbol
        + " | 市场: " + market + chr(10)
        + geom_text + chr(10) + chr(10)
        + "## 最近50根已收盘K线 (最旧在上):" + chr(10)
        + table + chr(10) + chr(10)
        + "## 姿态指引: " + tone + " " + guidance + chr(10) + chr(10)
        + "严格只输出一个 JSON 对象, 字段: "
        + "direction(「多」「空」「观望」), action(一句中文操作建议), "
        + "entry(切入点价格), stop(止损价), target(目标价), "
        + "risk_pct(风险评分0-10), rr(盈亏比数字), "
        + "key_levels(关键价位数组, 数字), reason(中文理由, 2-4句)。"
        + chr(10) + "不要输出任何围栏或解释, 只给 JSON。"
    )
    return prompt


def _parse_llm_json(reply: str) -> Optional[Dict[str, Any]]:
    """从模型回复鲁棒地提取最外层 JSON 对象."""
    if not reply:
        return None
    text = reply.strip()
    try:
        obj = json.loads(text)
        if isinstance(obj, dict):
            return obj
    except Exception:
        pass
    # 去掉可能的围栏: markdown 三连引号用 chr(96) 构造, 避免源码引号冲突
    tick = chr(96)
    fence = tick * 3
    if fence in text:
        parts = text.split(fence)
        if len(parts) >= 3:
            candidate = parts[-2].strip()
            low = candidate.lower()
            if low.startswith("json"):
                candidate = candidate[4:].lstrip()
            try:
                obj = json.loads(candidate)
                if isinstance(obj, dict):
                    return obj
            except Exception:
                pass
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            obj = json.loads(text[start:end + 1])
            if isinstance(obj, dict):
                return obj
        except Exception:
            pass
    return None


def _run_llm(cfg: Dict[str, Any], prompt: str, timeout: float, max_tokens: int = 6000) -> dict:
    """在后台线程里执行真实 LLM 调用, 返回 (llm, err)."""
    out = {"llm": None, "err": None}

    def _call():
        try:
            import openai  # 懒导入 openai (不在模块顶层)
            client = openai.OpenAI(
                base_url=cfg.get("base_url") or DEFAULT_BASE_URL,
                api_key=cfg.get("api_key") or "EMPTY",
                timeout=timeout,
            )
            resp = client.chat.completions.create(
                model=cfg.get("model") or DEFAULT_MODEL,
                messages=[
                    {"role": "system", "content": _sys_payload() + chr(10)*2 + "只输出 JSON, 禁止解释文字。"},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.0,
                max_tokens=max_tokens,
                response_format={"type": "json_object"},
            )
            if not getattr(resp, "choices", None):
                out["err"] = "no-choices"
                return
            msg = resp.choices[0].message
            content = getattr(msg, "content", None)
            text = content if isinstance(content, str) else (content or "")
            if not text.strip():
                # 推理模型可能把答案放在 reasoning_content 扩展字段
                rc = getattr(msg, "reasoning_content", None)
                if isinstance(rc, str) and rc.strip():
                    text = rc
            parsed = _parse_llm_json(text)
            if parsed is not None:
                out["llm"] = parsed
            else:
                out["err"] = "no-json-parse: " + (text[:200] or "")
        except Exception as exc:
            out["err"] = repr(exc)

    worker = threading.Thread(target=_call, daemon=True)
    worker.start()
    worker.join(timeout=timeout)
    if worker.is_alive():
        out["err"] = "timeout"
    return out


def run_agent(df, symbol: str = "", market: str = "", stance: str = "6.16",
              timeout: float = 150.0, max_tokens: int = 6000) -> Dict[str, Any]:
    """主入口: 按姿态(6.16稳 / 6.24激进) 驱动一个 LLM 交易 Agent.

    返回至少包含 symbol/market/stance/tone/label/features/llm/llm_err,
    且当 llm 成功解析时追加扁平 direction/action/entry/stop/target/risk_pct/rr/reason。
    """
    cfg = _load_gateway_config()
    mode = _resolve_stance(stance)
    tone = "稳而审慎 · 6.16" if mode == "conservative" else "激进敢为 · 6.24"
    label = "稳健 Agent · 6.16" if mode == "conservative" else "激进 Agent · 6.24"

    features = price_action_features(df)
    prompt = _build_prompt(df, symbol, market, stance, features)

    res = _run_llm(cfg, prompt, timeout, max_tokens)
    llm = res["llm"]
    llm_err = res["err"]

    base = {
        "symbol": symbol,
        "market": market,
        "stance": stance,
        "tone": tone,
        "label": label,
        "features": features,
        "llm": llm,
        "llm_err": llm_err,
    }
    if llm is not None:
        base["direction"] = llm.get("direction")
        base["action"] = llm.get("action")
        base["entry"] = llm.get("entry")
        base["stop"] = llm.get("stop")
        base["target"] = llm.get("target")
        base["risk_pct"] = llm.get("risk_pct")
        base["rr"] = llm.get("rr")
        base["reason"] = llm.get("reason")
    return base
