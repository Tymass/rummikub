import sys
import random
from PyQt6.QtWidgets import QApplication, QWidget, QListView, QAbstractItemView, QTableWidget, QHeaderView, QPushButton, QTableWidgetItem, QGraphicsScene, QGraphicsView, QMainWindow, QGraphicsProxyWidget, QMessageBox, QVBoxLayout, QLabel, QLineEdit
from PyQt6.QtWidgets import QApplication, QWidget, QListView, QAbstractItemView, QTableWidget, QHeaderView, QPushButton, QTableWidgetItem, QGraphicsScene, QGraphicsView, QMainWindow, QGraphicsProxyWidget, QMessageBox
from PyQt6.QtGui import QStandardItemModel, QIcon, QStandardItem, QKeyEvent, QPainter, QColor, QDrag
from PyQt6.QtCore import Qt, QTimer, QTime, QRectF, QSize, QMimeData, QPoint
import xml.etree.ElementTree as ET
import sqlite3
import json
import resources_rc
import socket

# List 1 class


class ListView_Left(QListView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.m_model = QStandardItemModel(self)
        self.setModel(self.m_model)
        self.setAcceptDrops(True)
        self.setIconSize(QSize(100, 100))
        self.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        self.setResizeMode(QListView.ResizeMode.Fixed)
        self.setFixedHeight(130)
        self.setFixedWidth(1300)
        self.setViewMode(QListView.ViewMode.IconMode)

    def dropEvent(self, event):
        super().dropEvent(event)
        self.parent.listViewRight.model().removeRow(
            self.parent.listViewRight.currentIndex().row())

# Board class


class Board(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(6, 18, parent)  # Set the number of rows and columns
        self.parent = parent
        # self.setAcceptDrops(True)
        self.setIconSize(QSize(250, 200))

        self.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setVisible(False)
        self.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.setShowGrid(True)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        header.setDefaultSectionSize(int(w/18-1))

        header = self.verticalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        header.setDefaultSectionSize(int(h/12+5))

        self.last_move = None
        self.dragStartPosition = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            row = self.rowAt(int(event.position().y()))
            col = self.columnAt(int(event.position().x()))
            if self.item(row, col):
                self.dragStartPosition = event.position()

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if (not self.dragStartPosition) or ((event.buttons() & Qt.MouseButton.LeftButton) == 0):
            return

        if (event.position() - self.dragStartPosition).manhattanLength() < QApplication.startDragDistance():
            return

        row = self.rowAt(int(self.dragStartPosition.y()))
        col = self.columnAt(int(self.dragStartPosition.x()))

        drag_item = self.item(row, col)
        if not drag_item:
            return

        mime_data = QMimeData()
        mime_data.setText("dragging")

        drag = QDrag(self)
        drag.setMimeData(mime_data)
        drag.setPixmap(drag_item.icon().pixmap(self.iconSize()))
        drag.setHotSpot(QPoint(self.iconSize().width() //
                        2, self.iconSize().height() // 2))

        self.takeItem(row, col)
        self.dragStartPosition = None

        drop_action = drag.exec(Qt.DropAction.MoveAction)
        if drop_action == Qt.DropAction.IgnoreAction:
            self.setItem(row, col, drag_item)

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.dragStartPosition = None
        super().mouseReleaseEvent(event)

    def dropEvent(self, event):
        # Get the source widget (QListView)
        source = event.source()

        # Get the selected Tile object
        selected_item = source.model().itemFromIndex(source.currentIndex())
        tile = Tile(selected_item.number, selected_item.color)
        tile.setIcon(selected_item.icon())

        # Get the drop position and find the corresponding cell
        pos = event.position()  # Corrected here
        row = self.rowAt(int(pos.y()))
        col = self.columnAt(int(pos.x()))

        # If the cell is empty, add the Tile
        if not self.item(row, col):
            self.setItem(row, col, TileTableWidgetItem(tile))

        # Remove the selected item from the source (QListView)
        source.model().removeRow(source.currentIndex().row())

        self.last_move = (row, col, source, selected_item)
        # Call the superclass dropEvent to handle other events
        super().dropEvent(event)


# List 2 class
class ListView_Right(QListView):
    def __init__(self,  parent=None):
        super().__init__(parent)
        self.parent = parent
        self.m_model = QStandardItemModel(self)
        self.setModel(self.m_model)
        self.setAcceptDrops(True)
        self.setIconSize(QSize(100, 100))
        self.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        self.setResizeMode(QListView.ResizeMode.Fixed)
        self.setFixedHeight(130)
        self.setFixedWidth(1300)
        self.setViewMode(QListView.ViewMode.IconMode)
        self.installEventFilter(self)

    def eventFilter(self, source, event):
        if event.type() == QKeyEvent.Type.KeyPress and event.key() == Qt.Key.Key_Delete:
            if source == self:
                row_indx = self.currentIndex().row()
                self.model().remove().removeRow(row_indx)
        return super().eventFilter(source, event)

    def dropEvent(self, event):
        super().dropEvent(event)
        self.parent.listViewLeft.model().removeRow(
            self.parent.listViewLeft.currentIndex().row())

# Tile classes


class Tile(QStandardItem):
    def __init__(self, number, color):
        super().__init__()

        self.number = number
        self.color = color


class TileTableWidgetItem(QTableWidgetItem):
    def __init__(self, tile: Tile):
        super().__init__()
        self.tile = tile
        self.setIcon(self.tile.icon())

# Analog Timer class


class AnalogTimer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.timer = QTimer(self)
        self.time = QTime(0, 0, 30)
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(10)  # update every 10 ms

    def update_timer(self):
        self.time = self.time.addMSecs(-10)  # subtract 10 ms
        if self.time == QTime(0, 0, 0):
            self.timer.stop()  # stop the timer when it reaches 0
        self.update()

    def restart_timer(self):
        self.time = QTime(0, 0, 30)
        self.timer.start(10)

    def paintEvent(self, event):
        side = min(self.width(), self.height())
        target = QRectF(0, 0, side, side)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setViewport(target.toRect())
        painter.setWindow(-50, -50, 100, 100)

        self.draw_face(painter)
        self.draw_hands(painter)

    def draw_face(self, painter):
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(255, 255, 255))
        painter.drawEllipse(-48, -48, 96, 96)

    def draw_hands(self, painter):
        second = self.time.second() + self.time.msec() / 1000
        second_angle = 360 - (second / 30) * 360
        msec_angle = 360 - (self.time.msec() / 1000) * 360

        painter.setPen(Qt.GlobalColor.red)
        painter.save()
        painter.rotate(second_angle)
        painter.drawLine(0, 0, 24, 0)
        painter.restore()

        painter.setPen(Qt.GlobalColor.blue)
        painter.save()
        painter.rotate(msec_angle)
        painter.drawLine(0, 0, 0, -24)
        painter.restore()


class IpPortInput(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QVBoxLayout(self)

        self.ip_label = QLabel("IP Address:")
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("Enter your IP Address")
        self.ip_input.setText(self.get_local_ip())

        self.port_label = QLabel("Port Number:")
        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("Enter Port Number")

        self.apply_button = QPushButton("Apply")
        self.apply_button.clicked.connect(self.get_ip_port)

        self.layout.addWidget(self.ip_label)
        self.layout.addWidget(self.ip_input)
        self.layout.addWidget(self.port_label)
        self.layout.addWidget(self.port_input)
        self.layout.addWidget(self.apply_button)

    def get_ip_port(self):
        ip_address = self.ip_input.text()
        port_number = self.port_input.text()
        print(f'IP address: {ip_address}, \nPort number: {port_number}')
        return ip_address, port_number

    def get_local_ip(self):
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        return ip_address

# Main window class


class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('MyApp')
        self.showFullScreen()
        self.initialize_history_files()
        self.init_db()
        self.player_tiles_nr = 14
        self.container = []
        self.upper_bar_moves = []
        self.move_history = []

        # Create a QGraphicsScene
        self.scene = QGraphicsScene()

        # Create for all widgets
        self.listViewLeft = ListView_Left()
        self.board = Board()
        self.listViewRight = ListView_Right()
        self.quit_button = QPushButton("Quit")
        self.check_moves_button = QPushButton("Check Moves")
        self.analog_timer = AnalogTimer()
        self.restart_button = QPushButton("Restart")
        self.restart_button.setFixedWidth(200)
        self.load_piece_button = QPushButton("Add Piece")
        self.load_piece_button_up = QPushButton("Add Piece")
        self.undo_button = QPushButton("Save game state")
        self.save_json = QPushButton("Save history to Jason")
        self.ip_input = IpPortInput()

        # Create QGraphicsProxyWidget objects for all widgets
        # List 1
        self.listViewLeftProxy = QGraphicsProxyWidget()
        self.listViewLeftProxy.setWidget(self.listViewLeft)
        self.listViewLeftProxy.setPos(420, 750)
        # Board
        self.boardProxy = QGraphicsProxyWidget()
        self.boardProxy.setWidget(self.board)
        self.boardProxy.setPos(130, 150)
        self.boardProxy.resize(1900, 580)
        # List 2
        self.listViewRightProxy = QGraphicsProxyWidget()
        self.listViewRightProxy.setWidget(self.listViewRight)
        self.listViewRightProxy.setPos(420, -50)
        # Quit button
        self.quit_button_proxy = QGraphicsProxyWidget()
        self.quit_button_proxy.setWidget(self.quit_button)
        self.quit_button_proxy.setPos(150, 800)
        # Check moves button
        self.check_moves_button_proxy = QGraphicsProxyWidget()
        self.check_moves_button_proxy.setWidget(self.check_moves_button)
        self.check_moves_button_proxy.setPos(150, 750)
        # Analog timer
        self.analog_timer_proxy = QGraphicsProxyWidget()
        self.analog_timer_proxy.setWidget(self.analog_timer)
        self.analog_timer_proxy.setPos(150, -110)
        # Restart button
        self.restart_button_proxy = QGraphicsProxyWidget()
        self.restart_button_proxy.setWidget(self.restart_button)
        self.restart_button_proxy.setPos(150, 100)
        # Load piece buttons
        self.load_piece_button_proxy = QGraphicsProxyWidget()
        self.load_piece_button_proxy.setWidget(self.load_piece_button)
        self.load_piece_button_proxy.setPos(1800, 750)

        self.load_piece_button_up_proxy = QGraphicsProxyWidget()
        self.load_piece_button_up_proxy.setWidget(self.load_piece_button_up)
        self.load_piece_button_up_proxy.setPos(1800, 59)
        # Undo button
        self.undo_button_proxy = QGraphicsProxyWidget()
        self.undo_button_proxy.setWidget(self.undo_button)
        self.undo_button_proxy.setPos(1900, 59)
        # Save buttons
        self.save_jason_proxy = QGraphicsProxyWidget()
        self.save_jason_proxy.setWidget(self.save_json)
        self.save_jason_proxy.setPos(1700, 59)

        self.ip_input_proxy = QGraphicsProxyWidget()
        self.ip_input_proxy.setWidget(self.ip_input)
        self.ip_input_proxy.setPos(1800, -120)

        # Add the QGraphicsProxyWidget objects to the QGraphicsScene
        self.scene.addItem(self.listViewLeftProxy)
        self.scene.addItem(self.boardProxy)
        self.scene.addItem(self.listViewRightProxy)
        self.scene.addItem(self.quit_button_proxy)
        self.scene.addItem(self.check_moves_button_proxy)
        self.scene.addItem(self.analog_timer_proxy)
        self.scene.addItem(self.restart_button_proxy)
        self.scene.addItem(self.load_piece_button_proxy)
        self.scene.addItem(self.load_piece_button_up_proxy)
        self.scene.addItem(self.undo_button_proxy)
        self.scene.addItem(self.ip_input_proxy)
        # self.scene.addItem(self.save_jason_proxy)

        # Set the QGraphicsScene as the central widget of the main window
        self.view = QGraphicsView(self.scene)
        self.setCentralWidget(self.view)

        # Load the icons for the ListView widgets
        self.loadIcons()

        # Additional  settings
        self.quit_button.setFixedWidth(200)
        self.check_moves_button_proxy.setMinimumWidth(200)
        self.quit_button.clicked.connect(QApplication.closeAllWindows)
        self.check_moves_button.clicked.connect(self.check_board)
        self.analog_timer.setFixedSize(200, 200)
        self.restart_button.clicked.connect(self.analog_timer.restart_timer)
        self.load_piece_button.clicked.connect(self.load_piece)
        self.load_piece_button_up.clicked.connect(self.load_piece_up)
        self.undo_button.clicked.connect(self.save_board_state)
        # self.save_json.clicked.connect(self.save_board_state_to_json_file)

    def init_db(self):
        conn = sqlite3.connect("game_history.db")
        c = conn.cursor()

        c.execute('''
            CREATE TABLE IF NOT EXISTS game_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                state TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

    def initialize_history_files(self):
        # Clear the JSON history file
        with open("board_state_json.json", "w") as f:
            f.write("[]")

        # Clear the XML history file
        with open("board_state.xml", "w") as f:
            f.write("<boardHistory></boardHistory>")

    # Loading items
    def loadIcons(self):
        self.upper_bar = []
        self.lower_bar = []
        for i in range(1, 15):
            for color in ['red', 'blue', 'black', 'green']:
                icon_name = f":/images/{i}-{color}.png"
                icon = QIcon(icon_name)

                item = Tile(number=i, color=color)
                item.setIcon(icon)

                item.setData(i, Qt.ItemDataRole.UserRole)
                self.container.append(item)

        # Drawing tiles
        for i in range(0, self.player_tiles_nr):
            self.rnd_tile = random.randint(0, len(self.container)-1)
            self.upper_bar.append(self.container[self.rnd_tile])
            self.container.remove(self.container[self.rnd_tile])

            self.rnd_tile = random.randint(0, len(self.container)-1)
            self.lower_bar.append(self.container[self.rnd_tile])
            self.container.remove(self.container[self.rnd_tile])

        self.upper_bar.sort(key=lambda item: item.number)
        self.lower_bar.sort(key=lambda item: item.number)

        for item in self.upper_bar:
            self.listViewLeft.m_model.appendRow(item)

        for item in self.lower_bar:
            self.listViewRight.m_model.appendRow(item)

    def load_piece(self):
        if self.container:
            rnd_tile = random.randint(0, len(self.container)-1)
            self.listViewLeft.m_model.appendRow(self.container[rnd_tile])
            self.container.remove(self.container[rnd_tile])

    def load_piece_up(self):
        if self.container:
            rnd_tile = random.randint(0, len(self.container)-1)
            self.listViewRight.m_model.appendRow(self.container[rnd_tile])
            self.container.remove(self.container[rnd_tile])
            # self.move_history.append(self.save_board_state())
            # print(self.move_history)

    def save_board_state_to_json_file(self, state, file_name):
        # Read the existing history
        with open(file_name, 'r') as f:
            history = json.load(f)

        # Append the current state
        history.append(state)

        # Save the modified history
        with open(file_name, 'w') as f:
            json.dump(history, f, indent=4)

    def save_board_state_to_xml_file(self, state, file_name):
        # Read the existing history
        with open(file_name, 'r') as f:
            xml_content = f.read()

        # Parse the XML content
        root = ET.fromstring(xml_content)

        # Create a new <boardState> element
        board_state_element = ET.Element("boardState")

        # Append the current state as <row> elements
        for row in state:
            row_element = ET.SubElement(board_state_element, "row")
            for cell in row:
                if cell:
                    cell_element = ET.SubElement(row_element, "cell")
                    cell_element.set("number", str(cell[0]))
                    cell_element.set("color", cell[1])
                    #cell_element.set("icon", cell[2])
                else:
                    ET.SubElement(row_element, "emptyCell")

        # Append the <boardState> element to the root
        root.append(board_state_element)

        # Save the modified history
        with open(file_name, 'w') as f:
            f.write(ET.tostring(root, encoding="unicode"))

    def save_game_state(self, state):
        conn = sqlite3.connect("game_history.db")
        c = conn.cursor()

        c.execute("INSERT INTO game_history (state) VALUES (?)", (state,))
        conn.commit()
        conn.close()

    def save_board_state(self):
        state_copy = []
        for row in range(self.board.rowCount()):
            row_copy = []
            for col in range(self.board.columnCount()):
                item = self.board.item(row, col)
                if item:
                    row_copy.append(
                        (item.tile.number, item.tile.color))
                else:
                    row_copy.append(None)
            state_copy.append(row_copy)
        # print(state_copy)
        self.save_board_state_to_xml_file(state_copy, "board_state.xml")
        self.save_board_state_to_json_file(state_copy, "board_state_json.json")
        json_state = json.dumps(state_copy)
        self.save_game_state(json_state)

        return state_copy

    def get_tile_by_id(self, tile_id):
        for tile in self.tiles:
            if tile.id == tile_id:
                return tile
        return None

    def undo_move(self):
        if len(self.move_history) > 1:  # Ensure there's a previous state to revert to
            self.move_history.pop()  # Remove the current state
            previous_state = self.move_history[-1]

            for row, row_state in enumerate(previous_state):
                for col, cell_state in enumerate(row_state):
                    if cell_state:
                        piece_id, icon = cell_state
                        tile = self.get_tile_by_id(piece_id)
                        if tile:
                            item = TileTableWidgetItem(tile)
                            item.setIcon(icon)
                            self.board.setItem(row, col, item)
                    else:
                        self.board.takeItem(row, col)

    # Moves checker
    def check_board(self):
        def is_valid_group(group):
            if len(group) < 3:
                return False
            numbers = [tile.number for tile in group]
            colors = [tile.color for tile in group]
            return len(set(numbers)) == 1 and len(set(colors)) == len(group)

        def is_valid_run(run):
            if len(run) < 3:
                return False
            run.sort(key=lambda tile: tile.number)
            for i in range(len(run) - 1):
                if run[i].color != run[i + 1].color or run[i].number + 1 != run[i + 1].number:
                    return False
            return True

        tiles = []
        for row in range(self.board.rowCount()):
            for col in range(self.board.columnCount()):
                item = self.board.item(row, col)
                if item:
                    tile = item.tile
                    tiles.append((row, col, tile))

        groups_runs = []
        visited = set()

        for r, c, tile in tiles:
            if (r, c) in visited:
                continue

            same_number = [t for _, _, t in tiles if t.number == tile.number]
            same_color = [t for _, _, t in tiles if t.color == tile.color]

            if is_valid_group(same_number):
                groups_runs.append(same_number)
                visited.update((r, c) for r, c, t in tiles if t in same_number)
            if is_valid_run(same_color):
                groups_runs.append(same_color)
                visited.update((r, c) for r, c, t in tiles if t in same_color)

        all_valid = all(is_valid_group(group) or is_valid_run(group)
                        for group in groups_runs)
        remaining = [tile for r, c, tile in tiles if (r, c) not in visited]

        if all_valid and not remaining:
            QMessageBox.information(
                self, "Board Validation", "The board is valid according to Rummikub rules.")
        else:
            QMessageBox.warning(
                self, "Board Validation", "The board is not valid according to Rummikub rules.")


if __name__ == '__main__':

    app = QApplication(sys.argv)

    screen = app.primaryScreen()
    size = screen.size()
    w = size.width()
    h = size.height()
    myApp = MyApp()
    myApp.show()

    try:
        sys.exit(app.exec())
    except SystemExit:
        print('Closing Window...')
