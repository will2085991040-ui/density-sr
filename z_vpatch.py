# -*- coding: utf-8 -*-
import os, sys, time, subprocess, urllib.request
exe=r"C:/Users/mine/Downloads/quant_research/dist_v92/dsr_sr.exe"
boot=os.path.expanduser("~/_dsr_sr_boot.txt")
try: os.remove(boot)
except Exception: pass
p=subprocess.Popen([exe], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
url=None
for _ in range(130):
    if os.path.exists(boot):
        try: url=open(boot).read().strip(); break
        except Exception: pass
    if p.poll() is not None: break
    time.sleep(1)
print("boot:", url)
if not url: p.kill(); sys.exit(1)
js=urllib.request.urlopen(url+"chart_realtime.js", timeout=20).read().decode("utf-8","replace")
print("chart_rt len:", len(js))
print("has dates-axis patch:", "K-K线用真实日期刻度" in js or "dates&&dates[j]" in js)
# also confirm echarts + rt routes
idx=urllib.request.urlopen(url+"index.html", timeout=20).status
print("index:", idx)
p.kill()
