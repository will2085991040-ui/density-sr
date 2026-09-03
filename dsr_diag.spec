# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:/Users/mine/Downloads/quant_research/z_diag_entry.py'],
    pathex=['C:/Users/mine/Downloads/quant_research', 'C:/Users/mine/Downloads/quant_research/aiquant/engine/vendor'],
    binaries=[],
    datas=[('C:/Users/mine/Downloads/quant_research/webui/index.html', 'webui'), ('C:/Users/mine/Downloads/quant_research/aiquant/market/names.json', 'aiquant/market')],
    hiddenimports=['aiquant.server', 'webview'],
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
    name='dsr_diag',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
