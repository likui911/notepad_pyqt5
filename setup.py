
import sys
from cx_Freeze import setup, Executable
'''
    程序打包可支持文件脚本
    python setup.py build
'''

base = None
if sys.platform == 'win32':
    base = 'Win32GUI'

options = {
    'build_exe': {
        'includes': 'atexit',
        # 包含文件
        'include_files':'resource'
    }
}

executables = [
    Executable('notepad.pyw', base=base)
]

setup(name='notepad',
      version='0.1',
      description='Sample cx_Freeze script',
      options=options,
      executables=executables
      )
