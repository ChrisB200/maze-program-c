# -*- mode: python ; coding: utf-8 -*-

import sys
from PyInstaller.utils.hooks import copy_metadata

# Determine platform-specific library extensions and paths
if sys.platform == 'win32':
    # On Windows
    binaries = [
        ('lib/maze-generator.dll', '.'),
        ('lib/maze-solver.dll', '.')
    ]
elif sys.platform == 'linux':
    # On Linux
    binaries = [
        ('lib/libmaze-generator.so', '.'),
        ('lib/libmaze-solver.so', '.')
    ]
else:
    raise RuntimeError(f"Unsupported platform: {sys.platform}")

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=[],
    hiddenimports=[],
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
    name='main',
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

