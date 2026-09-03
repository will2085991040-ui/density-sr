# -*- coding: utf-8 -*-
"""Build the 方案C single-file EXE (onefile) with embedded 2.3GB data pack."""
import os, PyInstaller.__main__
HERE = os.path.dirname(os.path.abspath(__file__))
def j(*a): return os.path.join(HERE, *a)
webui = []
for fname in ('index.html','styles.css','echarts.min.js','app.js','chart_interactive.js','chart_realtime.js','pa_llm_ui.js','rt_monitor.js','sentiment_panel.js','channel_panel.js'):
    webui += ['--add-data', j('webui', fname) + os.pathsep + 'webui']
PyInstaller.__main__.run([
    '--noconfirm','--onefile','--windowed','--name','dsr_sr',
    '--distpath', j('dist_v92'), '--workpath', j('build_v92'), '--specpath', HERE,
    '--paths', HERE,
    '--add-data', j('aiquant','market','names.json') + os.pathsep + 'aiquant/market',
    '--paths', j('aiquant','engine','vendor'),
    '--collect-submodules','src',
    '--collect-all','src',
    '--hidden-import','aiquant.factor_mine','--hidden-import','aiquant.live_connector',
    '--hidden-import','aiquant.rt_agent_module','--hidden-import','aiquant.pa_llm','--hidden-import','aiquant.market','--hidden-import','aiquant.market_sentiment','--hidden-import','aiquant.signal_engine','--hidden-import','aiquant.realtime_ths','--hidden-import','aiquant.realtime_sina',
    '--hidden-import','requests','--hidden-import','sklearn','--hidden-import','joblib',
    '--hidden-import','sklearn.ensemble','--hidden-import','sklearn.tree','--hidden-import','sklearn.metrics',
    '--hidden-import','webview','--hidden-import','bottle','--hidden-import','pythonnet',
    '--hidden-import','typing_extensions','--hidden-import','proxy_tools',
    '--collect-submodules','matplotlib',
    '--hidden-import','PyQt6','--hidden-import','PyQt6.QtCore','--hidden-import','PyQt6.QtGui',
    '--hidden-import','PyQt6.QtWidgets','--hidden-import','PyQt6.QtWebEngineWidgets',
    '--hidden-import','PyQt6.QtWebEngineCore','--hidden-import','PyQt6.QtWebEngine',
    '--collect-all','PyQt6.QtWebEngineCore',
    '--hidden-import','openai',
    '--hidden-import','aiquant.channel_analysis',
    '--add-data', j('build','data_pack.zip') + os.pathsep + '.',
    '--add-data', j('knowledge') + os.pathsep + 'knowledge',
    '--version-file', j('version_info.txt'),
    '--icon', j('app_icon.ico'),
] + webui + [
    j('webui_boot.py'),
])
print('DONE_ONEFILE')