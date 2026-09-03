# -*- coding: utf-8 -*-
import sys, traceback
try:
    from aiquant.ensure_data import ensure_data
    print("import ok")
    r = ensure_data()
    print("ensure_data ->", repr(r)[:120])
except Exception:
    traceback.print_exc()
