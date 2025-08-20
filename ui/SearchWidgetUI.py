# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'SearchWidgetUI.ui'
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
    QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QPushButton, QScrollArea, QSizePolicy, QSpacerItem,
    QTreeView, QVBoxLayout, QWidget)

class Ui_SearchWidget(object):
    def setupUi(self, SearchWidget):
        if not SearchWidget.objectName():
            SearchWidget.setObjectName(u"SearchWidget")
        SearchWidget.resize(777, 649)
        self.gridLayout = QGridLayout(SearchWidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(-1, -1, -1, 0)
        self.btn_selectFolder = QPushButton(SearchWidget)
        self.btn_selectFolder.setObjectName(u"btn_selectFolder")

        self.horizontalLayout_2.addWidget(self.btn_selectFolder)

        self.lineEdit_path = QLineEdit(SearchWidget)
        self.lineEdit_path.setObjectName(u"lineEdit_path")
        self.lineEdit_path.setReadOnly(True)

        self.horizontalLayout_2.addWidget(self.lineEdit_path)


        self.verticalLayout_3.addLayout(self.horizontalLayout_2)

        self.label = QLabel(SearchWidget)
        self.label.setObjectName(u"label")
        self.label.setMaximumSize(QSize(16777215, 20))

        self.verticalLayout_3.addWidget(self.label)

        self.treeView_folder = QTreeView(SearchWidget)
        self.treeView_folder.setObjectName(u"treeView_folder")

        self.verticalLayout_3.addWidget(self.treeView_folder)


        self.horizontalLayout.addLayout(self.verticalLayout_3)

        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(-1, -1, 0, -1)
        self.label_2 = QLabel(SearchWidget)
        self.label_2.setObjectName(u"label_2")

        self.verticalLayout_4.addWidget(self.label_2)

        self.lineEdit_search_input = QLineEdit(SearchWidget)
        self.lineEdit_search_input.setObjectName(u"lineEdit_search_input")

        self.verticalLayout_4.addWidget(self.lineEdit_search_input)

        self.listWidget = QListWidget(SearchWidget)
        self.listWidget.setObjectName(u"listWidget")

        self.verticalLayout_4.addWidget(self.listWidget)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(-1, -1, -1, 0)
        self.label_3 = QLabel(SearchWidget)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout_3.addWidget(self.label_3)

        self.btn_Preview = QPushButton(SearchWidget)
        self.btn_Preview.setObjectName(u"btn_Preview")

        self.horizontalLayout_3.addWidget(self.btn_Preview)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)


        self.verticalLayout_4.addLayout(self.horizontalLayout_3)

        self.scrollArea = QScrollArea(SearchWidget)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 366, 242))
        self.verticalLayout = QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_4.addWidget(self.scrollArea)

        self.label_status = QLabel(SearchWidget)
        self.label_status.setObjectName(u"label_status")

        self.verticalLayout_4.addWidget(self.label_status)


        self.horizontalLayout.addLayout(self.verticalLayout_4)


        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)


        self.retranslateUi(SearchWidget)

        QMetaObject.connectSlotsByName(SearchWidget)
    # setupUi

    def retranslateUi(self, SearchWidget):
        SearchWidget.setWindowTitle(QCoreApplication.translate("SearchWidget", u"Form", None))
        self.btn_selectFolder.setText(QCoreApplication.translate("SearchWidget", u"Select Folder", None))
        self.label.setText(QCoreApplication.translate("SearchWidget", u"File List:", None))
        self.label_2.setText(QCoreApplication.translate("SearchWidget", u"Search Results:", None))
        self.lineEdit_search_input.setPlaceholderText(QCoreApplication.translate("SearchWidget", u"Enter keyword to search...", None))
        self.label_3.setText(QCoreApplication.translate("SearchWidget", u"File Preview:", None))
        self.btn_Preview.setText(QCoreApplication.translate("SearchWidget", u"Preview", None))
        self.label_status.setText(QCoreApplication.translate("SearchWidget", u"Please select a folder to start", None))
    # retranslateUi

