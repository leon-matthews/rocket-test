
from argparse import ArgumentTypeError
from pprint import pprint as pp
from unittest import skip, TestCase

from rocket_lab.command_line import argparse_address_tuple


class ArgparseAddressTupleTest(TestCase):
    """
    Note that the argument is never an empty string.
    """
    def test_loopback_ipv4(self) -> None:
        address, port = argparse_address_tuple("127.0.0.0:6060")
        self.assertEqual(address, "127.0.0.0")
        self.assertEqual(port, 6060)

    def test_loopback_ipv6(self) -> None:
        address, port = argparse_address_tuple("::1:6060")
        self.assertEqual(address, "::1")
        self.assertEqual(port, 6060)

    def test_error_port_missing(self) -> None:
        message = r"^Port number missing. Use colon to separate.$"
        with self.assertRaisesRegex(ArgumentTypeError, message):
            argparse_address_tuple("192.168.0.10")

    def test_error_port_invalid(self) -> None:
        message = r"^Invalid port number. Expected integer, given 'banana'$"
        with self.assertRaisesRegex(ArgumentTypeError, message):
            argparse_address_tuple("192.168.0.10:banana")
