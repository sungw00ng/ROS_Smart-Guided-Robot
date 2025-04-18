import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QMovie, QPixmap
import pygame

class VoiceAssistant(QWidget):
    def __init__(self):
        super().__init__()
        pygame.init()
        pygame.mixer.init()
        self.initUI()
        QTimer.singleShot(500, self.play_startup_sounds)

    def initUI(self):
        self.setWindowTitle("ROS2_SerBotAGV")
        self.setGeometry(0, 0, 1440, 810)
        self.setStyleSheet("background-color: #000000;")

        layout = QVBoxLayout()
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(20)

        title_label = QLabel("AIMOB-고은", self)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            color: #00ddff;
            font-size: 40px;
            font-weight: bold;
            font-family: '맑은 고딕';
            text-shadow: 2px 2px 4px #007788;
        """)
        layout.addWidget(title_label)

        self.movie_label = QLabel(self)
        self.movie = QMovie("voice.gif")
        self.movie_label.setMovie(self.movie)
        self.movie.start()
        self.movie_label.setAlignment(Qt.AlignCenter | Qt.AlignTop)
        layout.addWidget(self.movie_label)

        self.voice_input_status = QLabel(self)
        self.voice_input_status.setAlignment(Qt.AlignCenter)
        self.voice_input_status.setStyleSheet("""
            color: white;
            font-size: 24px;
            font-family: '맑은 고딕';
        """)
        layout.addWidget(self.voice_input_status)

        self.input_line = QLineEdit(self)
        self.input_line.setPlaceholderText("질문을 입력하세요 (예: 313호는 어떤 장소야?)")
        self.input_line.setStyleSheet("""
            QLineEdit {
                background-color: #222222;
                color: white;
                padding: 10px;
                font-size: 18px;
                border: 2px solid #00ddff;
                border-radius: 10px;
                font-family: '맑은 고딕';
            }
        """)
        self.input_line.returnPressed.connect(self.handle_input)
        self.input_line.setEnabled(True)
        layout.addWidget(self.input_line)

        self.setLayout(layout)

        # 배경 이미지 라벨
        self.background_label = QLabel(self)
        self.background_label.setStyleSheet("background-color: rgba(0, 0, 0, 160); border: 2px solid #00ddff;")
        self.background_label.setAlignment(Qt.AlignCenter)
        self.background_label.hide()

        self.options_layout = QHBoxLayout()
        self.yes_label = QLabel("네", self)
        self.no_label = QLabel("아니오", self)
        for label in [self.yes_label, self.no_label]:
            label.setStyleSheet("color: white; font-size: 24px; padding: 20px; border: 2px solid #00ddff; border-radius: 10px;")
            label.setAlignment(Qt.AlignCenter)
        self.options_layout.addWidget(self.yes_label)
        self.options_layout.addWidget(self.no_label)
        layout.addLayout(self.options_layout)
        self.yes_label.hide()
        self.no_label.hide()

        font = QFont("맑은 고딕", 16)
        QApplication.instance().setFont(font)

    def play_startup_sounds(self):
        try:
            pygame.mixer.music.load("welcome.mp3")
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                QApplication.processEvents()
            pygame.mixer.music.load("question.mp3")
            pygame.mixer.music.play()
        except pygame.error as e:
            print(f"오디오 재생 오류: {e}")

    def handle_input(self):
        text = self.input_line.text().strip()
        self.input_line.clear()

        if "313호" in text:
            self.show_background_image("image/background_313.png")
            self.play_audio("voice_313.mp3")
            self.yes_label.show()
            self.no_label.show()

        elif "네" == text:
            self.play_audio("followme.mp3")

        elif "아니오" == text:
            self.background_label.hide()
            self.yes_label.hide()
            self.no_label.hide()
            self.play_audio("requestion.mp3")

    def show_background_image(self, image_path):
        pixmap = QPixmap(image_path)
        target_width = self.width() // 2
        target_height = self.height() // 2
        scaled_pixmap = pixmap.scaled(target_width, target_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.background_label.setPixmap(scaled_pixmap)

        # 이미지 중앙 위치로 이동
        self.background_label.resize(scaled_pixmap.width(), scaled_pixmap.height())
        self.background_label.move(
            (self.width() - scaled_pixmap.width()) // 2,
            (self.height() - scaled_pixmap.height()) // 2
        )
        self.background_label.show()

    def play_audio(self, audio_path):
        try:
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.play()
        except pygame.error as e:
            print(f"오디오 재생 오류: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = VoiceAssistant()
    ex.show()
    sys.exit(app.exec_())
