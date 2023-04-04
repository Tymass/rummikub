from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *


class DraggablePixmap(QGraphicsPixmapItem):
    def __init__(self, pixmap):
        super().__init__(pixmap)

        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsFocusable, True)
        # self.setZValue(1)  # ustawienie poziomu z-order na 1

        self.setFocus()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.mousePressPos = event.pos()
            self.mouseIsPressed = True

    def mouseMoveEvent(self, event):
        if self.mouseIsPressed:
            offset = event.pos() - self.mousePressPos
            self.setPos(self.pos() + offset)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.mouseIsPressed = False
