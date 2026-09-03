# -*- coding: utf-8 -*-
"""Feature 4 — 接入 API 高强度分析 (DeepSeek/OpenAI 兼容). 无 Key 依然离线可用."""
from __future__ import annotations
import json, os

_SYSTEM = "你是专业量化交易助理。基于给定数据给出中文、简洁、可执行的分析：方向、关键位、风险与仓位建议。不虚构未提供的信息。"

def load_key():
    for env in ("PA_API_KEY", "DEEPSEEK_API_KEY"):
        if os.environ.get(env):
            return os.environ[env]
    cfg = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "api_key.json")
    if os.path.exists(cfg):
        try:
            return json.load(open(cfg, encoding="utf-8")).get("api_key")
        except Exception:
            pass
    return None

def _client(key):
    from openai import OpenAI
    return OpenAI(api_key=key, base_url=os.environ.get("PA_BASE_URL", "https://api.deepseek.com"))

def deep_chat(json_input, key=None, system=_SYSTEM):
    key = key or load_key()
    if not key:
        return "未配置 API Key，已改用本地离线分析。"
    try:
        cli = _client(key)
        r = cli.chat.completions.create(
            model=os.environ.get("PA_MODEL", "deepseek-chat"),
            temperature=0.0,
            messages=[{"role": "system", "content": system},
                      {"role": "user", "content": json_input}])
        return r.choices[0].message.content
    except Exception as e:
        return "AI 分析请求失败: %s" % str(e)[:90]

def _offline_synopsis(signal):
    if not signal:
        return "当前无明确信号，建议观望。"
    s = signal
    txt = "[%s %s] 评分%s 置信%s" % (s.get("order", "观望"), s.get("direction", ""),
                                    s.get("score", 0), s.get("confidence", 0))
    if s.get("support"): txt += " | 支撑 %.4f" % s["support"]
    if s.get("resistance"): txt += " | 阻力 %.4f" % s["resistance"]
    txt += "。建议结合量能严格止损。"
    return txt

def high_intensity(symbol, kpv, sentiment, key=None, use_ai=True):
    """kpv: dict with close/order/direction/confidence/support/resistance.
    Returns dict {ai, report}. Offline unless use_ai and key present."""
    payload = {"symbol": symbol,
               "close": float(kpv.get("close")),
               "signal": {k: kpv.get(k) for k in ("order", "direction", "confidence", "support", "resistance")},
               "sentiment": (sentiment or {}).get("label"),
               "sentiment_score": (sentiment or {}).get("score"),
               "task": "高强度多维度综合分析：给方向、关键支撑/压力、风险与仓位建议，中文简洁"}
    used_ai = False
    if use_ai and (key or load_key()):
        reply = deep_chat(json.dumps(payload, ensure_ascii=False, default=str), key=key)
        if not reply.startswith("ok") and not reply.startswith("AI"):
            report = reply
        else:
            report = reply
        used_ai = True
        return {"ai": True, "text": reply, "payload": payload}
    return {"ai": False, "text": _offline_synopsis(payload["signal"]), "payload": payload}

def summarize_offline(symbol, signal, sentiment, backtest):
    lines = ["%s 量化分析" % symbol]
    if signal:
        lines.append(" - 信号 %s %s (评分%s / 置信%s)" % (signal.get("order"), signal.get("direction"),
                                                       signal.get("score", 0), signal.get("confidence", 0)))
        if signal.get("support"): lines.append(" - 支撑 %.4f / 阻力 %.4f" % (signal["support"], signal["resistance"]))
    if sentiment:
        lines.append(" - 情绪 %s (%s)" % (sentiment.get("label"), sentiment.get("score")))
    if backtest:
        good = [b for b in backtest if "error" not in b]
        if good:
            best = max(good, key=lambda r: r.get("sharpe", -9))
            lines.append(" - 最优策略 %s 收益%.1f%% 夏普%.2f" % (best["strategy"], (best["total_return"] or 0)*100, best["sharpe"]))
    return "\n".join(lines)
