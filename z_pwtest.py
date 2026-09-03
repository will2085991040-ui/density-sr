# -*- coding: utf-8 -*-
try:
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        print("chromium launched OK")
        b.close()
except Exception as e:
    print("LAUNCH-FAIL", repr(e)[:300])
