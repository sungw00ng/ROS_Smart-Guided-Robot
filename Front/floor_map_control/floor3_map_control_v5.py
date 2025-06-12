import sys
import heapq
import math
import os
import random
import re

from PySide2.QtWidgets import QApplication, QWidget, QMessageBox, QInputDialog
from PySide2.QtGui import QPainter, QColor, QPen, QFont, QBrush
from PySide2.QtCore import Qt, QRect, QTimer, QPoint, QUrl, Slot, Signal

# PySide2.QtMultimedia 대신 pygame.mixer 사용
try:
    import pygame

    pygame.init()
    pygame.mixer.init()
except ImportError:
    print("[MapWidget 오류] pygame이 설치되지 않았습니다. 오디오 재생이 작동하지 않습니다.")
    print("[MapWidget 오류] pip install pygame 를 실행하여 설치해주세요.")
    pygame = None
except Exception as e:
    print(f"[MapWidget 오류] pygame 초기화 실패: {e}")
    pygame = None

# --- 설정값 ---
WINDOW_WIDTH = 1500  # 맵 위젯의 고정된 너비에 맞춤
WINDOW_HEIGHT = 1080  # 맵 위젯의 고정된 높이에 맞춤
GRID_ROWS = 40
GRID_COLS = 60
CELL_WIDTH = WINDOW_WIDTH / GRID_COLS
CELL_HEIGHT = WINDOW_HEIGHT / GRID_ROWS

FLOOR_COLOR = QColor("#222222")
WALL_COLOR = QColor("#555555")
HALLWAY_COLOR = QColor("#eeeeee")
ROOM_COLOR = QColor("#dddddd")

DOOR_OPEN_COLOR = QColor("#A0522D")
DOOR_CLOSED_COLOR = QColor("#8B4513")

HIGHLIGHT_COLOR_CURRENT = QColor(40, 167, 69, 150)
HIGHLIGHT_COLOR_DESTINATION = QColor(220, 53, 69, 150)
GRID_CLICK_OVERLAY_COLOR = QColor(100, 100, 255, 60)
GRID_BORDER_COLOR = QColor(200, 200, 200, 30)

MAP_AREAS = [
    {"type": "room", "name": "313", "rect": QRect(130, 85, 221, 185)},
    {"type": "room", "name": "312", "rect": QRect(357, 85, 90, 185)},
    {"type": "room", "name": "311", "rect": QRect(465, 135, 120, 135)},
    {"type": "room", "name": "310", "rect": QRect(595, 135, 120, 135)},
    {"type": "room", "name": "309", "rect": QRect(725, 135, 120, 135)},
    {"type": "room", "name": "308", "rect": QRect(855, 135, 120, 135)},
    {"type": "room", "name": "307", "rect": QRect(985, 135, 120, 135)},
    {"type": "room", "name": "306", "rect": QRect(1115, 135, 120, 135)},
    {"type": "room", "name": "305", "rect": QRect(1245, 135, 120, 135)},
    {"type": "room", "name": "304", "rect": QRect(1375, 135, 125, 135)},
    {"type": "room", "name": "301", "rect": QRect(33, 405, 195, 188)},
    {"type": "room", "name": "302", "rect": QRect(235, 405, 115, 188)},
    {"type": "room", "name": "314", "rect": QRect(840, 405, 150, 135)},
    {"type": "room", "name": "303", "rect": QRect(1000, 405, 240, 135)},
    {"type": "hallway", "name": "상단 주 복도", "rect": QRect(0, 297, 1500, 81)},
    {"type": "hallway", "name": "중앙 세로 복도", "rect": QRect(580, 374, 120, 140)},
    {"type": "wall", "name": "엘리베이터", "rect": QRect(449, 378, 131, 243)},
    {"type": "hallway", "name": "중앙 복도", "rect": QRect(580, 474, 120, 147)},

    {"type": "wall", "name": "", "rect": QRect(351, 85, 6, 185)},
    {"type": "wall", "name": "", "rect": QRect(447, 135, 18, 135)},
    {"type": "wall", "name": "", "rect": QRect(585, 135, 10, 135)},
    {"type": "wall", "name": "", "rect": QRect(715, 135, 10, 135)},
    {"type": "wall", "name": "", "rect": QRect(845, 135, 10, 135)},
    {"type": "wall", "name": "", "rect": QRect(975, 135, 10, 135)},
    {"type": "wall", "name": "", "rect": QRect(1105, 135, 10, 135)},
    {"type": "wall", "name": "", "rect": QRect(1235, 135, 10, 135)},
    {"type": "wall", "name": "", "rect": QRect(1365, 135, 10, 135)},

    {"type": "wall", "name": "", "rect": QRect(228, 405, 7, 188)},
    {"type": "wall", "name": "", "rect": QRect(990, 405, 10, 135)},

    {"type": "door", "name": "313호 문", "rect": QRect(300, 270, 30, 15), "initial_state": True},
    {"type": "door", "name": "312호 문", "rect": QRect(420, 280, 7, 15), "initial_state": True},
    {"type": "door", "name": "311호 문", "rect": QRect(480, 280, 7, 15), "initial_state": True},
    {"type": "door", "name": "310호 문", "rect": QRect(680, 280, 7, 7), "initial_state": True},
    {"type": "door", "name": "309호 문", "rect": QRect(740, 280, 7, 7), "initial_state": True},
    {"type": "door", "name": "308호 문", "rect": QRect(950, 280, 7, 7), "initial_state": True},
    {"type": "door", "name": "307호 문", "rect": QRect(1010, 280, 7, 7), "initial_state": True},
    {"type": "door", "name": "306호 문", "rect": QRect(1200, 280, 7, 7), "initial_state": True},
    {"type": "door", "name": "305호 문", "rect": QRect(1270, 280, 7, 7), "initial_state": True},
    {"type": "door", "name": "304호 문", "rect": QRect(1480, 280, 7, 7), "initial_state": True},

    {"type": "door", "name": "301호 문", "rect": QRect(170, 390, 30, 7), "initial_state": True},
    {"type": "door", "name": "302호 문", "rect": QRect(260, 390, 7, 7), "initial_state": True},

    {"type": "door", "name": "314호 문", "rect": QRect(870, 390, 7, 7), "initial_state": True},
    {"type": "door", "name": "303호 문", "rect": QRect(1030, 390, 30, 7), "initial_state": True},

    # --- 각 문 아래 "도착지점" 블록 추가 (기존 유지) ---
    {"type": "destination_point", "name": "도착지점 313", "room_number": 313,
     "rect": QRect(300, 270 + int(CELL_HEIGHT), int(CELL_WIDTH), int(CELL_HEIGHT))},
    {"type": "destination_point", "name": "도착지점 312", "room_number": 312,
     "rect": QRect(416, 270 + int(CELL_HEIGHT), int(CELL_WIDTH), int(CELL_HEIGHT))},
    {"type": "destination_point", "name": "도착지점 311", "room_number": 311,
     "rect": QRect(480, 270 + int(CELL_HEIGHT), int(CELL_WIDTH), int(CELL_HEIGHT))},
    {"type": "destination_point", "name": "도착지점 310", "room_number": 310,
     "rect": QRect(672, 270 + int(CELL_HEIGHT), int(CELL_WIDTH), int(CELL_HEIGHT))},
    {"type": "destination_point", "name": "도착지점 309", "room_number": 309,
     "rect": QRect(736, 270 + int(CELL_HEIGHT), int(CELL_WIDTH), int(CELL_HEIGHT))},
    {"type": "destination_point", "name": "도착지점 308", "room_number": 308,
     "rect": QRect(928, 270 + int(CELL_HEIGHT), int(CELL_WIDTH), int(CELL_HEIGHT))},
    {"type": "destination_point", "name": "도착지점 307", "room_number": 307,
     "rect": QRect(992, 270 + int(CELL_HEIGHT), int(CELL_WIDTH), int(CELL_HEIGHT))},
    {"type": "destination_point", "name": "도착지점 306", "room_number": 306,
     "rect": QRect(1184, 270 + int(CELL_HEIGHT), int(CELL_WIDTH), int(CELL_HEIGHT))},
    {"type": "destination_point", "name": "도착지점 305", "room_number": 305,
     "rect": QRect(1248, 270 + int(CELL_HEIGHT), int(CELL_WIDTH), int(CELL_HEIGHT))},
    {"type": "destination_point", "name": "도착지점 304", "room_number": 304,
     "rect": QRect(1472, 270 + int(CELL_HEIGHT), int(CELL_WIDTH), int(CELL_HEIGHT))},

    {"type": "destination_point", "name": "도착지점 301", "room_number": 301,
     "rect": QRect(168, 378 - int(CELL_HEIGHT), int(CELL_WIDTH), int(CELL_HEIGHT))},
    {"type": "destination_point", "name": "도착지점 302", "room_number": 302,
     "rect": QRect(256, 378 - int(CELL_HEIGHT), int(CELL_WIDTH), int(CELL_HEIGHT))},
    {"type": "destination_point", "name": "도착지점 314", "room_number": 314,
     "rect": QRect(864, 378 - int(CELL_HEIGHT), int(CELL_WIDTH), int(CELL_HEIGHT))},
    {"type": "destination_point", "name": "도착지점 303", "room_number": 303,
     "rect": QRect(1040, 378 - int(CELL_HEIGHT), int(CELL_WIDTH), int(CELL_HEIGHT))}
]


def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def a_star(grid, start, goal):
    open_set = [(0, start)]
    came_from = {}
    g_score = {start: 0}

    while open_set:
        _, current = heapq.heappop(open_set)
        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            return path

        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            neighbor = (current[0] + dx, current[1] + dy)
            if 0 <= neighbor[0] < GRID_COLS and 0 <= neighbor[1] < GRID_ROWS:
                if grid[neighbor[1]][neighbor[0]] == 1:
                    continue
                tentative_g = g_score[current] + 1
                if tentative_g < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f = tentative_g + heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f, neighbor))
    return None


def get_distance_to_obstacle(pos, direction_vec, grid, doors):
    col, row = pos
    dist = 0
    dx, dy = direction_vec

    while True:
        next_col, next_row = col + dx, row + dy

        if not (0 <= next_col < GRID_COLS and 0 <= next_row < GRID_ROWS):
            return dist

        if grid[next_row][next_col] == 1:
            return dist

        col, row = next_col, next_row
        dist += 1


class MapWidget(QWidget):
    # 로봇 이동 완료 시그널 추가 (어떤 방에 도착했는지 알리기 위해)
    robot_moved_to_destination = Signal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("A* Navigation with Map")
        self.setGeometry(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.clicked_positions = []
        self.obstacles = set()
        self.doors = {}
        self.defined_map_elements_coords = set()
        self.room_rects = {}
        self.destination_points_map = {}
        self.current_destination_room = None  # 현재 이동 중인 목적지 방 번호 저장

        self.path = []
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_position)
        self.path_index = 0

        # 로봇 시작 위치 (24, 21)로 고정
        self.current_pos = (24, 21)
        self.start_pos_set = True  # 시작 위치가 설정되었다고 명시

        self.initialize_grid_with_map_areas()

        self.is_playing_audio = False  # pygame 오디오 재생 상태 플래그
        self.audio_playback_timer = QTimer(self)  # 오디오 재생 완료 확인용 타이머
        self.audio_playback_timer.timeout.connect(self._check_audio_playback_finished)

    def _check_audio_playback_finished(self):
        """Checks if pygame audio playback has finished."""
        if pygame is not None and not pygame.mixer.music.get_busy():
            self.is_playing_audio = False
            self.audio_playback_timer.stop()  # 재생 완료 시 타이머 중지
            print("MP3 재생 완료 (MapWidget 내부 타이머).")
            # 필요하다면 여기서 오디오 재생 완료 후 추가 동작을 정의할 수 있습니다.

    def play_audio(self, audio_file_path):
        """Plays an MP3 file using pygame.mixer."""
        if pygame is None or not pygame.mixer.get_init():
            print("[MapWidget 오류] pygame 믹서가 초기화되지 않아 오디오 재생을 할 수 없습니다. pygame이 설치되어 있는지 확인해주세요.")
            # QMessageBox.warning(self, "오디오 재생 오류", "pygame 믹서가 초기화되지 않아 오디오 재생을 할 수 없습니다.") # 디버그 콘솔 처리
            self.is_playing_audio = False
            return

        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            selected_file = os.path.join(base_dir, audio_file_path)

            if not os.path.exists(selected_file):
                print(f"[MapWidget 오류] 오디오 파일을 찾을 수 없습니다: {selected_file}")
                # QMessageBox.warning(self, "파일 없음", f"오디오 파일을 찾을 수 없습니다: {selected_file}") # 디버그 콘솔 처리
                self.is_playing_audio = False
                return

            pygame.mixer.music.load(selected_file)
            pygame.mixer.music.play()
            self.is_playing_audio = True
            print(f"MP3 재생 시작: {selected_file}")

            # 오디오 재생 완료를 감지하기 위해 타이머 시작
            self.audio_playback_timer.start(100)  # 100ms마다 체크

        except Exception as e:
            print(f"[MapWidget 오류] MP3 파일 재생 시작에 실패했습니다: {e}")
            # QMessageBox.warning(self, "재생 오류", f"MP3 파일 재생에 실패했습니다: {e}") # 디버그 콘솔 처리
            self.is_playing_audio = False

    def initialize_grid_with_map_areas(self):
        self.grid = [[1 for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
        self.doors.clear()
        self.defined_map_elements_coords.clear()
        self.room_rects.clear()
        self.destination_points_map.clear()
        # self.start_pos_set = False # 고정 위치 사용으로 주석 처리

        for area in MAP_AREAS:
            x1 = int(area['rect'].left() // CELL_WIDTH)
            y1 = int(area['rect'].top() // CELL_HEIGHT)
            x2 = int(area['rect'].right() // CELL_WIDTH)
            y2 = int(area['rect'].bottom() // CELL_HEIGHT)

            x1 = max(0, x1)
            y1 = max(0, y1)
            x2 = min(GRID_COLS - 1, x2)
            y2 = min(GRID_ROWS - 1, y2)

            if area['type'] == 'room':
                self.room_rects[area['name']] = area['rect']
            elif area['type'] == 'destination_point':
                room_name = str(area['room_number'])  # room_number를 string으로 변환
                dest_col = int(area['rect'].center().x() // CELL_WIDTH)
                dest_row = int(area['rect'].center().y() // CELL_HEIGHT)
                self.destination_points_map[room_name] = (dest_col, dest_row)

            for row in range(y1, y2 + 1):
                for col in range(x1, x2 + 1):
                    coord = (col, row)
                    self.defined_map_elements_coords.add(coord)

                    if area['type'] in ['room', 'hallway', 'destination_point']:
                        self.grid[row][col] = 0
                    elif area['type'] == 'wall':
                        self.grid[row][col] = 1
                    elif area['type'] == 'door':
                        initial_state = area.get('initial_state', True)
                        self.doors[coord] = initial_state
                        self.grid[row][col] = 0 if initial_state else 1

        self.update_obstacles_from_grid()

    def paintEvent(self, event):
        painter = QPainter(self)
        self.draw_grid(painter)
        self.draw_areas(painter)
        self.draw_doors(painter)
        self.draw_user_added_obstacles(painter)
        self.draw_destination_points(painter)
        self.draw_clicks(painter)
        self.draw_path(painter)
        self.draw_robot(painter)

        if self.current_pos:
            current_col, current_row = self.current_pos
            painter.setPen(Qt.black)
            painter.setFont(QFont("Arial", 14, QFont.Bold))
            painter.drawText(20, 30, f"현재 로봇 위치: ({current_col}, {current_row})")

    def draw_grid(self, painter):
        painter.setPen(QPen(GRID_BORDER_COLOR))
        for row in range(GRID_ROWS):
            y = row * CELL_HEIGHT
            painter.drawLine(0, y, WINDOW_WIDTH, y)
        for col in range(GRID_COLS):
            x = col * CELL_WIDTH
            painter.drawLine(x, 0, x, WINDOW_HEIGHT)

    def draw_areas(self, painter):
        for area in MAP_AREAS:
            if area['type'] == 'room':
                color = ROOM_COLOR
            elif area['type'] == 'hallway':
                color = HALLWAY_COLOR
            elif area['type'] == 'wall':
                color = WALL_COLOR
            elif area['type'] in ['door', 'destination_point']:
                continue
            else:
                continue

            painter.fillRect(area['rect'], color)
            painter.setPen(Qt.black)
            painter.setFont(QFont("Arial", 12))
            # Room name은 room_number로 직접 가져오기 (MAP_AREAS 정의에 room_number 추가했으므로)
            name_to_display = str(area.get('room_number', area['name']))
            painter.drawText(area['rect'], Qt.AlignCenter, name_to_display)

    def draw_doors(self, painter):
        for area in MAP_AREAS:
            if area['type'] == 'door':
                x1 = int(area['rect'].left() // CELL_WIDTH)
                y1 = int(area['rect'].top() // CELL_HEIGHT)
                x2 = int(area['rect'].right() // CELL_WIDTH)
                y2 = int(area['rect'].bottom() // CELL_HEIGHT)

                # 문은 한 칸이 아닐 수 있으므로, 각 격자 셀을 확인
                for row_idx in range(y1, y2 + 1):
                    for col_idx in range(x1, x2 + 1):
                        coord = (col_idx, row_idx)
                        # QRect와 실제 Grid cell이 1:1 매칭되도록 처리
                        if coord in self.doors:  # 실제로 문이 있는 격자 셀만 그림
                            is_open = self.doors.get(coord, True)
                            color = DOOR_OPEN_COLOR if is_open else DOOR_CLOSED_COLOR
                            x = col_idx * CELL_WIDTH
                            y = row_idx * CELL_HEIGHT
                            painter.fillRect(QRect(x, y, CELL_WIDTH, CELL_HEIGHT), color)

                            if not is_open:
                                painter.setPen(QPen(Qt.red, 2))
                                painter.drawLine(x, y, x + CELL_WIDTH, y + CELL_HEIGHT)
                                painter.drawLine(x + CELL_WIDTH, y, x, y + CELL_HEIGHT)

    def draw_destination_points(self, painter):
        destination_color = QColor(124, 252, 0, 150)
        painter.setPen(Qt.NoPen)
        painter.setFont(QFont("Arial", 10))
        for area in MAP_AREAS:
            if area['type'] == 'destination_point':
                # 도착지점은 맵 요소의 center를 기준으로 정의된 단일 격자 셀입니다.
                # 이는 initialize_grid_with_map_areas에서 self.destination_points_map에 저장됩니다.
                # 여기서는 단순히 그 rect를 사용하여 시각적으로 표시합니다.
                x1 = int(area['rect'].left() // CELL_WIDTH)
                y1 = int(area['rect'].top() // CELL_HEIGHT)
                x2 = int(area['rect'].right() // CELL_WIDTH)
                y2 = int(area['rect'].bottom() // CELL_HEIGHT)

                for row in range(y1, y2 + 1):
                    for col in range(x1, x2 + 1):
                        x = col * CELL_WIDTH
                        y = row * CELL_HEIGHT
                        painter.fillRect(QRect(x, y, CELL_WIDTH, CELL_HEIGHT), destination_color)
                        painter.setPen(Qt.black)
                        # room_number를 직접 사용
                        painter.drawText(QRect(x, y, CELL_WIDTH, CELL_HEIGHT), Qt.AlignCenter, str(area['room_number']))

    def draw_user_added_obstacles(self, painter):
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                coord = (c, r)
                # 미리 정의된 맵 요소(벽, 방, 복도, 문)가 아닌데 그리드에서 장애물(1)인 경우
                if self.grid[r][c] == 1 and coord not in self.defined_map_elements_coords:
                    x = c * CELL_WIDTH
                    y = r * CELL_HEIGHT
                    painter.fillRect(QRect(x, y, CELL_WIDTH, CELL_HEIGHT), QColor("black"))

    def draw_clicks(self, painter):
        painter.setFont(QFont("Arial", 10))
        # 경로 탐색의 도착지점을 표시하는 경우 (voice command 또는 클릭 후)
        if len(self.clicked_positions) == 1:  # self.clicked_positions에 도착지점이 들어있을 때
            col, row = self.clicked_positions[0]
            x = col * CELL_WIDTH
            y = row * CELL_HEIGHT
            painter.fillRect(QRect(x, y, CELL_WIDTH, CELL_HEIGHT), HIGHLIGHT_COLOR_DESTINATION)  # 목적지 색상
            painter.setPen(Qt.white)
            label = f"도착지\n({col},{row})"
            painter.drawText(QRect(x, y, CELL_WIDTH, CELL_HEIGHT), Qt.AlignCenter, label)

    def draw_path(self, painter):
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(HIGHLIGHT_COLOR_CURRENT, 3))
        for col, row in self.path:
            x = col * CELL_WIDTH
            y = row * CELL_HEIGHT
            painter.drawRect(QRect(x, y, CELL_WIDTH, CELL_HEIGHT))

    def draw_robot(self, painter):
        if self.current_pos:
            x = self.current_pos[0] * CELL_WIDTH + CELL_WIDTH / 2
            y = self.current_pos[1] * CELL_HEIGHT + CELL_HEIGHT / 2
            radius = min(CELL_WIDTH, CELL_HEIGHT) / 3
            painter.setBrush(QBrush(QColor(0, 0, 255)))  # 파란색 공
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QPoint(int(x), int(y)), int(radius), int(radius))

    def mousePressEvent(self, event):
        if self.is_playing_audio:  # pygame 오디오 재생 상태 플래그 확인
            print("[MapWidget 경고] 음성 안내가 재생 중입니다. 잠시 기다려주세요.")
            # QMessageBox.information(self, "잠시만요", "음성 안내가 재생 중입니다. 잠시 기다려주세요.") # 디버그 콘솔 처리
            return

        col = int(event.x() // CELL_WIDTH)
        row = int(event.y() // CELL_HEIGHT)
        clicked_coord = (col, row)

        is_door_clicked = False
        for area in MAP_AREAS:
            if area['type'] == 'door':
                # 문 QRect와 클릭된 좌표의 겹침 확인
                # 정확한 격자 좌표로 변환하여 확인
                door_grid_x1 = int(area['rect'].left() // CELL_WIDTH)
                door_grid_y1 = int(area['rect'].top() // CELL_HEIGHT)
                door_grid_x2 = int(area['rect'].right() // CELL_WIDTH)
                door_grid_y2 = int(area['rect'].bottom() // CELL_HEIGHT)

                if door_grid_x1 <= col <= door_grid_x2 and door_grid_y1 <= row <= door_grid_y2:
                    # 해당 격자 좌표가 실제로 문에 해당하는지 다시 확인
                    if clicked_coord in self.doors:
                        is_door_clicked = True
                        break

        clicked_room_name = None
        for room_name, room_rect in self.room_rects.items():
            if room_rect.contains(event.pos()):
                clicked_room_name = room_name
                break

        if event.button() == Qt.RightButton:
            # 시작 위치가 고정되었으므로 위치 추정/설정 로직은 더 이상 필요 없음
            if clicked_coord in self.defined_map_elements_coords:
                print("[MapWidget 경고] 미리 정의된 맵 요소(벽/문/도착지점)는 토글할 수 없습니다.")
                # QMessageBox.warning(self, "경고", "미리 정의된 맵 요소(벽/문/도착지점)는 토글할 수 없습니다.") # 디버그 콘솔 처리
            else:  # 사용자가 정의한 장애물 추가/제거
                if self.grid[row][col] == 0:
                    self.grid[row][col] = 1
                else:
                    self.grid[row][col] = 0
                self.update_obstacles_from_grid()

        elif event.button() == Qt.LeftButton:
            if is_door_clicked:
                current_state = self.doors.get(clicked_coord, True)
                self.doors[clicked_coord] = not current_state

                # 문 상태에 따라 그리드 값 업데이트
                self.grid[row][col] = 0 if self.doors[clicked_coord] else 1
                self.update_obstacles_from_grid()  # 장애물 셋도 갱신

                if self.doors[clicked_coord]:
                    print(f"[MapWidget 정보] 문 ({col},{row})이 열렸습니다.")
                    # QMessageBox.information(self, "문 상태", f"문 ({col},{row})이 열렸습니다.") # 디버그 콘솔 처리
                else:
                    print(f"[MapWidget 정보] 문 ({col},{row})이 닫혔습니다.")
                    # QMessageBox.information(self, "문 상태", f"문 ({col},{row})이 닫혔습니다.") # 디버그 콘솔 처리
            elif clicked_room_name:
                # VoiceAssistant에서 넘어오는 room_number는 문자열이므로, 여기서도 문자열로 처리
                destination_coord = self.destination_points_map.get(clicked_room_name)
                if destination_coord:
                    self.clicked_positions = [destination_coord]
                    self.current_destination_room = clicked_room_name  # 목적지 방 번호 저장
                    self.start_pathfinding()
                else:
                    print(f"[MapWidget 오류] {clicked_room_name}에 대한 도착지점 정보를 찾을 수 없습니다.")
                    # QMessageBox.warning(self, "오류", f"{clicked_room_name}에 대한 도착지점 정보를 찾을 수 없습니다.") # 디버그 콘솔 처리

            else:  # 일반 그리드 셀 클릭 (출발지 또는 도착지)
                if self.grid[row][col] == 1:
                    print("[MapWidget 경고] 벽은 출발지/도착지로 선택할 수 없습니다.")
                    # QMessageBox.warning(self, "경고", "벽은 출발지/도착지로 선택할 수 없습니다.") # 디버그 콘솔 처리
                    return

                self.clicked_positions = [clicked_coord]
                # 일반 클릭을 통한 도착지 설정 시에는 room_number가 없으므로 None으로 설정
                self.current_destination_room = None
                self.start_pathfinding()

        self.update()

    def update_obstacles_from_grid(self):
        self.obstacles.clear()
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                if self.grid[r][c] == 1:
                    self.obstacles.add((c, r))

    def navigate_to_room_from_voice(self, room_number):
        print(f"[MapWidget] 음성 명령: {room_number}호로 이동 요청 받음 (VoiceAssistant로부터 직접 호출됨)")

        destination_coord = self.destination_points_map.get(room_number)
        if destination_coord:
            self.clicked_positions = [destination_coord]  # 도착지점 표시
            self.current_destination_room = room_number  # 목적지 방 번호 저장
            self.start_pathfinding()  # 경로 탐색 및 이동 시작
            self.update()
        else:
            print(f"[MapWidget 오류] {room_number}에 대한 도착지점 정보를 찾을 수 없습니다.")
            # QMessageBox.warning(self, "오류", f"{room_number}에 대한 도착지점 정보를 찾을 수 없습니다.") # 디버그 콘솔 처리

    def start_pathfinding(self):
        if not self.clicked_positions or len(self.clicked_positions) != 1:
            print("[MapWidget 오류] 도착지를 정확히 지정해야 합니다.")
            # QMessageBox.warning(self, "오류", "도착지를 정확히 지정해야 합니다.") # 디버그 콘솔 처리
            return

        start = self.current_pos
        end = self.clicked_positions[0]

        self.path = a_star(self.grid, start, end)
        if self.path:
            self.path_index = 0
            self.current_pos = self.path[0]  # 경로의 첫 지점으로 로봇 위치 설정
            self.timer.start(100)  # 100ms마다 이동
            self.update()
        else:
            print("[MapWidget 정보] 경로를 찾을 수 없습니다. 벽을 피하거나 경로가 가능한 곳을 선택하세요.")
            # QMessageBox.information(self, "안내", "경로를 찾을 수 없습니다. 벽을 피하거나 경로가 가능한 곳을 선택하세요.") # 디버그 콘솔 처리

    def update_position(self):
        self.path_index += 1
        if self.path_index < len(self.path):
            self.current_pos = self.path[self.path_index]
            self.update()
        else:
            self.timer.stop()
            # 경로가 끝났을 때만 clicked_positions를 초기화하여 도착지점을 계속 표시
            self.clicked_positions.clear()  # 경로 이동 완료 후 도착지점 표시를 초기화
            self.update()
            print(f"로봇이 목적지 {self.current_pos}에 도착했습니다.")

            # 로봇이 목적지에 완전히 도착했을 때 시그널 방출
            if self.current_destination_room:
                self.robot_moved_to_destination.emit(self.current_destination_room)
                self.current_destination_room = None  # 시그널 방출 후 초기화

    def closeEvent(self, event):
        # 애플리케이션 종료 시 pygame mixer 종료
        if pygame and pygame.mixer.get_init():
            pygame.mixer.quit()
        super().closeEvent(event)

'''
if __name__ == "__main__":
    app = QApplication(sys.argv)
    map_widget = MapWidget()
    map_widget.show()
    sys.exit(app.exec_())
'''
