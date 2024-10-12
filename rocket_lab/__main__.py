"""
Application entry point.

Run the command-line application if arguments given, otherwise start the GUI.
"""
import argparse
import logging
from pprint import pprint as pp
import sys

from .networking import multicast_client

from . import MULTICAST_IP, MULTICAST_PORT


logger = logging.getLogger(__name__)


def parse(arguments: list[str]) -> argparse.Namespace:
    """
    Parse command-line arguments.

    Args:
        arguments:
            Plain list of strings, either from sys.args or test code.

    Returns:
        Options extracted from given arguments.
    """
    # Top-level parser
    parser = argparse.ArgumentParser(
        prog="rocket_lab",
        description="Rocket Lab Production Automation Coding Test",
        epilog="Run with zero aguments to start GUI",
    )
    subparsers = parser.add_subparsers()

    # Parser for 'discover' command
    discover = subparsers.add_parser(
        'discover',
        help='Find DUT simulators using UDP multicast',
    )
    discover.add_argument(
        '-t', '--timeout',
        default=1.0,
        type=float,
        help='seconds to wait for responses',
    )

    options = parser.parse_args()
    pp(options)
    return options


def main(options: argparse.Namespace) -> int:
    """
    Application entry point.
    """
    found = multicast_client(MULTICAST_IP, MULTICAST_PORT, b"ID;", timeout=1.0)
    pp(found)


if __name__ == '__main__':
    logging.basicConfig(
        format="%(levelname)-7s %(message)s",
        level=logging.DEBUG,
    )

    options = parse(sys.argv)
    sys.exit(main(options))
