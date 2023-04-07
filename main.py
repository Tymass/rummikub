import sys
from PyQt6.QtWidgets import QApplication, QWidget, QListView, QAbstractItemView, QTableWidget, QHeaderView, QPushButton, QTableWidgetItem, QGraphicsScene, QGraphicsView, QMainWindow, QGraphicsProxyWidget, QMessageBox
from PyQt6.QtGui import QStandardItemModel, QIcon, QStandardItem, QKeyEvent, QPainter, QColor
import random
from PyQt6.QtCore import Qt, QTimer, QTime, QRectF, QSize
import resources_rc


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

# Tile class


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

# Main window class


class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('MyApp')
        self.showFullScreen()
        self.player_tiles_nr = 14
        self.container = []
        self.upper_bar_moves = []

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
        self.undo_button = QPushButton("Undo Move")

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
        self.undo_button.clicked.connect(self.undo_move)

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

    def undo_move(self):
        if self.board.last_move:
            row, col, source, selected_item = self.board.last_move

            self.board.takeItem(row, col)

            tile = Tile(number=selected_item.number, color=selected_item.color)
            tile.setIcon(selected_item.icon())
            tile.setData(selected_item.number, Qt.ItemDataRole.UserRole)

            if source == self.listViewLeft:
                self.listViewLeft.m_model.appendRow(tile)

            self.board.last_move = None

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
