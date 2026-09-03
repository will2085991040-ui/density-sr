# -*- coding: utf-8 -*-
import os, glob
cands = [
 r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
 r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
 r"C:\Program Files\Google\Chrome\Application\chrome.exe",
 r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
]
for c in cands:
    print(os.path.exists(c), c)
# also try playwright default path fallback
for root in (r"C:\Users\mine\AppData\Local\ms-playwright",):
    for m in glob.glob(root+"/**/chrome*.exe", recursive=True) + glob.glob(root+"/**/msedge*.exe", recursive=True):
        print("PW", m)
