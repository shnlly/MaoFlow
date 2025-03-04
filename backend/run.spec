# run.spec
block_cipher = None

# 添加以下路径到pathex（根据你的conda环境路径）
conda_env_path = '/opt/homebrew/anaconda3/envs/MaoFlow12/lib/python3.12/site-packages/'

a = Analysis(
    ['run.py'],
    pathex=['/Users/shnlly/dev/MaoFlow/backend', conda_env_path],  # 添加项目路径和conda环境路径
    binaries=[],
    datas=[
        ('.env.development', '.'),  # 添加环境配置文件
        ('maoflow.db', '.'),  # 添加数据库文件
    ],
    hiddenimports=[
        'pydantic._internal._config',
        'pydantic._internal._fields',
        'uvicorn.protocols.websockets',
        # 增加以下内容
        'uvicorn.protocols.http.h11_impl',
        'uvicorn.protocols.websockets.websockets_impl',
        'uvicorn.protocols.websockets.wsproto_impl',
        'uvicorn.lifespan.on',
        'uvicorn.lifespan.off',
        'uvicorn.protocols.http',
        'uvicorn.protocols.websockets',
        'uvicorn.loops.auto',
        'pydantic.json',
        'sqlalchemy.util._collections',
        'sqlalchemy.util.queue',
        'aiosqlite',
        'sqlalchemy.dialects.sqlite',
        'sqlalchemy.ext.asyncio',
        'sqlalchemy.ext.asyncio.engine',
        'main',
        'fastapi',
        'uvicorn',
        'pydantic',
        'starlette',
        'pydantic.functional_validators',
        'fastapi.middleware.cors',
        'pydantic_settings',
        'pydantic_settings.main',
        'pydantic_settings.sources',
        'dotenv',
        'python-dotenv',
        # 添加新的依赖
        'uvicorn.config',
        'uvicorn.main',
        'uvicorn.server',
        'uvicorn.supervisors',
        'uvicorn.supervisors.multiprocess',
        'uvicorn.supervisors.statreload',
        'h11',
        'starlette.routing',
        'starlette.applications',
        'starlette.responses',
        'starlette.requests',
        'starlette.middleware',
        'starlette.middleware.cors',
        'starlette.middleware.base',
        'starlette.types',
        'starlette.datastructures',
        'starlette.background',
        'starlette.concurrency',
        'fastapi.applications',
        'fastapi.routing',
        'fastapi.encoders',
        'fastapi.responses',
        'fastapi.requests',
        'fastapi.params',
        'fastapi.dependencies',
        'fastapi.security',
        'fastapi.openapi',
        'fastapi.exception_handlers'
    ],  # 显式声明所有相关依赖
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
    name='maoflow',
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
