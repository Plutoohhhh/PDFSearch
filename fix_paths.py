# fix_paths.py
import sys
import os

if getattr(sys, 'frozen', False):
    # 重定向标准库路径
    base_path = sys._MEIPASS
    sys._stdlib_dir = os.path.join(base_path, 'lib')
    os.environ['PATH'] = base_path + os.pathsep + os.environ['PATH']

    # 添加PySide6插件路径
    from PySide6 import QtCore

    plugin_path = os.path.join(base_path, 'PySide6', 'plugins')
    QtCore.QCoreApplication.addLibraryPath(plugin_path)