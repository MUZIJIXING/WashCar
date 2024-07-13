import sys
import sqlite3
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel

from RegisitUi import Ui_RegisterWindow
import data.resources_rc  # 确保导入生成的资源文件

class RegisterWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_RegisterWindow()
        self.ui.setupUi(self)
        self.setup_connections()
        self.setup_ui()

        # 设置背景图片
        self.backgroundLabel = QLabel(self)
        self.backgroundLabel.setGeometry(0, 0, self.width(), self.height())
        self.backgroundLabel.setPixmap(QPixmap(":login_bk3.jpg"))
        self.backgroundLabel.setScaledContents(True)
        self.backgroundLabel.lower()  # 确保背景在最底层

    def setup_ui(self):
        self.setStyleSheet("""
            QWidget#RegisterWindow {
                background-image: url(:/images/background.jpg);
                background-repeat: no-repeat;
                background-position: center;
            }
            QLabel {
                color: black;
            }
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.8);
            }
            QPushButton {
                background-color: #007BFF;
                color: white;
                padding: 10px;
                font-size: 16px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #004080;
            }
            QPushButton#returnButton {
                background-color: #6c757d;
            }
            QPushButton#returnButton:hover {
                background-color: #5a6268;
            }
            QPushButton#returnButton:pressed {
                background-color: #4e555b;
            }
        """)

    def setup_connections(self):
        self.ui.registerButton.clicked.connect(self.register)
        self.ui.returnButton.clicked.connect(self.return_to_login)

    def validate_email(self, email):
        import re
        pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(pattern, email)

    def register(self):
        username = self.ui.usernameLineEdit.text()
        password = self.ui.passwordLineEdit.text()
        confirm_password = self.ui.confirmPasswordLineEdit.text()
        email = self.ui.emailLineEdit.text()

        if not username or not password or not confirm_password or not email:
            QtWidgets.QMessageBox.warning(self, "输入错误", "所有字段都是必填项")
            return

        if password != confirm_password:
            QtWidgets.QMessageBox.warning(self, "输入错误", "密码和确认密码不匹配")
            return

        # 在这里实现注册逻辑，例如保存用户信息到数据库
        try:
            conn = sqlite3.connect('washcar.db')
            cursor = conn.cursor()

            # 检查用户名是否已经存在
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            if cursor.fetchone() is not None:
                QtWidgets.QMessageBox.warning(self, "注册失败", "该用户已经存在")
                return

            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
            conn.commit()
            conn.close()
            QtWidgets.QMessageBox.information(self, "注册成功", "注册成功，请返回登录")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "注册失败", f"注册失败：{e}")

    def return_to_login(self):
        from loginFrame import LoginWindow
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = RegisterWindow()
    window.show()
    sys.exit(app.exec_())
