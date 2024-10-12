"""
Command-line argument parsing and subcommand implementation.
"""
import argparse
from pprint import pprint as pp
from typing import TypeAlias

from . import networking, DEFAULT_MULTICAST_IP, DEFAULT_MULTICAST_PORT
from .devices import Device


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
    found = networking.multicast_client(
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
    # Global arguments
    parser = argparse.ArgumentParser(
        prog="rocket_lab",
        description="Rocket Lab Production Automation Coding Test",
        epilog="Run with zero aguments to start GUI",
    )
    parser.add_argument(
        '-v', '--verbose', action='store_true',
        help="Enable debug logging output")

    # Subcommands...
    subparsers = parser.add_subparsers(
        dest='command',
        metavar="COMMAND",
    )

    # ...'discover' command arguments
    discover = subparsers.add_parser(
        'discover',
        help='Find devices on network via UDP multicast',
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
