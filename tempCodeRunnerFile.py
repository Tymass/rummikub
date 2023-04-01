from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class TimerWidget(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        # rysowanie tarczy timera
        pen = QPen()
        pen.setWidth(2)
        self.scene.addEllipse(-100, -100, 200, 200, pen)

        # rysowanie wskazówek
        self.minuteHand = self.scene.addLine(0, 0, 0, -70, pen)
        self.secondHand = self.scene.addLine(0, 0, 0, -80, pen)
        self.millisecondHand = self.scene.addLine(0, 0, 0, -90, pen)

        # ustawienie punktu obrotu wskazówek
        self.minuteHand.setTransformOriginPoint(0, 0)
        self.secondHand.setTransformOriginPoint(0, 0)
        self.millisecondHand.setTransformOriginPoint(0, 0)

        # ustawienie timera do odświeżania timera z dokładnością do 1ms
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(1)

        # ustawienie 30-sekundowego czasomierza
        self.timerCountdown = 30000  # milisekundy

    def update(self):
        self.timerCountdown -= 1

        # uaktualnienie pozycji wskazówek
        minuteAngle = (self.timerCountdown / 1000 / 60) * 360
        secondAngle = (self.timerCountdown / 1000 % 60) * 6
        millisecondAngle = (self.timerCountdown % 1000) * 0.36

        # obrot wskazówek
        self.minuteHand.setRotation(minuteAngle)
        self.secondHand.setRotation(secondAngle)
        self.millisecondHand.setRotation(millisecondAngle)

        # warunek stopu
        if self.timerCountdown == 0:
            self.timer.stop()


if __name__ == '__main__':
    app = QApplication([])
    timer = TimerWidget()
    timer.show()
    app.exec_()