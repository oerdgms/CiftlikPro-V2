# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

project_root = Path(SPECPATH)
app_root = project_root / "app"

a = Analysis(
    [str(app_root / "desktop_launcher.py")],
    pathex=[str(app_root)],
    binaries=[],
    datas=[
        (str(app_root / "README.txt"), "."),
        (str(app_root / "KURULUM.txt"), "."),
        (str(app_root / "FEATURES.md"), "."),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="CiftlikPro",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    icon=str(project_root / "CiftlikPro.ico"),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="CiftlikPro",
)
