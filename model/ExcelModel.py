# import sys
# import pandas as pd
# from PySide6.QtWidgets import (
#     QApplication, QMainWindow, QWidget, QPushButton, QTableView,
#     QVBoxLayout, QFileDialog
# )
# from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
#
#
# # ✅ 自定义表格模型（列优先）
# class ExcelModel(QAbstractTableModel):
#     def __init__(self, data_by_column=None, headers=None, parent=None):
#         """
#         data_by_column: list of lists, 每一列是一个列表
#         headers: 表头（列名）
#         """
#         super().__init__(parent)
#         self._data = data_by_column if data_by_column is not None else []
#         self._headers = headers if headers is not None else []
#
#     def rowCount(self, parent=QModelIndex()):
#         # 行数 = 每列的元素数量（假设每列长度一致）
#         return len(self._data[0]) if self._data and len(self._data) > 0 else 0
#
#     def columnCount(self, parent=QModelIndex()):
#         # 列数 = 列表的长度
#         return len(self._data)
#
#     def data(self, index, role=Qt.DisplayRole):
#         if not index.isValid():
#             return None
#         if role == Qt.DisplayRole:
#             # 行 = index.row(), 列 = index.column()
#             return self._data[index.column()][index.row()]
#         return None
#
#     def headerData(self, section, orientation, role=Qt.DisplayRole):
#         if role == Qt.DisplayRole:
#             if orientation == Qt.Horizontal:
#                 return self._headers[section] if section < len(self._headers) else ""
#             elif orientation == Qt.Vertical:
#                 return str(section + 1)  # 行号作为垂直表头
#         return None
#
#     def flags(self, index):
#         if not index.isValid():
#             return Qt.NoItemFlags
#         return Qt.ItemIsEnabled | Qt.ItemIsSelectable


from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from collections import defaultdict


# ✅ 自定义表格模型（列优先）
class ExcelModel(QAbstractTableModel):
    def __init__(self, data_by_column=None, headers=None, parent=None):
        super().__init__(parent)
        self._data = data_by_column if data_by_column is not None else []
        self._headers = headers if headers is not None else []

        # 新增变量，用于保存分组后的唯一值
        self.grouped_unique_first_col = []  # 第一列唯一值（Material Category）
        self.grouped_unique_second_col = []  # 第二列按第一列分组的唯一值
        self.grouped_unique_third_col = []  # 第三列按第一列分组的唯一值

        # ✅ 初始化后立即处理数据
        self.process_grouped_data()

    def rowCount(self, parent=QModelIndex()):
        if not self._data:
            return 0
        return len(self._data[0]) if self._data and len(self._data) > 0 else 0

    def columnCount(self, parent=QModelIndex()):
        return len(self._data)

    def data(self, index, role=Qt.DisplayRole):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            return self._data[index.column()][index.row()]
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._headers[section] if section < len(self._headers) else ""
            elif orientation == Qt.Vertical:
                return str(section + 1)
        return None

    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def process_grouped_data(self):
        """
        处理数据，对第1列进行去重并记录位置，
        然后对第2、3列进行分组并去重
        """
        if not self._data or len(self._data) < 3:
            print("⚠️ 数据为空或不足3列")
            return

        first_col = self._data[0]  # 第一列 Material Category
        second_col = self._data[1]  # 第二列 Material Model
        third_col = self._data[2]  # 第三列 APN

        # 1️⃣ 获取第一列唯一值及其位置
        value_positions = defaultdict(list)
        for idx, value in enumerate(first_col):
            value_positions[value].append(idx)

        unique_first_col = list(value_positions.keys())
        self.grouped_unique_first_col = unique_first_col

        # 2️⃣ 根据第一列唯一值对第二列和第三列进行分组
        second_col_grouped = []
        third_col_grouped = []

        for key in unique_first_col:
            indices = value_positions[key]
            second_group = [second_col[i] for i in indices]
            third_group = [third_col[i] for i in indices]
            second_col_grouped.append(second_group)
            third_col_grouped.append(third_group)

        # ✅ 去重函数（保留原始顺序）
        def get_unique_in_group(grouped_data):
            result = []
            for group in grouped_data:
                seen = set()
                unique_group = []
                for item in group:
                    if item not in seen:
                        seen.add(item)
                        unique_group.append(item)
                result.append(unique_group)
            return result

        self.grouped_unique_second_col = get_unique_in_group(second_col_grouped)
        self.grouped_unique_third_col = get_unique_in_group(third_col_grouped)

        # ✅ 打印结果
        print("✅ 第一列唯一值:", self.grouped_unique_first_col)
        print("\n✅ 第二列分组后唯一值：")
        for i, group in enumerate(self.grouped_unique_second_col):
            print(f"  Group {i + 1}: {group}")
        print("\n✅ 第三列分组后唯一值：")
        for i, group in enumerate(self.grouped_unique_third_col):
            print(f"  Group {i + 1}: {group}")
