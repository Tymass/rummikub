import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QGridLayout
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QPixmap, QDrag
from PyQt5.QtCore import Qt, QMimeData, QUrl


import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QGridLayout
from PyQt5.QtCore import Qt, QMimeData, QUrl
from PyQt5.QtGui import QPixmap


class ImageLabel(QLabel):
    def __init__(self, row, column):
        super().__init__()

        self.setAlignment(Qt.AlignCenter)
        self.setText('\n\n Drop Image Here \n\n')
        self.setStyleSheet('''
            QLabel{
                border: 4px dashed #aaa
            }
        ''')
        self.row = row
        self.column = column

    def setPixmap(self, image):
        super().setPixmap(image)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            mime_data = QMimeData()
            mime_data.setUrls([QUrl.fromLocalFile(self.file_path)])

            drag = QPixmap(self.size())
            self.render(drag)

            drag_icon = QLabel(self)
            drag_icon.setPixmap(drag)
            drag_icon.move(0, 0)
            drag_icon.show()

            drag = drag_icon.grab()

            self.drag = drag_icon
            self.drag.setPixmap(drag)
            self.drag.setFixedSize(drag.size())
            self.drag.show()

            drag.exec_()


class AppDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(800, 800)
        self.setAcceptDrops(True)
        self.file_paths = [None] * 16

        mainLayout = QGridLayout()

        for row in range(4):
            for column in range(4):
                imageLabel = ImageLabel(row, column)
                mainLayout.addWidget(imageLabel, row, column)

        self.setLayout(mainLayout)

    def dragEnterEvent(self, event):
        if event.mimeData().hasImage:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasImage:
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasImage:
            event.setDropAction(Qt.CopyAction)
            file_path = event.mimeData().urls()[0].toLocalFile()
            imageLabel = self.childAt(event.pos())
            if imageLabel and isinstance(imageLabel, ImageLabel):
                imageLabel.file_path = file_path
                self.file_paths[imageLabel.row * 4 +
                                imageLabel.column] = file_path
                imageLabel.setPixmap(QPixmap(file_path))
            event.accept()
        else:
            event.ignore()


app = QApplication(sys.argv)
demo = AppDemo()
demo.show()
sys.exit(app.exec_())
