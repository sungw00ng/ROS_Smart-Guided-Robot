# PySide2 기반 GUI + A* + 공간 지도
# v3.벽추가
# v4.문 추가, 각 방별 이벤트 처리(주황색)
# next for v5 : 문 주변에 map_301~314_information 이벤트 처리 예정
from PySide2.QtWidgets import QApplication, QWidget, QMessageBox
from PySide2.QtGui import QPainter, QColor, QPen, QFont, QBrush
from PySide2.QtCore import Qt, QRect, QTimer, QPoint
import sys
import heapq
import math

# --- 설정값 ---
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080
GRID_ROWS = 40
GRID_COLS = 60
CELL_WIDTH = WINDOW_WIDTH / GRID_COLS
CELL_HEIGHT = WINDOW_HEIGHT / GRID_ROWS

FLOOR_COLOR = QColor("#222222")
WALL_COLOR = QColor("#555555")  # 기존의 WALL_COLOR 유지
HALLWAY_COLOR = QColor("#eeeeee")
ROOM_COLOR = QColor("#dddddd")

DOOR_OPEN_COLOR = QColor("#A0522D")  # 열린 문 색상 (sienna)
DOOR_CLOSED_COLOR = QColor("#8B4513")  # 닫힌 문 색상 (saddlebrown)

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
    {"type": "wall", "name": "엘리베이터", "rect": QRect(465, 378, 110, 244)},  # 엘리베이터는 'wall' 타입으로 유지
    {"type": "hallway", "name": "중앙 복도", "rect": QRect(580, 474, 120, 147)},

    # --- 문 추가 예시 (3fmap.jpeg 이미지 기반 대략적인 위치) ---
    # 실제 문 위치에 맞춰 QRect를 조정해야 합니다.
    # width가 작고 height가 크면 세로 문, width가 크고 height가 작으면 가로 문입니다.
    # initial_state: True=열림 (통과 가능), False=닫힘 (통과 불가능)
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

    {"type": "door", "name": "301호 문", "rect": QRect(170, 390, 30, 7), "initial_state": True},  # 가로 문
    {"type": "door", "name": "302호 문", "rect": QRect(260, 390, 7, 7), "initial_state": True},  # 가로 문

    {"type": "door", "name": "314호 문", "rect": QRect(870, 390, 7, 7), "initial_state": True},
    {"type": "door", "name": "303호 문", "rect": QRect(1030, 390, 30, 7), "initial_state": True}
]


# --- A* 알고리즘 ---
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
                # 그리드 값이 1 (벽)이면 통과할 수 없음
                if grid[neighbor[1]][neighbor[0]] == 1:
                    continue
                tentative_g = g_score[current] + 1
                if tentative_g < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f = tentative_g + heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f, neighbor))
    return None


class MapWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("A* Navigation with Map")
        self.setGeometry(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.clicked_positions = []
        self.obstacles = set()  # A* 알고리즘이 사용할 모든 이동 불가 좌표 (벽, 닫힌 문, 사용자 추가 장애물)
        self.doors = {}  # {(col, row): True/False} 문의 개폐 상태
        self.defined_map_elements_coords = set()  # 미리 정의된 벽과 문 좌표 (우클릭 방지용)

        self.path = []
        self.grid = [[0 for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_position)
        self.path_index = 0
        self.current_pos = None

        self.initialize_grid_with_map_areas()  # 지도 영역을 기반으로 그리드 초기화

    def initialize_grid_with_map_areas(self):
        # 전체 그리드를 벽(1)으로 초기화 (기본적으로 모두 이동 불가능)
        self.grid = [[1 for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
        self.doors.clear()  # 문 상태 초기화
        self.defined_map_elements_coords.clear()  # 정의된 맵 요소 좌표 초기화

        # MAP_AREAS에 정의된 영역 처리
        for area in MAP_AREAS:
            x1 = int(area['rect'].left() // CELL_WIDTH)
            y1 = int(area['rect'].top() // CELL_HEIGHT)
            x2 = int(area['rect'].right() // CELL_WIDTH)
            y2 = int(area['rect'].bottom() // CELL_HEIGHT)

            # 그리드 범위를 벗어나지 않도록 클램프
            x1 = max(0, x1)
            y1 = max(0, y1)
            x2 = min(GRID_COLS - 1, x2)
            y2 = min(GRID_ROWS - 1, y2)

            for row in range(y1, y2 + 1):
                for col in range(x1, x2 + 1):
                    coord = (col, row)
                    self.defined_map_elements_coords.add(coord)  # 미리 정의된 요소로 등록

                    if area['type'] in ['room', 'hallway']:
                        self.grid[row][col] = 0  # 이동 가능 영역으로 설정
                    elif area['type'] == 'wall':
                        self.grid[row][col] = 1  # 벽으로 설정
                    elif area['type'] == 'door':
                        initial_state = area.get('initial_state', True)  # 기본값은 열림
                        self.doors[coord] = initial_state
                        self.grid[row][col] = 0 if initial_state else 1  # 초기 상태에 따라 그리드 설정

        # 초기화 완료 후 obstacles 집합 업데이트 (여기서는 미리 정의된 'wall'만 추가)
        self.update_obstacles_from_grid()

    def paintEvent(self, event):
        painter = QPainter(self)

        self.draw_grid(painter)
        # 중요: 그리기 순서
        # 1. 맵의 기본 영역 (방, 복도, 미리 정의된 벽)을 그립니다.
        self.draw_areas(painter)
        # 2. 문을 그립니다 (맵 영역 위에).
        self.draw_doors(painter)
        # 3. obstacles에 있는 사용자 추가 벽 (grid 값이 1이면서 미리 정의된 요소가 아닌 것)을 그립니다.
        self.draw_user_added_obstacles(painter)

        self.draw_clicks(painter)
        self.draw_path(painter)
        self.draw_robot(painter)

    def draw_grid(self, painter):
        painter.setPen(QPen(GRID_BORDER_COLOR))
        for row in range(GRID_ROWS):
            y = row * CELL_HEIGHT
            painter.drawLine(0, y, WINDOW_WIDTH, y)
        for col in range(GRID_COLS):
            x = col * CELL_WIDTH
            painter.drawLine(x, 0, x, WINDOW_HEIGHT)

    def draw_areas(self, painter):
        # MAP_AREAS에 정의된 영역을 그림. 'wall' 타입은 WALL_COLOR로, 'room'/'hallway'는 해당 색상으로 그립니다.
        # 'door' 타입은 여기서 그리지 않고 draw_doors에서 그립니다.
        for area in MAP_AREAS:
            if area['type'] == 'room':
                color = ROOM_COLOR
            elif area['type'] == 'hallway':
                color = HALLWAY_COLOR
            elif area['type'] == 'wall':
                color = WALL_COLOR  # 엘리베이터를 이 색상으로 그립니다.
            elif area['type'] == 'door':  # 문은 여기서 그리지 않고 별도 함수로 그립니다.
                continue
            else:  # 알 수 없는 타입은 그리지 않음
                continue

            painter.fillRect(area['rect'], color)
            painter.setPen(Qt.black)
            painter.setFont(QFont("Arial", 12))
            painter.drawText(area['rect'], Qt.AlignCenter, area['name'])

    def draw_doors(self, painter):
        # 문을 그립니다.
        for area in MAP_AREAS:
            if area['type'] == 'door':
                x1 = int(area['rect'].left() // CELL_WIDTH)
                y1 = int(area['rect'].top() // CELL_HEIGHT)
                x2 = int(area['rect'].right() // CELL_WIDTH)
                y2 = int(area['rect'].bottom() // CELL_HEIGHT)

                for row in range(y1, y2 + 1):
                    for col in range(x1, x2 + 1):
                        coord = (col, row)
                        is_open = self.doors.get(coord, True)  # 딕셔너리에 없으면 기본 열림
                        color = DOOR_OPEN_COLOR if is_open else DOOR_CLOSED_COLOR
                        x = col * CELL_WIDTH
                        y = row * CELL_HEIGHT
                        painter.fillRect(QRect(x, y, CELL_WIDTH, CELL_HEIGHT), color)

                        # 닫힌 문에 X 표시
                        if not is_open:
                            painter.setPen(QPen(Qt.red, 2))
                            painter.drawLine(x, y, x + CELL_WIDTH, y + CELL_HEIGHT)
                            painter.drawLine(x + CELL_WIDTH, y, x, y + CELL_HEIGHT)

    def draw_user_added_obstacles(self, painter):
        # grid가 1이면서 미리 정의된 맵 요소(벽, 문)가 아닌 셀만 검은색으로 그립니다.
        # 즉, 사용자가 우클릭으로 추가한 벽만 그립니다.
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                coord = (c, r)
                if self.grid[r][c] == 1 and coord not in self.defined_map_elements_coords:
                    x = c * CELL_WIDTH
                    y = r * CELL_HEIGHT
                    painter.fillRect(QRect(x, y, CELL_WIDTH, CELL_HEIGHT), QColor("black"))

    def draw_clicks(self, painter):
        painter.setFont(QFont("Arial", 10))
        for i, (col, row) in enumerate(self.clicked_positions):
            x = col * CELL_WIDTH
            y = row * CELL_HEIGHT
            painter.fillRect(QRect(x, y, CELL_WIDTH, CELL_HEIGHT), GRID_CLICK_OVERLAY_COLOR)
            painter.setPen(Qt.white)
            label = f"{'출발지' if i == 0 else '도착지'}\n({col},{row})"
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
            painter.setBrush(QBrush(QColor(0, 0, 255)))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QPoint(int(x), int(y)), int(radius), int(radius))

    def mousePressEvent(self, event):
        col = int(event.x() // CELL_WIDTH)
        row = int(event.y() // CELL_HEIGHT)
        clicked_coord = (col, row)

        # 클릭된 좌표가 MAP_AREAS에 정의된 'door' 영역에 속하는지 확인
        is_door_clicked = False
        for area in MAP_AREAS:
            if area['type'] == 'door':
                x1 = int(area['rect'].left() // CELL_WIDTH)
                y1 = int(area['rect'].top() // CELL_HEIGHT)
                x2 = int(area['rect'].right() // CELL_WIDTH)
                y2 = int(area['rect'].bottom() // CELL_HEIGHT)
                if x1 <= col <= x2 and y1 <= row <= y2:
                    # 클릭된 셀이 해당 문의 일부인지 정확히 확인
                    # 문은 여러 셀을 차지할 수 있으므로, 해당 셀이 문 영역 안에 있으면 door 클릭으로 간주
                    if (col, row) in self.doors:  # self.doors에 실제로 등록된 문 셀인지 확인
                        is_door_clicked = True
                        break

        if event.button() == Qt.RightButton:
            # 미리 정의된 맵 요소 (벽 또는 문)는 우클릭으로 토글되지 않도록 합니다.
            if clicked_coord in self.defined_map_elements_coords:
                QMessageBox.warning(self, "경고", "미리 정의된 맵 요소(벽/문)는 토글할 수 없습니다.")
                return

            # 우클릭 시 특정 셀을 토글하여 장애물로 추가/제거
            if self.grid[row][col] == 0:  # 이동 가능한 곳을 벽으로
                self.grid[row][col] = 1
            else:  # 벽을 이동 가능한 곳으로
                self.grid[row][col] = 0

            # 그리드 상태가 변경되었으므로 obstacles 집합을 다시 구성
            self.update_obstacles_from_grid()  # 사용자 추가 벽 업데이트

        elif event.button() == Qt.LeftButton:
            if is_door_clicked:
                # 문을 클릭한 경우 개폐 상태 토글
                current_state = self.doors.get(clicked_coord, True)  # 기본값은 열림
                self.doors[clicked_coord] = not current_state  # 상태 반전

                # 그리드 값 업데이트: 문이 닫히면 벽(1), 열리면 이동 가능(0)
                self.grid[row][col] = 0 if self.doors[clicked_coord] else 1

                # 문 상태가 변경되었으므로 obstacles 집합을 다시 구성 (A* 알고리즘용)
                self.update_obstacles_from_grid()

                if self.doors[clicked_coord]:  # 열림으로 변경됨 (원래 닫혀있었음)
                    QMessageBox.information(self, "문 상태", f"문 ({col},{row})이 열렸습니다.")
                else:  # 닫힘으로 변경됨 (원래 열려있었음)
                    QMessageBox.information(self, "문 상태", f"문 ({col},{row})이 닫혔습니다.")

            else:
                # 문이 아닌 일반 셀을 클릭한 경우 경로 탐색 시작/도착점 설정
                # 클릭한 위치가 벽이면 경로 탐색 시작점으로 선택할 수 없도록 합니다.
                if self.grid[row][col] == 1:
                    QMessageBox.warning(self, "경고", "벽은 출발지/도착지로 선택할 수 없습니다.")
                    return

                self.clicked_positions.append(clicked_coord)
                if len(self.clicked_positions) > 2:
                    self.clicked_positions.pop(0)
                if len(self.clicked_positions) == 2:
                    self.start_pathfinding()

        self.update()  # 화면 업데이트

    def update_obstacles_from_grid(self):
        """
        A* 알고리즘이 사용할 `self.grid`의 '1' 값들을 기반으로 `self.obstacles` 집합을 다시 구축합니다.
        이는 미리 정의된 벽, 닫힌 문, 사용자 추가 벽 모두를 포함합니다.
        """
        self.obstacles.clear()  # 기존 obstacles 초기화
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                if self.grid[r][c] == 1:  # grid 값이 1인 모든 곳은 A* 알고리즘의 장애물
                    self.obstacles.add((c, r))

    def start_pathfinding(self):
        start, end = self.clicked_positions
        # A* 알고리즘에 현재 그리드 상태를 전달합니다.
        # self.grid는 이미 문 상태와 사용자 추가 벽을 반영하고 있습니다.
        self.path = a_star(self.grid, start, end)
        if self.path:
            self.path_index = 0
            self.current_pos = self.path[0]
            self.timer.start(100)
        else:
            QMessageBox.information(self, "안내", "경로를 찾을 수 없습니다. 벽을 피하거나 경로가 가능한 곳을 선택하세요.")

    def update_position(self):
        self.path_index += 1
        if self.path_index < len(self.path):
            self.current_pos = self.path[self.path_index]
            self.update()
        else:
            self.timer.stop()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MapWidget()
    window.show()
    sys.exit(app.exec_())
