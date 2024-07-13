import sqlite3

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QLabel, QLineEdit, QPushButton
from PyQt5.QtGui import QPixmap
from login_ui import Ui_LoginWindow
from recframe import CarWashApp
import data.resources_rc  # 导入生成的资源文件

class LoginWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_LoginWindow()
        self.ui.setupUi(self)
        self.ui.loginButton.clicked.connect(self.login)
        self.ui.registerButton.clicked.connect(self.register)
        self.ui.forgotPasswordButton.clicked.connect(self.forgot_password)

        # 设置背景图片
        self.backgroundLabel = QLabel(self)
        self.backgroundLabel.setGeometry(0, 0, self.width(), self.height())
        self.backgroundLabel.setPixmap(QPixmap(":login_bk3.jpg"))
        self.backgroundLabel.setScaledContents(True)
        self.backgroundLabel.lower()  # 确保背景在最底层

        # 调整控件的样式
        self.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.8);
                border: 2px solid #CCCCCC;
                border-radius: 20px;
                padding: 10px;
                font-size: 18px;
                color: #333333;
            }
            QPushButton {  
                background-color: rgba(30, 144, 255, 0.3); /* 这里的0.5表示50%的透明度 */  
                color: white;  
                font-size: 18px;  
                border-radius: 20px;  
                padding: 10px;  
            }
            QPushButton:hover {
                background-color: #1C86EE;
            }
            QPushButton:pressed {
                background-color: #1874CD;
            }
            QLabel {
                color: black;
                font-size: 16px;
            }
        """)

        # 调整布局
        self.ui.systemTitleLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.ui.usernameLineEdit.setAlignment(QtCore.Qt.AlignCenter)
        self.ui.passwordLineEdit.setAlignment(QtCore.Qt.AlignCenter)

        # 添加透明背景
        self.ui.usernameLineEdit.setStyleSheet("background: transparent; border: 1px solid white; color: white;")
        self.ui.passwordLineEdit.setStyleSheet("background: transparent; border: 1px solid white; color: white;")

    def resizeEvent(self, event):
        self.backgroundLabel.setGeometry(0, 0, self.width(), self.height())
        self.backgroundLabel.setPixmap(self.backgroundLabel.pixmap().scaled(self.backgroundLabel.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        super(LoginWindow, self).resizeEvent(event)

    def login(self):
        username = self.ui.usernameLineEdit.text()
        password = self.ui.passwordLineEdit.text()

        # 连接到SQLite数据库
        conn = sqlite3.connect('washcar.db')
        cursor = conn.cursor()

        # 查询用户表
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()

        if user:
            self.main_window = CarWashApp()
            self.main_window.show()
            self.close()
        else:
            QtWidgets.QMessageBox.warning(self, "登录失败", "用户名或密码错误")

        # 关闭数据库连接
        conn.close()

    def register(self):
        from regisitframe import RegisterWindow
        self.register_window = RegisterWindow()
        self.register_window.show()
        self.close()

    def forgot_password(self):
        QtWidgets.QMessageBox.information(self, "忘记密码", "忘记密码功能暂未实现")

if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())
