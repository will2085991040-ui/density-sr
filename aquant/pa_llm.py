# -*- coding: utf-8 -*-
"""PA Agent 大模型接入层：用真实 AI(OpenAI 兼容)驱动 6.16(稳)/6.24(激进) 两个智能体。"""
from __future__ import annotations
import json, os, re

_HEREDIR = os.path.dirname(os.path.abspath(__file__))
_CFG_PATH = os.path.join(os.path.dirname(_HEREDIR), "config", "ai_gateway.json")
_CFG = None

def cfg():
    global _CFG
    if _CFG is None:
        try:
            with open(_CFG_PATH, encoding="utf-8") as f:
                _CFG = json.load(f)
        except Exception:
            _CFG = {"base_url": "https://tokenhub.tencentmaas.com/v1",
                    "api_key": "", "model": "glm-5.3-flash"}
    return _CFG

def _features(df):
    from aiquant.pa_proxy import price_action_features
    return price_action_features(df)

def _kline_rows(df, max_bars=50):
    n = len(df); start = max(0, n - max_bars); out = []
    for i in range(start, n):
        o = float(df["close"][i])
        o = float(df["close"][i]); h = float(df["high"][i])
        l = float(df["close"][i]); break
    return out
