#floor3_map_control이 309호에 해당하는 지점에 도착하였을 때,
#이 코드가 실행되어야한다.

from PySide2.QtWidgets import (
    QApplication, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QWidget
)
from PySide2.QtGui import QPixmap, QIcon
from PySide2.QtCore import Qt, QSize, Signal

import sys

# 클릭 가능한 QLabel 커스텀 클래스 추가
class ClickableLabel(QLabel):
    clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.PointingHandCursor)  # 마우스 포인터 변경

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mouseReleaseEvent(event)


class ProfessorCard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("교수님 정보 카드")
        self.setFixedSize(1920, 1080)
        self.setStyleSheet("background-color: #000000;") # 배경색 검정색으로 변경

        # --- 왼쪽 이미지 및 텍스트 ---
        self.main_img = QLabel()
        self.main_img.setPixmap(QPixmap("image/person_309.png").scaled(800, 600, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.main_img.setStyleSheet("padding: 20px;")

        self.sub_img = QLabel()
        self.sub_img.setPixmap(QPixmap("image/person_309_qr_dbpia.png").scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.sub_img.setStyleSheet("padding: 20px;")

        self.qr_text_label = QLabel("김창화 교수님 Dbpia")
        self.qr_text_label.setStyleSheet("""
            color: #FFFFFF;
            font-size: 24px;
        """)

        qr_layout = QHBoxLayout()
        qr_layout.addWidget(self.sub_img)
        qr_layout.addWidget(self.qr_text_label, alignment=Qt.AlignVCenter | Qt.AlignLeft)
        qr_layout.setSpacing(20)

        left_img_layout = QVBoxLayout()
        left_img_layout.addWidget(self.main_img, alignment=Qt.AlignTop | Qt.AlignLeft)
        left_img_layout.addLayout(qr_layout, alignment=Qt.AlignBottom | Qt.AlignLeft)

        left_container = QWidget()
        left_container.setLayout(left_img_layout)

        # --- 가운데 텍스트 정보 ---
        text = (
            "[309호]\n김창화 교수님 연구실\n\n[직위]\n교수\n"
            "\n[연구실번호]\n760-8663\n\n[이메일]\n kch@gwnu.ac.kr\n"
            "\n[전공분야]\n데이터베이스\n\n[연구실]\nW6-308\n"
        )
        info_label = QLabel(text)
        info_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        info_label.setStyleSheet(f"""
            color: #FFFFFF;
            font-size: 40px;
            line-height: 1.6;
            padding-left: 40px;
            padding-right: 40px;
            padding-top: 100px;
        """)
        info_label.setFixedWidth(500)

        center_layout = QVBoxLayout()
        center_layout.addWidget(info_label, alignment=Qt.AlignTop)
        center_layout.addStretch()

        center_container = QWidget()
        center_container.setLayout(center_layout)

        # --- 오른쪽 이미지 (클릭 가능) ---
        self.right_img = ClickableLabel()
        self.right_img.setPixmap(QPixmap("image/309호.png").scaled(600, 1200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.right_img.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.right_img.clicked.connect(self.on_click)  # 클릭 이벤트 연결

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
        main_layout.addWidget(left_container)
        main_layout.addWidget(center_container)
        main_layout.addWidget(right_container)

        self.setLayout(main_layout)

    def on_click(self):
        print("버튼 클릭됨! 원하는 동작을 여기에 넣으세요.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProfessorCard()
    window.show()
    sys.exit(app.exec_())
