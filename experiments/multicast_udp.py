#!/usr/bin/env python3
"""
Experiment with using UDP multicast to enumerate DUT simulators.
"""

import logging
import socket
import sys


HOSTNAME = "0.0.0.0"
MULTICAST_IP = "224.3.11.15"
MULTICAST_PORT = 31115
MULTICAST_TTL = 2


def send(address: str, port: int, message: bytes) -> None:
    """
    Send message to multicast group's subscribers.

    Args:
        address:
            IP address of multicast group to join
        port:
            UDP port for multicast socket.
        message:
            Byte string to send to multicast listeners.

    Returns:
        None
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, MULTICAST_TTL)
    address = (MULTICAST_IP, MULTICAST_PORT)
    sock.sendto(message, address)
    logging.debug(f"send {message} to {address!r}")


if __name__ == '__main__':
    logging.basicConfig(
        format="%(levelname)-7s %(message)s",
        level=logging.DEBUG,
    )

    send(MULTICAST_IP, MULTICAST_PORT, b"ID;")
    sys.exit(1)
