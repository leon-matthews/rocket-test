"""
Devices under test.
"""
from dataclasses import dataclass
from pprint import pprint as pp
from typing import Self

from . import DEFAULT_ENCODING
from .networking import Datagram


@dataclass(eq=True, frozen=True)
class Data:
    """
    Data contained in a message recived from a device.

    Several messages from the DUT simulator encode key/value pairs
    as a semi-colon delimited string. For example, the ID response from
    the discovery message is the byte string:

        b"ID;MODEL=M001;SERIAL=SN0123457;"

    This should be understood as message named 'ID' with the
    data {'model': 'M001', 'serial': 'SN0123457'}.

    Note that no attempt to parse numeric data is made.
    """
    name: str
    data: dict[str, str]

    @classmethod
    def from_message(self, binary: bytes) -> Self:
        """
        Create instance from the semicolon-delimited string from device.

        Raises:
            ValueError:
                If message string cannot be parsed.

        Returns:
            Data instance
        """
        string = binary.decode(DEFAULT_ENCODING, errors='replace')
        parts = string.split(";")
        name = parts[0]
        data = {}
        for part in parts[1:]:
            if not part:
                continue

            entry = part.split("=")
            if len(entry) == 2:
                data[entry[0]] = entry[1]
            else:
                raise ValueError(f"Could not parse {part} from {binary!r}")

        if not name:
            raise ValueError(f"Empty message")

        return Data(name, data)

    def to_string(self) -> str:
        """
        Serialise data to semi-colon delimited string.
        """
        # Serialise name and key/value pairs
        parts = [self.name]
        for k, v in self.data.items():
            parts.append(f"{k}={v}")

        # Insert semicolons, including one at end of message!
        parts = [f"{part};" for part in parts]
        string = "".join(parts)
        return string

    def to_bytes(self) -> bytes:
        """
        Serialise data to byte string.
        """
        return self.to_string().encode(DEFAULT_ENCODING, errors="replace")


@dataclass(eq=True, frozen=True)
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
            data:
                Networking Datagram namedtuple

        Returns:
            Device instance.
        """
        address = datagram.address
        port = datagram.port

        data = Data.from_message(datagram.message)
        model = data.data['MODEL']
        serial = data.data['SERIAL']
        return Device(address, port, model, serial)
