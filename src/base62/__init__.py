"""Base62: small, dependency-free encoding of integers as short URL-safe strings."""

from .core import encode, decode, CHARSET

__all__ = ["encode", "decode", "CHARSET"]
__version__ = "1.0.0"
