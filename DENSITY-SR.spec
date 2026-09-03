# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.utils.hooks import collect_all

datas = [('C:/Users/mine/Downloads/quant_research/aiquant/market/names.json', 'aiquant/market'), ('C:/Users/mine/Downloads/quant_research/aiquant/engine/vendor/data', 'data'), ('C:/Users/mine/Downloads/quant_research/aiquant/engine/vendor/data', 'aiquant/engine/vendor/data'), ('C:/Users/mine/Downloads/quant_research/webui/index.html', 'webui'), ('C:/Users/mine/Downloads/quant_research/webui/styles.css', 'webui'), ('C:/Users/mine/Downloads/quant_research/webui/app.js', 'webui'), ('C:/Users/mine/Downloads/quant_research/webui/echarts.min.js', 'webui')]
binaries = []
hiddenimports = ['aiquant.factor_mine', 'aiquant.live_connector', 'requests', 'sklearn', 'joblib', 'sklearn.ensemble', 'sklearn.tree', 'sklearn.metrics', 'webview', 'bottle', 'pythonnet', 'typing_extensions', 'proxy_tools']
hiddenimports += collect_submodules('src')
hiddenimports += collect_submodules('matplotlib')
tmp_ret = collect_all('src')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['C:/Users/mine/Downloads/quant_research/webui_boot.py'],
    pathex=['C:/Users/mine/Downloads/quant_research', 'C:/Users/mine/Downloads/quant_research/aiquant/engine/vendor'],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='DENSITY-SR',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='C:/Users/mine/Downloads/quant_research/version_info.txt',
    icon=['C:/Users/mine/Downloads/quant_research/app_icon.ico', 'C:/Users/mine/Downloads/quant_research/app_icon.ico'],
)
