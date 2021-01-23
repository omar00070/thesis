"""Field descriptors for GRIB message sections."""

from abc import abstractmethod
from typing import Generic, Optional, Type, TypeVar

from pupygrib import base, binary

S = TypeVar("S", bound="base.BaseSection")
V = TypeVar("V")


class BaseField(Generic[S, V]):
    """Base class for field descriptors of GRIB message sections.

    A field descriptor is responsible for converting binary octets of
    a GRIB message to Python objects.  The *octet* argument should be
    the 1-based index of the first octet that the field represents.

    """

    name: str

    def __init__(self, octet: int) -> None:
        self.offset = octet - 1  # octet is 1-based

    def __get__(self, section: S, sectiontype: Type[S]) -> V:
        if section is None:
            return self
        value = self.get_value(section, self.offset)
        # By putting the value in the section instance's __dict__,
        # this descriptor shouldn't be used the next time the
        # attribute is looked up.
        section.__dict__[self.name] = value
        return value

    @abstractmethod
    def get_value(self, section: S, offset: int) -> V:
        raise NotImplementedError


GeneralField = BaseField["base.BaseSection", V]


class BytesField(GeneralField[bytes]):
    """A raw bytes field.

    If a *size* is not given, all bytes until the end of the section
    will be included.

    """

    def __init__(self, octet: int, size: Optional[int] = None) -> None:
        super().__init__(octet)
        self.size = size

    def get_value(self, section: "base.BaseSection", offset: int) -> bytes:
        return section.buf[offset : self.size and offset + self.size].tobytes()


class Int8Field(GeneralField[int]):
    """An 8-bit signed magnitude integer field."""

    def get_value(self, section: "base.BaseSection", offset: int) -> int:
        return binary.unpack_int8_from(section.buf, offset)


class Int16Field(GeneralField[int]):
    """A 16-bit signed magnitude integer field."""

    def get_value(self, section: "base.BaseSection", offset: int) -> int:
        return binary.unpack_int16_from(section.buf, offset)


class Int24Field(GeneralField[int]):
    """A 24-bit signed magnitude integer field."""

    def get_value(self, section: "base.BaseSection", offset: int) -> int:
        return binary.unpack_int24_from(section.buf, offset)


class Uint8Field(GeneralField[int]):
    """An 8-bit unsigned integer field."""

    def get_value(self, section: "base.BaseSection", offset: int) -> int:
        return binary.unpack_uint8_from(section.buf, offset)


class Uint16Field(GeneralField[int]):
    """A 16-bit unsigned integer field."""

    def get_value(self, section: "base.BaseSection", offset: int) -> int:
        return binary.unpack_uint16_from(section.buf, offset)


class Uint24Field(GeneralField[int]):
    """A 24-bit unsigned integer field."""

    def get_value(self, section: "base.BaseSection", offset: int) -> int:
        return binary.unpack_uint24_from(section.buf, offset)


class Uint32Field(GeneralField[int]):
    """A 32-bit unsigned integer field."""

    def get_value(self, section: "base.BaseSection", offset: int) -> int:
        return binary.unpack_uint32_from(section.buf, offset)


class Uint64Field(GeneralField[int]):
    """A 64-bit unsigned integer field."""

    def get_value(self, section: "base.BaseSection", offset: int) -> int:
        return binary.unpack_uint64_from(section.buf, offset)
