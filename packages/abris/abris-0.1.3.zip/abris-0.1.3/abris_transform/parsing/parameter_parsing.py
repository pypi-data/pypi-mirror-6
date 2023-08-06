import unittest

from abris_transform import string_aliases


def parse_parameter(value):
    """
    @return: The best approximation of a type of the given value.
    """
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            if value in string_aliases.true_boolean_aliases:
                return True
            elif value in string_aliases.false_boolean_aliases:
                return False
            else:
                return str(value)


class ParseParameterTest(unittest.TestCase):

    def test_integer(self):
        integer = parse_parameter("1")
        self.assertIsInstance(integer, int)

    def test_float(self):
        float_numbers = [
            parse_parameter("1.001"),
            parse_parameter("1."),
            parse_parameter(".001")]
        for float_number in float_numbers:
            self.assertIsInstance(float_number, float)

    def test_true_boolean(self):
        true_booleans = [
            parse_parameter("True"),
            parse_parameter("true"),
        ]
        for boolean in true_booleans:
            self.assertIsInstance(boolean, bool)
            self.assertTrue(boolean)

    def test_false_boolean(self):
        false_booleans = [
            parse_parameter("False"),
            parse_parameter("false"),
        ]
        for boolean in false_booleans:
            self.assertIsInstance(boolean, bool)
            self.assertFalse(boolean)

    def test_string(self):
        strings = [
            parse_parameter("Some random text"),
            parse_parameter("more_text")
        ]
        for string in strings:
            self.assertIsInstance(string, str)

