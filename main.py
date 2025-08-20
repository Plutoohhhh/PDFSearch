import sys

from PySide6.QtWidgets import QApplication
from src.MainWindow import MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)  # 创建应用程序实例对象
    main_window = MainWindow()  # 创建窗口实例对象
    main_window.show()  # 显示窗口
    n = app.exec()  # 执行exec()方法，进入事件循环，若遇到窗口退出命令，返回整数n
    try:
        sys.exit(n)  # 通知python系统，结束程序运行。
    except SystemExit:
        print(f"程序非正常退出{n}")
