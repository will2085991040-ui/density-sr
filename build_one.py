# -*- coding: utf-8 -*-
"标准单文件发行版: PyInstaller --onefile + 图标 + 版本资源。"
import os, PyInstaller.__main__
HERE = os.path.dirname(os.path.abspath(__file__))
def j(*a): return os.path.join(HERE, *a)
extra = []
for fname in ("index.html","styles.css","app.js","echarts.min.js"):
    extra += ["--add-data", j("webui", fname) + os.pathsep + "webui"]
icons = ["--icon", j("app_icon.ico")] if os.path.exists(j("app_icon.ico")) else []
PyInstaller.__main__.run([
    "--noconfirm","--onefile","--windowed","--name","DENSITY-SR",
    "--distpath", j("dist_one"), "--workpath", j("work_one"), "--specpath", HERE,
    "--paths", HERE,
    "--add-data", j("aiquant","market","names.json") + os.pathsep + "aiquant/market",
    "--add-data", j("aiquant","engine","vendor","data") + os.pathsep + "data",
    "--add-data", j("aiquant","engine","vendor","data") + os.pathsep + "aiquant/engine/vendor/data",
    "--paths", j("aiquant","engine","vendor"),
    "--collect-submodules", "src", "--collect-all", "src",
    "--hidden-import", "aiquant.factor_mine", "--hidden-import", "aiquant.live_connector",
    "--hidden-import", "requests", "--hidden-import", "sklearn", "--hidden-import", "joblib",
    "--hidden-import", "sklearn.ensemble", "--hidden-import", "sklearn.tree", "--hidden-import", "sklearn.metrics",
    "--hidden-import","webview","--hidden-import","bottle","--hidden-import","pythonnet",
    "--hidden-import","typing_extensions","--hidden-import","proxy_tools",
    "--collect-submodules","matplotlib",
    "--version-file", j("version_info.txt"),
    "--icon", j("app_icon.ico"),
] + icons + extra + [
    j("webui_boot.py"),
])
print('DONE_ONEFILE')