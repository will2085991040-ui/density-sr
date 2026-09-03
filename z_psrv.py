# -*- coding: utf-8 -*-
p = "C:/Users/mine/Downloads/quant_research/server.py"
t = open(p, encoding="utf-8").read()
# Replace the Server + Start + webview_main section to match webui_boot interface:
old = '''class Server(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, port=0, host="127.0.0.1"):
        super().__init__((host, port), Handler)
        self.port = self.server_address[1]

    def url(self):
        return "http://127.0.0.1:%d/" % self.port


class Start(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self.server = Server(0)

    def run(self):
        self.server.serve_forever()


def webview_main():
    import webview
    sv = Start(); sv.start()
    time.sleep(1.2)
    url = sv.server.url()
    try:
        os.makedirs(os.path.expanduser("~"), exist_ok=True)
        open(os.path.expanduser("~/_dsr_sr_boot.txt"), "w").write(url)
    except Exception:
        pass
    webview.create_window("DENSITY-SR", url, width=1440, height=900,
                          background_color="#121212")
    try:
        webview.start(debug=False)
    finally:
        sv.server.shutdown()


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
        webview_main()


if __name__ == "__main__":
    main()'''
new = '''class Server(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, port=0, host="127.0.0.1"):
        super().__init__((host, port), Handler)
        self.port = self.server_address[1]
        self._th = None

    def url(self):
        return "http://127.0.0.1:%d/" % self.port + ""

    def start(self):
        # 兼容 webui_boot: Server(port).start() 在守护线程跑, 返回 self
        self._th = threading.Thread(target=self.serve_forever, daemon=True)
        self._th.start()
        import time as _t
        _t.sleep(0.6)
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
        import webui_boot  # noqa: F401  启动 webview 入口
        webui_boot.main()


if __name__ == "__main__":
    main()'''
assert old in t, "server section not found"
t = t.replace(old, new, 1)
open(p, "w", encoding="utf-8").write(t)
import py_compile
py_compile.compile(p, doraise=True)
print("Server.start/stop added, compiles")
# quick dev verify: webui_boot-style start
