# history_window.py
import csv
import datetime
import sqlite3
from PyQt5 import QtWidgets, QtGui, QtCore
from history import Ui_HistoryRecords

import data.resources_rc  # 导入生成的资源文件

class HistoryWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_HistoryRecords()
        self.ui.setupUi(self)
        self.ui.returnButton.clicked.connect(self.return_to_RecUi)
        self.ui.exportButton.clicked.connect(self.export_history)

        # 设置背景图片
        self.backgroundLabel = QtWidgets.QLabel(self)
        self.backgroundLabel.setGeometry(0, 0, self.width(), self.height())
        self.backgroundLabel.setPixmap(QtGui.QPixmap(":op_bk3"))
        self.backgroundLabel.setScaledContents(True)
        self.backgroundLabel.lower()  # 确保背景在最底层

        # 调整控件样式
        self.ui.tableWidget.setStyleSheet("background: transparent; border: 1px solid black; color: black;")
        self.ui.titleLabel.setStyleSheet("color: black; font-size: 18px;")
        self.ui.exportButton.setStyleSheet("""
                    QPushButton {
                        background-color: #007BFF;
                        color: black;
                        font-size: 14px;
                        border-radius: 5px;
                        padding: 5px;
                    }
                    QPushButton:hover {
                        background-color: #0056b3;
                    }
                    QPushButton:pressed {
                        background-color: #004080;
                    }
        """)
        self.ui.returnButton.setStyleSheet("""
                    QPushButton {
                        background-color: #FF5733;
                        color: black;
                        font-size: 14px;
                        border-radius: 5px;
                        padding: 5px;
                    }
                    QPushButton:hover {
                        background-color: #C70039;
                    }
                    QPushButton:pressed {
                        background-color: #900C3F;
                    }
        """)

        self.adjust_layout()
        self.load_data()

    def adjust_layout(self):
        # 调整布局以适应背景图片
        layout = self.layout()
        if layout is not None:
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)

    def resizeEvent(self, event):
        self.backgroundLabel.setGeometry(0, 0, self.width(), self.height())
        self.backgroundLabel.setPixmap(self.backgroundLabel.pixmap().scaled(self.backgroundLabel.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        super(HistoryWindow, self).resizeEvent(event)

    def return_to_RecUi(self):
        from app.recframe import CarWashApp
        self.RecWindow = CarWashApp()  # 创建历史记录窗口实例
        self.RecWindow.show()
        self.close()

    def load_data(self):
        # 连接到SQLite数据库
        conn = sqlite3.connect('washcar.db')
        cursor = conn.cursor()

        # 查询车辆表的所有数据
        cursor.execute("SELECT * FROM cars")
        rows = cursor.fetchall()

        # 设置表格行数和列数
        self.ui.tableWidget.setRowCount(len(rows))
        self.ui.tableWidget.setColumnCount(6)

        # 将数据添加到表格中
        for row_idx, row in enumerate(rows):
            for col_idx, col in enumerate(row):
                item = QtWidgets.QTableWidgetItem(str(col))
                self.ui.tableWidget.setItem(row_idx, col_idx, item)

        # 设置表头
        headers = ["记录编号", "车型", "洗车开始时间", "洗车结束时间", "洗车时长", "洗车费用"]
        self.ui.tableWidget.setHorizontalHeaderLabels(headers)

        # 关闭数据库连接
        conn.close()

    def export_history(self):
        # 获取表格数据
        row_count = self.ui.tableWidget.rowCount()
        column_count = self.ui.tableWidget.columnCount()

        # 生成带有时间戳的默认文件名
        current_time = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        default_file_name = f"历史记录_{current_time}.csv"

        # 提示文件保存对话框，自动填入默认文件名
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "保存文件", default_file_name, "CSV Files (*.csv)")

        if file_path:
            with open(file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                # 写入表头
                headers = [self.ui.tableWidget.horizontalHeaderItem(i).text() for i in range(column_count)]
                writer.writerow(headers)

                # 写入数据
                for row in range(row_count):
                    row_data = []
                    for column in range(column_count):
                        item = self.ui.tableWidget.item(row, column)
                        row_data.append(item.text() if item else '')
                    writer.writerow(row_data)
            QtWidgets.QMessageBox.information(self, "导出成功", "历史记录已成功导出")

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    window = HistoryWindow()
    window.show()
    sys.exit(app.exec_())
