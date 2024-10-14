
from unittest import skip, TestCase

from rocket_lab.data import Datagram, DeviceMessage, DiscoveryData, StatusData


class DeviceMessageTest(TestCase):
    def test_empty(self) -> None:
        """
        ValueError raised if message contains no data.
        """
        message = r"^Empty message$"
        with self.assertRaisesRegex(ValueError, message):
            DeviceMessage.from_bytes(b"")

    def test_invalid(self) -> None:
        """
        ValueError raised if message malformed.
        """
        message = (
            r"Could not parse MODEL=M001=M002 from "
            r"b'ID;MODEL=M001=M002;SERIAL=SN0123456;'"
        )
        with self.assertRaisesRegex(ValueError, message):
            DeviceMessage.from_bytes(b"ID;MODEL=M001=M002;SERIAL=SN0123456;")

    def test_to_string(self) -> None:
        """
        Serialise data into unicode string.
        """
        data = DeviceMessage(
            name='STATUS',
            data={
                'TIME': '100',
                'MV': '3.332',
                'MA': '45',
            }
        )
        string = data.to_string()
        expected = "STATUS;TIME=100;MV=3.332;MA=45;"
        self.assertEqual(string, expected)

    def test_to_bytes(self) -> None:
        """
        Encode serialised data into binary string with `DEFAULT_ENCODING`.
        """
        data = DeviceMessage(
            name='STATUS',
            data={
                'TIME': '100',
                'MV': '3.332',
                'MA': '45',
            }
        )
        binary = data.to_bytes()
        expected = b"STATUS;TIME=100;MV=3.332;MA=45;"
        self.assertEqual(binary, expected)

    def test_to_bytes_round_trip(self) -> None:
        """
        Ensure data survives being parsed then encoded again.
        """
        device_message = b"STATUS;TIME=100;MV=3.332;MA=45;"
        expected_data = DeviceMessage(
            name='STATUS',
            data={
                'TIME': '100',
                'MV': '3.332',
                'MA': '45',
            }
        )

        # Parse
        data = DeviceMessage.from_bytes(device_message)
        self.assertEqual(data, expected_data)

        # Re-encode
        binary = data.to_bytes()
        self.assertEqual(binary, device_message)

    def test_discovery(self) -> None:
        """
        Extract data from valid discovery message.
        """
        data = DeviceMessage.from_bytes(b"ID;MODEL=M001;SERIAL=SN0123456;")
        expected = DeviceMessage(
            name='ID',
            data={'MODEL': 'M001', 'SERIAL': 'SN0123456'},
        )
        self.assertEqual(data, expected)

    def test_discovery_outgoing(self) -> None:
        data = DeviceMessage.from_bytes(b"ID;")
        expected = DeviceMessage(
            name='ID',
            data={},
        )
        self.assertEqual(data, expected)

    def test_discovery_no_semicolon(self) -> None:
        data = DeviceMessage.from_bytes(b"ID")
        expected = DeviceMessage(
            name='ID',
            data={},
        )
        self.assertEqual(data, expected)

    def test_start(self) -> None:
        """
        Command device to start test.
        """
        message = b"TEST;CMD=START;DURATION=30;RATE=100;"
        data = DeviceMessage.from_bytes(message)
        expected = DeviceMessage(
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
        data = DeviceMessage.from_bytes(message)
        expected = DeviceMessage(
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
        data = DeviceMessage.from_bytes(message)
        expected = DeviceMessage(
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
        data = DeviceMessage.from_bytes(message)
        expected = DeviceMessage(
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
        data = DeviceMessage.from_bytes(message)
        expected = DeviceMessage(
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
        data = DeviceMessage.from_bytes(message)
        expected = DeviceMessage(
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
        message = b"STATUS;TIME=100;MV=3332;MA=45;"
        data = DeviceMessage.from_bytes(message)
        expected = DeviceMessage(
            name='STATUS',
            data={
                'TIME': '100',
                'MV': '3332',
                'MA': '45',
            }
        )
        self.assertEqual(data, expected)

    def test_idle(self) -> None:
        """
        Device reports idle state after test stops for any reason.
        """
        message = b"STATUS;STATE=IDLE;"
        data = DeviceMessage.from_bytes(message)
        expected = DeviceMessage(
            name='STATUS',
            data={
                'STATE': 'IDLE',
            }
        )
        self.assertEqual(data, expected)


DEVICE_DISCOVERY = Datagram(
    address='192.168.0.10',
    port=6062,
    data=b'ID;MODEL=M001;SERIAL=SN0123456;',
)

DEVICE_DISCOVERY2 = Datagram(
    address='192.168.0.10',
    port=6063,
    data=b'ID;MODEL=M001;SERIAL=SN0123457;',
)


class DiscoveryDataTest(TestCase):
    maxDiff = None

    def test_from_datagram(self) -> None:
        device = DiscoveryData.from_datagram(DEVICE_DISCOVERY)
        expected = DiscoveryData(
            address='192.168.0.10',
            port=6062,
            model='M001',
            serial='SN0123456',
        )
        self.assertEqual(device, expected)

    def test_from_datagrams(self) -> None:
        datagrams = [DEVICE_DISCOVERY, DEVICE_DISCOVERY2]
        devices = DiscoveryData.from_datagrams(datagrams)
        expected = [
            DiscoveryData(
                address='192.168.0.10',
                port=6062,
                model='M001',
                serial='SN0123456'),
            DiscoveryData(
                address='192.168.0.10',
                port=6063,
                model='M001',
                serial='SN0123457'),
        ]
        self.assertEqual(devices, expected)

    def test_hashable(self) -> None:
        """
        Confirm that we can use frozen dataclasses as the key in a dictionary.
        """
        # Try and use instance as key in dictionary
        device = DiscoveryData(
            address='192.168.0.10',
            port=6062,
            model='M001',
            serial='SN0123456',
        )
        mapping = {}
        mapping[device] = "It works!"

        # Same data, but different object
        device2 = DiscoveryData(
            address='192.168.0.10',
            port=6062,
            model='M001',
            serial='SN0123456',
        )

        self.assertNotEqual(id(device), id(device2))
        self.assertEqual(device, device2)
        self.assertEqual(mapping[device2], "It works!")

    def test_not_equal(self) -> None:
        """
        Devices with same model and serial number on different port numbers
        should NOT be considered equal.
        """
        device1 = DiscoveryData(
            address='192.168.0.10', port=6063,
            model='M002', serial='SN546314'
        )
        device2 = DiscoveryData(
            address='192.168.0.10', port=6064,
            model='M002', serial='SN546314'
        )
        self.assertNotEqual(device1, device2)

    def test_ordering(self) -> None:
        """
        Ensure sorting device data behaves as expected: model then serial.
        """
        devices = [
            DiscoveryData(
                address='192.168.0.10', port=6063,
                model='M002', serial='SN546314'),
            DiscoveryData(
                address='192.168.0.10', port=6063,
                model='M001', serial='SN0123457'),
            DiscoveryData(
                address='192.168.0.10', port=6062,
                model='M001', serial='SN0123456'),
        ]

        expected = [
            DiscoveryData(
                address='192.168.0.10', port=6062,
                model='M001', serial='SN0123456'),
            DiscoveryData(
                address='192.168.0.10', port=6063,
                model='M001', serial='SN0123457'),
            DiscoveryData(
                address='192.168.0.10', port=6063,
                model='M002', serial='SN546314'),
        ]

        devices.sort()
        self.assertEqual(devices, expected)


class StatusDataTest(TestCase):
    def test_from_message(self) -> None:
        message = DeviceMessage(
            "STATUS", {
                'TIME': '300',
                'MV': '4448.9',
                'MA': '-11.1',
            })
        data = StatusData.from_message(message)
        expected = StatusData(ma=-11.1, mv=4448.9, time=0.3)
        self.assertEqual(data, expected)

    def test_error_data_missing(self) -> None:
        # No millivolts?!
        message = DeviceMessage(
            "STATUS", {
                'TIME': '300',
                'MA': '-11.1',
            })
        error = r"^Status data missing: 'MV' not found$"
        with self.assertRaisesRegex(ValueError, error):
            StatusData.from_message(message)

    def test_error_data_bad(self) -> None:
        # How many volts?!
        message = DeviceMessage(
            "STATUS", {
                'TIME': '300',
                'MV': 'banana',
                'MA': '-11.1',
            })

        error = (
            r"^Invalid status data: could not "
            r"convert string to float: 'banana'$"
        )
        with self.assertRaisesRegex(ValueError, error):
            StatusData.from_message(message)

    def test_error_not_status(self) -> None:
        message = DeviceMessage.from_bytes(b"ID;MODEL=M001;SERIAL=SN0123456;")
        error = r"^Expected a message of type 'STATUS', got 'ID'"
        with self.assertRaisesRegex(ValueError, error):
            StatusData.from_message(message)
