#v2:실질 3층 맵에 A* 경로 탐색 적용
#v2:실질적인 출발지 목적지, 등을 연속적으로 정할 수 있다.
#벽을 뚫는 버그가 있으니, v3에 수정해야한다.
#v3에는 어느 특정 경로에 도착하면 이 장소가 어떤 장소인지 출력되도록 하자 (ex.navigation_309.py)

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
WALL_COLOR = QColor("#555555")
HALLWAY_COLOR = QColor("#eeeeee")
ROOM_COLOR = QColor("#dddddd")

HIGHLIGHT_COLOR_CURRENT = QColor(40, 167, 69, 150)
HIGHLIGHT_COLOR_DESTINATION = QColor(220, 53, 69, 150)
GRID_CLICK_OVERLAY_COLOR = QColor(100, 100, 255, 60)
GRID_BORDER_COLOR = QColor(200, 200, 200, 30)

MAP_AREAS = [
    {"type": "room", "name": "313", "rect": QRect(130, 80, 221, 190)},
    {"type": "room", "name": "312", "rect": QRect(357, 80, 100, 190)},
    {"type": "room", "name": "311", "rect": QRect(465, 130, 120, 140)},
    {"type": "room", "name": "310", "rect": QRect(595, 130, 120, 140)},
    {"type": "room", "name": "309", "rect": QRect(725, 130, 120, 140)},
    {"type": "room", "name": "308", "rect": QRect(855, 130, 120, 140)},
    {"type": "room", "name": "307", "rect": QRect(985, 130, 120, 140)},
    {"type": "room", "name": "306", "rect": QRect(1115, 130, 120, 140)},
    {"type": "room", "name": "305", "rect": QRect(1245, 130, 120, 140)},
    {"type": "room", "name": "304", "rect": QRect(1375, 130, 125, 140)},
    {"type": "room", "name": "301", "rect": QRect(30, 405, 200, 190)},
    {"type": "room", "name": "302", "rect": QRect(235, 405, 120, 190)},
    {"type": "room", "name": "314", "rect": QRect(840, 405, 150, 135)},
    {"type": "room", "name": "303", "rect": QRect(1000, 405, 240, 135)},
    {"type": "hallway", "name": "상단 주 복도", "rect": QRect(30, 297, 1470, 80)},
    {"type": "hallway", "name": "중앙 세로 복도", "rect": QRect(570, 360, 150, 140)},
    {"type": "hallway", "name": "엘리베이터", "rect": QRect(470, 374, 100, 220)},
    {"type": "hallway", "name": "중앙 복도", "rect": QRect(570, 474, 150, 120)},
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

        for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
            neighbor = (current[0]+dx, current[1]+dy)
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

class MapWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("A* Navigation with Map")
        self.setGeometry(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.clicked_positions = []
        self.obstacles = set()
        self.path = []
        self.grid = [[0 for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_position)
        self.path_index = 0
        self.current_pos = None

    def paintEvent(self, event):
        painter = QPainter(self)
        self.draw_grid(painter)
        self.draw_areas(painter)
        self.draw_obstacles(painter)
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

    def draw_obstacles(self, painter):
        for col, row in self.obstacles:
            x = col * CELL_WIDTH
            y = row * CELL_HEIGHT
            painter.fillRect(QRect(x, y, CELL_WIDTH, CELL_HEIGHT), QColor("black"))

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

        if event.button() == Qt.RightButton:
            self.obstacles.add((col, row))
            self.grid[row][col] = 1
        elif event.button() == Qt.LeftButton:
            self.clicked_positions.append((col, row))
            if len(self.clicked_positions) > 2:
                self.clicked_positions.pop(0)
            if len(self.clicked_positions) == 2:
                self.start_pathfinding()

        self.update()

    def start_pathfinding(self):
        start, end = self.clicked_positions
        self.path = a_star(self.grid, start, end)
        if self.path:
            self.path_index = 0
            self.current_pos = self.path[0]
            self.timer.start(100)
        else:
            QMessageBox.information(self, "안내", "경로를 찾을 수 없습니다.")

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
