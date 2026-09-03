# -*- coding: utf-8 -*-
try:
    import playwright
    print("python-playwright OK")
except Exception as e:
    print("no-python-playwright", repr(e))
import shutil
p = shutil.which("msedge") or shutil.which("chrome") or shutil.which("chromium")
print("browser bin:", p)
