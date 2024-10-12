
from unittest import TestCase


class DevicesTest(TestCase):
    def test_fail(self) -> None:
        self.fail("Yicks")
