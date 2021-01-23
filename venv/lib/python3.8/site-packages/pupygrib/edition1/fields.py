"""Fields for edition 1 GRIB messages."""

from pupygrib import binary, fields
from pupygrib.base import BaseSection


class FloatField(fields.GeneralField[float]):
    """A 32-bit GRIB 1 floating point field."""

    def get_value(self, section: BaseSection, offset: int) -> float:
        return binary.unpack_grib1float_from(section.buf, offset)
