#기존의 3F_map 수정
#세부적인 UI변경은 수정이 필요함.
#UI 용 좌표 지정 가능
from PySide2.QtWidgets import QApplication, QWidget
from PySide2.QtGui import QPainter, QColor, QPen, QFont
from PySide2.QtCore import Qt, QRect
import sys

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
        self.clicked_pos = None  # 클릭 위치 저장

    def paintEvent(self, event):
        painter = QPainter(self)
        self.draw_grid(painter)
        self.draw_areas(painter)
        if self.clicked_pos:
            self.draw_click(painter, *self.clicked_pos)

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

    def draw_click(self, painter, col, row):
        x = col * CELL_WIDTH
        y = row * CELL_HEIGHT
        painter.fillRect(QRect(x, y, CELL_WIDTH, CELL_HEIGHT), GRID_CLICK_OVERLAY_COLOR)
        painter.setPen(Qt.white)
        painter.setFont(QFont("Arial", 10))
        painter.drawText(QRect(x, y, CELL_WIDTH, CELL_HEIGHT), Qt.AlignCenter, f"({col}, {row})")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            col = int(event.x() // CELL_WIDTH)
            row = int(event.y() // CELL_HEIGHT)
            self.clicked_pos = (col, row)
            print(f"클릭한 셀: col={col}, row={row}")
            self.update()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MapWidget()
    window.show()
    sys.exit(app.exec_())
