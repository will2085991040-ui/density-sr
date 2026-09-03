# -*- coding: utf-8 -*-
"""aiquant 启用入口：有 --cli 参数走命令行，否则启动图形界面(EXE 双击)。"""
import os, sys
ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# 允许用户通过环境变量指定数据根目录（默认: 桌面大A量化监控系统）
if os.environ.get("PA_DATA_ROOT"):
    os.environ.setdefault("PAUNT_DIR", os.environ["PA_DATA_ROOT"])

def main():
    if "--cli" in sys.argv or len(sys.argv) > 1 and sys.argv[1] not in ("--cli",):
        import app as appc
        # 少数参数情形交给 app 的 argparse
        return app.main()
    import gui
    a = gui.AiquantApp()
    a.mainloop()

def cli():
    import app
    return app.main()

if __name__ == "__main__":
    if "--cli" in sys.argv:
        raise SystemExit(cli())
    import gui
    g = gui.AiquantApp()
    g.mainloop()
