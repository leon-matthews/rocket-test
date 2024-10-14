#!/usr/bin/env python3
"""
Experiment with using UDP multicast to enumerate DUT simulators.
"""

from collections import namedtuple
import logging
from pprint import pprint as pp
import socket
import sys


HOSTNAME = "0.0.0.0"
MAX_BYTES = 65535
MULTICAST_IP = "224.3.11.15"
MULTICAST_PORT = 31115
MULTICAST_TTL = 2


Datagram = namedtuple("Datagram", "address port message")


def multicast_client(
    address: str,
    port: int,
    message: bytes,
    timeout: float = 1.0,
) -> list[Datagram]:
    """
    Send message to multicast group's subscribers.

    Args:
        address:
            IP address of multicast group to join
        port:
            UDP port for multicast socket.
        message:
            Byte string to send to multicast listeners.
        timeout:
            Seconds to wait for discovery messages to come back

    Returns:
        None
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, MULTICAST_TTL)
    sock.settimeout(timeout)

    address = (MULTICAST_IP, MULTICAST_PORT)
    sock.sendto(message, address)
    logging.debug(f"send {message} to {address!r}")

    # Block for `timeout` seconds to collect multicast responses
    datagrams = []
    try:
        while True:
            data, address = sock.recvfrom(MAX_BYTES)
            datagrams.append(Datagram(*address, data))
    except TimeoutError:
        pass

    return datagrams


if __name__ == '__main__':
    logging.basicConfig(
        format="%(levelname)-7s %(message)s",
        level=logging.DEBUG,
    )

    returned = multicast_client(
        MULTICAST_IP, MULTICAST_PORT, b"ID;", timeout=1.0,
    )
    pp(returned)
    sys.exit(1)
