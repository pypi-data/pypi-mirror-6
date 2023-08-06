""" Tests for `exceptions` module. """
import unittest
from unittest.mock import (
    MagicMock,
    sentinel
    )

from jsonmanager.exceptions import (
    ValidationError,
    StructuredValidationError
    )

class TestValidationError(unittest.TestCase):
    """ `ValidationError` behavior. """

    def test_error_tuple(self):
        """ `error_code` and `message` are packed into a tuple and stored as
            `error` attribute. """
        expected = (sentinel.error_code, sentinel.error_message)
        error = ValidationError(*expected)
        assert error.error == expected

class TestStructuredValidationError(unittest.TestCase):
    """ `StructuredValidationError` behavior. """

    def test_subclass(self):
        """ `StructuredValidationError` is a subclass of `ValidationError`.
            This allows `except` statements to catch both. """
        assert issubclass(StructuredValidationError, ValidationError)

    def test_dict_error_passes(self):
        """ `error` dictionary value passes. """
        StructuredValidationError(MagicMock(dict))

    def test_non_dict_error_raises(self):
        """ `error` non-dictionary value raises. """
        with self.assertRaises(TypeError):
            StructuredValidationError(sentinel.not_a_dictionary)