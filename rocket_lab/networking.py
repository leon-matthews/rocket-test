"""
UDP networking code to communicate with DUT simulator.
"""

from collections import namedtuple
import logging
import socket

from . import DEFAULT_MULTICAST_TTL, UDP_MAX_BYTES


Datagram = namedtuple("Datagram", "address port message")
logger = logging.getLogger(__name__)


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
    logging.info("Send multicast UDP discovery message to find devices")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(
        socket.IPPROTO_IP,
        socket.IP_MULTICAST_TTL,
        DEFAULT_MULTICAST_TTL,
    )
    sock.settimeout(timeout)

    sock.sendto(message, (address, port))
    logging.debug("Sent %r to %r:%r", message, address, port)

    # Block for `timeout` seconds to collect multicast responses
    datagrams = []
    try:
        while True:
            data, address = sock.recvfrom(UDP_MAX_BYTES)
            logging.debug("Got  %r from %r", data, address)
            datagrams.append(Datagram(*address, data))
    except TimeoutError:
        pass

    return datagrams
