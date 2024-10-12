"""
Application entry point.

Run the command-line application if arguments given, otherwise start the GUI.
"""
import argparse
import logging
from pprint import pprint as pp
import sys
from typing import TypeAlias

from . import DEFAULT_MULTICAST_IP, DEFAULT_MULTICAST_PORT
from .devices import Device
from .networking import multicast_client


logger = logging.getLogger(__name__)
Options: TypeAlias = argparse.Namespace


def discover(options: Options) -> int:
    """
    Implement 'discover' subcommand for find devices via UDP multicast.

    Args:
        options:
            From command line, including default values.

    Returns:
        Zero if command completed successfully.
    """
    # Send multicast, collect responses
    found = multicast_client(
        DEFAULT_MULTICAST_IP,
        DEFAULT_MULTICAST_PORT, b"ID;",
        timeout=options.timeout,
    )

    # Parse and print device details
    devices = Device.from_datagrams(found)
    print(f"{len(devices)} devices responded to discovery:")
    for device in devices:
        print(f"{device.model:<6} {device.serial:<12} {device.address}:{device.port}")


def parse(arguments: list[str]) -> Options:
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
    subparsers = parser.add_subparsers(
        dest='command',
        metavar="COMMAND",
    )

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


def start_gui(options: Options) -> int:
    logger.info("Starting GUI...")
    return 0


def main(options: Options) -> int:
    """
    Application entry point.

    Start GUI if no commmand-line options given.
    """
    match options.command:
        case 'discover':
            return discover(options)
        case _:
            return start_gui(options)


if __name__ == '__main__':
    logging.basicConfig(
        format="%(levelname)-7s %(message)s",
        level=logging.DEBUG,
    )

    options = parse(sys.argv)
    sys.exit(main(options))
