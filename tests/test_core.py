import unittest

import base62


class TestEncode(unittest.TestCase):
    def test_zero(self):
        self.assertEqual(base62.encode(0), "0")

    def test_single_digit_values(self):
        # Values 0..61 map to individual alphabet characters.
        self.assertEqual(base62.encode(1), "1")
        self.assertEqual(base62.encode(10), "A")
        self.assertEqual(base62.encode(35), "Z")
        self.assertEqual(base62.encode(36), "a")
        self.assertEqual(base62.encode(61), "z")

    def test_first_multi_digit(self):
        # 62 is the first value that needs two characters: "10".
        self.assertEqual(base62.encode(62), "10")

    def test_known_values(self):
        cases = {
            63: "11",
            124: "20",
            3843: "zz",
            3844: "100",
            238327: "zzz",
            238328: "1000",
        }
        for value, expected in cases.items():
            with self.subTest(value=value):
                self.assertEqual(base62.encode(value), expected)

    def test_negative_raises(self):
        with self.assertRaises(ValueError):
            base62.encode(-1)

    def test_wrong_type_raises(self):
        with self.assertRaises(TypeError):
            base62.encode("7")  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            base62.encode(3.0)  # type: ignore[arg-type]


class TestDecode(unittest.TestCase):
    def test_zero(self):
        self.assertEqual(base62.decode("0"), 0)

    def test_single_chars(self):
        self.assertEqual(base62.decode("1"), 1)
        self.assertEqual(base62.decode("A"), 10)
        self.assertEqual(base62.decode("Z"), 35)
        self.assertEqual(base62.decode("a"), 36)
        self.assertEqual(base62.decode("z"), 61)

    def test_known_values(self):
        cases = {
            "10": 62,
            "11": 63,
            "20": 124,
            "zz": 3843,
            "100": 3844,
            "zzz": 238327,
            "1000": 238328,
        }
        for text, expected in cases.items():
            with self.subTest(text=text):
                self.assertEqual(base62.decode(text), expected)

    def test_empty_raises(self):
        with self.assertRaises(ValueError):
            base62.decode("")

    def test_invalid_char_raises(self):
        with self.assertRaises(ValueError):
            base62.decode("1-")
        with self.assertRaises(ValueError):
            base62.decode("+")
        with self.assertRaises(ValueError):
            base62.decode("AB!")

    def test_wrong_type_raises(self):
        with self.assertRaises(TypeError):
            base62.decode(7)  # type: ignore[arg-type]
        with self.assertRaises(TypeError):
            base62.decode(b"10")  # type: ignore[arg-type]


class TestRoundTrip(unittest.TestCase):
    def test_round_trip_range(self):
        # Sample values across magnitudes rather than every integer, to keep
        # the test fast while still exercising the carry logic at each width.
        for value in [0, 1, 61, 62, 63, 3843, 3844, 238327, 238328,
                      14776335, 14776336, 91613284715, 91613284716,
                      2**64, 2**128]:
            with self.subTest(value=value):
                self.assertEqual(base62.decode(base62.encode(value)), value)

    def test_lexicographic_order_for_equal_length(self):
        # Consecutive integers of the same encoding length must produce
        # lexicographically ordered strings. This is the property callers rely
        # on when using these as sortable ids.
        encs = [base62.encode(n) for n in range(62, 62 + 100)]
        for a, b in zip(encs, encs[1:]):
            self.assertLess(a, b)


class TestCharset(unittest.TestCase):
    def test_charset_length(self):
        self.assertEqual(len(base62.CHARSET), 62)

    def test_charset_unique(self):
        self.assertEqual(len(set(base62.CHARSET)), 62)

    def test_charset_order(self):
        # The order is part of the documented contract; pin it so a careless
        # edit is caught immediately.
        self.assertEqual(
            base62.CHARSET,
            "0123456789"
            "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            "abcdefghijklmnopqrstuvwxyz",
        )


if __name__ == "__main__":
    unittest.main()
