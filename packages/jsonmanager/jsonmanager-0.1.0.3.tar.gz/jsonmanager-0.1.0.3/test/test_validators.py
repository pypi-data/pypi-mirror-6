""" Tests for `validators` module. """

import unittest
from unittest.mock import (
    patch,
    sentinel
    )

from jsonmanager.exceptions import ValidationError
from jsonmanager.validators import (
    OneOf,
    Range,
    Regex,
    Required,
    )


class TestOneOf(unittest.TestCase):
    """ `OneOf` validator. """

    def test_yes_in_passes(self):
        """ `data` is in the collection. """
        validator = OneOf(sentinel.a, sentinel.target, sentinel.c)
        validator(sentinel.schema, sentinel.target)

    def test_not_in_raises(self):
        """ `data` is not in the collection. """
        validator = OneOf(sentinel.a, sentinel.b)
        with self.assertRaises(ValidationError):
            validator(sentinel.schema, sentinel.target)

class TestRange(unittest.TestCase):
    """ `Range` validator. """

    def setUp(self):
        self.validator = Range(1, 3)

    def test_in_range(self):
        """ `data` in range passes. """
        self.validator(sentinel.schema, 2)

    def test_lowest_inclusive(self):
        """ Range includes lowest value. """
        self.validator(sentinel.schema, 1)

    def test_highest_inclusive(self):
        """ Range includes highest value. """
        self.validator(sentinel.schema, 3)

    def test_out_of_range(self):
        """ `data` out of range raises `ValidationError`. """
        with self.assertRaises(ValidationError):
            self.validator(sentinel.schema, 4)

@patch('jsonmanager.validators.re.match')
class TestRegex(unittest.TestCase):
    """ `Regex` validator. """

    def setUp(self):
        self.validator = Regex(sentinel.pattern)

    def test_match_succeeds(self, mock_re_match):
        """ `data` matches the regular expression. """
        mock_re_match.return_value = True
        self.validator(sentinel.schema, sentinel.data)
        mock_re_match.assert_called_with(sentinel.pattern, sentinel.data)

    def test_match_fails(self, mock_re_match):
        """ `data` does not match the regular expression. """
        mock_re_match.return_value = False
        with self.assertRaises(ValidationError):
            self.validator(sentinel.schema, sentinel.data)
        mock_re_match.assert_called_with(sentinel.pattern, sentinel.data)

class TestRequired(unittest.TestCase):
    """ `Required` validator. """

    def test_some_value_passes(self):
        """ No `ValidationError` raised. """
        Required()(sentinel.schema, sentinel.data)

    def test_none_value_raises(self):
        """ `None` raises `ValidationError`. """
        with self.assertRaises(ValidationError):
            Required()(sentinel.schema, None)

    def test_empty_string_raises(self):
        """ Empty string raises `ValidationError`. """
        with self.assertRaises(ValidationError):
            Required()(sentinel.schema, '')
