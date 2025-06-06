import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QGraphicsDropShadowEffect, QFrame
)
from PyQt5.QtGui import QPixmap, QFont, QColor, QPalette, QBrush, QLinearGradient, QPainterPath, QRegion
from PyQt5.QtCore import Qt
import subprocess


class AugmentCard(QFrame):
    def __init__(self, title, tags, image_path, parent_window):
        super().__init__()
        self.title = title
        self.image_path = image_path
        self.parent_window = parent_window
        self.setFixedSize(400, 600)
        self.setCursor(Qt.PointingHandCursor)

        self.setStyleSheet("""
            QFrame {
                border-radius: 20px;
                background-color: transparent;
            }
            QFrame:hover {
                background-color: rgba(0, 0, 0, 40);
            }
        """)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)
        shadow.setOffset(0, 0)
        shadow.setColor(QColor(0, 0, 0, 180))
        self.setGraphicsEffect(shadow)

        background = QLabel(self)
        pixmap = QPixmap(image_path).scaled(
            self.size(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        background.setPixmap(pixmap)
        background.setFixedSize(self.size())
        background.setStyleSheet("border-radius: 20px;")
        background.lower()

        path = QPainterPath()
        path.addRoundedRect(0, 0, self.width(), self.height(), 20, 20)
        region = QRegion(path.toFillPolygon().toPolygon())
        self.setMask(region)

        overlay = QVBoxLayout(self)
        overlay.setContentsMargins(20, 20, 20, 20)
        overlay.setSpacing(10)
        overlay.addStretch()

        text_frame = QFrame()
        text_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(0, 0, 0, 150);
                border-radius: 12px;
            }
        """)
        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(15, 10, 15, 10)

        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 32, QFont.Bold))
        title_label.setStyleSheet("color: white;")

        desc = '\n'.join(f'#{tag}' for tag in tags) if isinstance(tags, list) else tags
        desc_label = QLabel(desc)
        desc_label.setFont(QFont("Arial", 20))
        desc_label.setStyleSheet("color: #dddddd;")
        desc_label.setWordWrap(True)

        text_layout.addWidget(title_label)
        text_layout.addWidget(desc_label)
        text_frame.setLayout(text_layout)
        overlay.addWidget(text_frame)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if self.title == "심규선":
            try:
                subprocess.Popen(["python", "AI_Sim_Gyu_Seon.py"])
                print("AI_Sim_Gyu_Seon.py 실행 시도 (ModelSelect 창 유지).")
            except Exception as e:
                print(f"Error: {e}")
        else:
            print(f"{self.title} clicked!")


class ModelSelect(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI 모델 선택")
        self.setFixedSize(1920, 1080)

        palette = QPalette()
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0.0, QColor("#0f0f0f"))
        gradient.setColorAt(1.0, QColor("#1f1f1f"))
        palette.setBrush(QPalette.Window, QBrush(gradient))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        root_layout = QVBoxLayout()
        root_layout.setContentsMargins(80, 50, 80, 50)
        root_layout.setSpacing(60)

        title_label = QLabel("AI 음성 비서 선택")
        title_label.setFont(QFont("Arial", 48, QFont.Bold))
        title_label.setStyleSheet("color: white;")
        title_label.setAlignment(Qt.AlignCenter)
        root_layout.addWidget(title_label)

        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(60)

        card1 = AugmentCard("민상", ["감미로운", "설레는", "신뢰가는", "저음의", "차분한"], "image/민상.png", self)
        card2 = AugmentCard("심규선", ["감미로운", "신뢰가는", "차분한", "친절한"], "image/심규선.png", self)
        card3 = AugmentCard("윤서", ["사랑스러운", "새침한", "설레는", "씩씩한"], "image/윤서.png", self)

        cards_layout.addWidget(card1)
        cards_layout.addWidget(card2)
        cards_layout.addWidget(card3)
        root_layout.addLayout(cards_layout)
        self.setLayout(root_layout)

    def closeEvent(self, event):
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ModelSelect()
    window.show()
    sys.exit(app.exec_())
