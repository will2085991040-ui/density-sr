# -*- coding: utf-8 -*-
p = "C:/Users/mine/Downloads/quant_research/webui_boot.py"
t = open(p, encoding="utf-8").read()
old = '''def main():
    # 方案2: 内嵌数据自解压(如需) - 必须在 server 加载数据前完成
    try:
        from aiquant.ensure_data import ensure_data
        _root = ensure_data()
        if _root:
            os.environ["DSRS_DATA_ROOT"] = _root
    except Exception as _e:
        sys.stderr.write("ensure_data error: %s\\n" % _e)

    import webview
    srv = server.Server(port=0).start()          # HTTP 引擎在守护线程,非 GUI
    url = srv.url()
    try:
        with open(os.path.join(os.path.expanduser("~"), "_dsr_sr_boot.txt"), "w") as f:
            f.write(url)
    except Exception:
        pass
    # pywebview/Qt 必须在主线程创建窗口。
    webview.create_window('''
new = '''def main():
    # 先启动 HTTP 引擎(可独立验证, 即便后续 GUI 失败也不影响可用性)
    try:
        srv = server.Server(port=0).start()
        url = srv.url()
        try:
            with open(os.path.join(os.path.expanduser("~"), "_dsr_sr_boot.txt"), "w") as f:
                f.write(url)
        except Exception:
            pass
    except Exception as _b:
        sys.stderr.write("server start error: %s\\n" % _b)
        raise

    # 方案2: 内嵌数据自解压(如需) - 必须在 server 加载数据前完成
    try:
        from aiquant.ensure_data import ensure_data
        _root = ensure_data()
        if _root:
            os.environ["DSRS_DATA_ROOT"] = _root
    except Exception as _e:
        sys.stderr.write("ensure_data error: %s\\n" % _e)

    import webview
    # pywebview/Qt 必须在主线程创建窗口。
    webview.create_window('''
assert old in t, "boot main block"
t = t.replace(old, new, 1)
open(p, "w", encoding="utf-8").write(t)
import py_compile; py_compile.compile(p, doraise=True)
print("webui_boot reordered")
