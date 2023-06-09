import sys
import random
from PyQt6.QtWidgets import QApplication, QWidget, QListView, QAbstractItemView, QTableWidget, QHeaderView, QPushButton, QTableWidgetItem, QGraphicsScene, QGraphicsView, QMainWindow, QGraphicsProxyWidget, QMessageBox, QVBoxLayout, QLabel, QLineEdit, QHBoxLayout, QRadioButton
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

    def set_tile(self, tile, row: int, col: int):
        table_widget_item = QTableWidgetItem()
        table_widget_item.setIcon(tile.icon())
        table_widget_item.tile = tile  # Store the Tile object for future reference
        self.setItem(row, col, table_widget_item)


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


class Server:
    def __init__(self, host_ip, port):
        self.host_ip = host_ip
        self.port = port

    def Tcp_server_wait(port):
        global s2
        s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s2.bind(('', port))
        # s2.listen(numofclientwait)

    def Tcp_server_next():
        global s
        s = s2.accept()[0]

    def Tcp_Write(D):
        mes = str(D + '\r')
        s.send(mes.encode())
        return

    def Tcp_Read():
        a = ' '
        b = ''
        while a != '\r':
            a = s.recv(1).decode()
            b = b + a

        b_dict = eval(b)  # dictionary format
        with open("database/json_received.json", "w") as f:
            json.dump(b_dict, f)

    def Tcp_Close():
        s.close()
        return


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

        self.ip_address = self.ip_input.text()
        self.port_number = self.port_input.text()
        print(
            f'IP address: {self.ip_address}, \nPort number: {self.port_number}')
        return self.ip_address, self.port_number

    def get_local_ip(self):
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        return ip_address


class Lobby(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.vbox = QVBoxLayout()
        self.hbox = QHBoxLayout()

        self.ip_input = IpPortInput()
        self.ip_input.hide()

        self.button1 = QRadioButton("Single player")
        self.button1.toggled.connect(self.updateLabel)
        self.button1.toggled.connect(self.ip_input.hide)
        self.button2 = QRadioButton("1 vs 1")
        self.button2.toggled.connect(self.updateLabel)
        self.button2.toggled.connect(self.ip_input.show)
        self.button3 = QRadioButton("Player vs AI")
        self.button3.toggled.connect(self.updateLabel)
        self.button3.toggled.connect(self.ip_input.hide)
        self.label = QLabel('', self)
        self.info = QLabel("Choose game mode:")
        self.accept_button = QPushButton("Accept game mode")
        self.accept_button.clicked.connect(self.showMainWindow)

        self.hbox.addWidget(self.button1)
        self.hbox.addWidget(self.button2)
        self.hbox.addWidget(self.button3)

        self.vbox.addWidget(self.info)
        self.vbox.addLayout(self.hbox)
        self.vbox.addWidget(self.label)
        self.vbox.addWidget(self.accept_button)
        self.vbox.addWidget(self.ip_input)

        self.setLayout(self.vbox)

        self.setGeometry(500, 500, 500, 250)
        self.setWindowTitle("Lobby")
        self.show()

    def updateLabel(self, _):

        rbtn = self.sender()

        if rbtn.isChecked() == True:
            self.label.setText(rbtn.text())

    def showMainWindow(self):
        self.game_mode = 0

        if self.button1.isChecked():
            self.game_mode = 1
        elif self.button2.isChecked():
            self.game_mode = 2
        elif self.button3.isChecked():
            self.game_mode = 3
        else:
            QMessageBox.warning(self, "Error", "Choose game mode")
            return

        if not hasattr(self.ip_input, "port_number") and self.game_mode == "2":
            QMessageBox.warning(self, "Error", "Choose port number")
            return

        if self.game_mode == "2":
            ip_address = self.ip_input.ip_address
            port_number = self.ip_input.port_number
        else:
            ip_address = "0"
            port_number = "0"
        #print(ip_address, port_number)

        self.mainWindow = MyApp(self.game_mode, ip_address, port_number)
        self.mainWindow.showFullScreen()
        self.destroy()
        return self.game_mode

# Main window class


class MyApp(QMainWindow, Lobby):
    def __init__(self, game_mode, ip_address, port_number):
        super().__init__()
        self.setWindowTitle('MyApp')
        # self.showFullScreen()
        self.initialize_history_files()
        self.init_db()
        self.game_mode = game_mode
        self.player_tiles_nr = 14
        self.container = []
        self.upper_bar_moves = []
        self.move_history = []
        self.ip_address = ip_address
        self.port_number = port_number

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
        self.undo_button = QPushButton("Next Round")
        self.save_json = QPushButton("Save history to Jason")
        self.refresh_button = QPushButton("Refresh")

        if self.game_mode == "2":
            server = Server(port_number)

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

        self.refresh_button_proxy = QGraphicsProxyWidget()
        self.refresh_button_proxy.setWidget(self.refresh_button)
        self.refresh_button_proxy.setPos(1900, 750)

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
        self.scene.addItem(self.refresh_button_proxy)

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
        # ------------------------------------------------------------------------------------
        self.undo_button.clicked.connect(server.Tcp_server_wait)
        self.undo_button.clicked.connect(server.Tcp_server_next)
        self.undo_button.clicked.connect(self.save_board_state)
        self.undo_button.clicked.connect(self.analog_timer.restart_timer)
        self.refresh_button.clicked.connect(self.load_board)
        self.refresh_button.clicked.connect(self.analog_timer.restart_timer)

    def init_db(self):
        conn = sqlite3.connect("database/game_history.db")
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
        with open("database/game_config_json.json", "w") as f:
            f.write("[]")

        with open("database/board_state_json.json", "w") as f:
            f.write("")

        # Clear the XML history file
        with open("database/board_state.xml", "w") as f:
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
        # Convert the state to a format suitable for JSON serialization
        json_state = {"board": []}

        for row_idx, row in enumerate(state):
            for col_idx, cell in enumerate(row):
                cell_name = f"cell_{row_idx}_{col_idx}"
                if cell:
                    json_state["board"].append({
                        cell_name: {
                            "empty": False,
                            "number": cell[0],
                            "color": cell[1]
                        }
                    })
                else:
                    json_state["board"].append({cell_name: {"empty": True}})

        # Save the JSON state to a file
        with open(file_name, "w") as f:
            json.dump(json_state, f)

    def save_game_config_to_json_file(self, file_name):
        # Read the existing history

        history = []
        # Append the current state
        config = {
            "ip_address": str(self.ip_address),
            "port_nr": str(self.port_number),
            "game_mode": str(self.game_mode),
        }

        history.append(config)

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
                    # cell_element.set("icon", cell[2])
                else:
                    ET.SubElement(row_element, "emptyCell")

        # Append the <boardState> element to the root
        root.append(board_state_element)

        # Save the modified history
        with open(file_name, 'w') as f:
            f.write(ET.tostring(root, encoding="unicode"))

    def save_game_state(self, state):
        conn = sqlite3.connect("database/game_history.db")
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
                    row_copy.append((item.tile.number, item.tile.color))
                else:
                    row_copy.append(None)
            state_copy.append(row_copy)

        # print(state_copy)
        self.save_board_state_to_xml_file(
            state_copy, "database/board_state.xml")
        self.save_game_config_to_json_file("database/game_config_json.json")
        json_state = json.dumps(state_copy)
        self.save_game_state(json_state)
        self.save_board_state_to_json_file(
            state_copy, "database/board_state_json.json")

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

    def load_board(self):
        with open('database/json_received.json', 'r') as file:
            data = json.load(file)

        board_data = data['board']

        for cell_data in board_data:
            cell_key = list(cell_data.keys())[0]
            cell_info = cell_data[cell_key]

            if not cell_info['empty']:
                row, col = map(int, cell_key.split('_')[1:])
                number = cell_info['number']
                color = cell_info['color']
                icon_name = f":/images/{number}-{color}.png"
                icon = QIcon(icon_name)

                tile = Tile(number=number, color=color)
                tile.setIcon(icon)
                tile.setData(number, Qt.ItemDataRole.UserRole)

                # Update the board
                self.board.set_tile(tile, row, col)

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
    # myApp = MyApp()

    ex = Lobby()

    try:
        sys.exit(app.exec())
    except SystemExit:
        print('Closing Window...')
