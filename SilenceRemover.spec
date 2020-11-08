# -*- mode: python -*-

block_cipher = None


a = Analysis(['SilenceRemover.py'],
             pathex=['C:\\Users\\Astrid\\Documents\\Qt Projects\\SilenceRemover'],
             binaries=[],
             datas=[('GenericParamForm.ui', '.'), ('SpecificParamForm.ui', '.')],
             hiddenimports=['PySide2.QtXml'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
a.datas += Tree("C:\\Users\\Astrid\\PycharmProjects\\scriptRemoveSilences\\venv\\Lib\\site-packages\\moviepy", prefix='moviepy')
a.datas += Tree("C:\\Users\\Astrid\\PycharmProjects\\scriptRemoveSilences\\venv\\Lib\\site-packages\\imageio_ffmpeg", prefix='imageio_ffmpeg')
a.datas += Tree("C:\\Users\\Astrid\\PycharmProjects\\scriptRemoveSilences\\venv\\Lib\\site-packages\\proglog", prefix='proglog')
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='SilenceRemover',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='SilenceRemover')
