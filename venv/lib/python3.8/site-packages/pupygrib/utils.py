"""Utility types for pupygrib."""

import sys
from typing import Callable, TypeVar, Union

if sys.version_info >= (3, 8):
    from functools import cached_property as cached_property
else:
    from functools import lru_cache

    T = TypeVar("T")

    def cached_property(f: Callable[..., T]) -> property:
        return property(lru_cache(maxsize=None)(f))


ReadableBuffer = Union[bytes, bytearray, memoryview]
