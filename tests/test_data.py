
from pprint import pprint as pp
from unittest import skip, TestCase

from rocket_lab.data import DeviceMessage, StatusData


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

        error = r"^Invalid status data: could not convert string to float: 'banana'$"
        with self.assertRaisesRegex(ValueError, error):
            StatusData.from_message(message)

    def test_error_not_status(self) -> None:
        message = DeviceMessage.from_bytes(b"ID;MODEL=M001;SERIAL=SN0123456;")
        error = r"^Expected a message of type 'STATUS', got 'ID'"
        with self.assertRaisesRegex(ValueError, error):
            StatusData.from_message(message)
