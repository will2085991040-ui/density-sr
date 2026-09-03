# -*- coding: utf-8 -*-
try:
    import openpyxl; print("openpyxl OK", openpyxl.__version__)
except Exception as e:
    print("NO openpyxl", repr(e))
