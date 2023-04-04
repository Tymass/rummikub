import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QGridLayout, QFrame
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap


class ImageLabel(QLabel):
    def __init__(self):
        super().__init__()

        self.setAlignment(Qt.AlignCenter)
        self.setText('\n\n Drop Tile Here \n\n')
        # dash border
        self.setStyleSheet('''                      
            QLabel{
                border: 1px dashed #aaa
            }
        ''')
        self.setAcceptDrops(True)

    def setPixmap(self, image):
        super().setPixmap(image)


class AppDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(1600, 700)  # resize window
        self.setAcceptDrops(True)

        mainLayout = QGridLayout()

        # create a 8x10 grid of ImageLabel widgets
        self.photoViewers = []
        for row in range(8):
            for col in range(10):
                photoViewer = ImageLabel()
                mainLayout.addWidget(photoViewer, row, col)
                self.photoViewers.append(photoViewer)

        self.setLayout(mainLayout)
        '''
        # create the top row
        self.topRow = QFrame()
        self.topRow.setFrameShape(QFrame.StyledPanel)
        self.topRowLayout = QGridLayout(self.topRow)
        self.topRowLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.addWidget(self.topRow, 0, 0, 1, 10)

        # create the bottom row
        self.bottomRow = QFrame()
        self.bottomRow.setFrameShape(QFrame.StyledPanel)
        self.bottomRowLayout = QGridLayout(self.bottomRow)
        self.bottomRowLayout.setContentsMargins(0, 0, 0, 0)
        mainLayout.addWidget(self.bottomRow, 9, 0, 1, 10)
        
        # add images to the top row
        for i in range(5):
            imageLabel = QLabel()
            pixmap = QPixmap('images/1-blue.png')
            imageLabel.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio))
            self.topRowLayout.addWidget(imageLabel, 0, i)

        # allow dragging and dropping of images in the top row
        for child in self.topRow.children():
            if isinstance(child, QLabel):
                child.setAcceptDrops(True)

        # allow dragging and dropping of images in the bottom row
        for child in self.bottomRow.children():
            if isinstance(child, QLabel):
                child.setAcceptDrops(True)
        '''

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

            # check if dropped on the grid
            for widget in self.photoViewers:
                if widget.geometry().contains(event.pos()):
                    widget.setPixmap(QPixmap(file_path))
                    event.accept()
                    return

            # check if dropped on the top row
            for child in self.topRow.children():
                if isinstance(child, QLabel) and child.geometry().contains(event.pos()):
                    pixmap = QPixmap(file_path)
                    child.setPixmap(pixmap.scaled(
                        100, 100, Qt.KeepAspectRatio))
                    event.accept()
                    return

            # check if dropped on the bottom row
            for child in self.bottomRow.children():
                if isinstance(child, QLabel) and child.geometry().contains(event.pos()):
                    pixmap = QPixmap(file_path)
                    child.setPixmap(pixmap.scaled(
                        100, 100, Qt.KeepAspectRatio))
                    event.accept()
                    return


app = QApplication(sys.argv)

demo = AppDemo()
demo.show()

sys.exit(app.exec())
