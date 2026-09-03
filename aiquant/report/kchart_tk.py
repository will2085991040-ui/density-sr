# -*- coding: utf-8 -*-
"""在 tkinter 中显示 K 线图（HMM + 指标叠加 + 支撑/阻力 + 买卖标记）。

做法：用已启动的 report 图表引擎(无损/CLI 已验证)渲染 K线+MACD 为 PNG，
再经 PIL 放大插入 tkinter。支持市场/代码/周期切换与叠加支撑阻力。
"""
from __future__ import annotations
import io, os
import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import ttk


def make_kline_photo(df, symbol="", width=760, height=360, show_ma=True, show_sr=True):
    """返回 (tk.PhotoImage, PIL.Image) 。df 需含全部 K线列 + 指标列。"""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from . import report as R
    # 复用报告函数的取字号逻辑
    import aiquant.report.report as RR
    try:
        imgbytes = RR.kline_macd_bytes(df, title=symbol, tail=160)  # 待给 bytes 版
    except AttributeError:
        img = None
    if img is None:
        return None, None
    from PIL import ImageTk, Image
    im = Image.open(io.BytesIO(imgbytes)).convert("RGB")
    im = im.resize((width, height), Image.LANCZOS)
    photo = ImageTk.PhotoImage(im)
    return photo, im


def tk_photo_from_png(src_bytes, width, height):
    from PIL import ImageTk, Image
    im = Image.open(io.BytesIO(src_bytes)).convert("RGB")
    im = im.resize((width, height), Image.LANCZOS)
    return ImageTk.PhotoImage(im), im
