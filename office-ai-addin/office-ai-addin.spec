# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for Office AI Add-in
Run: pyinstaller office-ai-addin.spec
This creates: dist/OfficeAI.exe (single file with everything bundled)
"""

import sys
from PyInstaller.utils.hooks import collect_submodules
from pathlib import Path

a = Analysis(
    ['launcher.py'],
    pathex=[str(Path.cwd())],
    binaries=[],
    datas=[
        ('addin', 'addin'),
        ('backend', 'backend'),
    ],
    hiddenimports=[
        'uvicorn',
        'fastapi',
        'pydantic',
        'httpx',
    ] + collect_submodules('PyQt5'),
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='OfficeAI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',  # Optional: add an icon
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='OfficeAI'
)
