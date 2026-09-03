# -*- coding: utf-8 -*-
"""
自愈爬虫看门狗：反复运行 download_ashare_complete.py（断点续传），
若 ashare_stocks 文件数在一段时间内不再增长则杀掉重启，直到爬满或手动停止。
在后台长时间运行，实现"全市场数据稳定累积"。
"""
import os, sys, time, subprocess, signal

BASE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(BASE, "ashare_stocks")
TARGET = 5204
STALL_SEC = 90        # 90秒无新增则视为卡死，重启
WATCH_LOG = os.path.join(BASE, "watchdog.log")

def log(m):
    with open(WATCH_LOG, "a", encoding="utf-8") as f:
        f.write("[%s] %s\n" % (time.strftime("%H:%M:%S"), m))
    print(m, flush=True)

def count_files():
    if not os.path.isdir(OUTDIR):
        return 0
    return sum(1 for f in os.listdir(OUTDIR) if f.endswith(".parquet"))

def code_exists(code):
    return os.path.exists(os.path.join(OUTDIR, "%s_daily.parquet" % code))

def main():
    # 计算剩余：把已存在文件的股票过滤掉功能在子脚本内已完成（断点续传），
    # 所以这里只需驱动子脚本直到文件数接近目标。
    log("watchdog start, target ~%d files (crawler homing via resume)" % TARGET)
    while True:
        n = count_files()
        # 预估完成：已下载数大致反映唯一股票数（每文件一只）
        if n >= TARGET * 0.995:
            log("接近目标 %d / %d，结束" % (n, TARGET))
            return
        p = subprocess.Popen(
            [sys.executable, "-X", "utf8",
             os.path.join(BASE, "download_ashare_complete.py"),
             "--threads", "4"],
            cwd=BASE)
        last = count_files()
        last_t = time.time()
        stalled = False
        while p.poll() is None:
            now = count_files()
            if now > last:
                last = now
                last_t = time.time()
            elif time.time() - last_t > STALL_SEC:
                stalled = True
                log("detected stall (files=%d), killing subprocess" % now)
                p.kill()
                break
            time.sleep(5)
        if not stalled:
            p.wait()
        log("subprocess ended (stall=%s), re-eval total=%d" % (stalled, count_files()))
        if count_files() >= TARGET * 0.995:
            log("target reached: %d" % count_files())
            return

if __name__ == "__main__":
    main()
