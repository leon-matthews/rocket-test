"""
General purpose UDP library functions.
"""

from collections import namedtuple
import logging
import socket
from typing import Iterator


logger = logging.getLogger(__name__)
DEFAULT_MULTICAST_TTL = 2
UDP_MAX_BYTES = 65535


Datagram = namedtuple("Datagram", "address port data")


def udp_client(
    address: str,
    port: int,
    message: bytes,
    timeout: float,
) -> Iterator[bytes]:
    """
    Generator over UDP server's responses to given message.

    Args:
        address:
            IP address of multicast group to join
        port:
            UDP port for multicast socket.
        timeout:
        message:
            Byte string to send to multicast listeners.
            Seconds to wait for response from server.

    Raises:
        TimeoutError:
            If nothing recieved from server for `timeout` seconds.

    Yields:
        Device data dataclass instances
    """
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.connect((address, port))
        sock.settimeout(timeout)
        logger.debug("Connected to %s:%s", address, port)

        sock.send(message)
        logger.debug("Sent: %r", message)

        while True:
            data = sock.recv(UDP_MAX_BYTES)
            logger.debug("Received: %r", data)
            yield data


def udp_multicast_client(
    address: str,
    port: int,
    message: bytes,
    timeout: float,
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
        List of datagram tuples containing responses and sender's details.
    """
    logging.info("Send multicast UDP discovery message to find devices")
    with socket.socket(
        socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP
    ) as sock:
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
