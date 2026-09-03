# -*- coding: utf-8 -*-
"""First-run data provisioning for the frozen DENSITY·SR EXE (方案2: 压缩内嵌, 首启自解压).

Embedded pack: data_pack.zip (contents: A股数据/..., MT5_K线数据(1)/..., OKX_K线数据(1)/...).
ensure_data() returns a data root containing "A股数据" - either an existing one on disk
(Desktop / DSRS_DATA_ROOT / sibling) or a self-extracted cache from the bundled pack.
"""
from __future__ import annotations
import os, sys, zipfile

_PACK_NAME = "data_pack.zip"


def _cache_dir() -> str:
    base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    return os.path.join(base, "DENSITY_SR", "data")


def _pack_candidates():
    out = []
    mp = getattr(sys, "_MEIPASS", None)
    if mp:
        out.append(os.path.join(mp, _PACK_NAME))
    if getattr(sys, "frozen", False):
        exe_dir = os.path.dirname(sys.executable)
        out.append(os.path.join(exe_dir, _PACK_NAME))
        out.append(os.path.join(exe_dir, "_internal", _PACK_NAME))
    pkg = os.path.dirname(os.path.abspath(__file__))
    out.append(os.path.join(pkg, _PACK_NAME))
    out.append(os.path.join(os.path.dirname(pkg), "build", _PACK_NAME))
    seen = set(); res = []
    for p in out:
        if p not in seen:
            seen.add(p); res.append(p)
    return res


def _is_root(root):
    return bool(root) and os.path.isdir(os.path.join(root, "A股数据"))


def existing_root() -> str:
    env = os.environ.get("DSRS_DATA_ROOT", "").strip()
    if env and _is_root(env):
        return env
    bases = []
    if getattr(sys, "frozen", False):
        exe_dir = os.path.dirname(sys.executable)
        bases += [os.path.join(os.path.dirname(exe_dir), "大A量化监控系统"),
                  os.path.join(exe_dir, "大A量化监控系统")]
    bases += [r"C:/Users/mine/Desktop/大A量化监控系统"]
    for c in bases:
        if _is_root(c):
            return c
    return ""


def ensure_data() -> str:
    """Return a usable data root (containing A股数据), extracting the embedded pack if needed."""
    ok = existing_root()
    if ok:
        return ok
    pack = "data_pack.zip"
    for cand in _pack_candidates():
        if os.path.isfile(cand):
            pack = cand
            break
    if not pack:
        return ""
    cache = _cache_dir()
    marker = os.path.join(cache, "extracted.flag")
    if not (os.path.isdir(cache) and os.path.isfile(marker) and _is_root(cache)):
        os.makedirs(cache, exist_ok=True)
        with zipfile.ZipFile(pack) as z:
            z.extractall(cache)
        with open(marker, "w", encoding="utf-8") as f:
            f.write("ok")
    os.environ["DSRS_DATA_ROOT"] = cache
    return cache