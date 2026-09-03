# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.utils.hooks import collect_all

datas = [('C:/Users/mine/Downloads/quant_research/aiquant/market/names.json', 'aiquant/market'), ('C:/Users/mine/Downloads/quant_research/build/data_pack.zip', '.'), ('C:/Users/mine/Downloads/quant_research/knowledge', 'knowledge'), ('C:/Users/mine/Downloads/quant_research/webui/index.html', 'webui'), ('C:/Users/mine/Downloads/quant_research/webui/styles.css', 'webui'), ('C:/Users/mine/Downloads/quant_research/webui/echarts.min.js', 'webui'), ('C:/Users/mine/Downloads/quant_research/webui/app.js', 'webui'), ('C:/Users/mine/Downloads/quant_research/webui/chart_interactive.js', 'webui'), ('C:/Users/mine/Downloads/quant_research/webui/chart_realtime.js', 'webui'), ('C:/Users/mine/Downloads/quant_research/webui/pa_llm_ui.js', 'webui'), ('C:/Users/mine/Downloads/quant_research/webui/rt_monitor.js', 'webui'), ('C:/Users/mine/Downloads/quant_research/webui/sentiment_panel.js', 'webui'), ('C:/Users/mine/Downloads/quant_research/webui/channel_panel.js', 'webui')]
binaries = []
hiddenimports = ['aiquant.factor_mine', 'aiquant.live_connector', 'aiquant.rt_agent_module', 'aiquant.pa_llm', 'aiquant.market', 'aiquant.market_sentiment', 'aiquant.signal_engine', 'aiquant.realtime_ths', 'aiquant.realtime_sina', 'requests', 'sklearn', 'joblib', 'sklearn.ensemble', 'sklearn.tree', 'sklearn.metrics', 'webview', 'bottle', 'pythonnet', 'typing_extensions', 'proxy_tools', 'PyQt6', 'PyQt6.QtCore', 'PyQt6.QtGui', 'PyQt6.QtWidgets', 'PyQt6.QtWebEngineWidgets', 'PyQt6.QtWebEngineCore', 'PyQt6.QtWebEngine', 'openai', 'aiquant.channel_analysis']
hiddenimports += collect_submodules('src')
hiddenimports += collect_submodules('matplotlib')
tmp_ret = collect_all('src')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('PyQt6.QtWebEngineCore')
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
    name='dsr_sr',
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
    icon=['C:/Users/mine/Downloads/quant_research/app_icon.ico'],
)
