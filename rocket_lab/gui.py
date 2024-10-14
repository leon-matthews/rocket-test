
import logging

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import (
    QApplication,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


from .command_line import Options
from .data import DiscoveryData


logger = logging.getLogger(__name__)


def main(options: Options) -> int:
    """
    Start GUI.
    """
    logger.info("Starting GUI...")
    app = QApplication([])
    devices = []
    window = MainWindow(devices)
    window.show()
    app.exec()
    return 0


class MainWindow(QWidget):
    """
    Applications main window.

    The GUI is organised into sub-objects as follows:

    There is one navigation bar containing buttons for switching between
    all of the detected devices.

    A details widget is created for every detected device. They are stacked on
    top of each other in a QStackedLayout. Buttons in the navigation bring
    them to the top of the stack.
    """
    def __init__(self, devices: list[DiscoveryData]):
        super().__init__()
        self.setWindowTitle("Leon's Rocket Lab Production Automation Test")
        self.layout()

    def layout(self):
        """
        Create window layout, creating subwidgets.
        """
        # Sensible sizes to start
        self.setMinimumSize(QSize(600, 300))
        self.resize(QSize(900, 600))

        # Navigation on left
        layout = QHBoxLayout()
        self.navigation = NavigationLayout()
        layout.addLayout(self.navigation)

        # Details on the right
        details = DetailLayout()
        layout.addLayout(details, stretch=1)

        self.setLayout(layout)


class Aggregates(QVBoxLayout):
    def __init__(self):
        super().__init__()
        self.addLabel()

    def addLabel(self):
        label = QLabel("Max: 3.22V\nMin:3.15V")
        label.setFrameStyle(QFrame.Panel | QFrame.Raised)
        self.addWidget(label)
        return label


class DetailLayout(QVBoxLayout):
    """
    Hold device and its test details.
    """
    def __init__(self):
        super().__init__()
        # Chart
        self.chart = self.addChart()

        # Aggregate data and device test form
        layout = QHBoxLayout()
        self.voltageAggregates = self.addAggregates(layout)
        self.currentAggregates = self.addAggregates(layout)
        self.startForm = self.addStartForm(layout)
        self.addLayout(layout)

        self.buttons = self.addStartStopButtons()

    def addAggregates(self, layout):
        aggregates = Aggregates()
        layout.addLayout(aggregates, 1)
        return aggregates

    def addChart(self):
        chart = QLabel("<b>CHART</b>")
        chart.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        chart.setScaledContents(True)
        chart.setFrameStyle(QFrame.Panel | QFrame.Raised)
        self.addWidget(chart)
        return chart

    def addStartForm(self, layout):
        form = StartForm()
        layout.addLayout(form, 1)
        return form

    def addStartStopButtons(self):
        layout = QHBoxLayout()

        stop = QPushButton("Stop")
        stop.setStyleSheet("padding: 20px;")
        layout.addWidget(stop)

        # Put start button in bottom right corner
        start = QPushButton("Start")
        start.setStyleSheet("padding: 20px;")
        layout.addWidget(start)

        self.addLayout(layout)


class DeviceButton(QPushButton):
    """
    Button to navigate to a device's details.
    """
    def __init__(self, model: str, serial: str):
        super().__init__()
        self.model = model
        self.serial = serial
        self.setText(f"Device {model}\n{serial}")
        self.setCheckable(True)


class NavigationLayout(QVBoxLayout):
    """
    Hold buttons to navigation between devices
    """
    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignTop)

        # Buttons
        self.addDeviceButton("M001", "SN0123456")
        self.addSpacing(10)
        self.addDeviceButton("M001", "SN0123457")
        self.addSpacing(10)
        self.addDeviceButton("M002", "SN024457")

        # Refresh
        self.addStretch(10)
        self.addWidget(QPushButton("Refresh Device List"))

    def addDeviceButton(self, model: str, serial: str) -> QPushButton:
        button = QPushButton(f"Device {model} {serial}")
        button.setStyleSheet("padding: 20px;")
        button.setCheckable(True)
        self.addWidget(button)


class StartForm(QFormLayout):
    def __init__(self):
        super().__init__()
        self.addRow("Duration", QLineEdit())
        self.addRow("Rate", QLineEdit())
