import sys
import fitz  # PyMuPDF
from PySide6.QtWidgets import (QMainWindow, QLabel, QVBoxLayout,
                               QWidget, QScrollArea
                               )
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import Qt


# ===== 新窗口类：用于在独立窗口中显示 PDF =====
class PDFWindow(QMainWindow):
    def __init__(self, filename=None):
        super().__init__()
        self.setWindowTitle("PDF 查看器 - 新窗口")
        self.resize(800, 600)

        # 滚动区域
        scroll_area = QScrollArea()
        content_widget = QWidget()
        self.image_layout = QVBoxLayout()

        content_widget.setLayout(self.image_layout)
        scroll_area.setWidget(content_widget)
        scroll_area.setWidgetResizable(True)

        self.setCentralWidget(scroll_area)

        if filename:
            self.load_pdf(filename)

    def load_pdf(self, filename):
        """加载并渲染 PDF 文件"""
        try:
            doc = fitz.open(filename)
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                zoom = fitz.Matrix(1.0, 1.0)
                pix = page.get_pixmap(matrix=zoom, dpi=150)

                # 构造 QImage（注意格式）
                image = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(image)

                label = QLabel()
                label.setPixmap(pixmap)
                label.setAlignment(Qt.AlignCenter)
                label.setScaledContents(True)

                self.image_layout.addWidget(label)
        except Exception as e:
            print("加载 PDF 失败：", e)
