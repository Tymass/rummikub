from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QVBoxLayout, QGridLayout
from PyQt5.QtCore import Qt

from kostka import Kostka
from test3 import DragWidget


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.drag = DragWidget(orientation=Qt.Orientation.Horizontal)
        for n, l in enumerate([1, 2, 8, 10]):
            kostka = Kostka(kolor='red', numer=l)
            kostka.drag_item.set_data(n)
            self.drag.add_item(kostka.drag_item)

        # Print out the changed order.
        self.drag.orderChanged.connect(print)

        container = QWidget()
        layout = QGridLayout()
        # layout.addStretch(1)
        layout.addWidget(self.drag)
        # layout.addStretch(1)
        container.setLayout(layout)

        self.setCentralWidget(container)


app = QApplication([])
w = MainWindow()
w.show()

app.exec_()
