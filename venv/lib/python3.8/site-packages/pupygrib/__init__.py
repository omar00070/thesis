"""A light-weight pure Python GRIB reader."""

import io
from typing import BinaryIO, Iterator, Optional, Type

import pkg_resources

from pupygrib import binary
from pupygrib.base import Message as Message
from pupygrib.edition1 import Edition1 as Edition1
from pupygrib.edition2 import Edition2 as Edition2
from pupygrib.exceptions import ParseError as ParseError

__version__ = pkg_resources.get_distribution("pupygrib").version


def _strip_zeros(stream: BinaryIO, n: int) -> None:
    # Remove up to n leading zeros from *stream*.
    stream.seek(-len(stream.read(n).lstrip(b"\0")), io.SEEK_CUR)


def _try_read_message(stream: BinaryIO) -> Optional[Message]:
    # Try to read one GRIB message from *stream*.  If end-of-file is
    # encountered immediately, return None.  If end-of-file is reached
    # while parsing the message or if the parsing fails for some other
    # reason, a ParseError is raised.

    # Skip initial zeros since some GRIB files seem to be padded with
    # zeros between the messages.
    _strip_zeros(stream, 256)

    # Check that we have a GRIB message
    startpos = stream.tell()
    magic = stream.read(4)
    if not magic:
        return None
    if magic != b"GRIB":
        raise ParseError("not a GRIB message")

    # Find the edition and length
    header = binary.checkread(stream, 4)
    edition = binary.unpack_uint8_from(header, 3)
    message_class: Type[Message]
    if edition == 1:
        length = binary.unpack_uint24_from(header)
        message_class = Edition1
    elif edition == 2:
        length = binary.unpack_uint64_from(binary.checkread(stream, 8))
        message_class = Edition2
    else:
        raise ParseError("unknown edition number '{}'".format(edition))

    # Read and check the end of the message
    stream.seek(startpos)
    data = binary.checkread(stream, length)
    if data[-4:] != b"7777":
        raise ParseError("end-of-message marker not found")

    # Create and return the message instance
    return message_class(data, getattr(stream, "name", None))


def read(stream: BinaryIO) -> Iterator[Message]:
    """Iterate over a GRIB file's messages.

    *stream* should be a readable binary file-like object that supports
    random access.  The easiest way to obtain such an object is simply
    to use the built-in open() function with mode set to 'rb'.

    """
    msg = _try_read_message(stream)
    while msg:
        yield msg
        msg = _try_read_message(stream)
