# -*- coding: utf-8 -*-
"""Build the 方案2 (方案C) data-embedded DENSITY·SR EXE.
Bundles Compressed data_pack.zip (3GB -> 2.3GB) via --add-data.
Output: dist_embed/dsr_sr (onedir) with data_pack.zip inside _internal/.
"""
import os, PyInstaller.__main__
HERE = os.path.dirname(os.path.abspath(__file__))
def j(*a): return os.path.join(HERE, *a)

webui = []
for fname in ("index.html","styles.css","app.js","pa_llm_ui.js","echarts.min.js"):
    webui += ["--add-data", j("webui", fname) + os.pathsep + "webui"]

PyInstaller.__main__.run([
    "--noconfirm","--onedir","--windowed","--name","dsr_sr",
    "--distpath", j("dist_embed"), "--workpath", j("build_embed"), "--specpath", HERE,
    "--paths", HERE,
    "--add-data", j("aiquant","market","names.json") + os.pathsep + "aiquant/market",
    "--add-data", j("aiquant","engine","vendor","data") + os.pathsep + "data",
    "--add-data", j("aiquant","engine","vendor","data") + os.pathsep + "aiquant/engine/vendor/data",
    "--paths", j("aiquant","engine","vendor"),
    "--collect-submodules", "src",
    "--collect-all", "src",
    "--hidden-import", "aiquant.factor_mine", "--hidden-import", "aiquant.live_connector",
    "--hidden-import", "requests", "--hidden-import", "sklearn", "--hidden-import", "joblib",
    "--hidden-import", "sklearn.ensemble", "--hidden-import", "sklearn.tree", "--hidden-import", "sklearn.metrics",
    "--hidden-import","webview","--hidden-import","bottle","--hidden-import","pythonnet",
    "--hidden-import","typing_extensions","--hidden-import","proxy_tools",
    "--collect-submodules","matplotlib",
    "--hidden-import","PyQt6","--hidden-import","PyQt6.QtCore",
    "--hidden-import","PyQt6.QtGui","--hidden-import","PyQt6.QtWidgets",
    "--hidden-import","PyQt6.QtWebEngineWidgets","--hidden-import","PyQt6.QtWebEngineCore",
    "--hidden-import","PyQt6.QtWebEngine",
    "--collect-all","PyQt6.QtWebEngineCore",
    "--hidden-import","openai",
    # 方案C: 内嵌压缩数据包 (2.3GB)
    "--add-data", j("build","data_pack.zip") + os.pathsep + ".",
    "--version-file", j("version_info.txt"),
    "--icon", j("app_icon.ico"),
] + webui + [
    j("webui_boot.py"),
])
print("DONE_EMBED")
