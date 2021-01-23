"""An edition 1 GRIB message."""

import datetime
from typing import Optional

import numpy

from pupygrib import binary
from pupygrib import fields as basefields  # Python gets confused without alias
from pupygrib.base import BaseSection, Message
from pupygrib.edition1 import bds, bitmap, gds, pds
from pupygrib.utils import cached_property


class IndicatorSection(BaseSection):
    """The indicator section (0) of an edition 1 GRIB message."""

    identifier = basefields.BytesField(1, 4)
    totalLength = basefields.Uint24Field(5)
    editionNumber = basefields.Uint8Field(8)


class EndSection(BaseSection):
    """The end section (5) of an edition 1 GRIB message."""

    endOfMessage = basefields.BytesField(1, 4)


class Edition1(Message):
    """An edition 1 GRIB message."""

    edition = 1

    def get_coordinates(self) -> numpy.ndarray:
        if self.gds is None:
            raise NotImplementedError("pupygrib does not support catalogued grids")
        return self.gds._get_coordinates()

    def get_time(self) -> datetime.datetime:
        century = self.pds.centuryOfReferenceTimeOfData
        if self.pds.yearOfCentury == 100:
            year = century * 100
        else:
            year = (century - 1) * 100 + self.pds.yearOfCentury
        return datetime.datetime(
            year, self.pds.month, self.pds.day, self.pds.hour, self.pds.minute
        )

    def get_values(self) -> numpy.ndarray:
        values = self.pds._scale_values(self.bds._unpack_values())
        if self.bitmap:
            mask = ~numpy.array(self.bitmap.bitmap, dtype=bool)
            mvalues = numpy.empty(len(mask), dtype=float)
            mvalues[~mask] = values
            values = numpy.ma.array(mvalues, mask=mask)
        if self.gds:
            values = self.gds._order_values(values)
        return values

    @cached_property
    def is_(self) -> IndicatorSection:
        return IndicatorSection(self.buf, 0, 8)

    @cached_property
    def pds(self) -> pds.ProductDefinitionSection:
        offset = self.is_.end
        length = binary.unpack_uint24_from(self.buf, offset)
        return pds.get_section(self.buf, offset, length)

    @cached_property
    def gds(self) -> Optional[gds.GridDescriptionSection]:
        if not self.pds.section1Flags & 0x80:
            return None

        offset = self.pds.end
        length = binary.unpack_uint24_from(self.buf, offset)
        return gds.get_section(self.buf, offset, length)

    @cached_property
    def bitmap(self) -> Optional[bitmap.BitMapSection]:
        if not self.pds.section1Flags & 0x40:
            return None

        offset = (self.gds or self.pds).end
        length = binary.unpack_uint24_from(self.buf, offset)
        return bitmap.BitMapSection(self.buf, offset, length)

    @cached_property
    def bds(self) -> bds.BinaryDataSection:
        offset = (self.bitmap or self.gds or self.pds).end
        length = binary.unpack_uint24_from(self.buf, offset)
        return bds.get_section(self.buf, offset, length)

    @cached_property
    def end(self) -> EndSection:
        return EndSection(self.buf, self.bds.end, 4)

    def __getitem__(self, index: int) -> Optional[BaseSection]:
        """Return a section of the GRIB message with the given *index*.

        If *index* is a valid section for the current GRIB edition but
        not included in the message, None is returned.

        """
        if index == 0:
            return self.is_
        if index == 1:
            return self.pds
        if index == 2:
            return self.gds
        if index == 3:
            return self.bitmap
        if index == 4:
            return self.bds
        if index == 5:
            return self.end
        raise IndexError("no such section")
