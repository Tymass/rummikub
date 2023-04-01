from PyQt5.QtCore import QPointF, QRectF

# przykładowe granice prostokąta
rect = QRectF(10, 10, 50, 50)

# współrzędne wierzchołka górnego lewego narożnika
tl = rect.topLeft()
print("Top left corner:", tl.x(), tl.y())

# współrzędne wierzchołka górnego prawego narożnika
tr = rect.topRight()
print("Top right corner:", tr.x(), tr.y())

# współrzędne wierzchołka dolnego lewego narożnika
bl = rect.bottomLeft()
print("Bottom left corner:", bl.x(), bl.y())

# współrzędne wierzchołka dolnego prawego narożnika
br = rect.bottomRight()
print("Bottom right corner:", br.x(), br.y())
