import sys
import os
import pygame  # pygame 라이브러리 임포트

from PySide2.QtWidgets import (
    QApplication, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QWidget
)
from PySide2.QtGui import QPixmap, QIcon
from PySide2.QtCore import Qt, QSize, Signal, QTimer


# 클릭 가능한 QLabel 커스텀 클래스
class ClickableLabel(QLabel):
    clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.PointingHandCursor)  # 마우스 커서를 손가락 모양으로 변경하여 클릭 가능함을 나타냄

    def mouseReleaseEvent(self, event):
        # 마우스 왼쪽 버튼을 놓았을 때만 clicked 시그널 방출
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mouseReleaseEvent(event)


class ProfessorCard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("교수님 정보 카드")  # 윈도우 제목 설정
        self.setFixedSize(1920, 1080)  # 윈도우 크기 고정
        self.setStyleSheet("background-color: #000000;")  # 배경을 검정색으로 설정

        # --- Pygame Mixer 초기화 ---
        try:
            pygame.init()  # Pygame 초기화 (선택 사항이지만 안전을 위해)
            pygame.mixer.init()  # Pygame 믹서 초기화
            pygame.mixer.music.set_volume(1.0)  # 볼륨을 100%로 설정
            self.pygame_initialized = True
            print("Pygame mixer 초기화 성공.")
        except Exception as e:
            self.pygame_initialized = False
            print(f"오류: Pygame mixer 초기화 실패 - {e}")
            print("오디오 재생이 작동하지 않을 수 있습니다.")

        # --- 경로 설정 ---
        # ROS 프로젝트의 루트 디렉토리를 기준으로 이미지 및 오디오 파일 경로를 설정합니다.
        # 스크립트 파일(__file__)의 디렉토리에서 두 번 상위로 이동하여 프로젝트 루트를 찾습니다.
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        # --- 왼쪽 이미지 및 텍스트 ---
        self.main_img = QLabel()
        # image/person_313.png 경로 그대로 사용 (변경 없음)
        main_img_path = os.path.join(self.project_root, "image", "person_313.png")
        pixmap_main = QPixmap(main_img_path)
        if not pixmap_main.isNull():
            self.main_img.setPixmap(pixmap_main.scaled(800, 600, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.main_img.setStyleSheet("color: white; font-size: 30px;")
            print(f"경고: 메인 이미지 파일을 찾을 수 없습니다: {main_img_path}")
        self.main_img.setStyleSheet("padding: 20px;")

        self.sub_img = QLabel()
        # image/person_313_qr_dbpia.png 경로 그대로 사용 (변경 없음)
        sub_img_path = os.path.join(self.project_root, "image", "person_313_qr_dbpia.png")
        pixmap_sub = QPixmap(sub_img_path)
        if not pixmap_sub.isNull():
            self.sub_img.setPixmap(pixmap_sub.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.sub_img.setStyleSheet("color: white; font-size: 30px;")
            print(f"경고: QR 이미지 파일을 찾을 수 없습니다: {sub_img_path}")
        self.sub_img.setStyleSheet("padding: 20px;")

        self.qr_text_label = QLabel("")  # 텍스트 변경 (사용자 요청에 따라 빈 문자열)
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

        # --- 가운데 텍스트 정보 (314호 내용으로 변경) ---
        text = (
            "\n\n\n[314호]\n세미나실이다."  # 내용 변경
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
        info_label.setFixedWidth(500)  # 가운데 텍스트 라벨의 고정 너비 설정

        center_layout = QVBoxLayout()
        center_layout.addWidget(info_label, alignment=Qt.AlignTop)
        center_layout.addStretch()

        center_container = QWidget()
        center_container.setLayout(center_layout)

        # --- 오른쪽 이미지 (클릭 가능, 314호 이미지로 변경) ---
        self.right_img = ClickableLabel()
        right_img_path = os.path.join(self.project_root, "image", "314호.png")  # 이미지 경로 314호로 변경
        pixmap_right = QPixmap(right_img_path)
        if not pixmap_right.isNull():
            self.right_img.setPixmap(pixmap_right.scaled(600, 1200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.right_img.setStyleSheet("color: white; font-size: 30px;")
            print(f"경고: 314호 이미지 파일을 찾을 수 없습니다: {right_img_path}")
        self.right_img.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.right_img.clicked.connect(self.on_click)  # 클릭 이벤트 연결

        right_layout = QVBoxLayout()
        right_layout.addWidget(self.right_img, alignment=Qt.AlignRight | Qt.AlignVCenter)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        right_container = QWidget()
        right_container.setLayout(right_layout)
        right_container.setStyleSheet("margin: 0px; padding: -100px;")  # 스타일시트 (오타 주의, -100px는 유효하지 않을 수 있음)

        # --- 전체 수평 레이아웃 ---
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(80, 60, 80, 60)
        main_layout.setSpacing(60)
        main_layout.addWidget(left_container)  # 왼쪽 컨테이너 추가
        main_layout.addWidget(center_container)  # 가운데 컨테이너 추가
        main_layout.addWidget(right_container)  # 오른쪽 컨테이너 추가

        self.setLayout(main_layout)

        # --- 오디오 재생 및 종료 로직 시작 ---
        self.audio_playback_timer = QTimer(self)
        self.audio_playback_timer.timeout.connect(self._check_audio_completion)

        # 시작하자마자 MP3 재생 (314호 정보 오디오로 변경)
        self.play_info_audio("AI_SIM_mp3/info_314.mp3")  # 오디오 파일명 314로 변경

    def play_info_audio(self, audio_file_path):
        """지정된 MP3 파일을 재생하고 재생 완료를 모니터링합니다."""
        if not self.pygame_initialized:
            print("Pygame mixer가 초기화되지 않아 오디오를 재생할 수 없습니다.")
            QApplication.instance().quit()  # 오디오 재생 불가 시 즉시 종료
            return

        try:
            # ROS 프로젝트의 루트 디렉토리를 기준으로 오디오 파일 경로를 설정합니다.
            selected_file = os.path.join(self.project_root, audio_file_path)

            if os.path.exists(selected_file):
                pygame.mixer.music.load(selected_file)
                pygame.mixer.music.play()
                print(f"MP3 재생 시작: {selected_file}")
                # 100ms 간격으로 오디오 재생 완료 여부 확인 타이머 시작
                self.audio_playback_timer.start(100)
            else:
                print(f"오류: 오디오 파일을 찾을 수 없습니다: {selected_file}")
                QApplication.instance().quit()  # 파일 없을 경우 즉시 종료
        except Exception as e:
            print(f"오류: 오디오 재생 중 문제 발생 - {e}")
            QApplication.instance().quit()  # 재생 오류 시 즉시 종료

    def _check_audio_completion(self):
        """오디오 재생 완료 여부를 확인하고, 완료되면 애플리케이션을 종료합니다."""
        if not self.pygame_initialized:
            self.audio_playback_timer.stop()
            return

        if not pygame.mixer.music.get_busy():  # 음악 재생이 끝났다면
            print("MP3 재생 완료. 애플리케이션을 종료합니다.")
            self.audio_playback_timer.stop()  # 타이머 중지
            QApplication.instance().quit()  # 애플리케이션 종료

    def on_click(self):
        """오른쪽 이미지 클릭 시 호출되는 함수."""
        print("이미지 클릭됨! (이 스크립트는 오디오 재생 후 자동 종료됩니다)")
        # 이 스크립트는 오디오 재생 후 자동으로 종료되므로, 추가적인 동작은 필요하지 않음.

    def closeEvent(self, event):
        """창이 닫힐 때 Pygame mixer를 정리합니다."""
        if self.pygame_initialized and pygame.mixer.get_init():
            pygame.mixer.music.stop()  # 재생 중인 음악 중지
            pygame.mixer.quit()  # 믹서 종료
            pygame.quit()  # Pygame 모듈 종료
            print("Pygame mixer 종료 완료.")
        super().closeEvent(event)  # 부모 클래스의 closeEvent 호출


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ProfessorCard()
    window.show()
    sys.exit(app.exec_())
