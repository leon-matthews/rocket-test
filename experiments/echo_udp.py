#!/usr/bin/env python3
"""
Slightly over-engineered UDP echo client and server, to get myself back
into the raw socket networking game!

Promiscuous UDP client

There are two modes of operation for UDP client code. Promiscuous and not. The
former will accept an UDP datagram to the client port from anywhere, the latter
rejects messages not from the server previously connected to.

    # Careful
    s.connect() -> s.send() -> s.recv()

    # Promiscuous
    sock.sendto() -> sock.recvfrom()


I've implemented both approaches in the echo server as `careful_client()` and
`promiscuous_client()`, as I'm not yet sure which will prove the most useful
for the final program.
"""
import argparse
import logging
import socket
import sys


logger = logging.getLogger(__name__)
LOOPBACK = "127.0.0.1"
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
    # Create socket: UDP on a IP network
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    address = (host, port)

    # Request address from OS, ie. (hostname, port)
    sock.bind(address)
    logger.info("UDP echo server listening on %r", sock.getsockname())

    # Listen, forever
    while True:
        data, address = sock.recvfrom(MAX_BYTES)
        logger.info(f"{address!r} sent {len(data):,} bytes:")
        logger.debug(data)
        sock.sendto(data, address)


def client(host: str, port: int) -> None:
    """
    Prompt user for string and send it to server in infinite loop.

    String from user is encoded into UTF-8 before hitting network, then
    decoded back into a string.

    Args:
        As per `server`.
    """
    while True:
        text = input("> ")
        message = text.encode("utf-8", errors="replace")
        received = careful_client(host, options.port, message)
        print(received.decode("utf-8", errors="replace"))


def careful_client(
    host: str,
    port: int,
    message: bytes,
    timeout: float = 5,
) -> bytes:
    """
    Create new socket and send single outgoing UDP message.

    Solves promiscuous UDP client problem by using `socket.connect()` to force
    OS to check sender address and reject packets not sent by destination
    server.

    Key socket calls:

        s.connect() -> s.send() -> s.recv()

    Args:
        host:
            Host to listen on, eg. '127.0.0.0' for loopback.
        port:
            UDP port number to listen on.
        message:
            Byte string to send to server.
        timeout:
            How many seconds to wait for server response.

    Raises:
        ConnectionRefusedError:
            Will immediately raise error if server not listening on port.
        TimeoutError:
            If server does not respond within `timeout` seconds.

    Returns:
        Byte string send back from server.
    """
    # Create socket
    # Note that port is assigned during call to connect, not on first message
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    address = (host, port)
    sock.connect(address)
    sock.settimeout(timeout)
    logger.info("UDP address assigned by OS: %r", sock.getsockname())

    # Send message to server, address not necessary
    sock.send(message)

    # Recieved data back from server
    data = sock.recv(MAX_BYTES)
    logger.info(f"Server sent back {len(data):,} bytes")
    return data


def promiscuous_client(host: str, port: int, message: bytes) -> bytes:
    """
    Create new socket and send single outgoing UDP message.

    Note that client will NOT raise a `ConnectionRefusedError` if client not
    running.

    Produces a promiscuous client which will accept message to the client
    port from anywhere. Key socket calls:

        sock.sendto() -> sock.recvfrom()

    Args:
        As per `careful_client()`

     Raises:
        TimeoutError:
            If server does not respond within `timeout` seconds.

    Returns:
        Byte string send back from server.
    """
    # Create socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(1)
    address = (host, port)

    # Send message to server
    # Note that port is not assigned by OS until AFTER message is sent
    sock.sendto(message, address)
    logger.info("UDP address assigned by OS: %r", sock.getsockname())

    # Recieved data back from server
    data, address = sock.recvfrom(MAX_BYTES)    # Warning! Promiscuous client!
    logger.info(f"Server {address} sent back {len(data):,} bytes")
    return data


def parse(arguments: list[str]) -> argparse.Namespace:
    """
    Parse command-line arguments.

    Args:
        arguments:
            Plain list of strings, either from sys.args or test code.

    Returns:
        Options extracted from given arguments.
    """
    parser = argparse.ArgumentParser(description='UDP echo client and server')
    parser.add_argument('role', choices=ROLES, help='run as client or server?')
    parser.add_argument(
        '-a', '--address',
        type=str,
        default=LOOPBACK,
        nargs="?",
        help=f"Address of interface to bind to (default {LOOPBACK!r})"
    )
    parser.add_argument(
        '-p', '--port',
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
    # Allow binding to all interfaces
    host = "" if options.address is None else options.address

    if options.role == 'client':
        client(host, options.port)
    elif options.role == 'server':
        server(host, options.port)
    else:
        print("Unknown role: {options.role!}", file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    logging.basicConfig(
        format="%(levelname)-7s %(message)s",
        level=logging.DEBUG,
    )
    options = parse(sys.argv[1:])
    sys.exit(main(options))
