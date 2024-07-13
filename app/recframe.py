import sys
import random
import cv2
import time
import sqlite3
from PyQt5 import QtWidgets, QtGui, QtCore
from RecUi import Ui_MainWindow
import data.resources_rc  # 导入生成的资源文件
from  ai.run.DenseNet import classify_image

class CarWashApp(QtWidgets.QMainWindow):
    def __init__(self):
        super(CarWashApp, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setup_connections()

        # 初始化摄像头
        self.cap = None
        self.video_timer = QtCore.QTimer(self)
        self.timer_timer = QtCore.QTimer(self)

        # 初始化计时器
        self.start_time = None

        # 设置按钮样式
        buttons = [
            self.ui.viewHistoryButton,
            self.ui.startWashButton,
            self.ui.stopWashButton,
            self.ui.startMonitoringButton,
            self.ui.stopMonitoringButton,
            self.ui.exitButton
        ]
        for button in buttons:
            button.setStyleSheet("""
                QPushButton {
                    background-color: #11304b;
                    color: white;
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

        # 设置背景图片
        self.backgroundLabel = QtWidgets.QLabel(self)
        self.backgroundLabel.setGeometry(0, 0, self.width(), self.height())
        self.backgroundLabel.setPixmap(QtGui.QPixmap(":op_bk1.jpg"))
        self.backgroundLabel.setScaledContents(True)
        self.backgroundLabel.lower()  # 确保背景在最底层

        # 调整控件样式
        self.ui.videoLabel.setStyleSheet("background: transparent; border: 1px solid white; color: white;")
        self.ui.statusLabel.setStyleSheet("color: white; font-size: 18px;")

        self.adjust_layout()

    def adjust_layout(self):
        # 调整布局以适应背景图片
        layout = self.layout()
        if layout is not None:
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)

    def resizeEvent(self, event):
        self.backgroundLabel.setGeometry(0, 0, self.width(), self.height())
        self.backgroundLabel.setPixmap(self.backgroundLabel.pixmap().scaled(self.backgroundLabel.size(), QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
        super(CarWashApp, self).resizeEvent(event)

    def setup_connections(self):
        self.ui.viewHistoryButton.clicked.connect(self.view_history)
        self.ui.startWashButton.clicked.connect(self.start_wash)
        self.ui.stopWashButton.clicked.connect(self.stop_wash)
        self.ui.startMonitoringButton.clicked.connect(self.start_monitoring)
        self.ui.stopMonitoringButton.clicked.connect(self.stop_monitoring)
        self.ui.exitButton.clicked.connect(self.exit_system)

    def view_history(self):
        from historyframe import HistoryWindow  # 导入历史记录窗口的UI类
        self.ui.statusLabel.setText("查看历史洗车记录")
        self.history_window = HistoryWindow()  # 创建历史记录窗口实例
        self.history_window.show()
        self.close()

    def start_wash(self):
        try:
            self.ui.statusLabel.setText("开始洗车")
            self.start_time = time.time()
            if self.timer_timer.isActive():
                self.timer_timer.stop()  # 确保计时器未运行
            # 确保断开连接前信号已连接
            try:
                self.timer_timer.timeout.disconnect(self.update_timer)
            except TypeError:
                pass
            self.timer_timer.timeout.connect(self.update_timer)
            self.timer_timer.start(1000)  # 每秒更新一次计时
            print("计时器已启动")
        except Exception as e:
            print(f"Error in start_wash: {e}")

    def stop_wash(self):
        paths = [
            '../ai/data/train/bus/0aa8c6bece0ab6ceda43e920634e4fa2.jpg',
            '../ai/data/train/family sedan/0b009c2bcc5c55389e0f25ff85a265e1.jpg',
            '../ai/data/train/fire engine/0bd6dbd1c72c27ec4b4169cfedddd781.jpg',
            '../ai/data/train/heavy truck/0ae81c7a93308563a19c220f7c9a670e.jpg',
            '../ai/data/train/jeep/0a5ba89747160a7b60f41c4efddd23c5.jpg',
            '../ai/data/train/minibus/0ca213d716580762cd08dc3307dfd8f2.jpg',
            '../ai/data/train/racing car/0b6f33b8b2957b1e69f58fec697c6101.jpg',
            '../ai/data/train/racing car/0b6f33b8b2957b1e69f58fec697c6101.jpg',
            '../ai/data/train/taxi/0a694bd8902e67d3e6337f7fe6cf9f30.jpg',
            '../ai/data/train/truck/0ba6b9ee096fc34a07deb2cd6fa53204.jpg',
        ]
        class_names = [
            "suv", "bus", "family sedan", "fire engine", "heavy truck", "jeep",
            "minibus", "racing car", "taxi", "truck"
        ]

        try:
            self.ui.statusLabel.setText("结束洗车")
            self.timer_timer.stop()
            self.update_timer()  # 最后更新一次计时
            print("计时器已停止")

            # 获取洗车结束时间和洗车时长
            end_time = time.time()
            elapsed_time = int(end_time - self.start_time)
            hours, remainder = divmod(elapsed_time, 3600)
            minutes, seconds = divmod(remainder, 60)
            wash_duration = f"{hours:02}:{minutes:02}:{seconds:02}"

            # 获取车型
            fee_times = 0
            random_number = random.randint(0, 9)
            car_kind = classify_image(paths[random_number])
            if car_kind in [1,3,4,9]:
                fee_times = 2
            else:
                fee_times = 1
            print("识别到的车型是{}".format(class_names[car_kind]))

            # 计算费用，每秒钟0.01元
            expenses = elapsed_time * 0.01 * fee_times

            # 将洗车记录插入到数据库
            conn = sqlite3.connect('washcar.db')
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO cars (model, start, end, time, expenses) VALUES (?, ?, ?, ?, ?)",
                (class_names[car_kind], time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.start_time)),
                 time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time)), wash_duration, expenses)
            )
            conn.commit()
            conn.close()

            print("洗车记录已插入到数据库")

        except Exception as e:
            print(f"Error in stop_wash: {e}")

    def start_monitoring(self):
        try:
            self.ui.statusLabel.setText("开启监控")
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                self.ui.statusLabel.setText("无法打开摄像头")
                print("无法打开摄像头")
                return
            if self.video_timer.isActive():
                self.video_timer.stop()  # 确保视频定时器未运行
            # 确保断开连接前信号已连接
            try:
                self.video_timer.timeout.disconnect(self.update_frame)
            except TypeError:
                pass
            self.video_timer.timeout.connect(self.update_frame)
            self.video_timer.start(30)  # 30ms刷新一次
            print("视频定时器已启动")
        except Exception as e:
            print(f"Error in start_monitoring: {e}")

    def stop_monitoring(self):
        try:
            self.ui.statusLabel.setText("关闭监控")
            self.video_timer.stop()
            if self.cap:
                self.cap.release()
                self.cap = None
            self.ui.videoLabel.setPixmap(QtGui.QPixmap())
            self.ui.videoLabel.setText("视频显示区域")
            print("视频定时器已停止")
        except Exception as e:
            print(f"Error in stop_monitoring: {e}")

    def update_frame(self):
        try:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                height, width, channel = frame.shape
                step = channel * width
                qImg = QtGui.QImage(frame.data, width, height, step, QtGui.QImage.Format_RGB888)
                self.ui.videoLabel.setPixmap(QtGui.QPixmap.fromImage(qImg))
            else:
                self.ui.statusLabel.setText("读取视频帧失败")
                print("读取视频帧失败")
        except Exception as e:
            print(f"Error in update_frame: {e}")

    def update_timer(self):
        try:
            if self.start_time:
                elapsed_time = int(time.time() - self.start_time)
                hours, remainder = divmod(elapsed_time, 3600)
                minutes, seconds = divmod(remainder, 60)
                self.ui.timerLabel.setText(f"计时：{hours:02}:{minutes:02}:{seconds:02}")
        except Exception as e:
            print(f"Error in update_timer: {e}")

    def exit_system(self):
        from loginFrame import LoginWindow
        try:
            self.ui.statusLabel.setText("账号正在退出...")
            print("账号正在退出")
            self.login_window = LoginWindow()  # 创建历史记录窗口实例
            self.login_window.show()
            self.close()
            # QtWidgets.QApplication.quit()

        except Exception as e:
            print(f"Error in exit_system: {e}")


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = CarWashApp()
    window.show()
    sys.exit(app.exec_())
