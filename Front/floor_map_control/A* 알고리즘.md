| 구성 요소           | 설명                                   |
| --------------- | ------------------------------------ |
| **격자 지도**       | 60 x 40 셀로 구성된 맵을 보여줌. (각 셀은 정사각형)   |
| **시작지/도착지 선택**  | 마우스 왼쪽 클릭으로 두 지점을 설정                 |
| **A\* 알고리즘**    | 시작지 → 도착지까지 가장 효율적인 경로 탐색            |
| **경로 시각화**      | 찾은 경로를 초록색으로 하이라이팅                   |
| **로봇 이동 애니메이션** | 원형 공이 경로를 따라 한 칸씩 이동 (`QTimer` 사용)   |
| **장애물 설정**      | 마우스 오른쪽 클릭 시 해당 셀을 장애물로 지정 (검은색 사각형) |

## Code
```python
import sys
from PySide2.QtWidgets import QApplication, QWidget, QMessageBox
from PySide2.QtGui import QPainter, QColor, QPen, QFont, QBrush
from PySide2.QtCore import Qt, QRectF, QTimer
import heapq

WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080
GRID_ROWS = 40
GRID_COLS = 60
CELL_WIDTH = WINDOW_WIDTH / GRID_COLS
CELL_HEIGHT = WINDOW_HEIGHT / GRID_ROWS

class MapWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("A* Pathfinding with Animation")
        self.setGeometry(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.start_pos = None
        self.end_pos = None
        self.obstacles = set()
        self.path = []
        self.robot_index = 0

        # 로봇 이동용 타이머
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.move_robot)
        self.robot_position = None

    def paintEvent(self, event):
        painter = QPainter(self)
        self.draw_grid(painter)
        self.draw_obstacles(painter)
        self.draw_path(painter)
        self.draw_robot(painter)

    def draw_grid(self, painter):
        pen = QPen(QColor(200, 200, 200, 50))
        painter.setPen(pen)
        for row in range(GRID_ROWS):
            y = row * CELL_HEIGHT
            painter.drawLine(0, y, WINDOW_WIDTH, y)
        for col in range(GRID_COLS):
            x = col * CELL_WIDTH
            painter.drawLine(x, 0, x, WINDOW_HEIGHT)

    def draw_obstacles(self, painter):
        painter.setBrush(QBrush(QColor(50, 50, 50)))
        for col, row in self.obstacles:
            x, y = col * CELL_WIDTH, row * CELL_HEIGHT
            painter.drawRect(x, y, CELL_WIDTH, CELL_HEIGHT)

    def draw_path(self, painter):
        painter.setBrush(QBrush(QColor(0, 255, 0, 100)))
        for col, row in self.path:
            x, y = col * CELL_WIDTH, row * CELL_HEIGHT
            painter.drawRect(x, y, CELL_WIDTH, CELL_HEIGHT)

    def draw_robot(self, painter):
        if self.robot_position:
            col, row = self.robot_position
            x = col * CELL_WIDTH
            y = row * CELL_HEIGHT
            painter.setBrush(QBrush(QColor(0, 120, 255)))
            radius = min(CELL_WIDTH, CELL_HEIGHT) / 2
            center_x = x + CELL_WIDTH / 2
            center_y = y + CELL_HEIGHT / 2
            painter.drawEllipse(QRectF(center_x - radius, center_y - radius, radius * 2, radius * 2))

    def mousePressEvent(self, event):
        col = int(event.x() // CELL_WIDTH)
        row = int(event.y() // CELL_HEIGHT)
        cell = (col, row)

        if event.button() == Qt.RightButton:
            if cell not in self.obstacles:
                self.obstacles.add(cell)
            else:
                self.obstacles.remove(cell)
            self.update()
            return

        if not self.start_pos:
            self.start_pos = cell
        elif not self.end_pos:
            self.end_pos = cell
            self.find_path()
        else:
            self.start_pos = cell
            self.end_pos = None
            self.path = []
            self.robot_position = None
            self.timer.stop()

        self.update()

    def find_path(self):
        def heuristic(a, b):
            return abs(a[0] - b[0]) + abs(a[1] - b[1])

        def neighbors(node):
            x, y = node
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < GRID_COLS and 0 <= ny < GRID_ROWS and (nx, ny) not in self.obstacles:
                    yield (nx, ny)

        frontier = [(0, self.start_pos)]
        came_from = {}
        cost_so_far = {self.start_pos: 0}

        while frontier:
            _, current = heapq.heappop(frontier)

            if current == self.end_pos:
                break

            for next in neighbors(current):
                new_cost = cost_so_far[current] + 1
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + heuristic(self.end_pos, next)
                    heapq.heappush(frontier, (priority, next))
                    came_from[next] = current

        # 경로 추적
        if self.end_pos not in came_from:
            QMessageBox.warning(self, "경로 없음", "도착지까지 갈 수 없습니다.")
            return

        self.path = []
        current = self.end_pos
        while current != self.start_pos:
            self.path.append(current)
            current = came_from[current]
        self.path.reverse()

        self.robot_index = 0
        self.robot_position = self.start_pos
        self.timer.start(100)

    def move_robot(self):
        if self.robot_index >= len(self.path):
            self.timer.stop()
            return
        self.robot_position = self.path[self.robot_index]
        self.robot_index += 1
        self.update()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MapWidget()
    window.show()
    sys.exit(app.exec_())

```
