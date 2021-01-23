"""An edition 2 GRIB message."""

import datetime
from typing import Optional

import numpy as np

from pupygrib import binary, fields
from pupygrib.base import BaseSection, Message
from pupygrib.utils import cached_property


class IndicatorSection(BaseSection):
    """The indicator section (0) of an edition 2 GRIB message."""

    identifier = fields.BytesField(1, 4)
    discipline = fields.Uint8Field(7)
    editionNumber = fields.Uint8Field(8)
    totalLength = fields.Uint64Field(9)


class IdentificationSection(BaseSection):
    """The identification section (1) of an edition 2 GRIB message."""

    section1Length = fields.Uint32Field(1)
    numberOfSection = fields.Uint8Field(5)
    centre = fields.Uint16Field(6)
    subCentre = fields.Uint16Field(8)
    tablesVersion = fields.Uint8Field(10)
    localTablesVersion = fields.Uint8Field(11)
    significanceOfReferenceTime = fields.Uint8Field(12)
    year = fields.Uint16Field(13)
    month = fields.Uint8Field(15)
    day = fields.Uint8Field(16)
    hour = fields.Uint8Field(17)
    minute = fields.Uint8Field(18)
    second = fields.Uint8Field(19)
    productionStatusOfProcessedData = fields.Uint8Field(20)
    typeOfProcessedData = fields.Uint8Field(21)


class LocalUseSection(BaseSection):
    """The local use section (2) of an edition 2 GRIB message."""

    section2Length = fields.Uint32Field(1)
    numberOfSection = fields.Uint8Field(5)


class GridDescriptionSection(BaseSection):
    """The grid description section (3) of an edition 2 GRIB message."""

    section3Length = fields.Uint32Field(1)
    numberOfSection = fields.Uint8Field(5)
    sourceOfGridDefinition = fields.Uint8Field(6)
    numberOfDataPoints = fields.Uint32Field(7)
    numberOfOctetsForNumberOfPoints = fields.Uint8Field(11)
    interpretationOfNumberOfPoints = fields.Uint8Field(12)
    gridDefinitionTemplateNumber = fields.Uint16Field(13)


class ProductDefinitionSection(BaseSection):
    """The product definition section (4) of an edition 2 GRIB message."""

    section4Length = fields.Uint32Field(1)
    numberOfSection = fields.Uint8Field(5)
    NV = fields.Uint16Field(6)
    productDefinitionTemplateNumber = fields.Uint16Field(8)


class DataRepresentationSection(BaseSection):
    """The data representation section (5) of an edition 2 GRIB message."""

    section5Length = fields.Uint32Field(1)
    numberOfSection = fields.Uint8Field(5)
    numberOfValues = fields.Uint32Field(6)
    dataRepresentationTemplateNumber = fields.Uint16Field(10)


class BitMapSection(BaseSection):
    """The bit-map section (6) of an edition 2 GRIB message."""

    section6Length = fields.Uint32Field(1)
    numberOfSection = fields.Uint8Field(5)
    bitMapIndicator = fields.Uint8Field(6)


class DataSection(BaseSection):
    """The data section (7) of an edition 2 GRIB message."""

    section7Length = fields.Uint32Field(1)
    numberOfSection = fields.Uint8Field(5)


class EndSection(BaseSection):
    """The end section (8) of an edition 2 GRIB message."""

    endOfMessage = fields.BytesField(1, 4)


class Edition2(Message):
    """An edition 2 GRIB message."""

    edition = 2

    def get_coordinates(self) -> np.ndarray:
        raise NotImplementedError(
            "Coordinate unpacking is not implemented for edition 2 messages"
        )

    def get_time(self) -> datetime.datetime:
        return datetime.datetime(
            self.ids.year,
            self.ids.month,
            self.ids.day,
            self.ids.hour,
            self.ids.minute,
            self.ids.second,
        )

    def get_values(self) -> np.ndarray:
        raise NotImplementedError(
            "Value unpacking is not implemented for edition 2 messages"
        )

    @cached_property
    def is_(self) -> IndicatorSection:
        return IndicatorSection(self.buf, 0, 16)

    @cached_property
    def ids(self) -> IdentificationSection:
        prevsection = self.is_
        length = binary.unpack_uint32_from(self.buf, prevsection.end)
        return IdentificationSection(self.buf, prevsection.end, length)

    @cached_property
    def loc(self) -> Optional[LocalUseSection]:
        prevsection = self.ids
        number = binary.unpack_uint8_from(self.buf, prevsection.end + 4)
        if number != 2:
            return None
        length = binary.unpack_uint32_from(self.buf, prevsection.end)
        return LocalUseSection(self.buf, prevsection.end, length)

    @cached_property
    def gds(self) -> GridDescriptionSection:
        prevsection = self.loc or self.ids
        length = binary.unpack_uint32_from(self.buf, prevsection.end)
        return GridDescriptionSection(self.buf, prevsection.end, length)

    @cached_property
    def pds(self) -> ProductDefinitionSection:
        prevsection = self.gds
        length = binary.unpack_uint32_from(self.buf, prevsection.end)
        return ProductDefinitionSection(self.buf, prevsection.end, length)

    @cached_property
    def drs(self) -> Optional[DataRepresentationSection]:
        prevsection = self.pds
        number = binary.unpack_uint8_from(self.buf, prevsection.end + 4)
        if number != 5:
            return None
        length = binary.unpack_uint32_from(self.buf, prevsection.end)
        return DataRepresentationSection(self.buf, prevsection.end, length)

    @cached_property
    def bitmap(self) -> BitMapSection:
        prevsection = self.drs or self.pds
        length = binary.unpack_uint32_from(self.buf, prevsection.end)
        return BitMapSection(self.buf, prevsection.end, length)

    @cached_property
    def data(self) -> DataSection:
        prevsection = self.bitmap
        length = binary.unpack_uint32_from(self.buf, prevsection.end)
        return DataSection(self.buf, prevsection.end, length)

    @cached_property
    def end(self) -> EndSection:
        return EndSection(self.buf, self.data.end, 4)

    def __getitem__(self, index: int) -> Optional[BaseSection]:
        """Return a section of the GRIB message with the given *index*.

        If *index* is a valid section for the current GRIB edition but
        not included in the message, None is returned.

        """
        if index == 0:
            return self.is_
        if index == 1:
            return self.ids
        if index == 2:
            return self.loc
        if index == 3:
            return self.gds
        if index == 4:
            return self.pds
        if index == 5:
            return self.drs
        if index == 6:
            return self.bitmap
        if index == 7:
            return self.data
        if index == 8:
            return self.end
        raise IndexError("no such section")
