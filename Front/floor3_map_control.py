from PySide2.QtWidgets import QApplication, QWidget, QMessageBox
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

class MapWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Map View")
        self.setGeometry(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
        self.clicked_positions = []  # 최대 2개 클릭 위치 저장

    def paintEvent(self, event):
        painter = QPainter(self)
        self.draw_grid(painter)
        self.draw_areas(painter)
        self.draw_clicks(painter)

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

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            col = int(event.x() // CELL_WIDTH)
            row = int(event.y() // CELL_HEIGHT)
            print(f"클릭한 셀: col={col}, row={row}")

            self.clicked_positions.append((col, row))
            if len(self.clicked_positions) > 2:
                self.clicked_positions.pop(0)

            if len(self.clicked_positions) == 2:
                start, end = self.clicked_positions
                msg = QMessageBox(self)
                msg.setWindowTitle("이동 안내")
                msg.setText(f"{start} 에서 {end}로 이동합니다.")
                msg.exec_()

            self.update()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MapWidget()
    window.show()
    sys.exit(app.exec_())
