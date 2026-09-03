# -*- coding: utf-8 -*-
"""Build aiquant EXE via PyInstaller."""
import PyInstaller.__main__
import os
HERE = os.path.dirname(os.path.abspath(__file__))
PyInstaller.__main__.run([
    "--noconfirm",
    "--onefile",
    "--windowed",
    "--name", "aiquant",
    "--distpath", os.path.join(HERE, "dist"),
    "--workpath", os.path.join(HERE, "build"),
    "--specpath", HERE,
    "--paths", HERE,
    "--add-data", os.path.join(HERE, "aiquant", "market", "names.json") + os.pathsep + "aiquant/market",
    "--add-data", os.path.join(HERE, "aiquant", "engine", "vendor", "data") + os.pathsep + "aiquant/engine/vendor/data",
    "--collect-submodules", "matplotlib",
    "--hidden-import", "openai",
    "--hidden-import", "wordcloud",
    os.path.join(HERE, "main.py"),
])
print("DONE")
