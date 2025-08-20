import os
import shutil
import subprocess
from PyInstaller.__main__ import run

# 清理之前的构建
if os.path.exists('build'):
    shutil.rmtree('build')
if os.path.exists('dist'):
    shutil.rmtree('dist')

# PyInstaller 配置
opts = [
    'main.py',
    '--name=PDFSearch',
    '--onefile',
    '--windowed',
    '--icon=img/app_icon.ico',
    '--add-data=ui;ui',
    '--add-data=img;img',
    '--add-data=src;src',
    '--hidden-import=PySide6.QtXml',
    '--hidden-import=pymupdf',
    '--hidden-import=pandas',
    '--collect-data=pymupdf'
]

# 运行打包
run(opts)