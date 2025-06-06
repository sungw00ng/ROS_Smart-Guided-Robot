import sys
import random
from floor3_map_control import MapWidget
import os
from PySide2.QtWidgets import (
    QApplication, QWidget, QLabel, QGridLayout, QVBoxLayout, QStackedLayout
)
from PySide2.QtGui import QPixmap, QMovie
from PySide2.QtCore import Qt, QSize, QUrl, QTimer
from PySide2.QtMultimedia import QMediaPlayer, QMediaContent

class ElevatorControl(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Elevator Control")
        self.setGeometry(0, 0, 1920, 1080)
        self.setStyleSheet("background-color: black;")

        # 미디어 플레이어 초기화
        self.media_player = QMediaPlayer()
        self.media_player.setVolume(100)

        # UI 초기화
        self.init_ui()

        # 0.5초 후 음성 재생
        QTimer.singleShot(500, self.play_random_audio)

    def init_ui(self):
        # 메인 레이아웃 설정
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        self.main_layout.addStretch(1)

        # 상단 라벨 설정
        font_size = int(1920 * 0.05)
        self.label_container = QWidget()
        stacked_layout = QStackedLayout()
        self.label_container.setLayout(stacked_layout)

        # 그림자 라벨
        self.click_floor_label_shadow = QLabel("Click Floor:)")
        self.click_floor_label_shadow.setStyleSheet(
            f"color: gray; font-size: {font_size}px; font-weight: bold;"
        )
        self.click_floor_label_shadow.setAlignment(Qt.AlignCenter)
        self.click_floor_label_shadow.move(1, 0)

        # 메인 라벨
        self.click_floor_label = QLabel("Click Floor:)")
        self.click_floor_label.setStyleSheet(
            f"color: white; font-size: {font_size}px; font-weight: bold;"
        )
        self.click_floor_label.setAlignment(Qt.AlignCenter)

        stacked_layout.addWidget(self.click_floor_label_shadow)
        stacked_layout.addWidget(self.click_floor_label)
        self.main_layout.addWidget(self.label_container)

        # 그리드 레이아웃 설정
        self.grid_layout = QGridLayout()
        self.grid_layout.setHorizontalSpacing(40)
        self.grid_layout.setVerticalSpacing(110)
        self.main_layout.addLayout(self.grid_layout)

        # 버튼 생성
        self.buttons = []
        button_width = int(1920 * 0.15)
        button_height = int(1080 * 0.15)
        button_font_size = int(button_height * 0.4)

        for i in range(1, 12):
            button_label = QLabel()
            pixmap = QPixmap(f"image/엘베버튼{i}.png")
            if not pixmap.isNull():
                button_label.setPixmap(pixmap.scaled(button_width, button_height, Qt.KeepAspectRatio))
            else:
                button_label.setText(f"{i}F")
                button_label.setAlignment(Qt.AlignCenter)
                button_label.setStyleSheet(
                    f"border: 2px solid gray; background-color: lightgray; "
                    f"color: white; font-weight: bold; font-size: {button_font_size}px;"
                )
            self.buttons.append(button_label)

        # 버튼 배치
        self.grid_layout.addWidget(self.buttons[0], 0, 0, alignment=Qt.AlignTop | Qt.AlignHCenter)   # 1F
        self.grid_layout.addWidget(self.buttons[3], 0, 1, alignment=Qt.AlignTop | Qt.AlignHCenter)   # 4F
        self.grid_layout.addWidget(self.buttons[6], 0, 3, alignment=Qt.AlignTop | Qt.AlignHCenter)   # 7F
        self.grid_layout.addWidget(self.buttons[9], 0, 4, alignment=Qt.AlignTop | Qt.AlignHCenter)   # 10F

        self.grid_layout.addWidget(self.buttons[1], 1, 0, alignment=Qt.AlignTop | Qt.AlignHCenter)   # 2F
        self.grid_layout.addWidget(self.buttons[4], 1, 1, alignment=Qt.AlignTop | Qt.AlignHCenter)   # 5F
        self.grid_layout.addWidget(self.buttons[7], 1, 3, alignment=Qt.AlignTop | Qt.AlignHCenter)   # 8F
        self.grid_layout.addWidget(self.buttons[10], 1, 4, alignment=Qt.AlignTop | Qt.AlignHCenter)  # 11F

        self.grid_layout.addWidget(self.buttons[2], 2, 0, alignment=Qt.AlignTop | Qt.AlignHCenter)   # 3F
        self.grid_layout.addWidget(self.buttons[5], 2, 1, alignment=Qt.AlignTop | Qt.AlignHCenter)   # 6F
        self.grid_layout.addWidget(self.buttons[8], 2, 3, alignment=Qt.AlignTop | Qt.AlignHCenter)   # 9F

        # 엘리베이터 애니메이션
        self.elevator_label = QLabel()
        self.movie = QMovie("image/엘베.gif")
        elevator_width = int(1920 * 0.2)
        elevator_height = int(1080 * 0.4)

        if self.movie.isValid():
            self.movie.setScaledSize(QSize(elevator_width, elevator_height))
            self.elevator_label.setMovie(self.movie)
            self.movie.start()
        else:
            self.elevator_label.setText("Elevator")
            self.elevator_label.setAlignment(Qt.AlignCenter)
            self.elevator_label.setStyleSheet(
                f"border: 4px solid purple; background-color: lavender; "
                f"font-size: {int(elevator_height * 0.2)}px; font-weight: bold; color: white;"
            )

        self.elevator_label.setAlignment(Qt.AlignCenter)
        self.grid_layout.addWidget(self.elevator_label, 0, 2, 3, 1, Qt.AlignCenter)

        self.main_layout.addStretch(7)
        self.buttons[2].mousePressEvent = self.switch_to_3f_map

    def switch_to_3f_map(self, event):
        self.map_window = MapWidget()
        self.map_window.show()
        self.close()  # 기존 엘리베이터 창 닫기

    def play_random_audio(self):
        try:
            # 음성 파일 목록
            audio_files = [
                "AI_SIM_mp3/3F_1.mp3",
                "AI_SIM_mp3/3F_2.mp3",
                "AI_SIM_mp3/3F_3.mp3",
                "AI_SIM_mp3/3F_4.mp3"
            ]

            # 절대 경로 변환
            base_dir = os.path.dirname(os.path.abspath(__file__))
            selected_file = os.path.join(base_dir, random.choice(audio_files))

            # 미디어 재생
            media_content = QMediaContent(QUrl.fromLocalFile(selected_file))
            self.media_player.setMedia(media_content)
            self.media_player.play()

        except Exception as e:
            print(f"음성 재생 오류: {str(e)}")

    def resizeEvent(self, event):
        if hasattr(self, 'movie') and self.movie.isValid() and hasattr(self, 'elevator_label'):
            self.movie.setScaledSize(self.elevator_label.size())
        super().resizeEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ElevatorControl()
    window.show()
    sys.exit(app.exec_())
