# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'TagsWidgetUI.ui'
##
## Created by: Qt User Interface Compiler version 6.6.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QGridLayout, QHBoxLayout, QHeaderView,
    QLabel, QLineEdit, QPushButton, QScrollArea,
    QSizePolicy, QTableView, QVBoxLayout, QWidget)

class Ui_TagsWidget(object):
    def setupUi(self, TagsWidget):
        if not TagsWidget.objectName():
            TagsWidget.setObjectName(u"TagsWidget")
        TagsWidget.resize(647, 507)
        self.gridLayout = QGridLayout(TagsWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(-1, -1, -1, 0)
        self.btn_selectExcel = QPushButton(TagsWidget)
        self.btn_selectExcel.setObjectName(u"btn_selectExcel")

        self.horizontalLayout_2.addWidget(self.btn_selectExcel)

        self.lineEdit_excel_path = QLineEdit(TagsWidget)
        self.lineEdit_excel_path.setObjectName(u"lineEdit_excel_path")
        self.lineEdit_excel_path.setReadOnly(True)

        self.horizontalLayout_2.addWidget(self.lineEdit_excel_path)


        self.verticalLayout_3.addLayout(self.horizontalLayout_2)

        self.label = QLabel(TagsWidget)
        self.label.setObjectName(u"label")
        self.label.setMaximumSize(QSize(16777215, 20))

        self.verticalLayout_3.addWidget(self.label)

        self.tableView_excel = QTableView(TagsWidget)
        self.tableView_excel.setObjectName(u"tableView_excel")

        self.verticalLayout_3.addWidget(self.tableView_excel)


        self.horizontalLayout.addLayout(self.verticalLayout_3)

        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(-1, -1, 0, -1)
        self.label_2 = QLabel(TagsWidget)
        self.label_2.setObjectName(u"label_2")

        self.verticalLayout_4.addWidget(self.label_2)

        self.scrollArea = QScrollArea(TagsWidget)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 301, 427))
        self.verticalLayout = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_4.addWidget(self.scrollArea)

        self.label_status = QLabel(TagsWidget)
        self.label_status.setObjectName(u"label_status")

        self.verticalLayout_4.addWidget(self.label_status)


        self.horizontalLayout.addLayout(self.verticalLayout_4)


        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)


        self.retranslateUi(TagsWidget)

        QMetaObject.connectSlotsByName(TagsWidget)
    # setupUi

    def retranslateUi(self, TagsWidget):
        TagsWidget.setWindowTitle(QCoreApplication.translate("TagsWidget", u"Form", None))
        self.btn_selectExcel.setText(QCoreApplication.translate("TagsWidget", u"Select Excel", None))
        self.label.setText(QCoreApplication.translate("TagsWidget", u"File List:", None))
        self.label_2.setText(QCoreApplication.translate("TagsWidget", u"Filter Tags:", None))
        self.label_status.setText(QCoreApplication.translate("TagsWidget", u"Please select a folder to start", None))
    # retranslateUi

