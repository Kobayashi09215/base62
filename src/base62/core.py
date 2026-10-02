"""Core encode/decode logic.

The alphabet is GMP-style: 0-9 then A-Z then a-z. This keeps the order such
that lexicographic sort of same-length encodings matches numeric order, which
matters when the output is used as a sortable short id.

Decode explicitly rejects empty input and input containing bytes outside the
known alphabet. We raise ValueError rather than returning a sentinel because
the most common call site is request handling, where a bad id should surface as
a 400 not a silent None.
"""

from __future__ import annotations

# Ordered so that for any two encodings of equal length, lexicographic order
# equals numeric order. This is a property callers rely on for short ids that
# sort correctly, so do not rearrange.
CHARSET: str = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

_INDEX = {c: i for i, c in enumerate(CHARSET)}
_BASE = len(CHARSET)  # 62


def encode(value: int) -> str:
    """Encode a non-negative integer into a base62 string.

    Zero encodes to "0" rather than the empty string, because an empty
    identifier is never useful in practice and would force every consumer to
    special-case it.

    Raises ValueError for negative input, since base62 has no canonical
    representation for negative numbers in this alphabet.
    """
    if not isinstance(value, int):
        raise TypeError(f"encode() expects int, got {type(value).__name__}")
    if value < 0:
        raise ValueError("encode() requires a non-negative integer")
    if value == 0:
        return "0"

    digits: list[str] = []
    n = value
    while n > 0:
        n, rem = divmod(n, _BASE)
        digits.append(CHARSET[rem])
    return "".join(reversed(digits))


def decode(text: str) -> int:
    """Decode a base62 string back to the original integer.

    Raises ValueError on empty input or on any character outside the
    alphabet. We do not accept leading-whitespace or signs; the alphabet is
    fixed and a stray character almost always indicates a caller bug or a
    truncated id from a URL, both of which should fail loudly.
    """
    if not isinstance(text, str):
        raise TypeError(f"decode() expects str, got {type(text).__name__}")
    if not text:
        raise ValueError("decode() requires a non-empty string")

    result = 0
    for ch in text:
        try:
            result = result * _BASE + _INDEX[ch]
        except KeyError:
            raise ValueError(f"invalid base62 character: {ch!r}") from None
    return result
