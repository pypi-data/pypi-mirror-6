# encoding: utf-8

import math
import sys
try:
    import unittest2 as unittest
except ImportError:
    import unittest

from pakker.php import dumps, loads


hunt_leaks = hasattr(sys, "gettotalrefcount")
if hunt_leaks:
    import gc


# Helpers for py3k compat

try:
    xrange
except NameError:
    xrange = range

    def u(s):
        return s
else:
    def u(s):
        return s.decode("unicode-escape")


# Leak hunter

def _is_not_suite(test):
    try:
        iter(test)
    except TypeError:
        return True
    return False


def _cleanup():
    sys._clear_type_cache()
    gc.collect()

def _hunt(test):
    def test_wrapper(*args, **kwargs):
        deltas = []
        _cleanup()
        for i in xrange(5):
            before = sys.gettotalrefcount()
            test(*args, **kwargs)
            _cleanup()
            after = sys.gettotalrefcount()
            if i > 2:
                deltas.append(after - before)
        if any(deltas):
            print("{0!r} leaks: {1}".format(test, deltas))
    return test_wrapper

class TestSuite(unittest.TestSuite):
    def __iter__(self):
        for test in super(TestSuite, self).__iter__():
            if hunt_leaks and _is_not_suite(test):
                yield _hunt(test)
            else:
                yield test

# Tests

class UnserializeTests(unittest.TestCase):
    def test_null(self):
        data = loads(b'n;')
        self.assertIsNone(data)

    def test_bool_true(self):
        data = loads(b'b:1;')
        self.assertTrue(data)
        data = loads(b'b:42;')
        self.assertTrue(data)

    def test_bool_false(self):
        data = loads(b'b:0;')
        self.assertFalse(data)

    def test_integer(self):
        data = loads(b'i:42;')
        self.assertEqual(data, 42)

    def test_negative_integer(self):
        data = loads(b'i:-42;')
        self.assertEqual(data, -42)

    def test_float(self):
        data = loads(b'd:4.2;')
        self.assertEqual(data, 4.2)

    def test_nan(self):
        data = loads(b'd:NAN;')
        self.assertTrue(math.isnan(data))

    def test_bytes(self):
        data = loads(b's:5:"sp\xc3\xa4m";', decode_strings=False)
        self.assertEqual(data, b"sp\xc3\xa4m")

    def test_bytes_null_byte(self):
        data = loads(b's:1:"\x00";')
        self.assertEqual(data, b"\x00")

    def test_unicode(self):
        data = loads(b's:5:"sp\xc3\xa4m";', decode_strings=True)
        self.assertEqual(data, u("sp\xe4m"))

    def test_empty_array(self):
        data = loads(b'a:0:{}')
        self.assertEqual(data, {})

    def test_nested_array(self):
        data = loads(b'a:1:{i:0;a:0:{}}')
        self.assertEqual(data, {0: {}})

    def test_array(self):
        data = loads(b'a:1:{s:4:"spam";s:4:"eggs";}')
        self.assertEqual(data, {b"spam": b"eggs"})

    def test_array_unicode(self):
        data = loads(b'a:1:{s:4:"spam";s:4:"eggs";}', decode_strings=True)
        self.assertEqual(data, {u("spam"): u("eggs")})


class ErrorHandlingTests(unittest.TestCase):
    def test_empty(self):
        with self.assertRaises(ValueError):
            loads(b"")

    def test_invalid_opcode(self):
        with self.assertRaises(ValueError):
            loads(b"x")

    def test_unterminated_null(self):
        with self.assertRaises(ValueError):
            loads(b"n")

    def test_decode_string_trueish_value_raises(self):
        class Spam(object):
            def __nonzero__(self):
                raise TypeError
            __bool__ = __nonzero__

        with self.assertRaises(TypeError):
            loads(b'n;', decode_strings=Spam())

    def test_recursive_array(self):
        "Verify that a deeply nested object doesn't result in a segfault."
        with self.assertRaises(RuntimeError):
            # Note: The actual serialized data is incomplete
            loads(b"a:1:{" * 100000)


class BoolErrorHandling(unittest.TestCase):
    def test_only_opcode(self):
        with self.assertRaises(ValueError):
            loads(b'b')

    def test_missing_opening_colon(self):
        with self.assertRaises(ValueError):
            loads(b'b1;')

    def test_missing_terminator(self):
        with self.assertRaises(ValueError):
            loads(b'b:1')

    def test_missing_number(self):
        with self.assertRaises(ValueError):
            loads(b'b:;')

    def test_number_malformed(self):
        with self.assertRaises(ValueError):
            loads(b'b:spam;')


class IntErrorHandling(unittest.TestCase):
    def test_only_opcode(self):
        with self.assertRaises(ValueError):
            loads(b'i')

    def test_missing_opening_colon(self):
        with self.assertRaises(ValueError):
            loads(b'i1;')

    def test_missing_terminator(self):
        with self.assertRaises(ValueError):
            loads(b'i:1')

    def test_missing_number(self):
        with self.assertRaises(ValueError):
            loads(b'i:;')

    def test_number_malformed(self):
        with self.assertRaises(ValueError):
            loads(b'i:spam;')

class FloatErrorHandling(unittest.TestCase):
    def test_only_opcode(self):
        with self.assertRaises(ValueError):
            loads(b'd')

    def test_missing_terminator(self):
        with self.assertRaises(ValueError):
            loads(b'd:4.2')

    def test_missing_number(self):
        with self.assertRaises(ValueError):
            loads(b'd:;')

    def test_number_malformed(self):
        with self.assertRaises(ValueError):
            loads(b'd:spam;')


class StringErrorHandling(unittest.TestCase):
    def test_missing_opening_quote(self):
        with self.assertRaises(ValueError):
            loads(b's:1:a";')

    def test_missing_closing_quote(self):
        with self.assertRaises(ValueError):
            loads(b's:1:"a;')

    def test_missing_terminator(self):
        with self.assertRaises(ValueError):
            loads(b's:1:"a"')

    def test_string_size_long_overflow(self):
        with self.assertRaises(OverflowError):
            # Note: the string is incomplete
            loads(b's:' + str(sys.maxsize + 1).encode() + b':"')

    def test_wrong_string_size(self):
        with self.assertRaises(ValueError):
            loads(b's:3:"ab";')
        with self.assertRaises(ValueError):
            loads(b's:3:"abcd";')

    def test_missing_string_size(self):
        with self.assertRaises(ValueError):
            loads(b's::"abcd";')

    def test_string_size_not_a_number(self):
        with self.assertRaises(ValueError):
            loads(b's:spam:"abcd";')

    def test_negative_size(self):
        with self.assertRaises(ValueError):
            loads(b's:-10:"spam";')

    def test_invalid_encoding(self):
        data = loads(b's:1:"\xc3";', decode_strings=True)
        self.assertEqual(data, u(""))


class ArrayErrorHandling(unittest.TestCase):
    def test_missing_closing_paren(self):
        with self.assertRaises(ValueError):
            loads(b'a:0:{')

    def test_incomplete_nested_array(self):
        with self.assertRaises(ValueError):
            loads(b'a:1:{i:0;a:0:{}')

    def test_missing_value(self):
        with self.assertRaises(ValueError):
            loads(b'a:1:{i:0;}')

    def test_incomplete_value(self):
        with self.assertRaises(ValueError):
            loads(b'a:1:{i:0;n}')

    def test_size_not_a_number(self):
        with self.assertRaises(ValueError):
            loads(b'a:spam:{};')

    def test_negative_size(self):
        with self.assertRaises(ValueError):
            print(loads(b'a:-10:{};'))

    def test_invalid_size(self):
        with self.assertRaises(ValueError):
            loads(b'a:42:{};')

    def test_overflow(self):
        with self.assertRaises(OverflowError):
            loads(b'a:' + str(sys.maxsize // 2).encode() + b':{};')


class SerializeTests(unittest.TestCase):
    def test_None(self):
        self.assertEqual(dumps(None), b'n;')

    def test_bool(self):
        self.assertEqual(dumps(True), b'b:1;')
        self.assertEqual(dumps(False), b'b:0;')

    def test_int(self):
        self.assertEqual(dumps(0), b'i:0;')
        self.assertEqual(dumps(42), b'i:42;')

    def test_long(self):
        data = dumps(12345678901234567812345678123456789)
        self.assertEqual(data, b'i:12345678901234567812345678123456789;')

    def test_float(self):
        self.assertEqual(dumps(-0.0), b'd:-0.0;')
        self.assertEqual(dumps(4.2), b'd:4.2;')

    def test_string(self):
        self.assertEqual(dumps("spam"), b's:4:"spam";')


class RoundTripTests(unittest.TestCase):
    def test_array(self):
        D = dict(zip([1, None, 0.1], range(3)))
        self.assertEqual(loads(dumps(D)), D)

    def test_None(self):
        self.assertIsNone(loads(dumps(None)))

    def test_bool(self):
        self.assertIs(loads(dumps(True)), True)
        self.assertIs(loads(dumps(False)), False)

    def test_int(self):
        self.assertEqual(loads(dumps(0)), 0)
        self.assertEqual(loads(dumps(-1)), -1)
        self.assertEqual(loads(dumps(42)), 42)
        n = 12345678901234567812345678123456789
        self.assertEqual(loads(dumps(n)), n)
        self.assertEqual(loads(dumps(-n)), -n)

    def test_bytes(self):
        self.assertEqual(loads(dumps(b'sp\xc3\xa4m')), b'sp\xc3\xa4m')
        self.assertEqual(loads(dumps(b'\x00')), b'\x00')

    def test_string(self):
        self.assertEqual(loads(dumps("spam"), decode_strings=True), "spam")
        self.assertEqual(loads(dumps("späm"), decode_strings=True), u("sp\xe4m"))


def test():
    loader = unittest.TestLoader()
    loader.suiteClass = TestSuite
    test = loader.discover(__name__)
    runner = unittest.TextTestRunner()
    result = runner.run(test)
    return not result.wasSuccessful()

if __name__ == "__main__":
    from pakker.tests.test_php import test
    sys.exit(test())
