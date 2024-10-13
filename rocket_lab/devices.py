"""
Devices under test.
"""
from dataclasses import dataclass
import logging
from typing import Self

from .data import DeviceMessage
from .networking import Datagram


logger = logging.getLogger(__name__)


@dataclass(eq=True, frozen=True, slots=True)
class Device:
    address: str
    port: int
    model: str
    serial: str

    @classmethod
    def from_datagram(cls, datagram: Datagram) -> Self:
        """
        Create instance from a discovery response.

        The datagram's message field should contain discovery data from
        the DUT, eg. "ID;MODEL=M001;SERIAL=SN0123457;"

        Args:
            datagram:
                Networking Datagram namedtuple

        Raises:
            RuntimeError:
                If problems encountered parsing device data.

        Returns:
            Device instance.
        """
        address = datagram.address
        port = datagram.port

        try:
            data = DeviceMessage.from_bytes(datagram.message)
            model = data.data['MODEL']
            serial = data.data['SERIAL']
        except KeyError as e:
            raise RuntimeError(f"Device data missing: {e} not found")
        except ValueError as e:
            raise RuntimeError(f"Device data error: {e}")

        return Device(address, port, model, serial)

    @classmethod
    def from_datagrams(cls, datagrams: list[Datagram]) -> list[Self]:
        """
        Create list of device instances by parsing list of datagrams.

        Catches and logs errors, returning only list of valid devices.

        Args:
            datagrams:
                List of networking Datagram namedtuples.

        Returns:
            List of device instances.
        """
        devices = []
        for datum in datagrams:
            try:
                device = Device.from_datagram(datum)
            except RuntimeError as e:
                logger.error("%s", e)
            else:
                devices.append(device)
        return devices
