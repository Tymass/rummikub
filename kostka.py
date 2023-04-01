import sys
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class Board(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.cell_size = 50
        self.num_cells = 10
        self.size = self.cell_size * self.num_cells

        self.setSceneRect(0, 0, self.size, self.size)

        self.grid = [[None for _ in range(self.num_cells)]
                     for _ in range(self.num_cells)]

        for i in range(self.num_cells):
            for j in range(self.num_cells):
                cell_rect = QRectF(i * self.cell_size, j *
                                   self.cell_size, self.cell_size, self.cell_size)
                self.addRect(cell_rect, QPen(Qt.gray), QBrush(Qt.white))

    def add_item(self, item):
        self.addItem(item)

        item_width = item.boundingRect().width()
        item_height = item.boundingRect().height()

        item.setPos(QPointF(self.cell_size * round(item.x() / self.cell_size),
                            self.cell_size * round(item.y() / self.cell_size)))

        for i in range(self.num_cells):
            for j in range(self.num_cells):
                cell_rect = QRectF(i * self.cell_size, j *
                                   self.cell_size, self.cell_size, self.cell_size)
                if item.collidesWithItem(self.itemAt(cell_rect.center(), QTransform())):
                    item.setPos(cell_rect.topLeft() + QPointF(self.cell_size / 2 - item_width / 2,
                                                              self.cell_size / 2 - item_height / 2))
                    return


class Item(QGraphicsRectItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    view = QGraphicsView()
    board = Board()
    view.setScene(board)

    item1 = Item(QRectF(0, 0, 2 * board.cell_size, 2 * board.cell_size))
    board.add_item(item1)

    item2 = Item(QRectF(0, 0, 3 * board.cell_size, 1 * board.cell_size))
    board.add_item(item2)

    view.show()
    sys.exit(app.exec_())
