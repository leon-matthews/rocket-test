"""
Command-line argument parsing and subcommand implementation.
"""
import argparse
from argparse import ArgumentTypeError
from pprint import pprint as pp
from typing import TypeAlias

from . import networking, DEFAULT_MULTICAST_IP, DEFAULT_MULTICAST_PORT
from .devices import Device


Options: TypeAlias = argparse.Namespace


def argparse_address_tuple(string: str) -> tuple[str, int]:
    """
    Convert and validate string argument containing IP address and port number.

    Don't try and parse the IP address here, that will just double up the
    processing done later.

    Args:
        string:
            Colon-delimited address string, eg. '192.168.0.10:6062'

    Raises:
        argparse.ArgumentTypeError:
            If path does not exist.

    Returns:
        2-tuple containing IP address and port number.
    """
    parts = string.rsplit(":", maxsplit=1)
    address = parts[0]
    port: int
    try:
        port = int(parts[1])
    except IndexError:
        raise ArgumentTypeError("Port number missing. Use colon to separate.")
    except ValueError:
        raise ArgumentTypeError(f"Invalid port number. Expected integer, given {parts[1]!r}")

    return (address, port)


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

    # ... 'test' command arguments
    discover = subparsers.add_parser(
        'test',
        help='Run test on the selected device',
    )
    discover.add_argument(
        '-d', '--duration',
        default=10,
        type=int,
        help='seconds to run test for',
    )
    discover.add_argument(
        '-r', '--rate',
        default=100,
        type=int,
        help='milliseconds between status reports',
    )
    discover.add_argument(
        dest='address',
        metavar='ADDRESS:PORT',
        type=argparse_address_tuple,
        help="IP address and port number of device, eg. 192.168.0.10:6062"
    )

    options = parser.parse_args()
    pp(options)
    return options
