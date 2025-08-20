from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout

from src.SearchWidget import SearchWidget
from src.TagsWidget import TagsWidget
from ui.MainWindowUI import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.resetUi()

    def resetUi(self):
        self.setWindowTitle("TDS Search Tool(1.1.2)")
        self.resize(1100, 900)
        self.statusbar.hide()

        # 完全移除 TabWidget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 创建新的布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)  # 去除所有边距

        # 直接添加 SearchWidget
        self.search_widget = SearchWidget()
        main_layout.addWidget(self.search_widget)
