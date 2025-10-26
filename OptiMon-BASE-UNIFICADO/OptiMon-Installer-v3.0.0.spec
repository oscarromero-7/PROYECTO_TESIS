# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['installer_gui.py'],
    pathex=[],
    binaries=[],
    datas=[('app.py', '.'), ('requirements.txt', '.'), ('docker-compose.yml', '.'), ('config', 'config'), ('core', 'core'), ('templates', 'templates'), ('.env.azure', '.')],
    hiddenimports=['tkinter', 'tkinter.ttk', 'requests'],
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
    name='OptiMon-Installer-v3.0.0',
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
