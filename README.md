# Base62

Encode non-negative integers as short, URL-safe base62 strings, and decode them back. Pure standard-library Python, no dependencies.

```python
import base62

encoded = base62.encode(238327)   # "ZZZ"
decoded = base62.decode("ZZZ")     # 238327
```

Exported names: `encode`, `decode`, and `CHARSET`.

## Why this exists

Database primary keys and sequential integers make poor URL identifiers: they are long, enumerable by incrementing, and reveal volume. Base62 maps an integer onto the 62 unreserved URL characters `[0-9A-Za-z]`, so the result drops into a path segment with no percent-encoding. `3844` becomes `100`; `238328` becomes `1000`. The trade-off is reversibility: anyone holding the alphabet can recover the original integer, so this is an obfuscation of scale, not encryption.

The alphabet is ordered `0-9 A-Z a-z` (GMP order, not RFC 4648). The specific property this buys is that two encodings of equal length sort lexicographically in the same order as their underlying integers, which matters if the strings are used as sortable keys.

## Edge cases you will hit

- `encode(0)` returns `"0"`, not the empty string. An empty identifier is never usable in a URL path.
- `encode` rejects negative integers and non-int inputs with `ValueError` / `TypeError`. There is no signed representation.
- `decode` raises `ValueError` on empty input or any character outside the 62-character alphabet. It does not tolerate whitespace, `+`, `/`, `=`, or any base64 character. A bad id should fail loudly at the boundary, not become a silent `None`.
- There is no support for fixed-width padding. If you need ids of a constant width, left-pad with `"0"` yourself and strip before decoding.

## Design notes

The window stores values eagerly rather than keeping running aggregates. Running
sums drift with floating point over long streams, and recomputing from a small
buffer is cheap enough that the drift is not worth the speed.

## Performance

The window keeps a bounded buffer, so `push` is constant time and memory does not
grow with the length of the stream. `peak` and `trough` are linear in the window
size, which is the trade that keeps `push` cheap.

