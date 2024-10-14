"""
Rocket Lab specific UDP communication with DUT simulator.
"""

import logging
from typing import Iterator

from .data import DeviceMessage, DiscoveryData
from .udp import udp_client, udp_multicast_client


logger = logging.getLogger(__name__)


def discover_devices(
    multicast_ip: str,
    multicast_port: int,
    timeout: float,
) -> list[DiscoveryData]:
    """
    Discover device simultors on the network using multicast UDP.

    Blocks for `timeout` seconds while waiting for clients to respond.

    Args:
        multicast_ip:
            Multicast IP address to use, eg. "224.3.11.15"
        multicast_port:
            Port number to use, eg. 31115
        timeout:
            How long to wait for responses.

    Returns:
        List of `DiscoveryData` instances, one per device.
    """
    # Send multicast, collect responses
    found = udp_multicast_client(
        multicast_ip,
        multicast_port, b"ID;",
        timeout=timeout,
    )

    # Parse and print device details
    devices = DiscoveryData.from_datagrams(found)
    logger.info(
        "%s devices found after waiting %f seconds",
        len(devices),
        timeout,
    )
    return devices


def test_device(
    address: str,
    port: int,
    duration: int,
    rate: int,
    timeout: float,
) -> Iterator[DeviceMessage]:
    """
    Send start test command to device, then collect and parse data.

    Stops when device sends on 'STATE=IDLE' status message, or if
    connection times out.

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
        Generator over test data.
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
