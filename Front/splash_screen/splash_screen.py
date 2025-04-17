#이미지 파일 및 ui파일 포함.import sys
import time
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.uic import loadUi
from PyQt5.QtCore import Qt


# 🔹 스플래시 스크린 클래스
class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        loadUi("splash.ui", self)  # ui 파일 확인 필수
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setFixedSize(960,540) #나중에 바꾸면 됨.

    def progress(self):
        for i in range(101):
            time.sleep(0.01)
            self.progressBar.setValue(i)
            QApplication.processEvents()
            if i == 100:
                self.label.setText("Loading Complete")
                font = self.label.font()
                font.setPointSize(14)
                font.setBold(True)
                self.label.setFont(font)
                self.label.setStyleSheet("color:#000000")
                self.label.setAlignment(Qt.AlignCenter)


# 🔹 메인 윈도우 클래스
class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('My First Application')
        self.move(300, 300)
        self.resize(400, 200)


# 🔹 앱 실행 부분
if __name__ == '__main__':
    app = QApplication(sys.argv)

    # 1. 스플래시 화면 먼저
    splash = SplashScreen()
    splash.show()
    splash.progress()

    # 2. 메인 앱 실행
    main_window = MyApp()
    main_window.show()
    splash.close()

    sys.exit(app.exec_())
