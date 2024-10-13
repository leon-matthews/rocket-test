"""
Parse and validate data into read-only dataclasses.
"""

from dataclasses import dataclass
from pprint import pprint as pp
from typing import Self

from . import DEFAULT_ENCODING


@dataclass(eq=True, frozen=True, slots=True)
class DeviceMessage:
    """
    Message data transfered to and from devices.

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
    def from_bytes(self, binary: bytes) -> Self:
        """
        Create instance from the semicolon-delimited byte string from device.

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
            raise ValueError("Empty message")

        return DeviceMessage(name, data)

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


@dataclass(eq=True, frozen=True, slots=True)
class StatusData:
    """
    A single status message from a device test.
    """
    ma: float       # Milliamps reported
    mv: float       # Millivolts reported
    time: float     # Seconds since test started

    @classmethod
    def from_message(self, message: DeviceMessage) -> Self:
        """
        Parse and convert a test's status data from a device message.

        Raises:
            ValueError:
                If any errors encountered in given messsage.

        Returns:
            Validated and converted test status data.
        """
        if message.name != 'STATUS':
            raise ValueError(
                f"Expected a message of type 'STATUS', got {message.name!r}"
            )

        try:
            ma = float(message.data['MA'])
            mv = float(message.data['MV'])
            time = float(message.data['TIME']) / 1000.0
        except KeyError as e:
            raise ValueError(f"Status data missing: {e} not found")
        except ValueError as e:
            raise ValueError(f"Invalid status data: {e}")

        return StatusData(ma, mv, time)
