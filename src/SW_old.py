import os
import platform
import sys
import shutil
import subprocess
from datetime import datetime, time
from pathlib import Path

import pandas as pd
from PySide6.QtGui import QImage, QPixmap, Qt, QAction, QStandardItem, QIcon, QStandardItemModel
from PySide6.QtWidgets import QFileDialog, QLabel, QMessageBox, QMenu, QInputDialog, \
    QFormLayout, QCheckBox, QDateEdit, QPushButton, QGroupBox, QListWidgetItem, QWidget, QTreeView, QAbstractItemView, \
    QApplication, QStyle, QFileIconProvider, QHBoxLayout, QComboBox, QLineEdit, QVBoxLayout
from PySide6.QtCore import QDir, QDate, QFileInfo, QStandardPaths
from PySide6.QtWidgets import QFileSystemModel

from src.PDFWindow import PDFWindow
# PyMuPDF
import pymupdf as fitz

from ui.SearchWidgetUI import Ui_SearchWidget


class SearchWidget(QWidget, Ui_SearchWidget):

    def __init__(self):
        super().__init__()
        self.model = None
        self.current_path = []
        self.icon_cache = {}
        self.virtual_root = None  # 虚拟根节点
        self.excel_path = None  # 添加excel_path变量存储路径
        # 用于保存新窗口对象（防止被 GC 回收）
        self.windows = []

        # 添加递归操作标志
        self.recursive_operation = False  # 防止递归操作死循环

        # 添加Excel数据存储变量
        self.excel_data = None
        self.grouped_unique_first_col = []
        self.grouped_unique_second_col = []
        self.grouped_unique_third_col = []

        self.setupUi(self)
        self.resetUi()
        self.bind()

    def resetUi(self):
        self.treeView_folder.setEnabled(False)
        self.lineEdit_search_input.setEnabled(False)
        # 页面缩放选项
        self.zoom_factor = 1.0
        self.scale_step = 0.1

        # 启用拖放
        self.treeView_folder.setAcceptDrops(True)
        self.treeView_folder.dragEnterEvent = self.dragEnterEvent
        self.treeView_folder.dragMoveEvent = self.dragMoveEvent
        self.treeView_folder.dropEvent = self.dropEvent

        # 重新组织布局 - 保持原有框架，只调整右侧布局
        # 获取右侧主布局
        main_layout = self.verticalLayout_4

        # 1. 将搜索输入框移动到顶部
        main_layout.removeWidget(self.lineEdit_search_input)
        main_layout.insertWidget(0, self.lineEdit_search_input)

        # 2. 添加文件夹选择行
        folder_layout = QHBoxLayout()
        folder_layout.addWidget(self.btn_selectFolder)
        folder_layout.addWidget(self.lineEdit_path)

        # 添加刷新按钮
        self.btn_refresh_folder = QPushButton()
        self.btn_refresh_folder.setIcon(QApplication.style().standardIcon(QStyle.SP_BrowserReload))
        self.btn_refresh_folder.setToolTip("刷新文件夹")
        self.btn_refresh_folder.setFixedSize(30, 30)
        folder_layout.addWidget(self.btn_refresh_folder)

        # 只添加一次布局
        main_layout.insertLayout(1, folder_layout)

        # 3. 添加Excel文件选择行
        excel_layout = QHBoxLayout()
        self.btn_selectExcel = QPushButton("选择Excel文件")
        self.lineEdit_excel_path = QLineEdit()
        self.lineEdit_excel_path.setReadOnly(True)

        # 添加"打开位置"按钮
        self.btn_open_excel_location = QPushButton()
        self.btn_open_excel_location.setIcon(QApplication.style().standardIcon(QStyle.SP_DirOpenIcon))
        self.btn_open_excel_location.setToolTip("在资源管理器中打开文件位置")
        self.btn_open_excel_location.setFixedSize(30, 30)  # 固定按钮大小
        self.btn_open_excel_location.setEnabled(False)  # 初始不可用

        # 修复：只添加一次布局
        excel_layout.addWidget(self.btn_selectExcel)
        excel_layout.addWidget(self.lineEdit_excel_path)
        excel_layout.addWidget(self.btn_open_excel_location)  # 添加打开位置按钮
        main_layout.insertLayout(2, excel_layout)

        # 4. 添加属性筛选区域
        self.property_filter_group = QGroupBox("属性筛选")
        property_layout = QVBoxLayout()

        # 添加属性筛选复选框和下拉框
        self.enable_category_checkbox = QCheckBox("Material Category")
        self.category_combo = QComboBox()

        self.enable_model_checkbox = QCheckBox("Material Model")
        self.model_combo = QComboBox()

        self.enable_apn_checkbox = QCheckBox("APN")
        self.apn_combo = QComboBox()

        # 添加自定义属性筛选
        self.enable_custom_filter_checkbox = QCheckBox("自定义属性")
        self.custom_filter_input = QLineEdit()
        self.custom_filter_input.setPlaceholderText("输入筛选关键词")

        # 使下拉框内容可复制
        self.category_combo.setEditable(True)
        self.category_combo.lineEdit().setReadOnly(True)
        self.category_combo.lineEdit().setAlignment(Qt.AlignCenter)

        self.model_combo.setEditable(True)
        self.model_combo.lineEdit().setReadOnly(True)
        self.model_combo.lineEdit().setAlignment(Qt.AlignCenter)

        self.apn_combo.setEditable(True)
        self.apn_combo.lineEdit().setReadOnly(True)
        self.apn_combo.lineEdit().setAlignment(Qt.AlignCenter)

        # 修复：确保初始状态与复选框一致
        self.enable_category_checkbox.setChecked(False)
        self.enable_model_checkbox.setChecked(False)
        self.enable_apn_checkbox.setChecked(False)
        self.enable_custom_filter_checkbox.setChecked(False)  # 默认启用

        # 连接复选框状态改变事件 - 使用新的连接方式
        self.enable_category_checkbox.toggled.connect(
            lambda checked: self.category_combo.setEnabled(checked))
        self.enable_model_checkbox.toggled.connect(
            lambda checked: self.model_combo.setEnabled(checked))
        self.enable_apn_checkbox.toggled.connect(
            lambda checked: self.apn_combo.setEnabled(checked))
        self.enable_custom_filter_checkbox.toggled.connect(
            lambda checked: self.custom_filter_input.setEnabled(checked))

        # 设置初始状态
        self.category_combo.setEnabled(False)
        self.model_combo.setEnabled(False)
        self.apn_combo.setEnabled(False)
        self.custom_filter_input.setEnabled(False)

        # 添加筛选行
        category_layout = QHBoxLayout()
        category_layout.addWidget(self.enable_category_checkbox)
        category_layout.addWidget(self.category_combo)
        property_layout.addLayout(category_layout)

        model_layout = QHBoxLayout()
        model_layout.addWidget(self.enable_model_checkbox)
        model_layout.addWidget(self.model_combo)
        property_layout.addLayout(model_layout)

        apn_layout = QHBoxLayout()
        apn_layout.addWidget(self.enable_apn_checkbox)
        apn_layout.addWidget(self.apn_combo)
        property_layout.addLayout(apn_layout)

        # 添加自定义筛选行
        custom_layout = QHBoxLayout()
        custom_layout.addWidget(self.enable_custom_filter_checkbox)
        custom_layout.addWidget(self.custom_filter_input)
        property_layout.addLayout(custom_layout)

        self.property_filter_group.setLayout(property_layout)
        main_layout.insertWidget(3, self.property_filter_group)

        # 5. 添加时间筛选区域
        self.start_date = QDateEdit()
        self.start_date.setCalendarPopup(True)
        self.start_date.setDate(QDate.currentDate().addDays(-7))  # 默认过去7天

        self.end_date = QDateEdit()
        self.end_date.setCalendarPopup(True)
        self.end_date.setDate(QDate.currentDate())

        self.clear_time_button = QPushButton("重置时间")
        self.clear_time_button.clicked.connect(self.reset_time_filter)

        self.enable_time_filter_checkbox = QCheckBox("启用时间筛选")

        time_group = QGroupBox("时间筛选（可选）")
        time_layout = QFormLayout()
        time_layout.addRow(self.enable_time_filter_checkbox)
        time_layout.addRow("起始日期:", self.start_date)
        time_layout.addRow("结束日期:", self.end_date)
        time_layout.addRow(self.clear_time_button)
        time_group.setLayout(time_layout)
        main_layout.insertWidget(4, time_group)

        # 6. 将搜索结果标签和列表移到下方
        # 确保搜索结果标签在列表上方
        main_layout.removeWidget(self.label_2)
        main_layout.insertWidget(5, self.label_2)

        main_layout.removeWidget(self.listWidget)
        main_layout.insertWidget(6, self.listWidget)

        # 7. 确保预览区域相关控件在底部
        # 获取 horizontalLayout_3 中的所有控件
        preview_label = self.label_3
        preview_button = self.btn_Preview
        spacer = self.horizontalSpacer

        # 从布局中移除这些控件
        self.horizontalLayout_3.removeWidget(preview_label)
        self.horizontalLayout_3.removeWidget(preview_button)
        self.horizontalLayout_3.removeItem(spacer)

        # 添加保存按钮（提前到这里）
        self.btn_save_as = QPushButton("另存为")
        self.btn_save_as.setEnabled(False)

        # 创建新的布局用于预览区域
        preview_layout = QHBoxLayout()
        preview_layout.addWidget(preview_label)
        preview_layout.addWidget(preview_button)

        # 添加全选和取消全选按钮
        self.btn_select_all_list = QPushButton("全选列表")
        self.btn_deselect_all_list = QPushButton("取消全选列表")
        preview_layout.addWidget(self.btn_select_all_list)
        preview_layout.addWidget(self.btn_deselect_all_list)

        preview_layout.addWidget(self.btn_save_as)  # 添加到预览布局中
        preview_layout.addItem(spacer)

        # 添加到主布局
        main_layout.insertLayout(7, preview_layout)

        # 设置列表支持复选框
        self.listWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)

        # 8. 添加预览区域
        main_layout.removeWidget(self.scrollArea)
        main_layout.insertWidget(8, self.scrollArea)

        # 9. 状态标签保持在底部
        main_layout.removeWidget(self.label_status)
        main_layout.addWidget(self.label_status)

        # 添加勾选状态监控变量
        self.has_selected_items = False




    def bind(self):
        self.btn_selectFolder.clicked.connect(self.select_folder)
        self.btn_selectExcel.clicked.connect(self.on_btn_selectExcel)
        self.btn_open_excel_location.clicked.connect(self.open_excel_location)
        self.category_combo.currentIndexChanged.connect(self.update_model_apn)
        # self.btn_selectpdf.clicked.connect(self.select_pdf)
        self.treeView_folder.clicked.connect(self.treeView_folder_clicked)
        self.lineEdit_search_input.textChanged.connect(self.search_files)
        self.enable_time_filter_checkbox.toggled.connect(self.search_files)
        self.start_date.dateChanged.connect(self.search_files)
        self.end_date.dateChanged.connect(self.search_files)
        self.btn_select_all_list.clicked.connect(self.select_all_in_list)
        self.btn_deselect_all_list.clicked.connect(self.deselect_all_in_list)
        self.btn_refresh_folder.clicked.connect(self.refresh_selected_folders)
        self.custom_filter_input.textChanged.connect(self.search_files)

        # 绑定列表项变化事件以更新按钮状态
        self.listWidget.itemChanged.connect(self.on_list_selection_changed)
        self.listWidget.customContextMenuRequested.connect(self.show_list_context_menu)
        self.listWidget.itemClicked.connect(self.show_file_preview)

        # treeView绑定右键点击事件
        self.treeView_folder.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treeView_folder.customContextMenuRequested.connect(self.show_context_menu)

        self.btn_Preview.clicked.connect(self.show_pdf_window)

        # 添加双击事件绑定
        self.treeView_folder.doubleClicked.connect(self.open_selected_file)
        self.listWidget.itemDoubleClicked.connect(self.open_selected_file)
        self.listWidget.setContextMenuPolicy(Qt.CustomContextMenu)

        # 绑定另存为按钮
        self.btn_save_as.clicked.connect(self.save_selected_files)

        # 复选框状态改变时触发搜索
        self.enable_category_checkbox.stateChanged.connect(self.trigger_search)
        self.enable_model_checkbox.stateChanged.connect(self.trigger_search)
        self.enable_apn_checkbox.stateChanged.connect(self.trigger_search)
        self.enable_custom_filter_checkbox.stateChanged.connect(self.trigger_search)

        # 下拉框和输入框变更时触发搜索
        self.category_combo.currentIndexChanged.connect(self.trigger_search)
        self.model_combo.currentIndexChanged.connect(self.trigger_search)
        self.apn_combo.currentIndexChanged.connect(self.trigger_search)
        self.custom_filter_input.textChanged.connect(self.trigger_search)

        # 绑定全选和取消全选按钮
        self.btn_select_all_list.clicked.connect(self.select_all_in_list)
        self.btn_deselect_all_list.clicked.connect(self.deselect_all_in_list)

    def trigger_search(self):
        """触发搜索的通用方法，确保所有条件变更都能正确触发搜索"""
        # 确保搜索在UI线程中执行
        QApplication.processEvents()
        self.search_files()
    # ----------- 菜单功能 Start -----------

    def show_context_menu(self, position):
        index = self.treeView_folder.indexAt(position)
        if not index.isValid():
            return

        item = self.model.itemFromIndex(index)
        path = item.data(Qt.UserRole)  # 从 UserRole 获取完整路径

        menu = QMenu(self)

        # 添加"打开"选项
        action_open = QAction("打开文件", self)
        action_open.triggered.connect(lambda: self.open_file(path))
        menu.addAction(action_open)

        # 添加"在资源管理器中显示"菜单项
        action_show_in_finder = QAction("显示在资源管理器中", self)
        action_show_in_finder.triggered.connect(lambda: self.show_in_finder(path))
        menu.addAction(action_show_in_finder)

        # 如果是文件夹，添加"新建文件夹"选项
        if os.path.isdir(path):
            action_new_folder = QAction("新建文件夹", self)
            action_new_folder.triggered.connect(lambda: self.create_new_folder(path))
            menu.addAction(action_new_folder)

        # 添加"重命名"和"删除"选项
        action_rename = QAction("重命名", self)
        action_rename.triggered.connect(lambda: self.rename_file(path))
        menu.addAction(action_rename)

        action_delete = QAction("删除", self)
        action_delete.triggered.connect(lambda: self.delete_file(path))
        menu.addAction(action_delete)

        # 添加"复制路径"选项
        action_copy_path = QAction("复制文件路径", self)
        action_copy_path.triggered.connect(lambda: self.copy_file_path(path))
        menu.addAction(action_copy_path)

        menu.addSeparator()

        action_select_all = QAction("全选", self)
        action_select_all.triggered.connect(self.select_all_in_tree)
        menu.addAction(action_select_all)

        action_deselect_all = QAction("取消全选", self)
        action_deselect_all.triggered.connect(self.deselect_all_in_tree)
        menu.addAction(action_deselect_all)

        # 添加对文件的选择支持
        if os.path.isfile(path):
            menu.addSeparator()
            action_select_file = QAction("选择此文件", self)
            action_select_file.triggered.connect(lambda: self.toggle_file_selection(path, True))
            menu.addAction(action_select_file)

            action_deselect_file = QAction("取消选择此文件", self)
            action_deselect_file.triggered.connect(lambda: self.toggle_file_selection(path, False))
            menu.addAction(action_deselect_file)

        menu.exec(self.treeView_folder.viewport().mapToGlobal(position))

    # 添加 toggle_file_selection 方法
    def toggle_file_selection(self, path, selected):
        """切换单个文件的选择状态"""
        if not self.model:
            return

        def find_and_set(parent_item):
            for row in range(parent_item.rowCount()):
                child_item = parent_item.child(row)
                child_path = child_item.data(Qt.UserRole)
                if child_path == path:
                    child_item.setCheckState(Qt.Checked if selected else Qt.Unchecked)
                    return True
                if child_item.hasChildren():
                    if find_and_set(child_item):
                        return True
            return False

        for row in range(self.virtual_root.rowCount()):
            root_item = self.virtual_root.child(row)
            find_and_set(root_item)
    # 添加选择功能
    def select_all_in_tree(self):
        """全选树视图中的项"""
        if not self.model:
            return

        def set_all_checked(parent_item, state):
            for row in range(parent_item.rowCount()):
                child_item = parent_item.child(row)
                child_item.setCheckState(state)
                if child_item.hasChildren():
                    set_all_checked(child_item, state)

        for row in range(self.virtual_root.rowCount()):
            root_item = self.virtual_root.child(row)
            set_all_checked(root_item, Qt.Checked)

    def deselect_all_in_tree(self):
        """取消全选树视图中的项"""
        if not self.model:
            return

        def set_all_checked(parent_item, state):
            for row in range(parent_item.rowCount()):
                child_item = parent_item.child(row)
                child_item.setCheckState(state)
                if child_item.hasChildren():
                    set_all_checked(child_item, state)

        for row in range(self.virtual_root.rowCount()):
            root_item = self.virtual_root.child(row)
            set_all_checked(root_item, Qt.Unchecked)

    def select_all_in_list(self):
        """全选列表视图中的项"""
        for i in range(self.listWidget.count()):
            item = self.listWidget.item(i)
            item.setCheckState(Qt.Checked)

    def deselect_all_in_list(self):
        """取消全选列表视图中的项"""
        for i in range(self.listWidget.count()):
            item = self.listWidget.item(i)
            item.setCheckState(Qt.Unchecked)

    # 添加新方法 update_save_button_state
    def update_save_button_state(self):
        """更新另存为按钮状态"""
        has_selected = False

        # 检查树视图是否有选中的项
        if self.model:
            # 使用栈进行非递归遍历
            stack = []
            for row in range(self.virtual_root.rowCount()):
                stack.append(self.virtual_root.child(row))

            while stack:
                item = stack.pop()
                if item.checkState() == Qt.Checked:
                    has_selected = True
                    break

                # 添加子项到栈中
                for row in range(item.rowCount()):
                    stack.append(item.child(row))

        # 检查列表视图是否有选中的项
        if not has_selected:
            for i in range(self.listWidget.count()):
                item = self.listWidget.item(i)
                if item.checkState() == Qt.Checked:
                    has_selected = True
                    break

        # 更新按钮状态
        self.btn_save_as.setEnabled(has_selected)
    def copy_file_path(self, path):
        """复制文件路径到剪贴板"""
        clipboard = QApplication.clipboard()
        clipboard.setText(path)
        QMessageBox.information(self, "复制成功", "文件路径已复制到剪贴板。")

    def show_in_finder(self, path):
        """在资源管理器中显示文件位置 - 已做跨平台兼容处理"""
        # 确保路径存在
        if not os.path.exists(path):
            QMessageBox.warning(self, "路径不存在", "该文件或文件夹不存在，无法打开。")
            return

        system = platform.system()

        try:
            # 在 Windows 部分添加更健壮的处理
            if system == "Windows":
                try:
                    # 使用 os.startfile 更可靠
                    if os.path.isfile(path):
                        subprocess.Popen(f'explorer /select,"{os.path.normpath(path)}"')
                    else:
                        os.startfile(os.path.normpath(path))
                except Exception as e:
                    QMessageBox.critical(self, "打开失败", f"无法在资源管理器中打开该路径：\n{e}")

            elif system == "Darwin":  # macOS
                if os.path.isfile(path):
                    # macOS中打开文件所在文件夹并选中文件
                    subprocess.run(["open", "-R", path])
                else:
                    # 直接打开文件夹
                    subprocess.run(["open", path])

            elif system == "Linux":
                # 尝试多种文件管理器
                try:
                    if os.path.isfile(path):
                        # 打开文件所在文件夹
                        subprocess.run(["xdg-open", os.path.dirname(path)])
                    else:
                        subprocess.run(["xdg-open", path])
                except:
                    try:
                        if os.path.isfile(path):
                            subprocess.run(["nautilus", os.path.dirname(path)])
                        else:
                            subprocess.run(["nautilus", path])
                    except:
                        try:
                            if os.path.isfile(path):
                                subprocess.run(["dolphin", os.path.dirname(path)])
                            else:
                                subprocess.run(["dolphin", path])
                        except:
                            QMessageBox.warning(self, "错误", "无法找到可用的文件管理器")
            else:
                QMessageBox.warning(self, "不支持的操作系统", "当前系统不支持'显示在资源管理器中'功能。")
        except Exception as e:
            QMessageBox.critical(self, "打开失败", f"无法在资源管理器中打开该路径：\n{e}")

    def create_new_folder(self, path):
        if os.path.isfile(path):
            path = os.path.dirname(path)

        folder_name, ok = QInputDialog.getText(self, "新建文件夹", "请输入文件夹名称:")
        if ok and folder_name:
            new_path = os.path.join(path, folder_name)
            if not os.path.exists(new_path):
                os.makedirs(new_path)
                self.refresh_folder(path)
            else:
                QMessageBox.warning(self, "错误", "文件夹已存在")

    def rename_file(self, old_path):
        dir_path = os.path.dirname(old_path)
        old_name = os.path.basename(old_path)
        new_name, ok = QInputDialog.getText(self, "重命名", "请输入新名称:", text=old_name)
        if ok and new_name and new_name != old_name:
            new_path = os.path.join(dir_path, new_name)
            if not os.path.exists(new_path):
                os.rename(old_path, new_path)
                self.refresh_folder(dir_path)
            else:
                QMessageBox.warning(self, "错误", "文件名已存在")

    def delete_file(self, path):
        reply = QMessageBox.question(self, "确认删除", f"确定要删除 {os.path.basename(path)} 吗？",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                if os.path.isdir(path):
                    os.rmdir(path)  # 只能删除空文件夹
                else:
                    os.remove(path)
                self.refresh_folder(os.path.dirname(path))
            except Exception as e:
                QMessageBox.critical(self, "删除失败", str(e))

    # 添加打开文件的方法
    def open_selected_file(self, item):
        """打开选中的文件"""
        if isinstance(item, QListWidgetItem):  # 来自搜索结果列表
            path = item.data(Qt.UserRole)
        else:  # 来自树视图
            index = self.treeView_folder.currentIndex()
            if not index.isValid():
                return
            item = self.model.itemFromIndex(index)
            if item is None:
                return
            path = item.data(Qt.UserRole)
            if not path:
                return

        self.open_file(path)

    def refresh_folder(self, folder_path):
        """刷新特定文件夹的内容"""
        if not self.model:
            return

        # 找到对应的文件夹项
        for row in range(self.virtual_root.rowCount()):
            root_item = self.virtual_root.child(row)
            if root_item.data(Qt.UserRole) == folder_path:
                # 删除所有子项
                root_item.removeRows(0, root_item.rowCount())
                # 重新填充文件夹内容
                self.populate_folder_tree(root_item, folder_path)
                self.treeView_folder.expand(root_item.index())
                break
            else:
                # 递归搜索子文件夹
                self.refresh_folder_recursive(root_item, folder_path)

    def open_file(self, path):
        if not os.path.exists(path):
            QMessageBox.warning(self, "文件不存在", "该文件可能已被删除或移动。")
            return

        try:
            if platform.system() == "Windows":
                # 使用更可靠的方式打开文件
                try:
                    os.startfile(path)
                except:
                    # 备用方法
                    subprocess.Popen(f'start "" "{path}"', shell=True)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", path])
            elif platform.system() == "Linux":
                subprocess.run(["xdg-open", path])
            else:
                QMessageBox.warning(self, "不支持的操作系统", "当前系统不支持直接打开文件。")
        except Exception as e:
            QMessageBox.critical(self, "打开失败", f"无法打开文件：\n{e}")

    def refresh_folder_recursive(self, parent_item, folder_path):
        """递归搜索并刷新文件夹"""
        for row in range(parent_item.rowCount()):
            child_item = parent_item.child(row)
            child_path = child_item.data(Qt.UserRole)

            if child_path == folder_path and os.path.isdir(child_path):
                # 删除所有子项
                child_item.removeRows(0, child_item.rowCount())
                # 重新填充文件夹内容
                self.populate_folder_tree(child_item, folder_path)
                self.treeView_folder.expand(child_item.index())
                return True

            if os.path.isdir(child_path) and folder_path.startswith(child_path):
                # 递归搜索子文件夹
                if self.refresh_folder_recursive(child_item, folder_path):
                    return True

        return False

    # ----------- 菜单功能 End -----------

    # ----------- 拖拽上传功能 Start -----------
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        # 获取点击位置的目录
        index = self.treeView_folder.indexAt(event.position().toPoint())
        path = self.model.filePath(index)
        if not index.isValid() or os.path.isfile(path):
            path = self.treeView_folder  # 如果点击无效或文件，则上传到根目录

        # 获取拖拽的文件路径
        for url in event.mimeData().urls():
            src_path = url.toLocalFile()
            dst_path = os.path.join(path, os.path.basename(src_path))

            if os.path.exists(dst_path):
                reply = QMessageBox.question(self, "覆盖确认", f"文件 {dst_path} 已存在，是否覆盖？")
                if reply != QMessageBox.Yes:
                    continue

            try:
                if os.path.isdir(src_path):
                    shutil.copytree(src_path, dst_path, dirs_exist_ok=True)
                else:
                    shutil.copy2(src_path, dst_path)
            except Exception as e:
                QMessageBox.critical(self, "复制失败", str(e))
                continue

        self.refresh_folder(path)
    # ----------- 拖拽上传功能 End -----------

    # ----------- 导入文件夹功能 Start -----------

    def select_folder(self):
        # 使用更友好的多选文件夹对话框
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.Directory)
        dialog.setOption(QFileDialog.DontUseNativeDialog, True)
        dialog.setOption(QFileDialog.ShowDirsOnly, True)
        dialog.setWindowTitle("选择文件夹 (可多选)")

        # 获取对话框中的树视图并启用多选
        tree_view = dialog.findChild(QTreeView)
        if tree_view:
            tree_view.setSelectionMode(QAbstractItemView.ExtendedSelection)

        if dialog.exec() == QFileDialog.Accepted:
            folders = dialog.selectedFiles()
        else:
            folders = []

        if folders:
            self.current_paths = folders
            self.lineEdit_search_input.setEnabled(True)
            self.label_status.setText(f"已选择 {len(folders)} 个文件夹")
            self.lineEdit_path.setText(", ".join([os.path.basename(f) for f in folders]))

            # 创建虚拟根模型来显示多个根节点
            self.model = QStandardItemModel()
            self.model.setHorizontalHeaderLabels(["文件夹"])

            # 为每个选择的文件夹创建根节点
            self.virtual_root = self.model.invisibleRootItem()
            for folder in folders:
                # 创建文件夹项 - 使用系统文件夹图标
                root_item = QStandardItem(QApplication.style().standardIcon(QStyle.SP_DirIcon),
                                          os.path.basename(folder))
                root_item.setData(folder, Qt.UserRole)  # 存储完整路径
                root_item.setEditable(False)
                self.virtual_root.appendRow(root_item)

                # 递归填充文件夹内容
                self.populate_folder_tree(root_item, folder)

            self.treeView_folder.setModel(self.model)
            self.treeView_folder.setHeaderHidden(True)
            self.treeView_folder.expandAll()
            self.treeView_folder.setEnabled(True)

            # 正确的信号连接方式 - 连接到模型而不是单个项
            self.model.itemChanged.connect(self.on_tree_item_changed)  # 修改为新的处理方法
            self.model.itemChanged.connect(self.update_save_button_state)

            # 初始更新一次按钮状态
            self.update_save_button_state()
            self.update_selected_count()

    def populate_folder_tree(self, parent_item, folder_path):
        """递归填充文件夹内容到树状视图"""
        try:
            # 获取文件夹内容并排序（先文件夹后文件）
            entries = []
            for entry in os.listdir(folder_path):
                full_path = os.path.join(folder_path, entry)
                if not entry.startswith('.'):  # 跳过隐藏文件
                    entries.append((entry, full_path, os.path.isdir(full_path)))

            # 排序：文件夹在前，文件在后
            entries.sort(key=lambda x: (not x[2], x[0].lower()))

            for entry, full_path, is_dir in entries:
                if is_dir:
                    # 添加文件夹项
                    dir_item = QStandardItem(QApplication.style().standardIcon(QStyle.SP_DirIcon), entry)
                    dir_item.setData(full_path, Qt.UserRole)
                    dir_item.setEditable(False)
                    dir_item.setCheckable(True)

                    # 删除错误的连接方式
                    # dir_item.dataChanged.connect(...)  # 这是错误的!

                    parent_item.appendRow(dir_item)

                    # 递归添加子文件夹（不立即展开）
                    self.populate_folder_tree(dir_item, full_path)
                else:
                    # 添加文件项
                    file_icon = self.get_file_icon(full_path)
                    file_item = QStandardItem()
                    file_item.setText(entry)
                    file_item.setIcon(file_icon)
                    file_item.setData(full_path, Qt.UserRole)
                    file_item.setEditable(False)
                    file_item.setCheckable(True)
                    file_item.setCheckState(Qt.Unchecked)
                    parent_item.appendRow(file_item)
        except PermissionError:
            # 创建无权限访问的提示项
            error_item = QStandardItem(QApplication.style().standardIcon(QStyle.SP_MessageBoxWarning),
                                       "无权限访问")
            error_item.setData(folder_path, Qt.UserRole)
            error_item.setEditable(False)
            error_item.setEnabled(False)
            parent_item.appendRow(error_item)
        except Exception as e:
            # 创建错误提示项
            error_item = QStandardItem(QApplication.style().standardIcon(QStyle.SP_MessageBoxCritical),
                                       f"错误: {str(e)}")
            error_item.setData(folder_path, Qt.UserRole)
            error_item.setEditable(False)
            error_item.setEnabled(False)
            parent_item.appendRow(error_item)
    def on_folder_checkstate_changed(self, state, path, item):
        """当文件夹勾选状态改变时，递归设置所有子项"""
        if self.recursive_operation:
            return

        self.recursive_operation = True
        try:
            # 获取新状态
            new_state = item.checkState()

            # 递归设置所有子项
            self.set_children_checkstate(item, new_state)

            # 更新保存按钮状态
            self.update_save_button_state()
        finally:
            self.recursive_operation = False

    def set_children_checkstate(self, parent_item, state):
        """递归设置所有子项的勾选状态"""
        for row in range(parent_item.rowCount()):
            child_item = parent_item.child(row)
            child_path = child_item.data(Qt.UserRole)

            # 跳过无效项
            if child_path is None:
                continue

            # 设置子项状态
            child_item.setCheckState(state)

            # 如果子项是文件夹，递归设置其子项
            if child_item.hasChildren() and os.path.isdir(child_path):
                self.set_children_checkstate(child_item, state)

    def get_file_icon(self, file_path):
        """跨平台获取文件图标"""
        # 检查缓存
        if file_path in self.icon_cache:
            return self.icon_cache[file_path]

        # 获取图标
        if os.path.isdir(file_path):
            icon = QApplication.style().standardIcon(QStyle.SP_DirIcon)
        else:
            # 使用更高效的方法获取文件图标
            file_info = QFileInfo(file_path)
            file_icon_provider = QFileIconProvider()
            icon = file_icon_provider.icon(file_info)

        # 存入缓存
        self.icon_cache[file_path] = icon
        return icon

    def select_pdf(self):
        # 弹出文件选择对话框，允许选择多个PDF文件
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "选择一个或多个PDF文件",
            "",
            "PDF Files (*.pdf);;All Files (*)"
        )

        # print("aaaa: ",file_paths)

        if not file_paths:
            return  # 用户取消选择

        # 过滤只保留PDF文件
        pdf_files = [f for f in file_paths if f.lower().endswith('.pdf')]
        if not pdf_files:
            return  # 没有有效PDF文件被选择

        # 设置当前路径为第一个PDF文件的所在目录
        self.current_path = os.path.dirname(pdf_files[0])

        # 启用搜索框
        self.lineEdit_search_input.setEnabled(True)
        # 显示当前路径
        self.label_status.setText(f"Current Path: {self.current_path}")

        # 设置左侧的文件树结构（显示所有PDF所在目录的公共路径）
        if len(pdf_files) == 1:
            common_parent = os.path.dirname(pdf_files[0])  # 取文件所在目录
        else:
            common_parent = os.path.commonpath(pdf_files)

        # 确保路径是有效目录
        if not os.path.isdir(common_parent):
            QMessageBox.warning(self, "路径错误", f"找不到有效的目录：{common_parent}")
            return

        self.model = QFileSystemModel()
        self.model.setRootPath(common_parent)
        self.model.setFilter(QDir.NoDotAndDotDot | QDir.AllEntries)
        # # 启用文件系统监听 默认开启
        # self.model.setOption(QFileSystemModel.Option.WatchForChanges)

        self.treeView_folder.setModel(self.model)
        self.treeView_folder.setRootIndex(self.model.index(common_parent))
        self.treeView_folder.setEnabled(True)

    # ----------- 导入文件夹功能 End -----------
    def show_list_context_menu(self, position):
        """显示列表的右键菜单"""
        menu = QMenu(self)

        # 添加"全选"选项
        action_select_all = QAction("全选", self)
        action_select_all.triggered.connect(self.select_all_in_list)
        menu.addAction(action_select_all)

        # 添加"取消全选"选项
        action_deselect_all = QAction("取消全选", self)
        action_deselect_all.triggered.connect(self.deselect_all_in_list)
        menu.addAction(action_deselect_all)

        menu.addSeparator()

        # 添加"打开文件"选项
        item = self.listWidget.itemAt(position)
        if item:
            path = item.data(Qt.UserRole)
            action_open = QAction("打开文件", self)
            action_open.triggered.connect(lambda: self.open_file(path))
            menu.addAction(action_open)

            # 添加"在资源管理器中显示"选项
            action_show_in_finder = QAction("显示在资源管理器中", self)
            action_show_in_finder.triggered.connect(lambda: self.show_in_finder(path))
            menu.addAction(action_show_in_finder)

        menu.exec(self.listWidget.viewport().mapToGlobal(position))

    def reset_time_filter(self):
        """重置为默认时间范围（过去7天）"""
        self.start_date.setDate(QDate.currentDate().addDays(-7))
        self.end_date.setDate(QDate.currentDate())
        self.search_files()

    # ----------- 搜索功能 Start -----------

    # ----------- 搜索功能 Start -----------

    def search_files(self):
        keyword = self.lineEdit_search_input.text().strip().lower()
        self.listWidget.clear()

        # 如果没有选择文件夹，则返回
        if not self.current_paths:
            self.btn_save_as.setEnabled(False)
            return

        # 获取所有筛选条件的当前状态
        category_enabled = self.enable_category_checkbox.isChecked()
        category_value = self.category_combo.currentText().lower() if category_enabled else ""

        model_enabled = self.enable_model_checkbox.isChecked()
        model_value = self.model_combo.currentText().lower() if model_enabled else ""

        apn_enabled = self.enable_apn_checkbox.isChecked()
        apn_value = self.apn_combo.currentText().lower() if apn_enabled else ""

        custom_enabled = self.enable_custom_filter_checkbox.isChecked()
        custom_value = self.custom_filter_input.text().strip().lower() if custom_enabled else ""

        time_enabled = self.enable_time_filter_checkbox.isChecked()

        # 检查是否有任何有效的筛选条件
        has_any_condition = (
                bool(keyword) or
                (category_enabled and category_value) or
                (model_enabled and model_value) or
                (apn_enabled and apn_value) or
                (custom_enabled and custom_value) or
                time_enabled
        )

        # 如果没有设置任何筛选条件，则清空结果
        if not has_any_condition:
            self.listWidget.clear()
            self.btn_save_as.setEnabled(False)
            return

        # 时间筛选处理
        start_timestamp = None
        end_timestamp = None

        if time_enabled:
            start_date = self.start_date.date().toPython()
            end_date = self.end_date.date().toPython()
            start_timestamp = int(datetime(start_date.year, start_date.month, start_date.day).timestamp())
            end_timestamp = int(
                datetime(end_date.year, end_date.month, end_date.day, 23, 59, 59).timestamp())

        # 遍历所有选择的路径
        for base_path in self.current_paths:
            for root, dirs, files in os.walk(base_path):
                for name in dirs + files:
                    full_path = os.path.join(root, name)
                    name_lower = name.lower()

                    # 1. 关键字匹配
                    keyword_match = not keyword or keyword in name_lower

                    # 2. 属性筛选
                    category_match = not (category_enabled and category_value) or category_value in name_lower
                    model_match = not (model_enabled and model_value) or model_value in name_lower
                    apn_match = not (apn_enabled and apn_value) or apn_value in name_lower

                    # 3. 自定义属性匹配
                    custom_match = not (custom_enabled and custom_value) or custom_value in name_lower

                    # 4. 时间匹配
                    time_match = True
                    if time_enabled:
                        try:
                            mtime = os.path.getmtime(full_path)
                            time_match = (start_timestamp <= mtime <= end_timestamp)
                        except OSError:
                            time_match = False  # 忽略无法访问的文件

                    # 应用所有筛选条件（使用逻辑与）
                    if not (keyword_match and category_match and model_match and
                            apn_match and custom_match and time_match):
                        continue

                    # 显示相对路径，使结果更清晰
                    rel_path = os.path.relpath(full_path, base_path)
                    display_text = f"{os.path.basename(base_path)}/{rel_path}"

                    item = QListWidgetItem(display_text)
                    item.setData(Qt.UserRole, full_path)  # 保存完整路径

                    # 设置文件图标
                    if os.path.isdir(full_path):
                        item.setIcon(QApplication.style().standardIcon(QStyle.SP_DirIcon))
                    else:
                        file_icon = self.get_file_icon(full_path)
                        item.setIcon(file_icon)

                    item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                    item.setCheckState(Qt.Unchecked)  # 初始状态为未选中

                    self.listWidget.addItem(item)

        # 更新按钮状态
        self.update_save_button_state()

    def select_all_in_list(self):
        """全选列表中的项"""
        for i in range(self.listWidget.count()):
            item = self.listWidget.item(i)
            item.setCheckState(Qt.Checked)

    def deselect_all_in_list(self):
        """取消全选列表中的项"""
        for i in range(self.listWidget.count()):
            item = self.listWidget.item(i)
            item.setCheckState(Qt.Unchecked)

    # ----------- 搜索功能 End -----------

    # 收集选中文件路径的方法
    def get_selected_files(self):
        """获取所有选中的文件路径（只包括明确勾选的文件）"""
        selected_files = set()

        # 收集树视图中选中的文件
        if self.model:
            # 使用栈进行非递归遍历
            stack = []
            for row in range(self.virtual_root.rowCount()):
                stack.append(self.virtual_root.child(row))

            while stack:
                item = stack.pop()
                path = item.data(Qt.UserRole)
                state = item.checkState()

                # 只处理被勾选的项
                if state == Qt.Checked:
                    if os.path.isfile(path):
                        selected_files.add(path)
                    elif os.path.isdir(path):
                        # 递归收集文件夹中所有文件（但不包括未勾选的子项）
                        self.collect_checked_files_from_folder(item, selected_files)

                # 如果项是部分勾选（文件夹中有部分文件被取消勾选），继续检查其子项
                elif state == Qt.PartiallyChecked or state == Qt.Unchecked:
                    # 添加子项到栈中
                    for row in range(item.rowCount()):
                        stack.append(item.child(row))

        # 收集列表视图中选中的文件
        for i in range(self.listWidget.count()):
            item = self.listWidget.item(i)
            if item.checkState() == Qt.Checked:
                path = item.data(Qt.UserRole)
                if os.path.isfile(path):
                    selected_files.add(path)

        return list(selected_files)
    # 添加另存为功能

    def collect_checked_files_from_folder(self, parent_item, selected_files):
        """递归收集文件夹中被勾选的文件"""
        for row in range(parent_item.rowCount()):
            child_item = parent_item.child(row)
            child_path = child_item.data(Qt.UserRole)
            state = child_item.checkState()

            # 只处理被勾选的项
            if state == Qt.Checked:
                if os.path.isfile(child_path):
                    selected_files.add(child_path)
                elif os.path.isdir(child_path):
                    # 递归收集子文件夹中被勾选的文件
                    self.collect_checked_files_from_folder(child_item, selected_files)

            # 如果子项是部分勾选（文件夹中有部分文件被取消勾选），继续检查其子项
            elif state == Qt.PartiallyChecked:
                # 递归收集子文件夹中被勾选的文件
                self.collect_checked_files_from_folder(child_item, selected_files)

    def save_selected_files(self):
        selected_files = self.get_selected_files()

        if not selected_files:
            QMessageBox.information(self, "无选中文件", "请先勾选要保存的文件")
            return

        # 弹出文件夹选择对话框
        save_dir = QFileDialog.getExistingDirectory(
            self,
            "选择保存位置",
            options=QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )

        if not save_dir:
            return  # 用户取消

        # 分析文件选择模式
        folder_selections = set()
        individual_files = set()

        # 收集所有被选中的文件夹
        if self.model:
            # 使用栈进行非递归遍历
            stack = []
            for row in range(self.virtual_root.rowCount()):
                stack.append(self.virtual_root.child(row))

            while stack:
                item = stack.pop()
                path = item.data(Qt.UserRole)
                if os.path.isdir(path) and item.checkState() == Qt.Checked:
                    folder_selections.add(path)

                # 添加子项到栈中
                for row in range(item.rowCount()):
                    stack.append(item.child(row))

        # 将文件分类：属于文件夹选择的 vs 单独选择的
        for file_path in selected_files:
            if os.path.isdir(file_path):
                continue  # 跳过文件夹本身

            # 检查文件是否属于某个被选中的文件夹
            in_folder = False
            norm_file_path = os.path.normcase(os.path.normpath(file_path))
            for folder in folder_selections:
                norm_folder = os.path.normcase(os.path.normpath(folder))
                if norm_file_path.startswith(norm_folder + os.sep):
                    in_folder = True
                    break

            if not in_folder:
                individual_files.add(file_path)

        # 检查目标位置是否有同名文件
        existing_files = []

        # 处理文件夹选择 - 保留原始结构
        for folder in folder_selections:
            # 找出所有属于这个文件夹的文件
            folder_files = [f for f in selected_files
                            if os.path.commonprefix([f, folder]) == folder]

            for file_path in folder_files:
                # 计算相对于源文件夹的相对路径
                rel_path = os.path.relpath(file_path, folder)
                dest_path = os.path.join(save_dir, os.path.basename(folder), rel_path)
                dest_dir = os.path.dirname(dest_path)

                if os.path.exists(dest_path):
                    existing_files.append(dest_path)

        # 检查单独选择的文件
        for file_path in individual_files:
            # 获取文件名（不带路径）
            file_name = os.path.basename(file_path)
            dest_path = os.path.join(save_dir, file_name)

            if os.path.exists(dest_path):
                existing_files.append(dest_path)

        # 初始化覆盖变量
        overwrite_all = False
        reply = QMessageBox.No  # 默认设置为不覆盖

        # 如果有重复文件，询问用户
        if existing_files:
            msg = f"检测到 {len(existing_files)} 个文件已存在:\n"
            msg += "\n".join([os.path.basename(f) for f in existing_files[:5]])  # 最多显示5个文件名
            if len(existing_files) > 5:
                msg += f"\n...及其他 {len(existing_files) - 5} 个文件"

            msg += "\n\n是否覆盖这些文件？"

            reply = QMessageBox.question(
                self,
                "文件已存在",
                msg,
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
                QMessageBox.No
            )

            if reply == QMessageBox.Cancel:
                return  # 用户取消操作
            elif reply == QMessageBox.YesToAll:
                overwrite_all = True

        # 复制文件，保持原始结构
        success_count = 0
        skipped_count = 0
        error_files = []

        # 处理文件夹选择 - 保留原始结构
        for folder in folder_selections:
            # 找出所有属于这个文件夹的文件
            folder_files = [f for f in selected_files
                            if os.path.commonprefix([f, folder]) == folder]

            for file_path in folder_files:
                # 计算相对于源文件夹的相对路径
                rel_path = os.path.relpath(file_path, folder)
                dest_path = os.path.join(save_dir, os.path.basename(folder), rel_path)
                dest_dir = os.path.dirname(dest_path)

                # 检查是否应该覆盖
                if os.path.exists(dest_path) and not overwrite_all and not (reply == QMessageBox.Yes):
                    skipped_count += 1
                    continue

                try:
                    # 创建目标目录
                    os.makedirs(dest_dir, exist_ok=True)

                    # 复制文件
                    shutil.copy2(file_path, dest_path)
                    success_count += 1
                except Exception as e:
                    error_files.append(f"{os.path.basename(file_path)}: {str(e)}")

        # 处理单独选择的文件 - 直接保存到根目录
        for file_path in individual_files:
            # 获取文件名（不带路径）
            file_name = os.path.basename(file_path)
            dest_path = os.path.join(save_dir, file_name)

            # 检查是否应该覆盖
            if os.path.exists(dest_path) and not overwrite_all and not (reply == QMessageBox.Yes):
                skipped_count += 1
                continue

            try:
                # 直接复制文件（不创建子目录）
                shutil.copy2(file_path, dest_path)
                success_count += 1
            except Exception as e:
                error_files.append(f"{file_name}: {str(e)}")

        # 显示结果
        result_msg = f"已成功保存 {success_count} 个文件到:\n{save_dir}"

        if skipped_count > 0:
            result_msg += f"\n跳过 {skipped_count} 个已存在文件"

        if error_files:
            error_msg = "\n".join(error_files[:10])  # 最多显示10个错误
            if len(error_files) > 10:
                error_msg += f"\n...共 {len(error_files)} 个文件出错"

            QMessageBox.warning(
                self,
                "保存完成但有错误",
                f"{result_msg}\n\n失败 {len(error_files)} 个文件:\n{error_msg}"
            )
        else:
            QMessageBox.information(
                self,
                "保存成功",
                result_msg
            )

    def treeView_folder_clicked(self, index):
        # 获取点击项的数据
        if not index.isValid():
            return

        # 获取模型项
        item = self.model.itemFromIndex(index)
        if item is None:
            return

        # 获取文件路径
        path = item.data(Qt.UserRole)
        if not path:
            return

        # 如果是文件，显示预览
        if os.path.isfile(path):
            self.show_file_preview(path)

    def show_file_preview(self, item):
        """显示文件预览"""
        # 如果是QListWidgetItem，则从中获取完整路径；如果是字符串，则直接使用
        if isinstance(item, QListWidgetItem):
            path = item.data(Qt.UserRole)
        else:
            path = item  # 此时item应该是字符串路径
        if not path:
            return

        # 在树视图中定位文件
        if self.model:
            # 递归搜索所有项
            found = False
            for row in range(self.virtual_root.rowCount()):
                root_item = self.virtual_root.child(row)
                found = self.locate_file_in_tree(root_item, path)
                if found:
                    break

        # 预览文件
        _, ext = os.path.splitext(path)
        ext = ext.lower()

        try:
            if ext == ".pdf":
                self.clear_pdf_pages()
                doc = fitz.open(path)
                self.path_pdf = path

                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    zoom = fitz.Matrix(self.zoom_factor, self.zoom_factor)
                    pix = page.get_pixmap(matrix=zoom, dpi=100)
                    image = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
                    pixmap = QPixmap.fromImage(image)

                    label = QLabel()
                    label.setPixmap(pixmap)
                    label.setAlignment(Qt.AlignCenter)
                    label.setScaledContents(True)
                    self.verticalLayout.addWidget(label)
        except Exception as e:
            print(f"预览错误: {e}")

        # 在文件树中定位文件
        if not os.path.exists(path):
            QMessageBox.warning(self, "文件不存在", "该文件可能已被删除。")
            return
    def locate_file_in_tree(self, parent_item, path):
        """在树视图中查找并定位文件"""
        # 检查当前项
        if parent_item.data(Qt.UserRole) == path:
            index = parent_item.index()
            self.treeView_folder.scrollTo(index)
            self.treeView_folder.setCurrentIndex(index)
            self.treeView_folder.expand(index.parent())
            return True

        # 递归检查子项
        for row in range(parent_item.rowCount()):
            child_item = parent_item.child(row)
            if self.locate_file_in_tree(child_item, path):
                return True

        return False

    def show_pdf_window(self, item):
        if getattr(self, 'path_pdf', None): #判断self.path_pdf是否定义
            if self.path_pdf:
                new_window = PDFWindow(self.path_pdf)  # 创建窗口并传入文件
                new_window.show()  # ✅ 显示窗口
                self.windows.append(new_window)  # ✅ 保存引用，防止被回收

    def clear_pdf_pages(self):
        """清除已有的页面"""
        while self.verticalLayout.count():
            child = self.verticalLayout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    # ----------- pdf预览功能 End -----------

    def sync_selection_between_views(self, path, checked):
        """同步树视图和列表视图的选择状态"""
        # 同步到树视图
        if self.model:
            # 使用栈进行非递归遍历
            stack = []
            for row in range(self.virtual_root.rowCount()):
                stack.append(self.virtual_root.child(row))

            while stack:
                item = stack.pop()
                item_path = item.data(Qt.UserRole)
                if item_path == path:
                    # 更新树视图中的状态
                    item.setCheckState(Qt.Checked if checked else Qt.Unchecked)
                    break

                # 添加子项到栈中
                for row in range(item.rowCount()):
                    stack.append(item.child(row))

        # 同步到列表视图
        for i in range(self.listWidget.count()):
            item = self.listWidget.item(i)
            if item.data(Qt.UserRole) == path:
                item.setCheckState(Qt.Checked if checked else Qt.Unchecked)
                break

    # 添加新的处理方法
    def on_tree_item_changed(self, item):
        """当树视图中的项改变时（包括勾选状态）"""
        # 获取路径
        path = item.data(Qt.UserRole)
        if path is None:
            return

        # 如果是文件夹项，则递归设置子项
        if os.path.isdir(path) and not self.recursive_operation:
            self.recursive_operation = True
            try:
                # 递归设置所有子项
                self.set_children_checkstate(item, item.checkState())
            finally:
                self.recursive_operation = False

        # 同步到列表视图（如果列表中有该项）
        self.sync_selection_between_views(path, item.checkState() == Qt.Checked)

        # 更新保存按钮状态
        self.update_save_button_state()
        self.update_selected_count()

    def on_list_selection_changed(self, item):
        """列表视图选择状态变化时的处理"""
        if item is None:
            return

        path = item.data(Qt.UserRole)
        if path is None:
            return

        checked = item.checkState() == Qt.Checked

        # 同步到树视图
        self.sync_selection_between_views(path, checked)

        # 更新按钮状态
        self.update_save_button_state()
        self.update_selected_count()

    def update_selected_count(self):
        """更新右下角状态标签显示已选择的文件夹和文件数量"""
        folder_count = 0
        file_count = 0

        # 遍历树视图统计选择数量
        if self.model and self.virtual_root:
            stack = []
            for row in range(self.virtual_root.rowCount()):
                stack.append(self.virtual_root.child(row))

            while stack:
                item = stack.pop()
                if item.checkState() == Qt.Checked:
                    path = item.data(Qt.UserRole)
                    if os.path.isdir(path):
                        folder_count += 1
                    else:
                        file_count += 1

                # 添加子项到栈中
                for row in range(item.rowCount()):
                    stack.append(item.child(row))

        # 更新状态标签
        self.label_status.setText(f"已选择: {folder_count}个文件夹, {file_count}个文件")


    # 添加Excel处理方法
    def on_btn_selectExcel(self):
        """处理Excel文件选择"""
        # 获取桌面路径
        desktop_path = QStandardPaths.writableLocation(QStandardPaths.DesktopLocation)
        # 用户选择Excel文件
        excel_path, _ = QFileDialog.getOpenFileName(self, "选择Excel文件", desktop_path,
                                                    "Excel files (*.xlsx *.xls *.csv)")
        if excel_path:
            self.lineEdit_excel_path.setText(excel_path)
            self.excel_path = excel_path  # 存储路径
            self.btn_open_excel_location.setEnabled(True)  # 启用打开位置按钮
            self.excel_read(excel_path)

    def excel_read(self, excel_path):
        """读取Excel文件并更新下拉框选项"""
        try:
            # 尝试读取Excel文件
            df = pd.read_excel(excel_path)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"读取Excel文件失败: {e}")
            return

        # 指定需要保留的列名
        desired_columns = ['Material Categroy', 'Material Model', 'APN']
        # 筛选出存在的列
        existing_columns = [col for col in desired_columns if col in df.columns]

        # 如果不存在这三列，则提示错误
        if len(existing_columns) < 3:
            QMessageBox.critical(self, "错误", "Excel文件中缺少必要的列")
            return

        # 前向填充NaN
        df = df[existing_columns].ffill()

        # 存储数据用于搜索
        self.excel_data = df

        # 将数据分组存储（用于下拉框）
        self.grouped_unique_first_col = df[existing_columns[0]].unique().tolist()
        self.grouped_unique_second_col = []
        self.grouped_unique_third_col = []

        # 按第一列分组，获取第二列和第三列的唯一值
        grouped = df.groupby(existing_columns[0])
        for name, group in grouped:
            # 第二列的唯一值
            unique_second = group[existing_columns[1]].unique().tolist()
            self.grouped_unique_second_col.append(unique_second)
            # 第三列的唯一值
            unique_third = group[existing_columns[2]].unique().tolist()
            self.grouped_unique_third_col.append(unique_third)

        # 更新下拉框
        self.category_combo.clear()
        self.category_combo.addItems(self.grouped_unique_first_col)

        # 更新后两个下拉框（根据当前选中的第一列）
        self.update_model_apn()
        # 在更新下拉框后触发搜索
        self.search_files()

    # 添加打开Excel位置的方法
    def open_excel_location(self):
        """打开Excel文件所在位置"""
        if not self.excel_path or not os.path.exists(self.excel_path):
            QMessageBox.warning(self, "文件不存在", "Excel文件路径无效或文件已被移动")
            return

        # 调用已有的方法在资源管理器中显示文件位置
        self.show_in_finder(self.excel_path)

    def update_model_apn(self):
        """更新模型和APN下拉框选项"""
        # 获取当前选中的类别索引
        index = self.category_combo.currentIndex()
        if index < 0:
            return

        # 更新模型下拉框
        self.model_combo.clear()
        if index < len(self.grouped_unique_second_col):
            self.model_combo.addItems(self.grouped_unique_second_col[index])

        # 更新APN下拉框
        self.apn_combo.clear()
        if index < len(self.grouped_unique_third_col):
            self.apn_combo.addItems(self.grouped_unique_third_col[index])

        # 修复：确保下拉框启用状态与复选框一致
        self.category_combo.setEnabled(self.enable_category_checkbox.isChecked())
        self.model_combo.setEnabled(self.enable_model_checkbox.isChecked())
        self.apn_combo.setEnabled(self.enable_apn_checkbox.isChecked())

        # 更新后触发搜索
        self.search_files()

    # 修改 refresh_selected_folders 方法
    def refresh_selected_folders(self):
        """刷新已选择的文件夹树"""
        if hasattr(self, 'current_paths') and self.current_paths:
            # 保存当前路径
            current_paths = self.current_paths.copy()

            # 重新选择文件夹（模拟用户选择）
            self.current_paths = current_paths
            self.lineEdit_path.setText(", ".join([os.path.basename(f) for f in current_paths]))
            self.label_status.setText(f"已刷新 {len(current_paths)} 个文件夹")

            # 重新构建文件树
            self.model = QStandardItemModel()
            self.model.setHorizontalHeaderLabels(["文件夹"])
            self.virtual_root = self.model.invisibleRootItem()

            for folder in current_paths:
                root_item = QStandardItem(QApplication.style().standardIcon(QStyle.SP_DirIcon),
                                          os.path.basename(folder))
                root_item.setData(folder, Qt.UserRole)
                root_item.setEditable(False)
                self.virtual_root.appendRow(root_item)
                self.populate_folder_tree(root_item, folder)

            self.treeView_folder.setModel(self.model)
            self.treeView_folder.setHeaderHidden(True)
            self.treeView_folder.expandAll()
            self.treeView_folder.setEnabled(True)

            # 重新绑定事件
            try:
                self.treeView_folder.clicked.disconnect()  # 断开旧连接
            except TypeError:
                pass  # 忽略没有连接的错误
            self.treeView_folder.clicked.connect(self.treeView_folder_clicked)

            # 使用正确的信号连接方式
            # 正确的信号连接方式
            self.model.itemChanged.connect(self.on_tree_item_changed)  # 修改为新的处理方法
            self.model.itemChanged.connect(self.update_save_button_state)

            # 初始更新一次按钮状态
            self.update_save_button_state()
            self.update_selected_count()
