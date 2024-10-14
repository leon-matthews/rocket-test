"""
Create PyQT5 GUI for running device tests and collecting resultant data.

CamelCase style should be used in this module to match the PyQT5 API style.
"""
from functools import partial
import logging
from pprint import pprint as pp
import time

from PyQt5.QtCore import QSize, Qt, QThread
from PyQt5.QtWidgets import (
    QApplication,
    QButtonGroup,
    QDialog,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressDialog,
    QPushButton,
    QStackedLayout,
    QVBoxLayout,
    QWidget,
)

from . import command_line, networking
from .data import DiscoveryData as Device, StatusData


logger = logging.getLogger(__name__)


def main(options: command_line.Options) -> int:
    """
    Start GUI.
    """
    logger.info("Starting GUI...")
    app = QApplication([])
    window = MainWindow(options)
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
    def __init__(self, options: command_line.Options):
        super().__init__()
        # Quick device search to start with
        self.options = options
        self.devices = self.findDevices(timeout=0.2)

        # Main window
        self.setWindowTitle("Leon's Rocket Lab Production Automation Test")
        self.setMinimumSize(QSize(600, 300))
        self.resize(QSize(900, 600))

        # Layout navigation and device details
        layout = QHBoxLayout()

        self.navigation = Navigation(self.devices)
        layout.addLayout(self.navigation)

        self.details = DeviceDetails()
        layout.addLayout(self.details, stretch=1)

        self.setLayout(layout)

    def findDevices(self, *, timeout: float) -> list[Device]:
        """
        Search for devices using multicast UDP networking.
        """
        multicast_ip, multicast_port = self.options.multicast
        devices = networking.discover_devices(
            multicast_ip, multicast_port, timeout=timeout,
        )
        return devices

    def selectDevice(self, device: Device):
        """
        User has selected the given device.

        Bring its DeviceDetails instance to the top of the DeviceDetailsStack.
        """
        logger.info(f"Show details for {device.model} {device.serial}")

    def updateDeviceList(self):
        """
        Update list of devices.

        Rather than start another background thread, we're going to pop
        up a modal dialog for just a couple of seconds until the operation
        concludes - we don't want users interacting with elements that are
        about to disapear after all!
        """
        logger.info("Updating device list")
        worker = DeviceListUpdater(self)
        worker.finished.connect(self.updateDeviceListFinished)
        worker.start()

    def updateDeviceListFinished(self):
        logger.info("updateDeviceListFinished")


class DeviceListUpdater(QThread):
    def __init__(self, parent):
        super().__init__(parent)

    def run(self):
        time.sleep(1)
        logger.debug("DeviceListUpdater.run()")
        self.devices = [1, 1, 2, 3, 5, 8, 13]


class Aggregates(QVBoxLayout):
    def __init__(self):
        super().__init__()
        self.addLabel()

    def addLabel(self):
        label = QLabel("Max: 3.22V\nMin:3.15V")
        label.setFrameStyle(QFrame.Panel | QFrame.Raised)
        self.addWidget(label)
        return label


class DeviceDetailsStack(QStackedLayout):
    pass


class DeviceDetails(QVBoxLayout):
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


class Navigation(QVBoxLayout):
    """
    Hold buttons to navigation between devices.
    """
    def __init__(self, devices: list[Device]):
        """
        Initialise navigation.

        Build one button for each given device.

        Args:
            devices:
                List of devices discovered on network.
        """
        super().__init__()
        self.setAlignment(Qt.AlignTop)
        self.devices = devices
        self._create_layout()

    def _create_layout(self):
        # Device buttons
        self.buttonGroup = QButtonGroup()
        self.buttonGroup.setExclusive(True)
        self.buttonGroup.buttonClicked.connect(self.deviceButtonClicked)
        self.updateButtonGroup()

        # Refresh button
        self.addStretch(1)
        refreshButton = QPushButton("Refresh Device List")
        refreshButton.clicked.connect(self.refreshButtonClicked)
        self.addWidget(refreshButton)

    def updateButtonGroup(self):
        """
        Add/remove buttons from navigation using new list of devices.

        If new list of devices matches old, nothing changes. Internal cache
        of devices is updated.
        """
        self.deviceButtons = {}
        for device in self.devices:
            button = DeviceButton(device)
            self.addWidget(button)
            self.addSpacing(10)
            self.buttonGroup.addButton(button)
            self.deviceButtons[device] = button

    def deviceButtonClicked(self):
        button = self.buttonGroup.checkedButton()
        device = button.device
        logger.debug("Device button [%s %s] pressed", device.model, device.serial)
        self.parentWidget().selectDevice(device)

    def refreshButtonClicked(self):
        logger.debug("Button [Refresh] pressed")
        self.parentWidget().updateDeviceList()


class DeviceButton(QPushButton):
    def __init__(self, device: Device):
        super().__init__()
        self.device = device
        self.setCheckable(True)
        self.setText(f"{self.device.model} {self.device.serial}")
        self.setStyleSheet("padding: 20px;")


class StartForm(QFormLayout):
    def __init__(self):
        super().__init__()
        self.addRow("Duration", QLineEdit())
        self.addRow("Rate", QLineEdit())
