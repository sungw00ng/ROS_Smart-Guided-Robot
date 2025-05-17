# Voice_Assistant_Sim_v3
#코사인유사도 측정 추가(핵심 단어 파악)
#오류 재생 관련 수정
#사이킷런으로 모델학습으로 사용자 음성 인식 향상
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
import random
import difflib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib  # 모델 저장 및 불러오기
import subprocess

MODEL_SAVE_PATH = "models/voice_model.joblib"  # 모델 저장 파일 경로

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
        self.is_playing = False

    @Slot(str)
    def play(self, filename):
        try:
            if os.path.exists(filename):
                pygame.mixer.music.load(filename)
                pygame.mixer.music.play()
                self.is_playing = True
                while pygame.mixer.music.get_busy():
                    QApplication.processEvents()
                self.is_playing = False
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

        # 오디오 플레이어 초기화
        self.audio_player = AudioPlayer()
        self.response_audio_player = AudioPlayer()
        self.error_audio_player = AudioPlayer()
        self.sim_exception_player = AudioPlayer()

        # 오류 발생 상태 플래그
        self.is_error_state = False

        # 쿼리-응답 딕셔너리 정의 (이 부분을 위로 이동)
        self.query_response = {
            "너는 뭐하는 로봇이야": "AI_SIM_mp3/introduction.mp3",
            "길을 어떻게 알아": "AI_SIM_mp3/way.mp3",
            "어떤 인공지능 써": "AI_SIM_mp3/what_the_ai.mp3",
            "3층에서 길 안내": "AI_SIM_mp3/floor3.mp3",
            "길 잘못 들면 어떡해": "AI_SIM_mp3/notcorrectway.mp3",
            "어디까지 알고 있어": "AI_SIM_mp3/knowledge.mp3",
            "너한테 이름 있어": "AI_SIM_mp3/name.mp3",
            "3층에는 어떤 수업들이 있어": "AI_SIM_mp3/what_clsss.mp3",
            "최상일 교수님 연구실은 어디에 있어": "AI_SIM_mp3/311.mp3",
            "김창화 교수님 연구실은 어디에 있어": "AI_SIM_mp3/309.mp3",
            "권기태 교수님 연구실은 어디에 있어": "AI_SIM_mp3/307.mp3",
            "이형원 교수님 연구실은 어디에 있어": "AI_SIM_mp3/305.mp3",
            "디지털스토리텔링프레젠테이션 수업 언제야": "AI_SIM_mp3/learn1.mp3",
            "과학수사의 원리와 이해 수업 언제야": "AI_SIM_mp3/learn2.mp3",
            "정보 컴퓨터교육론 수업 언제야": "AI_SIM_mp3/learn3.mp3",
            "딥러닝 프로젝트 수업 언제야?": "AI_SIM_mp3/learn4.mp3",
            "데이터마이닝 수업 언제야": "AI_SIM_mp3/learn5.mp3",
            "데이터베이스 설계 수업 언제야": "AI_SIM_mp3/learn6.mp3",
            "층수 이동": "elevator_command",
        }

        # 텍스트 벡터화 객체 초기화 및 불러오기 시도
        self.vectorizer = self.load_model()
        self.query_texts = list(self.query_response.keys())
        if self.vectorizer is None:
            self.vectorizer = TfidfVectorizer()
            self.vectorizer.fit(self.query_texts)
            self.save_model()  # 초기 학습 후 모델 저장
        else:
            print("[정보] 저장된 음성 모델을 불러왔습니다.")

        # 시그널 연결
        self.audio_player.finished.connect(self.start_recording)
        self.response_audio_player.finished.connect(self.start_recording)
        self.sim_exception_player.finished.connect(self.start_recording)
        self.error_audio_player.finished.connect(self.reset_error_state)

        self.initUI()
        QTimer.singleShot(500, self.play_startup_sounds)
        self.recognized_queries = []

    def initUI(self):
        self.setWindowTitle("ROS2_SerBotAGV")
        self.setGeometry(0, 0, 1920, 1080)
        self.setStyleSheet("background-color: #000000;")

        layout = QVBoxLayout()
        layout.setContentsMargins(70, 70, 70, 70)
        layout.setSpacing(30)

        # GIF 라벨
        gif_size = 800
        self.movie_label = QLabel(self)
        self.movie_label.setFixedSize(gif_size, gif_size)
        self.movie_label.setAlignment(Qt.AlignCenter)
        self.movie = QMovie("voice.gif")
        self.movie_label.setMovie(self.movie)
        self.movie.start()

        # 이미지 오버레이
        overlay_size = 200
        self.image_overlay_label = QLabel(self.movie_label)
        pixmap = QPixmap("image/Sim_Gyu_Seon.png")
        if not pixmap.isNull():
            scaled_pixmap = pixmap.scaled(overlay_size, overlay_size,
                                          Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_overlay_label.setPixmap(scaled_pixmap)
            self.image_overlay_label.setFixedSize(overlay_size, overlay_size)
            self.image_overlay_label.setAlignment(Qt.AlignCenter)
            self.image_overlay_label.setStyleSheet(f"""
                border-radius: {overlay_size // 2}px;
                background: transparent;
            """)
            self.image_overlay_label.move(
                (self.movie_label.width() - overlay_size) // 2,
                (self.movie_label.height() - overlay_size) // 2
            )
            self.image_overlay_label.raise_()
        else:
            print("[경고] 이미지 로드 실패: image/Sim_Gyu_Seon.png")

        layout.addWidget(self.movie_label, alignment=Qt.AlignCenter)

        # 음성 인식 버튼
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

        # 배경 이미지 레이블
        self.background_label = QLabel(self)
        self.background_label.setStyleSheet("""
            background-color: rgba(0, 0, 0, 160);
            border: 3px solid #00ddff;
        """)
        self.background_label.setAlignment(Qt.AlignCenter)
        self.background_label.hide()

    def load_model(self):
        """저장된 모델을 불러옵니다."""
        try:
            return joblib.load(MODEL_SAVE_PATH)
        except FileNotFoundError:
            return None

    def save_model(self):
        """학습된 모델을 저장합니다."""
        joblib.dump(self.vectorizer, MODEL_SAVE_PATH)
        print(f"[정보] 음성 모델을 '{MODEL_SAVE_PATH}'에 저장했습니다.")

    def play_startup_sounds(self):
        try:
            welcome_dir = "welcome"
            welcome_files = [f for f in os.listdir(welcome_dir)
                             if f.startswith("welcome_") and f.endswith(".mp3")]

            if welcome_files:
                random_welcome = os.path.join(welcome_dir, random.choice(welcome_files))
                if os.path.exists(random_welcome):
                    self.audio_player.play(random_welcome)
                else:
                    print(f"[경고] 파일 없음: {random_welcome}")
                    self.start_recording()
            else:
                print(f"[경고] 환영 파일 없음: {welcome_dir}")
                self.start_recording()
        except Exception as e:
            print(f"[오류] 오디오 재생 실패: {str(e)}")
            self.start_recording()

    def toggle_voice_input(self):
        if not self.is_recording and not self.is_error_state:
            self.start_recording()
        else:
            self.finish_recognition()

    def start_recording(self):
        if any([
            self.audio_player.is_playing,
            self.response_audio_player.is_playing,
            self.sim_exception_player.is_playing,
            self.error_audio_player.is_playing,
            self.is_error_state
        ]):
            QTimer.singleShot(500, self.start_recording)
            return

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
            self.handle_recording_error()

    def handle_recording_error(self):
        self.is_error_state = True
        self.error_audio_player.play("AI_SIM_mp3/mic_error.mp3")
        self.is_recording = False
        self.voice_button.setText("음성 인식 시작")
        self.voice_button.setEnabled(True)

    def reset_error_state(self):
        self.is_error_state = False
        print("[디버그] 오류 상태 해제")
        self.voice_button.setEnabled(True)
        self.voice_button.setText("음성 인식 시작")

    def process_voice_recognition(self):
        print("음성 인식 시작...")
        with self.microphone as source:
            try:
                audio = self.recognizer.listen(
                    source, timeout=10, phrase_time_limit=8
                )
                text = self.recognizer.recognize_google(audio, language='ko-KR')
                QApplication.postEvent(self, VoiceRecognitionEvent(text))

            except sr.WaitTimeoutError:
                print("[타임아웃] 음성 입력 없음")
                self.response_audio_player.play("AI_SIM_mp3/not_voice_detection.mp3")
                while self.response_audio_player.is_playing:
                    QApplication.processEvents()
                self.start_recording()

            except sr.UnknownValueError:
                self.handle_recording_error()
            except sr.RequestError as e:
                self.handle_recording_error()
            except Exception as e:
                print(f"[오류 발생 (음성 인식 중)]: {e}")
                self.handle_recording_error()
            finally:
                QApplication.postEvent(self, VoiceRecognitionFinishedEvent())

    def event(self, event):
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
        self.recognized_queries.append(text)
        print(f"인식된 질문: {text}")
        self.process_query(text)

    def process_query(self, text):
        text_lower = text.lower().strip()
        user_vector = self.vectorizer.transform([text_lower])
        query_vectors = self.vectorizer.transform(self.query_texts)
        print("사용자 벡터:", user_vector)
        print("질문 벡터:", query_vectors)
        similarities = cosine_similarity(user_vector, query_vectors)[0]
        best_similarity_index = similarities.argmax()
        best_similarity = similarities[best_similarity_index]
        best_query = self.query_texts[best_similarity_index]
        response_file = self.query_response.get(best_query)

        SIMILARITY_THRESHOLD = 0.5  # 코사인 유사도 임계값 설정

        print(f"입력: {text_lower}")
        print(f"가장 유사한 질문: {best_query} (유사도: {best_similarity:.4f})")

        if best_similarity >= SIMILARITY_THRESHOLD:
            if best_query == "층수 이동":
                self.navigate_to_elevator()
            elif response_file:
                self.response_audio_player.play(response_file)
            else:
                self.sim_exception_player.play("AI_SIM_mp3/sim_exception.mp3") # 응답 파일 없는 경우
        else:
            self.sim_exception_player.play("AI_SIM_mp3/sim_exception.mp3") # 유사도 낮은 경우

    def navigate_to_elevator(self):
        """엘리베이터 페이지로 전환"""
        try:
            self.close()
            subprocess.Popen(["python", "elevator_page.py"])
        except Exception as e:
            print(f"페이지 전환 오류: {str(e)}")
            self.sim_exception_player.play("AI_SIM_mp3/sim_exception.mp3")

    def finish_recognition(self):
        self.is_recording = False
        self.voice_button.setText("음성 인식 시작")
        self.voice_button.setEnabled(True)

    def show_error_message(self, message):
        QMessageBox.warning(self, "오류 발생", message)

    def closeEvent(self, event):
        pygame.mixer.quit()
        self.save_model() # 프로그램 종료 시 모델 저장 (선택 사항)
        event.accept()


if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    assistant = VoiceAssistant()
    assistant.setGeometry(0, 0, 1920, 1080)
    assistant.show()
    sys.exit(app.exec_())
