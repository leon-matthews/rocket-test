
from pprint import pprint as pp
from unittest import skip, TestCase

from rocket_lab.devices import Data, Device
from rocket_lab.networking import Datagram


DEVICE_DISCOVERY = Datagram(
    address='192.168.0.10',
    port=6062,
    message=b'ID;MODEL=M001;SERIAL=SN0123456;',
)


class DataTest(TestCase):
    def test_empty(self) -> None:
        """
        ValueError raised if message contains no data.
        """
        message = r"^Empty message$"
        with self.assertRaisesRegex(ValueError, message):
            Data.from_message(b"")

    def test_invalid(self) -> None:
        """
        ValueError raised if message malformed.
        """
        message = r"Could not parse MODEL=M001=M002 from b'ID;MODEL=M001=M002;SERIAL=SN0123456;'"
        with self.assertRaisesRegex(ValueError, message):
            Data.from_message(b"ID;MODEL=M001=M002;SERIAL=SN0123456;")

    def test_discovery(self) -> None:
        """
        Extract data from valid discovery message.
        """
        data = Data.from_message(b"ID;MODEL=M001;SERIAL=SN0123456;")
        expected = Data(
            name='ID',
            data={'MODEL': 'M001', 'SERIAL': 'SN0123456'},
        )
        self.assertEqual(data, expected)

    def test_discovery_outgoing(self) -> None:
        data = Data.from_message(b"ID;")
        expected = Data(
            name='ID',
            data={},
        )
        self.assertEqual(data, expected)

    def test_discovery_no_semicolon(self) -> None:
        data = Data.from_message(b"ID")
        expected = Data(
            name='ID',
            data={},
        )
        self.assertEqual(data, expected)

    def test_start(self) -> None:
        """
        Command device to start test.
        """
        message = b"TEST;CMD=START;DURATION=30;RATE=100;"
        data = Data.from_message(message)
        expected = Data(
            name='TEST',
            data={
                'CMD': 'START',
                'DURATION': '30',
                'RATE': '100',
            },
        )
        self.assertEqual(data, expected)

    def test_stop_test(self) -> None:
        """
        Command device to stop test.
        """
        message = b"TEST;CMD=STOP;"
        data = Data.from_message(message)
        expected = Data(
            name='TEST',
            data={
                'CMD': 'STOP',
            }
        )
        self.assertEqual(data, expected)

    def test_started(self) -> None:
        """
        Device reports that test started successfully.
        """
        message = b"TEST;RESULT=STARTED;"
        data = Data.from_message(message)
        expected = Data(
            name='TEST',
            data={
                'RESULT': 'STARTED',
            }
        )
        self.assertEqual(data, expected)

    def test_stopped(self) -> None:
        """
        Device reports that test stopped successfully.
        """
        message = b"TEST;RESULT=STOPPED;"
        data = Data.from_message(message)
        expected = Data(
            name='TEST',
            data={
                'RESULT': 'STOPPED',
            }
        )
        self.assertEqual(data, expected)

    @skip("More data needed")
    def test_already_running_error(self) -> None:
        """
        Device reports that test was already running.
        """
        message = b"TEST;RESULT=error;MSG=reason;"
        data = Data.from_message(message)
        expected = Data(
            name='TEST',
            data={
                'RESULT': 'STOPPED',
            }
        )
        self.assertEqual(data, expected)

    @skip("More data needed")
    def test_already_stopped_error(self) -> None:
        """
        Device reports that test was already stopped.
        """
        message = b"TEST;RESULT=error;MSG=reason;"
        data = Data.from_message(message)
        expected = Data(
            name='TEST',
            data={
                'RESULT': 'STOPPED',
            }
        )
        self.assertEqual(data, expected)

    def test_status(self) -> None:
        """
        Device sends status messages at some rate while test is running.
        """
        message = b"STATUS;TIME=100;MV=3.332;MA=45;"
        data = Data.from_message(message)
        expected = Data(
            name='STATUS',
            data={
                'TIME': '100',
                'MV': '3.332',
                'MA': '45',
            }
        )
        self.assertEqual(data, expected)

    def test_idle(self) -> None:
        """
        Device reports idle state after test stops for any reason.
        """
        message = b"STATUS;STATE=IDLE;"
        data = Data.from_message(message)
        expected = Data(
            name='STATUS',
            data={
                'STATE': 'IDLE',
            }
        )
        self.assertEqual(data, expected)


class DevicesTest(TestCase):
    def test_from_datagram(self) -> None:
        device = Device.from_datagram(DEVICE_DISCOVERY)
        expected = Device(
            address='192.168.0.10',
            port=6062,
            model='M001',
            serial='SN0123456',
        )
        self.assertEqual(device, expected)
