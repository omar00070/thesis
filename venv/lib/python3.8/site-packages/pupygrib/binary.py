"""Functions to handle binary data."""

import struct
from typing import BinaryIO

from pupygrib.exceptions import ParseError
from pupygrib.utils import ReadableBuffer

error = struct.error

_uint8struct = struct.Struct(b">B")
_uint16struct = struct.Struct(b">H")
_uint24struct = struct.Struct(b">HB")
_uint32struct = struct.Struct(b">I")
_uint64struct = struct.Struct(b">Q")

_grib1_float_magic = 2 ** -24


def unpack_grib1float_from(buf: ReadableBuffer, offset: int = 0) -> float:
    """Unpack a 32-bit GRIB 1 floating point value from *buf* at *offset*.

    GRIB edition 1 does not use the IEEE 754 floating point standard.
    Instead, it uses a leading sign bit (s), a 7-bit exponent (A), and
    a 24-bit significand (B).  The represented value is then given by

        R = (-1)^s * 2^-24 * B * 16^(A - 64)

    """
    (i,) = _uint32struct.unpack_from(buf, offset)
    s = i >> 31
    A = (i & 0x7FFFFFFF) >> 24
    B = i & 0x00FFFFFF
    return (-1) ** s * _grib1_float_magic * B * 16 ** (A - 64)


def unpack_int8_from(buf: ReadableBuffer, offset: int = 0) -> int:
    """Unpack an 8-bit signed magnitude integer from *buf* at *offset*."""
    (b,) = _uint8struct.unpack_from(buf, offset)
    return (-1) ** (b >> 7) * (b & 0x7F)


def unpack_int16_from(buf: ReadableBuffer, offset: int = 0) -> int:
    """Unpack a 16-bit signed magnitude integer from *buf* at *offset*."""
    (h,) = _uint16struct.unpack_from(buf, offset)
    return (-1) ** (h >> 15) * (h & 0x7FFF)


def unpack_int24_from(buf: ReadableBuffer, offset: int = 0) -> int:
    """Unpack a 24-bit signed magnitude integer from *buf* at *offset*."""
    h, b = _uint24struct.unpack_from(buf, offset)
    return (-1) ** (h >> 15) * (((h & 0x7FFF) << 8) + b)


def unpack_uint8_from(buf: ReadableBuffer, offset: int = 0) -> int:
    """Unpack an 8-bit unsigned integer from *buf* at *offset*."""
    return _uint8struct.unpack_from(buf, offset)[0]


def unpack_uint16_from(buf: ReadableBuffer, offset: int = 0) -> int:
    """Unpack a 16-bit unsigned integer from *buf* at *offset*."""
    return _uint16struct.unpack_from(buf, offset)[0]


def unpack_uint24_from(buf: ReadableBuffer, offset: int = 0) -> int:
    """Unpack a 24-bit unsigned integer from *buf* at *offset*."""
    h, b = _uint24struct.unpack_from(buf, offset)
    return (h << 8) + b


def unpack_uint32_from(buf: ReadableBuffer, offset: int = 0) -> int:
    """Unpack a 32-bit unsigned integer from *buf* at *offset*."""
    return _uint32struct.unpack_from(buf, offset)[0]


def unpack_uint64_from(buf: ReadableBuffer, offset: int = 0) -> int:
    """Unpack a 64-bit unsigned integer from *buf* at *offset*."""
    return _uint64struct.unpack_from(buf, offset)[0]


def checkread(stream: BinaryIO, n: int) -> bytes:
    """Read exactly *n* bytes from *stream*.

    A ParseError is raised if less than *n* bytes are available.

    """
    data = stream.read(n)
    if len(data) < n:
        raise ParseError("unexpected end of file")
    return data
