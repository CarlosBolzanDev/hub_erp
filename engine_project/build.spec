# PyInstaller spec for GenericRuntime (onedir recommended for plugin/script runtime)
block_cipher = None

a = Analysis(
    ['runtime_entry.py'],
    pathex=[],
    binaries=[],
    datas=[('configs', 'configs'), ('app/assets', 'app/assets')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name='GenericRuntime', console=False)
coll = COLLECT(exe, a.binaries, a.zipfiles, a.datas, name='GenericRuntime')
