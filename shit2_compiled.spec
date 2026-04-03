# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['shit2.py'],
    pathex=[],
    binaries=[],
    datas=[('axe', 'axe'), ('background', 'background'), ('bad1', 'bad1'), ('bad2', 'bad2'), ('new_enemy_black', 'new_enemy_black'), ('new_enemy_white', 'new_enemy_white'), ('new_player', 'new_player'), ('player', 'player'), ('seagull', 'seagull'), ('weapon', 'weapon')],
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
    name='shit2_compiled',
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
