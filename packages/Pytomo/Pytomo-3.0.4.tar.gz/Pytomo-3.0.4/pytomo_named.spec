# -*- mode: python -*-
from platform import system, machine

a = Analysis([os.path.join(HOMEPATH,'support/_mountzlib.py'), os.path.join(HOMEPATH,'support/useUnicode.py'), '/home/louis/streaming/pytomo/Pytomo/bin/pytomo'],
             pathex=['/home/louis/streaming/pytomo/Pytomo/', '/home/louis/streaming/pytomo/Pytomo/pytomo/', '/home/louis/Downloads/pyinstaller-1.5-rc1'])
pyz = PYZ(a.pure)
exe = EXE( pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name=''.join(('_'.join(('pytomo', system().lower(), machine())),
                          '.exe')),
          #name=os.path.join('dist',
          #    '_'.join(('pytomo', system().lower(), machine()))),
          #name=os.path.join('dist', 'pytomo'),
          debug=False,
          strip=False,
          upx=True,
          console=1 )

#for MAC
import sys
if sys.platform.startswith("darwin"):
    app = BUNDLE(exe,
                 name=os.path.join('dist', 'NAME.app'),
                 version=version)

