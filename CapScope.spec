# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec file for CapScope"""

import sys
from pathlib import Path

block_cipher = None

a = Analysis(
    ['run_gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('data', 'data'),  # 包含股票池数据
    ],
    hiddenimports=[
        'capscope',
        'capscope.universe',
        'capscope.metadata',
        'capscope.prices',
        'capscope.compute',
        'capscope.export',
        'capscope.gui',
        'capscope.gui.app',
        'capscope.gui.main_window',
        'capscope.gui.model',
        'capscope.gui.worker',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='CapScope',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 不显示控制台
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # icon='assets/icon.ico',  # 取消注释并添加图标文件
)
