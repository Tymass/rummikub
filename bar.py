import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeView, QFileSystemModel, QWidget, QVBoxLayout


class FileBrowser(QMainWindow):
    def __init__(self):
        super().__init__()

        # set window title and geometry
        self.setWindowTitle("File Browser")
        self.setGeometry(100, 100, 800, 600)

        # create a file system model and set its root path to /dupa
        self.model = QFileSystemModel()
        self.model.setRootPath("/dupa")

        # create a tree view and set the model
        self.tree = QTreeView()
        self.tree.setModel(self.model)

        # hide the root index (i.e., /dupa)
        self.tree.setRootIndex(self.model.index("/images"))

        # add the tree view to a layout and set the layout on a widget
        widget = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.tree)
        widget.setLayout(layout)

        # set the main widget
        self.setCentralWidget(widget)


if __name__ == '__main__':
    # create the Qt application
    app = QApplication(sys.argv)

    # create the main window
    window = FileBrowser()

    # show the window
    window.show()

    # start the event loop
    sys.exit(app.exec_())
