"""
UDP networking code to communicate with DUT simulator.
"""

from collections import namedtuple
import logging
from pprint import pprint as pp
import socket
from typing import Iterator

from .data import DeviceMessage

from . import DEFAULT_MULTICAST_TTL, UDP_MAX_BYTES


Datagram = namedtuple("Datagram", "address port message")
logger = logging.getLogger(__name__)


def run_test(
    address: str,
    port: int,
    duration: int,
    rate: int,
    timeout: float,
) -> Iterator[DeviceMessage]:
    """
    Send start test command to device, then collect and parse data.

    Stops when device sends on 'STATE=IDLE' status message, or if
    connection timesout.

    Args:
        address:
            IP address of multicast group to join
        port:
            UDP port for multicast socket.
        duration:
            Seconds to run test for.
        rate:
            Milliseconds between status report.
        timeout:
            Seconds to wait for response from server.

    Returns:
        List of test data.
    """
    message = DeviceMessage(
        'TEST', {
            'CMD': 'START',
            'DURATION': duration,
            'RATE': rate,
        }
    ).to_bytes()

    # Parse and send back to caller as it arrives
    for raw in udp_client(address, port, message, timeout):
        datum = DeviceMessage.from_bytes(raw)

        # Check result messages
        if datum.name == 'TEST':
            match datum.data:
                case {'RESULT': 'STARTED'}:
                    logger.info("Received 'test started' from device")

                case _:
                    pass

            # Don't send test messages back to caller
            continue

        # Exit when device reports that test is complete
        if "STATE" in datum.data and datum.data["STATE"] == "IDLE":
            logger.info("Received 'test completed' from device")
            return

        yield datum


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
        message:
            Byte string to send to multicast listeners.
        timeout:
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
        List of datagram tuples containing responses and their sender's details.
    """
    logging.info("Send multicast UDP discovery message to find devices")
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
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
