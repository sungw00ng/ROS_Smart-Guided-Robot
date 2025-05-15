from PySide2.QtWidgets import QApplication, QWidget, QPushButton, QLabel
from PySide2.QtGui import QFont
from PySide2.QtCore import Qt
import sys

class FloorMap(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("3F Floor Map")
        self.setGeometry(0, 0, 1920, 1080)
        self.setStyleSheet("background-color: black;")
        self.initUI()

    def initUI(self):
        # 상단 오른쪽 3F 라벨
        label_3f = QLabel("3F", self)
        label_3f.setFont(QFont("Arial", 80, QFont.Bold))
        label_3f.setStyleSheet("color: white;")
        label_3f.move(1725, 50)

        # 버튼 스타일 공통
        btn_style = """
            QPushButton {
                background-color: #eeeeee;
                color: black;
                font-size: 30px;
                font-weight: bold;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #bbbbbb;
            }
        """

        # 위 줄 방들 (왼→오)
        self.make_room("room313", "313",  190, 230, 180, 150, btn_style)
        self.make_room("room312", "312", 375, 230, 140, 150, btn_style)
        self.make_room("room311", "311", 520, 230, 140, 150, btn_style)
        self.make_room("room310", "310", 665, 230, 140, 150, btn_style)
        self.make_room("room309", "309", 810, 230, 140, 150, btn_style)
        self.make_room("room308", "308", 955, 230, 140, 150, btn_style)
        self.make_room("room307", "307", 1100, 230, 140, 150, btn_style)
        self.make_room("room306", "306", 1245, 230, 140, 150, btn_style)
        self.make_room("room305", "305", 1390, 230, 140, 150, btn_style)
        self.make_room("room304", "304", 1535, 230, 140, 150, btn_style)

        # 아래 줄 방들
        self.make_room("room301", "301",  55,  550, 160, 175, btn_style)
        self.make_room("room302", "302", 225, 550, 120, 175, btn_style)

        # 중앙 복도
        hallway = QPushButton("중앙 복도", self)
        hallway.setGeometry(530, 550, 330, 175)
        hallway.setStyleSheet("""
            QPushButton {
                background-color: #eeeeee;
                color: black;
                font-size: 32px;
                font-weight: bold;
                border-radius: 12px;
            }
            QPushButton:hover {
                background-color: #bbbbbb;
            }
            QPushButton:pressed {
                background-color: #aaaaaa;
            }
        """)
        hallway.clicked.connect(lambda: self.on_click("중앙 복도"))

        # 아래 오른쪽 방
        self.make_room("room314", "314", 970, 550, 120, 175, btn_style)
        self.make_room("room303", "303", 1100, 550, 270, 175, btn_style)

    def make_room(self, object_name, text, x, y, w, h, style):
        btn = QPushButton(text, self)
        btn.setObjectName(object_name)
        btn.setGeometry(x, y, w, h)
        btn.setStyleSheet(style)
        btn.clicked.connect(lambda: self.on_click(text))

    def on_click(self, room_number):
        print(f"[클릭됨] 방 번호: {room_number}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = FloorMap()
    win.show()
    sys.exit(app.exec_())
