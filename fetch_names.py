# -*- coding: utf-8 -*-
"""抓取A股名称<->代码映射(经新浪行情API), 写入 aiquant/market/names.json。
循环 50 只/请求, 覆盖整个数据目录内全部A股代码。"""
import os, re, json, sys, time
import urllib.request
sys.path.insert(0, r"C:\Users\mine\Downloads\quant_research")

def scan_codes():
    """从数据目录提取全部A股6位代码(去重, 按 600/000 等)."""
    root = r"C:\Users\mine\Desktop\大A量化监控系统"
    base = os.path.join(root, "A股数据", "parquet", "stocks")
    codes = set()
    if os.path.isdir(base):
        for fn in os.listdir(base):
            if not fn.endswith("_daily.parquet"): continue
            sym = fn[: -len("_daily.parquet")]
            if re.fullmatch(r"\d{6}", sym): codes.add(sym)
    return sorted(codes)

def to_sina(code):
    if code[0] in "69": return "sh" + code  # 6 / 9 开头, 沪
    return "sz" + code                       # 0/3 深

def fetch_batch(codes):
    req = urllib.request.Request("https://hq.sinajs.cn/list=" + ",".join(codes), headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Referer": "https://finance.sina.com.cn/"})
    raw = urllib.request.urlopen(req, timeout=25).read().decode("gbk", "replace")
    out = {}
    for m in re.finditer(r'hq_str_(\w+?)=(?:"([^"]*)"|;)', raw):
        sid, val = m.group(1), m.group(2)
        if not val: continue
        name = val.split(",")[0].strip("\xef\xbb\xbf").strip()
        code = sid[2:]
        if name: out[code] = name
    return out

def board(code):
    if code.startswith(("688", "689")): return "科创板"
    if code.startswith(("300", "301", "302")): return "创业板"
    if code.startswith(("8", "4", "92")): return "北交所"
    return "沪深主板"

def main2():
    codes = scan_codes()
    print("codes found:", len(codes))
    mapping = {}
    for i in range(0, len(codes), 50):
        chunk = codes[i:i+50]
        sina = [to_sina(c) for c in chunk]
        try:
            names = parse_batch(sina)
            for c in chunk:
                if c in names: mapping[c] = {"name": names[c], "board": board(c)}
        except Exception as e:
            print("batch fail", i, e)
        time.sleep(0.15)
        if i % 500 == 0: print("progress", i)
    out_path = os.path.join(r"C:\Users\mine\Downloads\quant_research", "aiquant", "market", "names.json")
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(mapping, fh, ensure_ascii=False)
    print("saved", len(mapping), "codes ->", out_path)

# --- real entry (renamed helpers) ---
def parse_batch(sina_codes):
    import urllib.request
    req = urllib.request.Request("https://hq.sinajs.cn/list=" + ",".join(sina_codes), headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Referer": "https://finance.sina.com.cn/"})
    raw = urllib.request.urlopen(req, timeout=25).read().decode("gbk", "replace")
    out = {}
    for m in re.finditer(r'hq_str_(\w+?)=(?:"([^"]*)"|;)', raw):
        sid, val = m.group(1), m.group(2)
        if not val: continue
        name = val.split(",")[0].strip()
        if name: out[sid[2:]] = name
    return out

def board(code):
    if code.startswith(("688", "689")): return "科创板"
    if code.startswith(("300", "301", "302")): return "创业板"
    if code.startswith(("8", "4", "92")): return "北交所"
    return "沪深主板"

if __name__ == "__main__":
    main2()
