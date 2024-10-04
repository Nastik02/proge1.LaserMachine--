import time
from math import sqrt

from PyQt6.QtCore import QTimer, QPoint, pyqtSignal, QObject, QSize, QPointF
from PyQt6.QtGui import QAction, QPainter, QStaticText, QKeyEvent
from PyQt6.QtWidgets import QWidget, QMainWindow, QLabel

from MarkerState import MarkerState


class PropertyEvent(QObject):
    changed = pyqtSignal()


class LaserMachine():
    def __init__(self):
        self.__timer = QTimer()
        self.__timer.timeout.connect(self.__processOneThing)
        self.__laserState = MarkerState.HIDE
        self.__position = QPointF(0.0, 0.0)
        self.__oldPosition = QPointF(0.0, 0.0)
        self.__destination = QPointF(0.0, 0.0)
        self.__isMoving = False
        self.__maxSpeed = 5.0
        self.__bounds = QSize(500, 500)
        self.laserStateChanged = PropertyEvent()
        self.positionChanged = PropertyEvent()
        self.oldPositionChanged = PropertyEvent()
        self.destinationChanged = PropertyEvent()
        self.isMovingChanged = PropertyEvent()
        self.__nextMoveTime = 0
        self.__error = 0

    def stateChange(self):
        state = self.getLaserState()
        if state == MarkerState.OFF or state == MarkerState.HIDE:
            self.__laserState = MarkerState.ON
        else:
            self.__laserState = MarkerState.OFF
        print(self.getLaserState())

    def __setIsMoving(self, value):
        self.__isMoving = value
        if (self.__isMoving):
            self.__timer.start()
        else:
            self.__timer.stop()
        self.isMovingChanged.changed.emit()

    def setSpeed(self, value):
        self.__maxSpeed = value

    def keyPressEvent(self, event: QKeyEvent):
        self.__maxSpeed = int(event.text())

    def getLaserState(self) -> MarkerState:
        return self.__laserState

    def getPosition(self) -> QPointF:
        return self.__position

    def getOldPosition(self) -> QPointF:
        return self.__oldPosition

    def getDestination(self) -> QPointF:
        return self.__destination

    def getMaxSpeed(self) -> float:
        return self.__maxSpeed

    def getBounds(self) -> QSize:
        return self.__bounds

    def setLaserState(self) -> MarkerState:
        self.__laserState = MarkerState((self.__laserState + 1) % 3)

    def setDestination(self, x, y):
        self.__destination = QPointF(x, y)
        self.destinationChanged.changed.emit()
        self.__setIsMoving(True)
        self.__setOldPosition(self.__position.x(), self.__position.y())

    def __setPosition(self, x, y):
        self.__position.setX(x)
        self.__position.setY(y)
        self.positionChanged.changed.emit()

    def __setOldPosition(self, x, y):
        self.__oldPosition.setX(x)
        self.__oldPosition.setY(y)
        self.oldPositionChanged.changed.emit()

    def __processOneThing(self):
        step_time = 1.0 / self.__maxSpeed
        # step_time = 0.2
        # deltaTime = time.time() - self.__lastTimerTick
        self.__lastTimerTick = time.time()
        # print(self.__position)
        if self.__isMoving and self.__lastTimerTick > self.__nextMoveTime:
            self.step = False
            self.__doMove()
            self.__nextMoveTime = self.__lastTimerTick + step_time

    def __doMove(self):
        xs = self.__oldPosition.x()
        ys = self.__oldPosition.y()

        x0 = self.__position.x()
        y0 = self.__position.y()

        x1 = self.__destination.x()
        y1 = self.__destination.y()

        dx = x1 - xs
        dy = y1 - ys


        xstep = dx / 100
        ystep = dy / 100


        if dx <= 1 and dy <= 1:
            self.__setPosition(x1, y1)
            if self.__position == self.__destination:
                self.__setIsMoving(False)

        elif self.__position == self.__destination:
            self.__setIsMoving(False)

        else:
            x = x0 + xstep
            y = y0 + ystep
            self.__setPosition(x, y)
            if self.__position == self.__destination:
                self.__setIsMoving(False)





