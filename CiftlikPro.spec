# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

project_root = Path(SPECPATH)
app_root = project_root / "app"

datas = []
for optional_name in ("README.txt", "KURULUM.txt", "FEATURES.md", "feed_catalog.json"):
    optional_file = app_root / optional_name
    if optional_file.exists():
        datas.append((str(optional_file), "."))

a = Analysis(
    [str(app_root / "desktop_launcher.py")],
    pathex=[str(app_root)],
    binaries=[],
    datas=datas,
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
