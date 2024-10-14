"""
Command-line argument parsing and subcommand implementation.
"""
import argparse
from argparse import ArgumentTypeError
from pprint import pprint as pp
from typing import TypeAlias

from . import networking, DEFAULT_MULTICAST_IP, DEFAULT_MULTICAST_PORT
from .data import DiscoveryData, StatusData


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
        raise ArgumentTypeError(
            f"Invalid port number. Expected integer, given {parts[1]!r}"
        )

    return (address, port)


def run_discovery(options: Options) -> int:
    """
    Implement 'discover' subcommand for find devices via UDP multicast.

    Args:
        options:
            From command line, including default values.

    Returns:
        Zero if command completed successfully.
    """
    multicast_ip, multicast_port = options.multicast
    devices = networking.discover_devices(
        multicast_ip, multicast_port, timeout=options.timeout,
    )
    print(f"{len(devices)} devices responded to discovery:")
    for device in devices:
        print(
            f"{device.model:<6} {device.serial:<12} "
            f"{device.address}:{device.port}"
        )


def run_device_test(options: Options) -> int:
    """
    Implement 'test' subcommand for devices.

    Args:
        options:
            From command line, including default values.

    Returns:
        Zero if command completed successfully.
    """
    # Prepare
    address, port = options.address
    duration = options.duration
    rate = options.rate
    print(
        f"Start test on {address}:{port} for "
        f"{duration}s, status every {rate}ms"
    )

    # Print and collect data as it comes in
    runner = networking.test_device(
        address,
        port,
        duration,
        rate,
        timeout=options.timeout,
    )
    ma_history = []
    mv_history = []
    for message in runner:
        status = StatusData.from_message(message)
        ma_history.append(status.ma)
        mv_history.append(status.mv)
        ma = f"{status.ma:,.2f}mA"
        mv = f"{status.mv:,.2f}mV"
        print(f"{status.time*1000:>6,.0f} milliseconds: {ma:>12} {mv:>12}")

    # Print aggregate data
    def aggregates(values: list[float]) -> (str, str, str):
        """
        Calcuate, format, and return mean, max, and min - and in that order.
        """
        mean = sum(values) / len(values)
        return (f"{mean:,.2f}", f"{max(values):,.2f}", f"{min(values):,.2f}")

    ma_mean, ma_max, ma_min  = aggregates(ma_history)
    print(f"Current mean {ma_mean}mA, max {ma_max}mA, min {ma_min}mA")

    mv_mean, mv_max, mv_min  = aggregates(mv_history)
    print(f"Voltage mean  {mv_mean}mV, max {mv_max}mV, min {mv_min}mV")


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
        epilog="The default action is to start the GUI",
    )
    multicast_default = f"{DEFAULT_MULTICAST_IP}:{DEFAULT_MULTICAST_PORT}"
    parser.add_argument(
        '--multicast',
        default=multicast_default,
        dest='multicast',
        metavar='ADDRESS:PORT',
        type=argparse_address_tuple,
        help=f"Multicast IP address and port (default {multicast_default})",
    )
    parser.add_argument(
        '-t', '--timeout',
        default=1.0,
        type=float,
        help='Seconds to wait for response',
    )
    parser.add_argument(
        '-v', '--verbose', action='store_true',
        help="Enable debug logging output"
    )

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

    # ... 'test' command arguments
    discover = subparsers.add_parser(
        'test',
        help='Run test on the selected device',
    )
    discover.add_argument(
        '-d', '--duration',
        default=2,
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

    # ...'gui' command
    discover = subparsers.add_parser(
        'gui',
        help='Start PyQT graphical user interface (default)',
    )

    options = parser.parse_args()
    return options
