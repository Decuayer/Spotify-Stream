# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['stream-script.py'],
    pathex=[],
    hiddenimports=[
        'undetected_chromedriver', 
        'selenium.webdriver.chrome.service', 
        'selenium.webdriver.chrome.options', 
        'selenium.webdriver.common.by', 
        'selenium.webdriver.common.keys', 
        'selenium.webdriver.support.ui', 
        'selenium.webdriver.support.expected_conditions', 
        'selenium.webdriver.support.ui.Select',
        'selenium.webdriver.ActionChains', 
        'selenium.common.exceptions.StaleElementReferenceException', 
        'webdriver_manager.chrome', 
        'fake_useragent', 
        'selenium_stealth', 
        'fake_headers'
    ],
    binaries=[],
    datas=[
        ('env/Lib/site-packages/undetected_chromedriver/*', 'undetected_chromedriver'),
        ('env/Lib/site-packages/selenium/*', 'selenium'),
        ('env/Lib/site-packages/webdriver_manager/*', 'webdriver_manager'),
        ('env/Lib/site-packages/fake_useragent/*', 'fake_useragent'),
        ('env/Lib/site-packages/selenium_stealth/*', 'selenium_stealth'),
        ('env/Lib/site-packages/fake_headers/*', 'fake_headers'),
    ],
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
    name='stream-script',
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
