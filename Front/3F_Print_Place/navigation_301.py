from PySide2.QtWidgets import (
    QApplication, QLabel, QVBoxLayout, QHBoxLayout, QWidget
)
from PySide2.QtGui import QPixmap
from PySide2.QtCore import Qt, Signal
import sys

# 클릭 가능한 QLabel 커스텀 클래스
class ClickableLabel(QLabel):
    clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.PointingHandCursor)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mouseReleaseEvent(event)

class ProfessorCard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("강의실 정보")
        self.setFixedSize(1920, 1080)
        self.setStyleSheet("background-color: #000000;")  # 배경 검정

        # --- 텍스트 정보 (왼쪽 영역) ---
        text = (
            "[301호]\n소프트웨어 실습실2\n\n"
            "[수업]\n"
            "-월요일-\n데이터베이스 5~7 딥러닝 18~19\n\n"
            "-화요일-\n데이터마이닝 10~13 딥러닝 14~19\n\n"
            "-수요일-\n데이터마이닝 10~13 데이터구조 14~17\n\n"
            "-목요일-\n데이터베이스 5~7 데이터구조 14~17\n\n"
            "-이러닝-\n디지털 & 과학수사"
        )

        info_label = QLabel(text)
        info_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        info_label.setStyleSheet("""
            color: #FFFFFF;
            font-size: 40px;
            line-height: 1.6;
            padding-left: 40px;
            padding-top: 20px;
        """)
        info_label.setFixedWidth(1200)  # 넓게 설정

        text_layout = QVBoxLayout()
        text_layout.addWidget(info_label, alignment=Qt.AlignTop)
        text_layout.addStretch()

        text_container = QWidget()
        text_container.setLayout(text_layout)

        # --- 오른쪽 이미지 (그대로 유지) ---
        self.right_img = ClickableLabel()
        self.right_img.setPixmap(QPixmap("image/301호.png").scaled(600, 1200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.right_img.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.right_img.clicked.connect(self.on_click)

        right_layout = QVBoxLayout()
        right_layout.addWidget(self.right_img, alignment=Qt.AlignRight | Qt.AlignVCenter)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        right_container = QWidget()
        right_container.setLayout(right_layout)
        right_container.setStyleSheet("margin: 0px; padding: -100px;")

        # --- 전체 수평 레이아웃 ---
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(80, 60, 80, 60)
        main_layout.setSpacing(60)
        main_layout.addWidget(text_container, alignment=Qt.AlignLeft)
        main_layout.addWidget(right_container)

        self.setLayout(main_layout)

    def on_click(self):
        print("버튼 클릭됨! 원하는 동작을 여기에 넣으세요.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProfessorCard()
    window.show()
    sys.exit(app.exec_())
