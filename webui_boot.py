# -*- coding: utf-8 -*-
"DENSITY-SR engine web EXE entry (offline).  GUI/webview 在 主线程 运行。"
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import server


def main():
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
        sys.stderr.write("server start error: %s\n" % _b)
        raise

    # 方案2: 内嵌数据自解压(如需) - 必须在 server 加载数据前完成
    try:
        from aiquant.ensure_data import ensure_data
        _root = ensure_data()
        if _root:
            os.environ["DSRS_DATA_ROOT"] = _root
    except Exception as _e:
        sys.stderr.write("ensure_data error: %s\n" % _e)

    import webview
    # pywebview/Qt 必须在主线程创建窗口。
    webview.create_window(
        "DENSITY·SR 阿尔法量化价格行为 · 支撑阻力引擎 (v3.2)",
        url, width=1640, height=940, min_size=(1200, 740),
    )
    webview.start()
    srv.stop()


if __name__ == "__main__":
    main()
