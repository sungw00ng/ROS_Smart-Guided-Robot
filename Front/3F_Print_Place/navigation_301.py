import sys
import os
import pygame  # pygame 라이브러리 임포트

from PySide2.QtWidgets import (
    QApplication, QLabel, QVBoxLayout, QHBoxLayout, QWidget
)
from PySide2.QtGui import QPixmap
from PySide2.QtCore import Qt, Signal, QTimer  # QTimer 임포트


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
        self.setWindowTitle("강의실 정보")  # 윈도우 제목 설정
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
        info_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)  # 텍스트를 왼쪽 상단에 정렬
        info_label.setStyleSheet("""
            color: #FFFFFF; /* 텍스트 색상을 흰색으로 */
            font-size: 40px; /* 폰트 크기 설정 */
            line-height: 1.6; /* 줄 간격 설정 */
            padding-left: 40px; /* 왼쪽 패딩 */
            padding-top: 20px; /* 위쪽 패딩 */
        """)
        info_label.setFixedWidth(1200)  # 텍스트 라벨의 고정 너비 설정

        text_layout = QVBoxLayout()
        text_layout.addWidget(info_label, alignment=Qt.AlignTop)  # 텍스트 라벨을 상단에 추가
        text_layout.addStretch()  # 남은 공간을 채우기 위해 스트레치 추가

        text_container = QWidget()
        text_container.setLayout(text_layout)  # 텍스트 컨테이너에 레이아웃 설정

        # --- 오른쪽 이미지 (그대로 유지) ---
        self.right_img = ClickableLabel()  # 클릭 가능한 QLabel 인스턴스 생성
        # 이미지 로드 및 크기 조정, 부드러운 변환 적용
        # 이미지 파일 경로도 ROS 프로젝트 루트에서 찾도록 수정
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        image_path = os.path.join(project_root, "image", "301호.png")
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            self.right_img.setPixmap(pixmap.scaled(600, 1200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.right_img.setText("301호 이미지 없음")  # 이미지 파일 없을 경우 대체 텍스트
            self.right_img.setStyleSheet("color: white; font-size: 30px;")
            print(f"경고: 이미지 파일을 찾을 수 없습니다: {image_path}")

        self.right_img.setAlignment(Qt.AlignRight | Qt.AlignVCenter)  # 이미지를 오른쪽 중앙에 정렬
        self.right_img.clicked.connect(self.on_click)  # 이미지 클릭 시그널 연결

        right_layout = QVBoxLayout()
        right_layout.addWidget(self.right_img, alignment=Qt.AlignRight | Qt.AlignVCenter)
        right_layout.setContentsMargins(0, 0, 0, 0)  # 레이아웃 마진 제거
        right_layout.setSpacing(0)  # 위젯 간 간격 제거

        right_container = QWidget()
        right_container.setLayout(right_layout)  # 오른쪽 이미지 컨테이너에 레이아웃 설정
        right_container.setStyleSheet("margin: 0px; padding: -100px;")  # 스타일시트 (오타 주의, -100px는 유효하지 않을 수 있음)

        # --- 전체 수평 레이아웃 ---
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(80, 60, 80, 60)  # 전체 레이아웃 마진 설정
        main_layout.setSpacing(60)  # 위젯 간 간격 설정
        main_layout.addWidget(text_container, alignment=Qt.AlignLeft)  # 텍스트 컨테이너를 왼쪽 정렬로 추가
        main_layout.addWidget(right_container)  # 이미지 컨테이너 추가

        self.setLayout(main_layout)  # 메인 레이아웃 설정

        # --- 오디오 재생 및 종료 로직 시작 ---
        self.audio_playback_timer = QTimer(self)
        self.audio_playback_timer.timeout.connect(self._check_audio_completion)

        # 시작하자마자 MP3 재생
        self.play_info_audio("AI_SIM_mp3/info_301.mp3")

    def play_info_audio(self, audio_file_path):
        """지정된 MP3 파일을 재생하고 재생 완료를 모니터링합니다."""
        if not self.pygame_initialized:
            print("Pygame mixer가 초기화되지 않아 오디오를 재생할 수 없습니다.")
            QApplication.instance().quit()  # 오디오 재생 불가 시 즉시 종료
            return

        try:
            # ROS 프로젝트의 루트 디렉토리를 기준으로 오디오 파일 경로를 설정합니다.
            # 스크립트 파일(__file__)의 디렉토리에서 두 번 상위로 이동합니다.
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            selected_file = os.path.join(project_root, audio_file_path)

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
