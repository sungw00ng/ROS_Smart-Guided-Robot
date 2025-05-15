#Voice_Assistant_Sim
import sys
import pygame
from PySide2.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QHBoxLayout, QPushButton, QMessageBox
)
from PySide2.QtGui import QMovie, QPixmap
from PySide2.QtCore import Qt, QTimer, QEvent, QObject, Signal, Slot
import speech_recognition as sr
import threading
import os
import random  # random 모듈 추가


class VoiceRecognitionEvent(QEvent):
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())

    def __init__(self, text, error_msg=None):
        super().__init__(VoiceRecognitionEvent.EVENT_TYPE)
        self.text = text
        self.error_msg = error_msg


class VoiceRecognitionFinishedEvent(QEvent):
    EVENT_TYPE = QEvent.Type(QEvent.registerEventType())

    def __init__(self):
        super().__init__(VoiceRecognitionFinishedEvent.EVENT_TYPE)


class AudioPlayer(QObject):
    finished = Signal()

    def __init__(self):
        super().__init__()
        self.is_playing = False # 재생 상태를 추적하는 플래그 추가

    @Slot(str)
    def play(self, filename):
        try:
            if os.path.exists(filename):
                pygame.mixer.music.load(filename)
                pygame.mixer.music.play()
                self.is_playing = True # 재생 시작 시 플래그 설정
                while pygame.mixer.music.get_busy():
                    QApplication.processEvents()
                self.is_playing = False # 재생 완료 시 플래그 해제
                self.finished.emit()
            else:
                print(f"[경고] 오디오 파일 없음: {filename}")
                self.is_playing = False
                self.finished.emit()
        except Exception as e:
            print(f"[오류] 오디오 재생 실패: {str(e)}")
            self.is_playing = False
            self.finished.emit()


class VoiceAssistant(QWidget):
    def __init__(self):
        super().__init__()
        pygame.init()
        pygame.mixer.init()
        self.is_recording = False
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone(
            device_index=None,
            sample_rate=16000,
            chunk_size=1024
        )
        self.audio_player = AudioPlayer()
        self.audio_player.finished.connect(self.start_recording) # welcome 재생 후 바로 녹음 시작
        self.response_audio_player = AudioPlayer()
        self.error_audio_player = AudioPlayer()
        self.sim_exception_player = AudioPlayer() # sim_exception.mp3 재생을 위한 AudioPlayer

        self.initUI()
        QTimer.singleShot(500, self.play_startup_sounds)
        self.recognized_queries = []
        self.waiting_for_audio_finish = False

    def initUI(self):
        """UI 초기화: 중앙 GIF 위에 이미지 오버레이"""
        self.setWindowTitle("ROS2_SerBotAGV")
        self.setGeometry(0, 0, 1920, 1080)
        self.setStyleSheet("background-color: #000000;")

        layout = QVBoxLayout()
        layout.setContentsMargins(70, 70, 70, 70)
        layout.setSpacing(30)

        # ===== GIF 라벨 =====
        gif_size = 800  # GIF 크기를 약 두 배로 조정 (800 * 2)
        self.movie_label = QLabel(self)
        self.movie_label.setFixedSize(gif_size, gif_size)
        self.movie_label.setAlignment(Qt.AlignCenter)

        self.movie = QMovie("voice.gif")
        self.movie_label.setMovie(self.movie)
        self.movie.start()

        # ===== 이미지 오버레이 (movie_label 안에 포함) =====
        overlay_size = 200  # 오버레이 이미지 크기를 약 두 배로 조정 (200 * 2)
        self.image_overlay_label = QLabel(self.movie_label)  # movie_label의 자식으로 설정
        pixmap = QPixmap("image/Sim_Gyu_Seon.png")
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(overlay_size, overlay_size, Qt.KeepAspectRatio,
                                          Qt.SmoothTransformation)  # KeepAspectRatio 사용
            self.image_overlay_label.setPixmap(scaled_pixmap)
            self.image_overlay_label.setFixedSize(overlay_size, overlay_size)
            self.image_overlay_label.setAlignment(Qt.AlignCenter)
            self.image_overlay_label.setStyleSheet(f"""
                border-radius: {overlay_size // 2}px; /* 원형 테두리를 이미지 크기에 맞춰 조정 */
                background: transparent;
            """)
            # 이미지 중앙 위치 이동 (GIF 라벨의 변경된 크기에 맞춰 계산)
            self.image_overlay_label.move(
                (self.movie_label.width() - self.image_overlay_label.width()) // 2,
                (self.movie_label.height() - self.image_overlay_label.height()) // 2
            )
            self.image_overlay_label.raise_()
        else:
            print("[경고] 이미지 로드 실패: image/Sim_Gyu_Seon.png")

        layout.addWidget(self.movie_label, alignment=Qt.AlignCenter)

        # ===== 음성 인식 버튼 =====
        self.voice_button = QPushButton("음성 인식 시작", self)
        self.voice_button.setStyleSheet("""
            QPushButton {
                background-color: #00ddff;
                color: white;
                font-size: 30px;
                padding: 20px;
                border-radius: 15px;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #aaaaaa;
            }
        """)
        self.voice_button.clicked.connect(self.toggle_voice_input)
        layout.addWidget(self.voice_button, alignment=Qt.AlignCenter)

        self.setLayout(layout)

        # 배경 이미지 레이블(필수)
        self.background_label = QLabel(self)
        self.background_label.setStyleSheet("""
            background-color: rgba(0, 0, 0, 160);
            border: 3px solid #00ddff;
        """)
        self.background_label.setAlignment(Qt.AlignCenter)
        self.background_label.hide()


    def play_startup_sounds(self):
        """시작 음성 재생 (welcome 파일 랜덤 재생)"""
        try:
            welcome_dir = "welcome"
            welcome_files = [f for f in os.listdir(welcome_dir) if f.startswith("welcome_") and f.endswith(".mp3")]

            if welcome_files:
                random_welcome_file = os.path.join(welcome_dir, random.choice(welcome_files))
                if os.path.exists(random_welcome_file):
                    self.audio_player.play(random_welcome_file) # 재생 시작
                    self.audio_player.finished.connect(self.start_recording) # 재생 끝나면 녹음 시작
                else:
                    print(f"[경고] 랜덤 환영 오디오 파일 없음: {random_welcome_file}")
                    self.start_recording() # 파일 없으면 바로 녹음 시작
            else:
                print(f"[경고] 환영 오디오 파일이 디렉토리에 없습니다: {welcome_dir}")
                self.start_recording() # 폴더 없으면 바로 녹음 시작

        except Exception as e:
            print(f"[오류] 오디오 재생 실패: {str(e)}")
            self.start_recording() # 오류 발생해도 바로 녹음 시작

    def toggle_voice_input(self):
        """음성 인식 시작/중지 토글"""
        if not self.is_recording:
            self.start_recording()
        else:
            self.finish_recognition()

    def start_recording(self):
        """음성 인식 시작"""
        self.is_recording = True
        self.voice_button.setText("듣는 중...")
        self.voice_button.setEnabled(False)

        try:
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            threading.Thread(
                target=self.process_voice_recognition,
                daemon=True
            ).start()
        except Exception as e:
            self.error_audio_player.play("AI_SIM_mp3/mic_error.mp3")
            self.is_recording = False
            self.voice_button.setText("음성 인식 시작")
            self.voice_button.setEnabled(True)

    def process_voice_recognition(self):
        """음성 인식 처리"""
        print("음성 인식 시작...")
        with self.microphone as source:
            try:
                audio = self.recognizer.listen(
                    source,
                    timeout=10,
                    phrase_time_limit=8
                )
                text = self.recognizer.recognize_google(audio, language='ko-KR')
                QApplication.postEvent(self, VoiceRecognitionEvent(text))

            except sr.WaitTimeoutError:
                print("[디버그] 음성 입력 없음 감지, not_voice_detection 재생 시도")
                self.response_audio_player.play("AI_SIM_mp3/not_voice_detection.mp3")
                if not pygame.mixer.music.get_busy():
                    print("[디버그] not_voice_detection 재생 실패")
                while self.response_audio_player.is_playing:
                    QApplication.processEvents()
                self.start_recording()

            except sr.UnknownValueError:
                self.error_audio_player.play("AI_SIM_mp3/mic_error.mp3")
                self.is_recording = False
                self.voice_button.setText("음성 인식 시작")
                self.voice_button.setEnabled(True)
            except sr.RequestError as e:
                self.error_audio_player.play("AI_SIM_mp3/mic_error.mp3")
                self.is_recording = False
                self.voice_button.setText("음성 인식 시작")
                self.voice_button.setEnabled(True)
            except Exception as e:
                self.error_audio_player.play("AI_SIM_mp3/mic_error.mp3")
                self.is_recording = False
                self.voice_button.setText("음성 인식 시작")
                self.voice_button.setEnabled(True)
            finally:
                QApplication.postEvent(self, VoiceRecognitionFinishedEvent())

    def event(self, event):
        """사용자 정의 이벤트 처리"""
        if isinstance(event, VoiceRecognitionEvent):
            if event.error_msg:
                self.show_error_message(event.error_msg)
            elif event.text:
                self.handle_recognized_text(event.text)
            return True
        elif isinstance(event, VoiceRecognitionFinishedEvent):
            self.finish_recognition()
            return True
        return super().event(event)

    def handle_recognized_text(self, text):
        """인식된 텍스트 처리"""
        self.recognized_queries.append(text)
        print(f"인식된 질문: {text}")
        self.process_query(text)

    def process_query(self, text):
        """사용자 질문 처리"""
        text_lower = text.lower()

        if "313호" in text_lower or "313" in text_lower or "삼일삼" in text_lower:
            self.show_message("313호 관련 기능은 제거되었습니다.")
        else:
            self.sim_exception_player.play("AI_SIM_mp3/sim_exception.mp3")

    def finish_recognition(self):
        """음성 인식 종료"""
        self.is_recording = False
        self.voice_button.setText("음성 인식 시작")
        self.voice_button.setEnabled(True)

    def reset_voice_input(self, delay_ms):
        """음성 입력 상태 초기화 및 음성 인식 시작"""
        QTimer.singleShot(delay_ms, self.start_voice_recognition)

    def start_voice_recognition(self):
        """음성 인식 시작 (버튼 없이)"""
        if not self.is_recording:
            self.start_recording()

    def show_error_message(self, message):
        """오류 메시지 표시"""
        QMessageBox.warning(self, "오류 발생", message)

    def closeEvent(self, event):
        """창 닫기 이벤트 처리"""
        pygame.mixer.quit()
        event.accept()


if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    assistant = VoiceAssistant()
    assistant.setGeometry(0, 0, 1920, 1080)
    assistant.show()
    sys.exit(app.exec_())
