import sys
import os
import glob
from PyQt6.QtWidgets import QApplication, QWidget, QListView, QAbstractItemView, QHBoxLayout, QVBoxLayout, QGridLayout, QTableWidget, QHeaderView, QPushButton, QTableWidgetItem
from PyQt6.QtCore import QSize, Qt, QMimeData, QEvent
from PyQt6.QtGui import QStandardItemModel, QIcon, QStandardItem, QKeyEvent, QDrag, QPixmap, QPainter, QBrush, QPen
# from PyQt5.QtCore import Qt


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
        self.setFixedHeight(int(h*0.2))
        self.setFixedWidth(int(w*0.7))
        self.setViewMode(QListView.ViewMode.IconMode)

    def dropEvent(self, event):
        super().dropEvent(event)
        self.parent.listViewRight.model().removeRow(
            self.parent.listViewRight.currentIndex().row())


class Board(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(6, 18, parent)  # Set the number of rows and columns to 8
        self.parent = parent
        self.setAcceptDrops(True)
        self.setIconSize(QSize(250, 100))

        self.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.verticalHeader().setVisible(False)
        self.horizontalHeader().setVisible(False)
        self.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.setShowGrid(False)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.size = self.size()

        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        header.setDefaultSectionSize(int(w/18))

        header = self.verticalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        header.setDefaultSectionSize(int(h/12))

        # layout = QVBoxLayout(self.parent)
        # layout.addWidget(self)

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self.viewport())
        w, h = self.columnWidth(0), self.rowHeight(0)

        painter.setPen(QPen(Qt.GlobalColor.black, 1))
        for i in range(1, 18):
            painter.drawLine(i*w, 0, i*w, 6*h)
        for j in range(1, 8):
            painter.drawLine(0, j*h, 18*w, j*h)


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
        self.setFixedHeight(int(h*0.2))
        self.setFixedWidth(int(w*0.7))
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


class MyApp(QWidget):
    def __init__(self):
        super().__init__()

        self.showFullScreen()

        container = []
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.listViewLeft = ListView_Left(self)
        layout.addWidget(self.listViewLeft, 1,
                         alignment=Qt.AlignmentFlag.AlignHCenter)

        self.board = Board(self)
        layout.addWidget(self.board, 2)

        self.listViewRight = ListView_Right(self)
        layout.addWidget(self.listViewRight, 3,
                         alignment=Qt.AlignmentFlag.AlignHCenter)

        self.loadIcons(container=container)

        self.quit_button = QPushButton("Quit")
        self.quit_button.setFixedWidth(200)
        self.quit_button.clicked.connect(self.close)
        layout.addWidget(self.quit_button, 3)

    def loadIcons(self, container):
        icon_folder = os.path.join(os.getcwd(), 'images')
        for icon in glob.glob(os.path.join(icon_folder, '*.png')):
            item = QStandardItem()
            item.setIcon(QIcon(icon))
            container.append(item)

            self.listViewLeft.m_model.appendRow(item)


if __name__ == '__main__':
    # don't auto scale when drag app to a different monitor.
    # QGuiApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    app = QApplication(sys.argv)
    app.setStyleSheet('''
        QWidget {
            font-size: 17px;
        }
    ''')
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
