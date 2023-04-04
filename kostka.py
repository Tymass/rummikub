import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from draggable_pixmap import DraggablePixmap
from test3 import DragItem


class Kostka():
    def __init__(self, x: int = 0, y: int = 0, kolor: str = 'red', numer: str = '1') -> None:
        self.kolor = kolor
        self.numer = numer
        self.x = x
        self.y = y

        self.drag_item = DragItem(f'images/{numer}-{kolor}.png')
