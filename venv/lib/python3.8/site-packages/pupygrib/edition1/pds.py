"""Product definition sections of edition 1 GRIB messages."""

from typing import Tuple, Union

import numpy

from pupygrib import binary, fields
from pupygrib.base import BaseField, BaseSection

Level = Union[Tuple[int, int], int]


class LevelField(BaseField["ProductDefinitionSection", Level]):
    """Height, pressure, etc. of levels."""

    split_level_types = {101, 104, 106, 108, 110, 112, 114, 116, 120, 121, 128, 141}

    def get_value(self, section: "ProductDefinitionSection", offset: int = 10) -> Level:
        if section.indicatorOfTypeOfLevel in self.split_level_types:
            l1 = binary.unpack_uint8_from(section.buf, offset)
            l2 = binary.unpack_uint8_from(section.buf, offset + 1)
            return (l1, l2)
        else:
            return binary.unpack_uint16_from(section.buf, offset)


class ProductDefinitionSection(BaseSection):
    """The product definition section (1) of an edition 1 GRIB message."""

    section1Length = fields.Uint24Field(1)
    table2Version = fields.Uint8Field(4)
    centre = fields.Uint8Field(5)
    generatingProcessIdentifier = fields.Uint8Field(6)
    gridDefinition = fields.Uint8Field(7)
    section1Flags = fields.Uint8Field(8)
    indicatorOfParameter = fields.Uint8Field(9)
    indicatorOfTypeOfLevel = fields.Uint8Field(10)
    level = LevelField(11)
    yearOfCentury = fields.Uint8Field(13)
    month = fields.Uint8Field(14)
    day = fields.Uint8Field(15)
    hour = fields.Uint8Field(16)
    minute = fields.Uint8Field(17)
    unitOfTimeRange = fields.Uint8Field(18)
    P1 = fields.Uint8Field(19)
    P2 = fields.Uint8Field(20)
    timeRangeIndicator = fields.Uint8Field(21)
    numberIncludedInAverage = fields.Uint16Field(22)
    numberMissingFromAveragesOrAccumulations = fields.Uint8Field(24)
    centuryOfReferenceTimeOfData = fields.Uint8Field(25)
    subCentre = fields.Uint8Field(26)
    decimalScaleFactor = fields.Int16Field(27)

    def _scale_values(self, values: numpy.ndarray) -> numpy.ndarray:
        return 10 ** -self.decimalScaleFactor * values


class LocalProductDefinitionSection(ProductDefinitionSection):
    """A local product definition section if an edition 1 GRIB message."""

    localDefinitionNumber = fields.Uint8Field(41)


class MatchV1ProductSection(LocalProductDefinitionSection):
    """A MATCH v1.0 product definition section of a GRIB 1 message."""

    generatingProcess = fields.Uint8Field(42)
    sort = fields.Uint8Field(43)
    timeRepres = fields.Uint8Field(44)
    landType = fields.Uint8Field(45)
    suplScale = fields.Int16Field(46)
    molarMass = fields.Uint16Field(48)
    logTransform = fields.Uint8Field(50)
    threshold = fields.Int16Field(51)
    totalSizeClasses = fields.Uint8Field(60)
    sizeClassNumber = fields.Uint8Field(61)
    integerScaleFactor = fields.Int8Field(62)
    lowerRange = fields.Uint16Field(63)
    upperRange = fields.Uint16Field(65)
    meanSize = fields.Uint16Field(67)
    STDV = fields.Uint16Field(69)

    def _scale_values(self, values: numpy.ndarray) -> numpy.ndarray:
        values = super(MatchV1ProductSection, self)._scale_values(values)
        if self.logTransform:
            values = numpy.exp(values)
        return values


def get_section(buf: memoryview, offset: int, length: int) -> ProductDefinitionSection:
    """Return a new section 1 of the correct type from *buf* at *offset*."""
    if length <= 40:
        return ProductDefinitionSection(buf, offset, length)

    proddef = LocalProductDefinitionSection(buf, offset, length)
    try:
        sectionclass = {(82, 0, 2): MatchV1ProductSection}[
            (proddef.centre, proddef.subCentre, proddef.localDefinitionNumber)
        ]
    except KeyError:
        return proddef
    else:
        return sectionclass(buf, offset, length)
