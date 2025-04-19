#Voice_Assistant_Version 3
#background_313.png가 밀려서 1시에 나타나던 오류 수정
#'네' 혹은 '아니오' 입력 시 실행되지 않던 오류 수정
#음성 인식 시 '네' 대신 '그걸로 부탁해'일 때 실행가능함.
#향후 Markov Chain을 통해 v4에서 더 다양한 상황을 만들어볼 예정. 
import sys
import pygame
from PySide2.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QHBoxLayout, QPushButton, QMessageBox
)
from PySide2.QtGui import QMovie, QPixmap, QFont
from PySide2.QtCore import Qt, QTimer, QEvent, QObject, Signal, Slot
import speech_recognition as sr
import threading
import os


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

    @Slot(str)
    def play(self, filename):
        try:
            if os.path.exists(filename):
                pygame.mixer.music.load(filename)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    QApplication.processEvents()
                self.finished.emit()
            else:
                print(f"[경고] 오디오 파일 없음: {filename}")
                self.finished.emit()
        except Exception as e:
            print(f"[오류] 오디오 재생 실패: {str(e)}")
            self.finished.emit()


class VoiceAssistant(QWidget):
    def __init__(self):
        super().__init__()
        pygame.init()
        pygame.mixer.init()
        self.waiting_yes_no = False
        self.is_recording = False
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone(
            device_index=None,
            sample_rate=16000,
            chunk_size=1024
        )
        self.audio_player = AudioPlayer()
        self.audio_player.finished.connect(self.start_voice_recognition_after_question)

        self.initUI()
        QTimer.singleShot(500, self.play_startup_sounds)
        self.recognized_queries = []

    def initUI(self):
        """UI 초기화"""
        self.setWindowTitle("ROS2_SerBotAGV")
        self.setGeometry(0, 0, 1440, 810)
        self.setStyleSheet("background-color: #000000;")

        layout = QVBoxLayout()
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(20)

        # 제목 레이블
        title_label = QLabel("AIMOB-고은", self)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            color: #00ddff;
            font-size: 40px;
            font-weight: bold;
        """)
        layout.addWidget(title_label)

        # 애니메이션 레이블
        self.movie_label = QLabel(self)
        self.movie = QMovie("voice.gif")
        self.movie_label.setMovie(self.movie)
        self.movie.start()
        self.movie_label.setAlignment(Qt.AlignCenter | Qt.AlignTop)
        layout.addWidget(self.movie_label)

        # 음성 인식 버튼
        self.voice_button = QPushButton("음성 인식 시작", self)
        self.voice_button.setStyleSheet("""
            QPushButton {
                background-color: #00ddff;
                color: white;
                font-size: 20px;
                padding: 15px;
                border-radius: 10px;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #aaaaaa;
            }
        """)
        self.voice_button.clicked.connect(self.toggle_voice_input)
        layout.addWidget(self.voice_button)

        self.setLayout(layout)

        # 배경 이미지 레이블
        self.background_label = QLabel(self)
        self.background_label.setStyleSheet("""
            background-color: rgba(0, 0, 0, 160);
            border: 2px solid #00ddff;
        """)
        self.background_label.setAlignment(Qt.AlignCenter)
        self.background_label.hide()

        # 예/아니오 버튼
        self.button_layout = QHBoxLayout()
        self.yes_button = QPushButton("네")
        self.no_button = QPushButton("아니오")

        button_style = """
            font-size: 18px;
            background-color: #00ddff;
            color: black;
            border-radius: 10px;
        """

        for btn in [self.yes_button, self.no_button]:
            btn.setFixedSize(100, 50)
            btn.setStyleSheet(button_style)

        self.yes_button.clicked.connect(self.yes_clicked)
        self.no_button.clicked.connect(self.no_clicked)

        self.button_layout.addWidget(self.yes_button)
        self.button_layout.addWidget(self.no_button)
        layout.addLayout(self.button_layout)
        self.hide_yes_no_buttons()

    def play_startup_sounds(self):
        """시작 음성 재생"""
        try:
            sound_files = ["welcome.mp3", "question.mp3"]
            if os.path.exists(sound_files[0]):
                pygame.mixer.music.load(sound_files[0])
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    QApplication.processEvents()
            else:
                print(f"[경고] 오디오 파일 없음: {sound_files[0]}")

            if os.path.exists(sound_files[1]):
                self.audio_player.play(sound_files[1])
            else:
                print(f"[경고] 오디오 파일 없음: {sound_files[1]}")
                self.start_voice_recognition_after_question()

        except Exception as e:
            print(f"[오류] 오디오 재생 실패: {str(e)}")
            self.start_voice_recognition_after_question()

    def start_voice_recognition_after_question(self):
        """question.mp3 재생 후 음성 인식 시작"""
        QTimer.singleShot(500, self.toggle_voice_input)

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
            self.show_error_message(f"마이크 오류: {str(e)}")
            self.finish_recognition()

    def process_voice_recognition(self):
        """음성 인식 처리"""
        print("음성 인식 시작...")
        with self.microphone as source:
            try:
                audio = self.recognizer.listen(
                    source,
                    timeout=5,
                    phrase_time_limit=8
                )
                text = self.recognizer.recognize_google(audio, language='ko-KR')
                QApplication.postEvent(self, VoiceRecognitionEvent(text))

            except sr.WaitTimeoutError:
                QApplication.postEvent(self, VoiceRecognitionEvent(None, "음성 입력 없음"))
            except sr.UnknownValueError:
                QApplication.postEvent(self, VoiceRecognitionEvent(None, "음성 이해 불가"))
            except sr.RequestError as e:
                QApplication.postEvent(self, VoiceRecognitionEvent(None, f"서비스 오류: {str(e)}"))
            except Exception as e:
                QApplication.postEvent(self, VoiceRecognitionEvent(None, f"오류 발생: {str(e)}"))
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

        if self.waiting_yes_no:
            if "그걸로 부탁해" in text_lower:
                self.play_response("followme.mp3")
            else:
                self.play_response("requestion.mp3")
            self.reset_voice_input(3000)
            return

        if self.is_313_question(text_lower):
            self.show_313_info()
        else:
            self.show_error_message("지원하지 않는 질문입니다.")
            self.reset_voice_input(3000)

    def is_313_question(self, text):
        """313호 관련 질문 확인"""
        keywords = ["313호", "313", "삼일삼"]
        return any(k in text for k in keywords)

    def show_313_info(self):
        """313호 정보 표시"""
        try:
            if os.path.exists("background_313.png"):
                pixmap = QPixmap("background_313.png")
                if not pixmap.isNull():
                    scaled = pixmap.scaled(800, 450, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                    self.background_label.setPixmap(scaled)
                    self.background_label.resize(scaled.size())
                    self.background_label.move(
                        (self.width() - scaled.width()) // 2,
                        (self.height() - scaled.height()) // 2
                    )
                    self.background_label.show()

                    if os.path.exists("voice_313.mp3"):
                        pygame.mixer.music.load("voice_313.mp3")
                        pygame.mixer.music.play()

                    self.waiting_yes_no = True
                    self.show_yes_no_buttons()
                    QTimer.singleShot(1000, self.toggle_voice_input)  # 이미지 표시 후 1초 뒤 음성 인식 시작
                    return

        except Exception as e:
            print(f"[오류] 이미지 표시 실패: {str(e)}")

        self.show_error_message("정보를 표시할 수 없습니다.")
        self.reset_voice_input(3000)

    def play_response(self, audio_file):
        """응답 오디오 재생"""
        if os.path.exists(audio_file):
            try:
                pygame.mixer.music.load(audio_file)
                pygame.mixer.music.play()
            except Exception as e:
                print(f"[오류] 오디오 재생 실패: {str(e)}")
        else:
            print(f"[경고] 오디오 파일 없음: {audio_file}")

    def reset_voice_input(self, delay_ms):
        """음성 입력 상태 초기화"""
        self.waiting_yes_no = False
        self.hide_yes_no_buttons()
        self.hide_background_image()
        QTimer.singleShot(delay_ms, self.toggle_voice_input)

    def show_yes_no_buttons(self):
        """예/아니오 버튼 표시"""
        self.yes_button.show()
        self.no_button.show()

    def hide_yes_no_buttons(self):
        """예/아니오 버튼 숨기기"""
        self.yes_button.hide()
        self.no_button.hide()

    def hide_background_image(self):
        """배경 이미지 숨기기"""
        self.background_label.hide()

    def finish_recognition(self):
        """음성 인식 종료"""
        self.is_recording = False
        self.voice_button.setText("음성 인식 시작")
        self.voice_button.setEnabled(True)

    def show_error_message(self, message):
        """오류 메시지 표시"""
        QMessageBox.warning(self, "오류 발생", message)

    def yes_clicked(self):
        """'네' 버튼 클릭 처리"""
        self.process_response(True)

    def no_clicked(self):
        """'아니오' 버튼 클릭 처리"""
        self.process_response(False)

    def process_response(self, is_yes):
        """버튼 응답 처리"""
        response = "네" if is_yes else "아니오"
        print(f"버튼 선택: {response}")
        self.handle_recognized_text(response)

    def closeEvent(self, event):
        """창 닫기 이벤트 처리"""
        pygame.mixer.quit()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    assistant = VoiceAssistant()
    assistant.show()
    sys.exit(app.exec_())
