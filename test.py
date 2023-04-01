from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, QApplication, QGraphicsItem
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import sys


app = QApplication(sys.argv)
# Tworzenie obiektów QGraphicsPixmapItem dla dwóch grafik


class DraggablePixmap(QGraphicsPixmapItem):
    def __init__(self, pixmap):
        super().__init__()
        self.setPixmap(pixmap)
        self.setFlag(QGraphicsPixmapItem.ItemIsMovable, True)

    def boundingRect(self):
        return self.pixmap().rect()

    def paint(self, painter, option, widget=None):
        painter.drawPixmap(self.boundingRect(), self.pixmap())

    def mouseMoveEvent(self, event):
        # Sprawdź, czy inny element na scenie jest przesuwany
        for item in self.scene().items():
            if item != self and item.flags() & QGraphicsPixmapItem.ItemIsMovable:
                # Jeśli inny element jest przesuwany, zablokuj przesuwanie tego elementu
                self.setFlag(QGraphicsPixmapItem.ItemIsMovable, False)
                break
        else:
            # Jeśli żaden inny element nie jest przesuwany, odblokuj przesuwanie tego elementu
            self.setFlag(QGraphicsPixmapItem.ItemIsMovable, True)
        super().mouseMoveEvent(event)


pixmap1 = QPixmap("images/1.png")
item1 = DraggablePixmap(pixmap1)

pixmap2 = QPixmap("images/2.png")
item2 = DraggablePixmap(pixmap2)


# Ustawienie pozycji obiektów na scenie
item1.setPos(0, 0)
item2.setPos(0, 100)

item1.setZValue(1)
item2.setZValue(0)

# Tworzenie obiektu QGraphicsScene i dodawanie do niego obiektów
scene = QGraphicsScene()
scene.addItem(item1)
scene.addItem(item2)

# Tworzenie obiektu QGraphicsView i ustawienie go na scenę
view = QGraphicsView(scene)

# Wyświetlenie widoku
view.show()
app.exec()
