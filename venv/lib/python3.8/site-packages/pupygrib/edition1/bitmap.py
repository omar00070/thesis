"""Bit-map section of edition 1 GRIB messages."""

import numpy

from pupygrib import fields
from pupygrib.base import BaseField, BaseSection


class BitMapField(BaseField["BitMapSection", numpy.ndarray]):
    def get_value(self, section: "BitMapSection", offset: int) -> numpy.ndarray:
        if section.tableReference > 0:
            raise NotImplementedError("pupygrib does not support catalogued bit-maps")

        bitmap = numpy.frombuffer(section.buf, dtype="u1", offset=offset)
        unused_bits = section.numberOfUnusedBitsAtEndOfSection3
        return numpy.unpackbits(bitmap)[:-unused_bits]


class BitMapSection(BaseSection):
    """The bit-map section (3) of an edition 1 GRIB message."""

    section3Length = fields.Uint24Field(1)
    numberOfUnusedBitsAtEndOfSection3 = fields.Uint8Field(4)
    tableReference = fields.Uint16Field(5)
    bitmap = BitMapField(7)
