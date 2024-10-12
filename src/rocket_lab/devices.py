"""
Devices under test.
"""

from dataclasses import dataclass


@dataclass(eq=True, frozen=True)
class Device:
    address: str
    port: int
    model: str
    serial: str
