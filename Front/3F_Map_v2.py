from PySide2.QtWidgets import QApplication, QWidget, QMessageBox
from PySide2.QtGui import QPainter, QColor, QPen, QFont
from PySide2.QtCore import Qt, QRect, QTimer  # QTimer 추가: 필요 시 이동 시뮬레이션에 사용

# Pilot.py에서 필요한 클래스 임포트 (가정)
# 실제 Pilot.py 파일이 같은 디렉토리에 있거나 PYTHONPATH에 추가되어 있어야 합니다.
# Pilot.py에 여러 클래스가 있지만, 여기서는 Driver 또는 AutoCar 클래스를 사용한다고 가정합니다.
# Pilot.py 파일의 구조에 따라 정확한 임포트 방식이 달라질 수 있습니다.
# 예시: from Pilot import Driver 또는 from Pilot import AutoCar
try:
    from Pilot import Driver  # Driver 클래스를 사용한다고 가정합니다.

    # 만약 AutoCar를 사용한다면: from Pilot import AutoCar
    # 또는 특정 get_Control 함수를 통해 인스턴스를 얻는다면: from Pilot import get_Control
    print("Pilot 모듈의 Driver 클래스를 성공적으로 임포트했습니다.")
except ImportError:
    print("Pilot 모듈 또는 Driver 클래스를 임포트할 수 없습니다.")
    print("실제 로봇 제어 기능은 작동하지 않으며, 더미 함수로 대체됩니다.")


    # 실제 환경에서 Pilot.py가 없는 경우를 대비한 더미 클래스/함수
    class Driver:
        def __init__(self):
            print("Driver 더미 클래스 초기화.")

        def setSpeed(self, speed):
            print(f"더미: 로봇 속도 설정: {speed}")

        def move(self, distance, direction=0, angle=0):  # Pilot.py의 move 함수 시그니처에 따라 다름
            print(f"더미: 로봇이 {distance}만큼 이동 ({direction=}, {angle=}).")

        def stop(self):
            print("더미: 로봇 정지.")
    # class AutoCar: # AutoCar를 사용한다면 이 더미 클래스를 사용
    #     def __init__(self):
    #         print("AutoCar 더미 클래스 초기화.")
    #     def setSpeed(self, speed):
    #         print(f"더미: 로봇 속도 설정: {speed}")
    #     def forward(self, speed=None):
    #         print(f"더미: 로봇이 앞으로 이동 (속도: {speed})")
    #     def stop(self):
    #         print("더미: 로봇 정지.")

import sys
import math

# --- 설정값 ---
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080
GRID_ROWS = 40
GRID_COLS = 60
CELL_WIDTH = WINDOW_WIDTH / GRID_COLS
CELL_HEIGHT = WINDOW_HEIGHT / GRID_ROWS

FLOOR_COLOR = QColor("#222222")
WALL_COLOR = QColor("#555555")
HALLWAY_COLOR = QColor("#eeeeee")
ROOM_COLOR = QColor("#dddddd")

HIGHLIGHT_COLOR_CURRENT = QColor(40, 167, 69, 150)
HIGHLIGHT_COLOR_DESTINATION = QColor(220, 53, 69, 150)
GRID_CLICK_OVERLAY_COLOR = QColor(100, 100, 255, 60)
GRID_BORDER_COLOR = QColor(200, 200, 200, 30)

MAP_AREAS = [
    {"type": "room", "name": "313", "rect": QRect(165, 140, 160, 120)},
    {"type": "room", "name": "312", "rect": QRect(335, 140, 120, 120)},
    {"type": "room", "name": "311", "rect": QRect(465, 140, 120, 120)},
    {"type": "room", "name": "310", "rect": QRect(595, 140, 120, 120)},
    {"type": "room", "name": "309", "rect": QRect(725, 140, 120, 120)},
    {"type": "room", "name": "308", "rect": QRect(855, 140, 120, 120)},
    {"type": "room", "name": "307", "rect": QRect(985, 140, 120, 120)},
    {"type": "room", "name": "306", "rect": QRect(1115, 140, 120, 120)},
    {"type": "room", "name": "305", "rect": QRect(1245, 140, 120, 120)},
    {"type": "room", "name": "304", "rect": QRect(1375, 140, 150, 120)},
    {"type": "room", "name": "301", "rect": QRect(165, 490, 120, 120)},
    {"type": "room", "name": "302", "rect": QRect(295, 490, 120, 120)},
    {"type": "room", "name": "314", "rect": QRect(985, 490, 120, 120)},
    {"type": "room", "name": "303", "rect": QRect(1115, 490, 120, 120)},
    {"type": "hallway", "name": "상단 주 복도", "rect": QRect(130, 290, 1660, 90)},
    {"type": "hallway", "name": "좌측 세로 복도", "rect": QRect(275, 290, 90, 320)},
    {"type": "hallway", "name": "중앙 세로 복도", "rect": QRect(760, 290, 150, 320)},
    {"type": "hallway", "name": "우측 세로 복도", "rect": QRect(1280, 290, 90, 320)},
    {"type": "hallway", "name": "중앙 복도", "rect": QRect(450, 490, 400, 120)},
]


class MapWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Map View")
        self.setGeometry(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.clicked_positions = []  # 최대 2개 클릭 위치 저장

        # Pilot.py의 Driver 인스턴스 생성 (혹은 get_Control() 호출)
        try:
            self.robot_driver = Driver()  # Driver 클래스의 인스턴스 생성
            # 만약 get_Control() 함수를 통해 인스턴스를 얻는다면:
            # self.robot_driver = get_Control()
        except NameError:  # Pilot 모듈 임포트 실패 시 (더미 클래스가 생성된 경우)
            self.robot_driver = Driver()

        # 로봇의 현재 위치 (임시로 출발 지점의 중심에 있다고 가정)
        self.robot_current_grid_pos = None  # (col, row)
        self.robot_target_grid_pos = None  # (col, row)

    def paintEvent(self, event):
        painter = QPainter(self)
        self.draw_grid(painter)
        self.draw_areas(painter)
        self.draw_clicks(painter)
        self.draw_robot_position(painter)  # 로봇 현재 위치 그리기 추가

    def draw_grid(self, painter):
        pen = QPen(GRID_BORDER_COLOR)
        painter.setPen(pen)
        for row in range(GRID_ROWS):
            y = row * CELL_HEIGHT
            painter.drawLine(0, y, WINDOW_WIDTH, y)
        for col in range(GRID_COLS):
            x = col * CELL_WIDTH
            painter.drawLine(x, 0, x, WINDOW_HEIGHT)

    def draw_areas(self, painter):
        for area in MAP_AREAS:
            color = ROOM_COLOR if area['type'] == 'room' else HALLWAY_COLOR
            painter.fillRect(area['rect'], color)
            painter.setPen(Qt.black)
            painter.setFont(QFont("Arial", 12))
            painter.drawText(area['rect'], Qt.AlignCenter, area['name'])

    def draw_clicks(self, painter):
        painter.setFont(QFont("Arial", 10))
        for i, (col, row) in enumerate(self.clicked_positions):
            x = col * CELL_WIDTH
            y = row * CELL_HEIGHT
            painter.fillRect(QRect(x, y, CELL_WIDTH, CELL_HEIGHT), GRID_CLICK_OVERLAY_COLOR)
            painter.setPen(Qt.white)
            label = f"{'출발지' if i == 0 else '도착지'}\n({col},{row})"
            painter.drawText(QRect(x, y, CELL_WIDTH, CELL_HEIGHT), Qt.AlignCenter, label)

    def draw_robot_position(self, painter):
        if self.robot_current_grid_pos:
            col, row = self.robot_current_grid_pos
            x = col * CELL_WIDTH
            y = row * CELL_HEIGHT
            painter.fillRect(QRect(x, y, CELL_WIDTH, CELL_HEIGHT), HIGHLIGHT_COLOR_CURRENT)
            painter.setPen(Qt.white)
            painter.setFont(QFont("Arial", 10))
            painter.drawText(QRect(x, y, CELL_WIDTH, CELL_HEIGHT), Qt.AlignCenter, "로봇 현재 위치")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            col = int(event.x() // CELL_WIDTH)
            row = int(event.y() // CELL_HEIGHT)
            print(f"클릭한 셀: col={col}, row={row}")

            # 첫 클릭은 출발지, 두 번째 클릭은 목적지
            if not self.clicked_positions:
                self.clicked_positions.append((col, row))
                self.robot_current_grid_pos = (col, row)  # 로봇 현재 위치 설정
                self.robot_target_grid_pos = None  # 목적지 초기화
            elif len(self.clicked_positions) == 1:
                self.clicked_positions.append((col, row))
                self.robot_target_grid_pos = (col, row)  # 로봇 목적지 설정
            else:  # 2개 이상 클릭 시 첫 번째 클릭 제거 후 새 클릭 추가 (슬라이딩 윈도우)
                self.clicked_positions.pop(0)
                self.clicked_positions.append((col, row))
                self.robot_current_grid_pos = self.clicked_positions[0]
                self.robot_target_grid_pos = self.clicked_positions[1]

            if len(self.clicked_positions) == 2:
                start_grid, end_grid = self.clicked_positions
                msg = QMessageBox(self)
                msg.setWindowTitle("이동 안내")
                msg.setText(f"로봇을 {start_grid} 에서 {end_grid}로 이동시킵니다.")
                msg.exec_()

                # 로봇 이동 명령 실행 (Pilot.py의 함수 사용)
                self.move_robot_to_target(start_grid, end_grid)

            self.update()  # 화면 업데이트

    def move_robot_to_target(self, start_grid, end_grid):
        """
        Pilot.py의 함수들을 사용하여 로봇을 출발지에서 목적지로 이동시킵니다.
        여기서는 간단한 직선 이동을 가정합니다. 실제 경로는 더 복잡할 수 있습니다.
        """
        start_col, start_row = start_grid
        end_col, end_row = end_grid

        # 실제 로봇 이동을 위한 거리 계산 (예시: 픽셀 단위 또는 그리드 셀 단위)
        # 픽셀 좌표로 변환 (셀의 중앙을 기준으로 할 수 있음)
        start_x = start_col * CELL_WIDTH + CELL_WIDTH / 2
        start_y = start_row * CELL_HEIGHT + CELL_HEIGHT / 2
        end_x = end_col * CELL_WIDTH + CELL_WIDTH / 2
        end_y = end_row * CELL_HEIGHT + CELL_HEIGHT / 2

        # x, y 방향으로의 거리 차이
        dx = end_x - start_x
        dy = end_y - start_y

        # 유클리드 거리 계산
        distance_pixels = math.sqrt(dx ** 2 + dy ** 2)
        # 실제 로봇의 'move' 함수는 'cm' 또는 'mm' 단위를 사용할 수 있으므로,
        # 픽셀 거리를 실제 거리로 변환하는 스케일링 필요 (예: 1픽셀 = 0.1mm)
        # distance_cm = distance_pixels * (픽셀당 실제 거리 비율)

        # 각도 계산 (로봇의 방향을 맞추기 위해 필요할 수 있음)
        # math.atan2(dy, dx)는 라디안 단위의 각도를 반환합니다.
        # 로봇 시스템에 따라 각도 체계가 다를 수 있습니다 (0도 = 정면, 시계방향 등)
        angle_rad = math.atan2(dy, dx)
        angle_deg = math.degrees(angle_rad)

        print(f"로봇 이동 시작: {start_grid} -> {end_grid}")
        print(f"픽셀 거리: {distance_pixels:.2f}, 각도: {angle_deg:.2f}도")

        # Pilot.py의 setSpeed 함수 호출
        # 속도는 적절한 값으로 설정 (예: 100)
        self.robot_driver.setSpeed(100)
        print("로봇 속도 설정 (Pilot.py의 setSpeed 호출)")

        # Pilot.py의 move 함수 호출 (가정)
        # Pilot.py의 Driver 클래스 `move` 함수 시그니처에 따라 인자를 조정해야 합니다.
        # 예: move(distance, direction=0, angle=0) 또는 move(x_dist, y_dist) 등
        # 여기서는 단순히 계산된 픽셀 거리를 넘겨주고, 방향은 각도로 조정한다고 가정합니다.
        # 실제 로봇이 X, Y를 직접 움직이는 함수가 없다면 여러 번의 'forward'와 'turn' 조합이 필요합니다.

        # 간단하게 전체 이동 거리를 한 번에 이동
        # Pilot.py의 Driver.move 함수가 (거리, 방향) 또는 (거리, 각도) 형태라고 가정
        # (예시: Driver.move(거리_cm, 각도_deg))
        # 정확한 함수 시그니처를 확인하세요.
        try:
            # Pilot.py Driver 클래스의 move 함수가 (거리, 방향(라디안), 각도(도))를 받을 수 있다고 가정
            self.robot_driver.move(distance_pixels, direction=angle_rad, angle=angle_deg)
            print(f"로봇 이동 명령 실행 (Pilot.py의 move 호출): 거리={distance_pixels:.2f} (픽셀), 각도={angle_deg:.2f} (도)")
            self.robot_driver.stop()  # 이동 후 정지
            print("로봇 정지 (Pilot.py의 stop 호출)")

            # 이동 완료 후 로봇의 현재 위치를 목적지로 업데이트
            self.robot_current_grid_pos = end_grid
            self.update()  # 로봇 위치 업데이트 반영
            QMessageBox.information(self, "이동 완료", f"로봇이 {end_grid}에 도착했습니다.")

        except AttributeError:
            print("Pilot.py의 Driver 클래스에 'move' 또는 'setSpeed' 함수가 없습니다.")
            print("더미 함수를 사용합니다. 실제 로봇 제어는 이루어지지 않습니다.")
            self.robot_driver.setSpeed(100)  # 더미 함수 호출
            self.robot_driver.move(distance_pixels, direction=angle_rad, angle=angle_deg)  # 더미 함수 호출
            self.robot_driver.stop()
            self.robot_current_grid_pos = end_grid
            self.update()
            QMessageBox.information(self, "이동 완료 (시뮬레이션)", f"로봇이 {end_grid}에 도착한 것으로 시뮬레이션 됩니다.")

        # 만약 Pilot.py에 forward 함수만 있다면, 여러 단계로 나눠서 이동 로직을 구현해야 합니다.
        # 예시:
        # self.robot_driver.setSpeed(100)
        # self.robot_driver.forward(distance_pixels) # 만약 forward가 거리 인자를 받으면
        # self.robot_driver.stop()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MapWidget()
    window.show()
    sys.exit(app.exec_())
