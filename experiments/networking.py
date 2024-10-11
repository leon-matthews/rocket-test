#!/usr/bin/env python3

import argparse
import logging
from pprint import pprint as pp
import socket
import sys


logger = logging.getLogger(__name__)
LOCALHOST = "127.0.0.1"
DEFAULT_PORT = 6060
MAX_BYTES = 65535
ROLES = ('client', 'server')


def server(host: str, port: int) -> None:
    """
    Very chatty UDP echo server.

    Args:
        host:
            Host to listen on, eg. '127.0.0.0' for loopback.
        port:
            UDP port number to listen on.

    Returns:
        Loops forever
    """
    # Create IP datagram socket and bind as server
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    address = (host, port)
    sock.bind(address)

    # Fetch address directly from socket and log
    logger.info("UDP echo server listening on %r", sock.getsockname())

    # Listen, forever
    while True:
        data, address = sock.recvfrom(MAX_BYTES)
        logger.info(f"{address!r} sent {len(data):,} bytes:")
        print(data)
        sock.sendto(data, address)


def client(host: str, port: int, text: str) -> None:
    """
    Create and tear-down socket for every mesage

    Args:
        host:
            Host to listen on, eg. '127.0.0.0' for loopback.
        port:
            UDP port number to listen on.
        text:
            Unicode text to send. Will be encoded to UTF-8 for transport.

    Returns:
        None
    """
    # Create socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    address = (host, port)
    logger.info("UDP address assigned by OS: %r", sock.getsockname())

    # Prepare and send data
    data = text.encode('utf-8')
    sock.sendto(data, address)

    # Warning! Promiscuous client!
    data, address = sock.recvfrom(MAX_BYTES)

    logger.info(f"Server {address} sent back {len(data):,} bytes:")
    print(text)


def parse(arguments: list[str]) -> argparse.Namespace:
    """
    Parse command-line arguments.

    Args:
        arguments:
            Plain list of strings, either from sys.args or test code.

    Returns:
        Options extracted from given arguments.
    """
    parser = argparse.ArgumentParser(description='Raw socket experiments for Rocket Lab')
    parser.add_argument('role', choices=ROLES, help='run as client or server?')
    parser.add_argument(
        '-p', '--port',
        metavar='PORT',
        type=int,
        default=DEFAULT_PORT,
        help=f"UDP port to use (default {DEFAULT_PORT})"
    )
    options = parser.parse_args()
    return options


def main(options: argparse.Namespace) -> int:
    """
    Main entry point.

    Args:
        options:
            Command-line options built by `parse()`.

    Returns:
        Zero on success
    """
    host = LOCALHOST
    if options.role == 'client':
        while True:
            text = input("> ")
            client(host, options.port, text)
    elif options.role == 'server':
        server(host, options.port)
    else:
        print("Unknown role: {options.role!}" ,file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    logging.basicConfig(format="%(message)s", level=logging.INFO)
    options = parse(sys.argv[1:])
    sys.exit(main(options))
