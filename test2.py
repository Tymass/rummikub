from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class PixmapItem(QGraphicsPixmapItem):
    def __init__(self, pixmap):
        super().__init__(pixmap)
        self.setFlag(QGraphicsItem.ItemIsMovable)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setCursor(Qt.ClosedHandCursor)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            mime_data = QMimeData()
            mime_data.setImageData(self.pixmap().toImage())
            drag = QDrag(event.widget())
            drag.setMimeData(mime_data)
            drag.setPixmap(self.pixmap())
            drag.setHotSpot(event.pos() - self.boundingRect().topLeft())
            drag.exec_(Qt.MoveAction)
            self.setCursor(Qt.OpenHandCursor)

    def mouseReleaseEvent(self, event):
        self.setCursor(Qt.OpenHandCursor)


class GraphicsView(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.setScene(QGraphicsScene())
        self.setAcceptDrops(True)
        pixmap = QPixmap("image.png")
        pixmap_item = PixmapItem(pixmap)
        self.scene().addItem(pixmap_item)
        self.setSceneRect(pixmap_item.boundingRect())

    def dragEnterEvent(self, event):
        if event.mimeData().hasImage():
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasImage():
            event.setDropAction(Qt.MoveAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasImage():
            position = event.pos()
            item = PixmapItem(QPixmap.fromImage(event.mimeData().imageData()))
            self.scene().addItem(item)
            item.setPos(position)
            event.setDropAction(Qt.MoveAction)
            event.accept()
        else:
            event.ignore()


if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    view = GraphicsView()
    view.show()
    sys.exit(app.exec_())
