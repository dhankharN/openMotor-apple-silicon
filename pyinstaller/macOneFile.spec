# -*- mode: python ; coding: utf-8 -*-
# Build from any working directory with scripts/build-macos-arm64.sh.
import re
from pathlib import Path

root = Path(SPECPATH).parent
version_match = re.search(
    r'^appVersion\s*=\s*\(([^)]+)\)',
    (root / 'uilib' / 'fileIO.py').read_text(),
    re.M,
)
appVersionStr = '.'.join(part.strip() for part in version_match.group(1).split(','))

a = Analysis(
    [str(root / 'main.py')],
    pathex=[str(root)],
    binaries=[],
    datas=[
        (str(root / 'resources'), 'resources'),
        (str(root / 'resources/oMFile256.icns'), '.'),
        (str(root / 'LICENSE'), '.'),
    ],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    # setuptools/pkg_resources are build-only. PyInstaller's pkg_resources
    # runtime hook crashes on setuptools 80 because vendored `backports`
    # is not importable in the frozen app. imageio imports pkg_resources
    # optionally and continues if it is missing.
    excludes=['PyQt5', 'PySide2', 'PySide6', 'tkinter', 'Cython', 'setuptools', 'pkg_resources'],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='openMotor',
    debug=False,
    bootloader_ignore_signals=False,
    # Qt handles its own macOS events; argv emulation conflicts with Qt.
    argv_emulation=False,
    strip=False,
    upx=False,
    console=False,
    target_arch='arm64',
    codesign_identity=None,
)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name='openMotor')
app = BUNDLE(
    coll,
    name='openMotor.app',
    icon=str(root / 'resources/oMIconCycles.icns'),
    version=appVersionStr,
    bundle_identifier='org.openmotor.openMotor',
    info_plist={
        'NSHighResolutionCapable': True,
        'LSMinimumSystemVersion': '12.0',
        'CFBundleDocumentTypes': [{
            'CFBundleTypeName': 'openMotor Motor File',
            'CFBundleTypeExtensions': ['ric'],
            'CFBundleTypeRole': 'Editor',
            'CFBundleTypeIconFile': 'oMFile256.icns',
            'LSHandlerRank': 'Owner',
        }],
    },
)
