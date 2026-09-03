# -*- coding: utf-8 -*-
import py_compile
f = r"C:/Users/mine/Downloads/quant_research/server.py"
t = open(f, encoding="utf-8").read()

paOld = "def run_pa(symbol, market, tf, stance):\n    from aiquant.market import load\n    from aiquant.pa_llm import run_agent\n    try:\n        df = load(_cat(), \"A股\", symbol, \"daily\")\n    except Exception:\n        df = None\n    try:\n        return run_agent(df, symbol=symbol, market=market, stance=stance)\n    except Exception as e:\n        return {\"label\": (\"激进\" if \"6.24\" in (str(stance) or \"\") else \"稳健\"),\n                \"direction\": \"观望\", \"entry\": None, \"stop\": None, \"target\": None,\n                \"reason\": \"AI 调用失败: %s\" % e, \"tone\": str(stance)}"
paNew = "def run_pa(symbol, market, tf, stance):\n    from aiquant.market import load\n    from aiquant.pa_llm import run_agent\n    try:\n        df = load(_cat(), 'A股', symbol, 'daily')\n    except Exception:\n        df = None\n    try:\n        return run_agent(df, symbol=symbol, market=market, stance=stance)\n    except Exception as e:\n        return {'label': ('激进' if '6.24' in str(stance) else '稳健'),\n                'direction': '观望', 'entry': None, 'stop': None, 'target': None,\n                'reason': 'AI 调用失败: %s' % e, 'tone': str(stance)}"
if paOld in t:
    t = t.replace(paOld, paNew, 1)
    print("run_pa replaced")
else:
    print("run_pa NOT found - appending fresh")
    if 'def run_pa' not in t:
        t += "\n\n" + paNew + "\n"

tail = '''
def _esc(s):
    return str(s or "").replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")


def _api(p):
    path = urlparse(p).path
    qs = parse_qs(urlparse(p).query)
    _q = lambda k, d: qs.get(k, [d])[0]
    if path == "/api/init":
        code, d = init_json(_q("market", "A股"))
        return code, json.dumps(d), "application/json"
    if path == "/api/detail":
        sym = _q("symbol", "600519"); mk = _q("market", "A股"); tf = _q("tf", "daily")
        n = int(_q("n", "160")); lv = int(_q("levels", "4"))
        return 200, json.dumps(detail_json(sym, tf, n, lv, mk)), "application/json"
    if path == "/api/scan":
        return 200, json.dumps(scan_rows(int(_q("limit", "260")))), "application/json"
    if path == "/api/export":
        rows = scan_rows(500).get("rows", [])
        typ = _q("type", "csv")
        if typ == "html":
            return 200, export_html(rows), "text/html; charset=utf-8"
        return 200, export_csv(rows), "text/csv; charset=utf-8"
    if path == "/api/rt/realtime":
        return 200, json.dumps(realtime_json(_q("symbol", "600519"), _q("market", "A股"), _q("tf", "daily"))), "application/json"
    if path == "/api/rt/sentiment":
        return 200, json.dumps(emotion_json()), "application/json"
    if path == "/api/live/quotes":
        syms = qs.get("symbols", ["600519,000001"])[0].split(",")
        return 200, json.dumps(live_quotes(syms)), "application/json"
    if path == "/api/ai/analyze":
        sym = _q("symbol", "600519"); n = int(_q("n", "150"))
        return 200, json.dumps(ai_analyze(sym, n)), "application/json"
    if path == "/api/factor/mine":
        lim = int(_q("limit", "8"))
        return 200, json.dumps(factor_mine(lim)), "application/json"
    if path == "/api/pa/llm":
        sym = _q("symbol", "600519"); mk = _q("market", "A股"); tf = _q("tf", "日线 (D1)"); st = _q("stance", "6.16")
        return 200, json.dumps(run_pa(sym, mk, tf, st)), "application/json"
    return 404, "Not Found", "text/plain"
'''
if "_api(p)" not in t:
    t += tail + "\n"

route_tail = '''

def _route(p):
    path = urlparse(p).path
    if path.startswith("/api"):
        return _api(p)
    if path in ("", "/"):
        path = "/index.html"
    fp = os.path.normpath(os.path.join(WEB, path.lstrip("/")))
    if not os.path.isfile(fp):
        return 404, b"Not Found", "text/html"
    ctype = _CT.get(os.path.splitext(fp)[1].lower(), "application/octet-stream")
    with open(fp, "rb") as fh:
        return 200, fh.read(), ctype


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def do_GET(self):
        try:
            code, body, ctype = _route(self.path)
        except Exception as e:
            code, body, ctype = 500, str(e).encode("utf-8"), "text/plain"
        if isinstance(body, str):
            body = body.encode("utf-8", "replace")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)


class Server(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, port=0, host="127.0.0.1"):
        super().__init__((host, port), Handler)
        self.port = self.server_address[1]
        self._th = None

    def url(self):
        return "http://127.0.0.1:%d/" % self.port

    def start(self):
        self._th = threading.Thread(target=self.serve_forever, daemon=True)
        self._th.start()
        time.sleep(0.6)
        return self

    def stop(self):
        try:
            self.shutdown()
        except Exception:
            pass


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=0)
    ap.add_argument("--no-webview", action="store_true")
    a = ap.parse_args()
    if a.no_webview:
        sv = Server(a.port)
        print("API http://127.0.0.1:%d/" % sv.port)
        sv.serve_forever()
    else:
        import webui_boot  # noqa: F401
        webui_boot.main()


if __name__ == "__main__":
    main()
'''
if "class Handler(BaseHTTPRequestHandler)" not in t:
    t += route_tail + "\n"

open(f, "w", encoding="utf-8").write(t)
py_compile.compile(f, doraise=True)
print("server.py finalized + compiles")