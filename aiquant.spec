# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = ['openai', 'wordcloud']
hiddenimports += collect_submodules('matplotlib')


a = Analysis(
    ['C:/Users/mine/Downloads/quant_research/main.py'],
    pathex=['C:/Users/mine/Downloads/quant_research'],
    binaries=[],
    datas=[('C:/Users/mine/Downloads/quant_research/aiquant/market/names.json', 'aiquant/market'), ('C:/Users/mine/Downloads/quant_research/aiquant/engine/vendor/data', 'aiquant/engine/vendor/data')],
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
    name='aiquant',
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
)
