import sys
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsItem, QGraphicsRectItem, QGraphicsEllipseItem, QApplication
from PyQt5.QtGui import QBrush, QPen
from PyQt5.QtCore import Qt
# from main import ClockWidget


app = QApplication(sys.argv)

# Defining a scene rect of 400x200, with it's origin at 0,0.
# If we don't set this on creation, we can set it later with .setSceneRect
scene = QGraphicsScene(0, 0, 400, 200)

# Draw a rectangle item, setting the dimensions.
rect = QGraphicsRectItem(0, 0, 200, 50)

# Set the origin (position) of the rectangle in the scene.
rect.setPos(50, 20)

# Define the brush (fill).
brush = QBrush(Qt.red)
rect.setBrush(brush)

# Define the pen (line)
pen = QPen(Qt.cyan)
pen.setWidth(10)
rect.setPen(pen)

ellipse = QGraphicsEllipseItem(0, 0, 100, 100)
ellipse.setPos(75, 30)

brush = QBrush(Qt.blue)
ellipse.setBrush(brush)

pen = QPen(Qt.green)
pen.setWidth(5)
ellipse.setPen(pen)

# Add the items to the scene. Items are stacked in the order they are added.
scene.addItem(ellipse)
scene.addItem(rect)


ellipse.setFlag(QGraphicsItem.ItemIsMovable)

view = QGraphicsView(scene)
view.show()
app.exec()
