import sys
from PyQt6.QtCore import QSize, QRectF, QEvent, Qt, QPoint, QPointF
from PyQt6.QtGui import QImage, QColor, QPainter
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QSpinBox, QLabel
from PyQt6 import uic

from LaserMachine import LaserMachine
from QZoomStageView import QZoomStageView
from MarkerState import MarkerState


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.image = QImage()
        self.layout = QVBoxLayout()
        self.userIsResizing = False
        self.resize(800, 500)
        self.init_image(self.size())
        self.stageView = QZoomStageView()
        self.setWindowTitle("Virtual Laser")
        self.installEventFilter(self)
        self.__connectedMachine: LaserMachine = None
        self.stageView.signals.mouseStageClicked.connect(self.mouse_stage_clicked)
        self.button = QPushButton("ON/OFF", self.stageView)
        self.button.setGeometry(200, 0, 50, 50)
        self.button.clicked.connect(self.the_button_click)
        self.velobox = QSpinBox(self.stageView)
        self.velobox.setGeometry(700, 25, 50, 25)
        self.velobox.valueChanged.connect(self.the_velocity_change)
        self.velobox.setRange(1, 10000)
        self.velobox.setSingleStep(1)
        self.velobox.setValue(5)
        self.velolable = QLabel(self.stageView)
        self.velolable.setGeometry(700, 0, 50, 25)
        self.velolable.setText('Velocity')
        self.velolable.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.velolable.setStyleSheet("color: black; background-color: white")
        # self.layout.addWidget(button)
        # self.stageView.setLayout(self.layout)
        self.setCentralWidget(self.stageView)

    def the_button_click(self):
        self.__connectedMachine.stateChange()
        self.stageView.setMarkerState()
        print("pressed")

    def mouse_stage_clicked(self, wpos: QPointF):
        self.__connectedMachine.setDestination(wpos.x(), -wpos.y())
        self.stageView.setOldPosition(self.__connectedMachine.getOldPosition())

    def connectMachine(self, machine: LaserMachine):
        if self.__connectedMachine is not None:
            self.__connectedMachine.positionChanged.changed.disconnected(self.machine_position_changed)
        self.__connectedMachine = machine
        self.__connectedMachine.positionChanged.changed.connect(self.machine_position_changed)
        self.stageView.setStageLimits(machine.getBounds())

    def machine_position_changed(self):
        self.stageView.setCurrentPosition(self.__connectedMachine.getPosition())

    def eventFilter(self, object, event) -> bool:
        if event.type() == QEvent.Type.MouseButtonRelease and event.button() == Qt.MouseButton.LeftButton and self.userIsResizing:
            self.complete_resize()
        elif event.type() == QEvent.Type.NonClientAreaMouseButtonRelease and self.userIsResizing:
            self.complete_resize()
        return super().eventFilter(object, event)

    def resizeEvent(self, e) -> None:
        self.userIsResizing = True

    def complete_resize(self):
        self.userIsResizing = False
        self.init_image(self.size())
        self.update()

    def init_image(self, size: QSize):
        self.image = QImage(size.width(), size.height(), QImage.Format.Format_ARGB32)

    def the_velocity_change(self):
        if self.__connectedMachine is not None:
            self.__connectedMachine.setSpeed(self.velobox.value())


# def dest_changed():
#     print(f"destination changed to {machine.getDestination()}")

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    machine = LaserMachine()
    window.connectMachine(machine)
    # machine.destinationChanged.changed.connect(dest_changed)
    machine.setDestination(0, 0)
    sys.exit(app.exec())
