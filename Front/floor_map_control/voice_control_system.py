#floor3_map_control_v5.py && 음성 인식 및 출력
import sys
import re
import os
import subprocess  # QProcess로 대체될 예정이지만, 임시로 남겨둠

from PySide2.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QMessageBox, \
    QHBoxLayout
from PySide2.QtGui import QFont
from PySide2.QtCore import Qt, QTimer, QUrl, Signal, Slot, QProcess  # QProcess 추가
from PySide2.QtMultimedia import QMediaPlayer, QMediaContent

from floor3_map_control_v5 import MapWidget

try:
    import speech_recognition as sr
except ImportError:
    print("SpeechRecognition 또는 PyAudio가 설치되지 않았습니다. 음성 입력이 작동하지 않습니다.")
    print("pip install SpeechRecognition PyAudio 를 실행하여 설치해주세요.")
    sr = None


class VoiceAssistant(QMainWindow):
    voice_recognized = Signal(str)
    voice_error = Signal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("로봇 음성 제어 시스템")
        self.setGeometry(100, 100, 1920, 1080)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_h_layout = QHBoxLayout(central_widget)

        voice_control_container = QWidget()
        voice_v_layout = QVBoxLayout(voice_control_container)
        voice_control_container.setFixedWidth(400)

        self.status_label = QLabel("음성 명령 대기 중...", self)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont("Arial", 24, QFont.Bold))
        voice_v_layout.addWidget(self.status_label)

        self.start_voice_btn = QPushButton("음성 입력 시작")
        self.start_voice_btn.clicked.connect(self.start_listening)
        self.start_voice_btn.setEnabled(True)
        voice_v_layout.addWidget(self.start_voice_btn)

        self.stop_voice_btn = QPushButton("음성 입력 중지")
        self.stop_voice_btn.clicked.connect(self.stop_listening)
        self.stop_voice_btn.setEnabled(False)
        voice_v_layout.addWidget(self.stop_voice_btn)

        voice_v_layout.addStretch(1)
        main_h_layout.addWidget(voice_control_container)

        self.map_widget_3f = MapWidget()
        self.map_widget_3f.setFixedSize(1500, 1080)
        main_h_layout.addWidget(self.map_widget_3f)
        self.current_map_widget = self.map_widget_3f

        self.recognizer = None
        self.microphone = None
        self.stop_listening_callback = None
        self.is_listening = False

        if sr:
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()

        self.media_player = QMediaPlayer(self)
        self.media_player.setVolume(100)
        self.media_player.stateChanged.connect(self.handle_media_state_changed)
        self.is_playing_audio = False
        self._pending_map_navigation_room = None

        # QProcess 인스턴스 추가 (기존 스크립트 실행용)
        self.script_process = QProcess(self)
        self.script_process.finished.connect(self.on_script_finished)
        self.script_process.readyReadStandardOutput.connect(self.read_script_output)
        self.script_process.readyReadStandardError.connect(self.read_script_error)

        # QProcess 인스턴스 추가 (review_gui.py 실행용)
        self.review_gui_process = QProcess(self)
        self.review_gui_process.finished.connect(self.on_review_gui_finished)
        self.review_gui_process.readyReadStandardOutput.connect(lambda: print("Review GUI Output:", self.review_gui_process.readAllStandardOutput().data().decode('utf-8').strip()))
        self.review_gui_process.readyReadStandardError.connect(lambda: print("Review GUI Error:", self.review_gui_process.readAllStandardError().data().decode('utf-8').strip()))


        # 시그널과 슬롯 연결
        self.voice_recognized.connect(self.process_voice_command)
        self.voice_error.connect(self.update_status_label_with_error)
        self.current_map_widget.robot_moved_to_destination.connect(self.on_robot_arrival_complete)

        # 종료 키워드 목록 정의
        self.termination_keywords = [
            "종료", "마침", "끝", "완료", "끝남", "나가기", "닫기", "종결", "정리", "종착",
            "마지막", "다음", "탈출", "이탈", "나감", "종료됨", "종료하기", "끝내기", "마무리",
            "접기", "그만하기", "세션종료", "끝으로", "헤어지기", "닫음", "정료", "Exit",
            "End", "Close", "Finish", "Quit", "Done"
        ]
        # 시작 안내 음성 재생 (QTimer를 사용하여 비동기적으로 시작)
        QTimer.singleShot(500, lambda: self.play_audio("AI_SIM_mp3/navi.mp3"))

    def play_audio(self, audio_file_path):
        """Plays an MP3 file."""
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            selected_file = os.path.join(base_dir, audio_file_path)

            if not os.path.exists(selected_file):
                QMessageBox.warning(self, "파일 없음", f"오디오 파일을 찾을 수 없습니다: {selected_file}")
                print(f"Error: Audio file not found at {selected_file}")
                self.is_playing_audio = False
                # 오디오 파일이 없으면 바로 다음 음성 입력 대기 상태로 전환
                self.start_listening_after_audio_check()
                return

            media_content = QMediaContent(QUrl.fromLocalFile(selected_file))
            self.media_player.setMedia(media_content)
            self.media_player.play()
            self.is_playing_audio = True
            print(f"MP3 재생 시작: {selected_file}")

            self.start_voice_btn.setEnabled(False)
            self.stop_voice_btn.setEnabled(False)
            self.status_label.setText("음성 안내 재생 중...")

        except Exception as e:
            print(f"음성 재생 오류: {str(e)}")
            QMessageBox.warning(self, "재생 오류", f"MP3 파일 재생에 실패했습니다: {e}")
            self.is_playing_audio = False
            # 재생 오류 시에도 다음 음성 입력 대기 상태로 전환
            self.start_listening_after_audio_check()

    def handle_media_state_changed(self, state):
        """Slot called when media player state changes."""
        if state == QMediaPlayer.StoppedState:
            self.is_playing_audio = False
            print("MP3 재생 완료.")

            # 음성 재생이 끝났을 때만 다음 동작으로 진행
            if self._pending_map_navigation_room:
                room_number_to_navigate = self._pending_map_navigation_room
                self._pending_map_navigation_room = None  # 반드시 초기화

                if self.current_map_widget:
                    self.current_map_widget.navigate_to_room_from_voice(room_number_to_navigate)
                    self.status_label.setText(f"{room_number_to_navigate}호로 경로 안내를 시작합니다.")
                else:
                    self.status_label.setText("맵이 초기화되지 않았습니다.")
                # 경로 안내 시작 후에는 바로 음성 입력 대기 모드로 가지 않음 (맵 이동 중이므로)
                # 맵 이동 완료 시그널 (on_robot_arrival_complete)에서 처리

            else:
                # 초기 안내 음성 재생 후나 다른 음성 재생 후에는 바로 음성 입력 대기
                self.start_listening_after_audio_check()

    @Slot(str)
    def on_robot_arrival_complete(self, room_number):
        """Slot called when the robot has visually arrived at the destination on the map."""
        print(f"Robot visual arrival complete for room: {room_number}. Executing script...")
        self.status_label.setText(f"{room_number}호 도착. 스크립트 실행 준비 중...")
        # 2초 딜레이 추가 후 스크립트 실행
        QTimer.singleShot(2000, lambda: self.execute_room_navigation_script(room_number))

    def execute_room_navigation_script(self, room_number):
        """Executes the specific navigation script for the given room number using QProcess."""
        script_name = f"navigation_{room_number}.py"
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "navigation", script_name)

        if not os.path.exists(script_path):
            self.status_label.setText(f"오류: {script_name} 파일을 찾을 수 없습니다. (경로: {script_path})")
            print(f"Error: Navigation script not found at {script_path}")
            # 파일이 없으면 바로 다음 음성 입력 대기
            QTimer.singleShot(2000, self.start_listening_after_audio_check)
            return

        try:
            self.status_label.setText(f"{room_number}호 스크립트 실행 중...")
            print(f"Executing: python {script_path}")

            # QProcess를 사용하여 비동기적으로 스크립트 실행
            self.script_process.start(sys.executable, [script_path])
            # 스크립트가 시작되었으므로, 여기서 self.start_listening_after_audio_check()를 바로 호출하지 않음
            # 스크립트 완료 시그널 (on_script_finished)에서 처리

        except Exception as e:
            self.status_label.setText(f"스크립트 실행 시작 오류: {e}")
            print(f"Error starting script {script_name}: {e}")
            QTimer.singleShot(2000, self.start_listening_after_audio_check)

    @Slot(int, QProcess.ExitStatus)
    def on_script_finished(self, exit_code, exit_status):
        """Slot called when the QProcess finishes."""
        script_name = "unknown_script.py"  # 스크립트 이름은 여기서 알 수 없으므로 임시
        if self.script_process.arguments():
            script_name = os.path.basename(self.script_process.arguments()[0])

        if exit_status == QProcess.NormalExit and exit_code == 0:
            self.status_label.setText(f"스크립트 실행 완료. 다음 음성 명령 대기 중...")
            print(f"Script {script_name} finished successfully.")
        else:
            error_output = self.script_process.readAllStandardError().data().decode('utf-8').strip()
            self.status_label.setText(f"스크립트 실행 오류: {script_name} 종료 코드 {exit_code}, {error_output}")
            print(f"Script {script_name} failed with exit code {exit_code}. Error: {error_output}")

        # 스크립트 완료 후 2초 딜레이 추가 후 음성 입력 대기
        QTimer.singleShot(2000, self.start_listening_after_audio_check)

    @Slot()
    def read_script_output(self):
        """Reads and prints standard output from the running script."""
        output = self.script_process.readAllStandardOutput().data().decode('utf-8').strip()
        if output:
            print(f"Script Output: {output}")

    @Slot()
    def read_script_error(self):
        """Reads and prints standard error from the running script."""
        error = self.script_process.readAllStandardError().data().decode('utf-8').strip()
        if error:
            print(f"Script Error: {error}")

    def start_listening_after_audio_check(self):
        """Checks if audio playback is finished and then starts voice recognition."""
        # 사용자 요청: 모든 음성 입력은 mp3 재생이 끝난 뒤에 입력 받도록 설정 (이미 구현됨)
        if not self.is_playing_audio:
            self.start_listening()
        else:
            # MP3 재생 중이면 상태 업데이트만 하고, 재생 완료 시그널에서 다시 호출되도록 함
            self.status_label.setText("음성 안내 재생 중... 재생 완료 후 자동 시작.")

    def start_listening(self):
        """Starts voice recognition."""
        if not sr:
            self.status_label.setText("음성 인식 라이브러리를 찾을 수 없습니다.")
            return

        if self.is_listening:
            print("이미 음성 인식 중입니다.")
            return

        if self.is_playing_audio:
            self.status_label.setText("음성 안내 재생 중... 잠시 후 자동으로 시작됩니다.")
            return

        self.status_label.setText("음성 명령을 듣는 중...")

        self.start_voice_btn.setEnabled(False)
        self.stop_voice_btn.setEnabled(True)

        self.is_listening = True
        print("음성 인식 시작...")
        # `listen_in_background`는 자체 스레드에서 실행되므로 UI 블로킹 없음
        self.stop_listening_callback = self.recognizer.listen_in_background(
            self.microphone, self._voice_callback
        )

    def stop_listening(self):
        """Stops voice recognition."""
        if self.stop_listening_callback:
            self.stop_listening_callback(wait_for_stop=False)
            self.stop_listening_callback = None
            self.is_listening = False
            self.status_label.setText("음성 입력 중지됨.")
            self.start_voice_btn.setEnabled(True)
            self.stop_voice_btn.setEnabled(False)
            print("음성 인식 중지.")

    def _voice_callback(self, recognizer, audio):
        """Callback function when voice recognition result is available.
        This runs in a background thread."""
        try:
            recognized_text = recognizer.recognize_google(audio, language="ko-KR")
            print(f"[VoiceAssistant] 인식된 음성: {recognized_text}")
            self.voice_recognized.emit(recognized_text)
        except sr.UnknownValueError:
            print("[VoiceAssistant] 음성을 이해할 수 없습니다.")
            self.voice_error.emit("음성을 이해할 수 없습니다.")
            QTimer.singleShot(500, self.start_listening_after_audio_check)
        except sr.RequestError as e:
            print(f"[VoiceAssistant] Google STT 서비스 오류; {e}")
            self.voice_error.emit(f"STT 서비스 오류: {e}")
            QTimer.singleShot(500, self.start_listening_after_audio_check)
        except Exception as e:
            print(f"[VoiceAssistant] 음성 인식 중 알 수 없는 오류 발생: {e}")
            self.voice_error.emit(f"음성 인식 오류: {e}")
            QTimer.singleShot(500, self.start_listening_after_audio_check)

    @Slot(str)
    def update_status_label_with_error(self, message):
        """음성 인식 오류 메시지를 상태 라벨에 업데이트하는 슬롯."""
        self.status_label.setText(message)

    @Slot(str)
    def process_voice_command(self, recognized_text):
        """Parses and processes the recognized voice command.
        This runs in the main thread (due to signal connection)."""
        self.status_label.setText(f"인식: {recognized_text}")

        # 모든 음성 입력을 소문자로 변환하여 비교 (대소문자 구분 없이)
        lower_recognized_text = recognized_text.lower()

        # 종료 키워드 확인
        for keyword in self.termination_keywords:
            if keyword.lower() in lower_recognized_text:
                self.status_label.setText("종료 명령 감지. review_gui.py를 실행합니다.")
                self.stop_listening() # 현재 음성 인식을 중지
                self.execute_review_gui()
                return # 종료 명령 처리 후 함수 종료

        # 기존 로직 유지 (방 번호, 엘리베이터 등)
        match = re.search(r'(\d{3})(?:호|으로|번|실)?', recognized_text)
        if match:
            room_number = match.group(1)
            if 301 <= int(room_number) <= 314:
                print(f"[VoiceAssistant] 방 번호 감지: {room_number}")

                audio_file_to_play = f"AI_SIM_mp3/move_{room_number}.mp3"
                self.play_audio(audio_file_to_play)
                self._pending_map_navigation_room = room_number

            else:
                self.status_label.setText(f"{room_number}호는 유효하지 않은 방 번호입니다. 301호부터 314호까지 입력해주세요.")
                QTimer.singleShot(500, self.start_listening_after_audio_check)
        elif "엘리베이터" in lower_recognized_text or "층 이동" in lower_recognized_text:
            self.status_label.setText("엘리베이터 페이지로 이동합니다. (현재 맵 위젯에 통합되지 않음)")
            print("[VoiceAssistant] 엘리베이터/층 이동 명령")
            QTimer.singleShot(500, self.start_listening_after_audio_check)
        else:
            self.status_label.setText("명령을 이해할 수 없습니다.")
            QTimer.singleShot(500, self.start_listening_after_audio_check)

    def execute_review_gui(self):
        """Executes the review_gui.py script and closes the current application."""
        review_gui_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "review_gui.py")

        if not os.path.exists(review_gui_path):
            QMessageBox.critical(self, "오류", f"review_gui.py 파일을 찾을 수 없습니다: {review_gui_path}")
            self.status_label.setText("review_gui.py 파일 없음.")
            self.start_listening_after_audio_check()  # 파일 없으면 다시 음성 인식 시작
            return

        try:
            self.status_label.setText("review_gui.py 실행 중...")
            print(f"Executing review_gui.py: python {review_gui_path}")

            # *** CORRECTION HERE: Only capture the boolean success value ***
            # QProcess.startDetached returns only a boolean indicating success.
            # To get the PID, you would typically use start() and then process.processId().
            # However, for a detached process, the PID is less directly useful from the parent.
            success = QProcess.startDetached(sys.executable, [review_gui_path])

            if success:
                # Removed PID logging as it's not directly returned by startDetached in this manner
                print(f"review_gui.py launched successfully. Closing current application.")
                # If detached successfully, it's safe to close this application immediately
                self.close()
            else:
                QMessageBox.critical(self, "실행 오류", f"review_gui.py 실행 시작 실패.")
                self.status_label.setText("review_gui.py 실행 시작 실패.")
                self.start_listening_after_audio_check()  # 오류 발생 시 다시 음성 인식 시작

        except Exception as e:
            QMessageBox.critical(self, "실행 오류", f"review_gui.py 실행 중 예외 발생: {e}")
            self.status_label.setText(f"review_gui.py 실행 오류: {e}")
            self.start_listening_after_audio_check()  # 오류 발생 시 다시 음성 인식 시작

    @Slot(int, QProcess.ExitStatus)
    def on_review_gui_finished(self, exit_code, exit_status):
        """Slot called when the review_gui.py process finishes."""
        if exit_status == QProcess.NormalExit and exit_code == 0:
            print("review_gui.py finished successfully.")
        else:
            error_output = self.review_gui_process.readAllStandardError().data().decode('utf-8').strip()
            print(f"review_gui.py failed with exit code {exit_code}. Error: {error_output}")
        # review_gui.py가 종료되면 현재 애플리케이션도 종료될 예정이므로 추가적인 액션은 필요 없음

if __name__ == "__main__":
    app = QApplication(sys.argv)
    voice_control_system = VoiceAssistant()
    voice_control_system.show()
    sys.exit(app.exec_())
