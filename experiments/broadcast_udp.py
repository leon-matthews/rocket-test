#!/usr/bin/env python3
"""
Simple UDP broadcast (*not* multicast) experiment

Not strictly required for the main program, but fun anyway!

Run multiple instances of the server, then one client. Every server
will see the messages sent by the client.
"""
import socket
import sys
import textwrap


DEFAULT_PORT = 6060
MAX_BYTES = 65535


def server(address: str, port: int) -> None:
    """
    Server for UDP broadcast.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Required on Linux kernel >= 3.9 to run multiple servers on same port
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    sock.bind((address, port))
    print(f"Listening on {sock.getsockname()!r}")
    while True:
        data, address = sock.recvfrom(MAX_BYTES)
        print(f"Client {address!r} sent {data!r}")


def client(address: str, port: int, message: bytes) -> None:
    """
    Client for UDP broadcast.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(message, (address, port))


if __name__ == '__main__':
    if len(sys.argv) < 3:
        usage = textwrap.dedent(f"""
            usage: {sys.argv[0]} {{client,server}} ADDRESS [PORT]
            The address may the IP of an interface on the machine, or
            an empty string '' to represent INADDR_ANY, or the special
            string '<broadcast>' to represent INADDR_BROADCAST.
        """).strip()
        print(usage, file=sys.stderr)
        sys.exit(1)

    address = sys.argv[2]
    try:
        port = int(sys.argv[3])
    except IndexError:
        port = DEFAULT_PORT

    if sys.argv[1] == 'client':
        client(address, port, b"Hello, world!")
    else:
        server(address, port)
    sys.exit(0)
