# SistemaLuthier.spec

a = Analysis(
    ['run.py'],
    pathex=['C:\\Program Files\\GTK3-Runtime Win64\\bin'],
    binaries=[],
    datas=[
        ('config.py', '.'),      # <-- Linha crítica 1: Adiciona o config.py
        ('luthier.db', '.'),     # <-- Adiciona o banco de dados
        ('app/templates', 'app/templates'),
        ('app/static', 'app/static')
    ],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False
)
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SistemaLuthier',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,        # <-- Linha crítica 2: Usa a lista de 'datas' acima
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SistemaLuthier'
)