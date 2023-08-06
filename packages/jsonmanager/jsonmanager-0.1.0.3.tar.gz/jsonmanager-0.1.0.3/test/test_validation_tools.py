""" Tests for `validation_tools` module. """

import unittest
from unittest.mock import (
    call,
    MagicMock,
    patch,
    sentinel,
    )

from jsonmanager.exceptions import (
    ValidationError,
    StructuredValidationError
    )
from jsonmanager.validation_tools import (
    validate,
    _validate_scalar,
    _confirm_mapping_type,
    _validate_dict,
    _validate_DictOf,
    _confirm_sequence_type,
    _validate_list,
    _validate_ListOf,
    _validate_tuple,
    validation
    )
from jsonmanager.schema_types import (
    DictOf,
    ListOf
    )

from .common import ConfiguredDecoratorTest


class TestValidate(unittest.TestCase):
    """ `validate` calls the appropriate validation function depending on
        `schema` type. """

    @patch('jsonmanager.validation_tools.select_processor')
    def test_calls_select_processor(self, mock_select_processor):
        """ `select_processor` called to get validation function.
            Validation function return value returned. """
        validation_function = MagicMock()
        mock_select_processor.return_value = validation_function

        result = validate(sentinel.schema, sentinel.data)

        validation_function.assert_called_with(sentinel.schema, sentinel.data)
        assert result is sentinel.data

    def validation_function_test(self, mock_validation_function, schema_type):
        """ `validate` calls the appropriate function.
            If no exceptions are raised, `data` is returned unchanged.

            These tests are necessary to ensure that `validation_map` is
            defined correctly. """
        schema = MagicMock(schema_type)

        result = validate(schema, sentinel.data)

        mock_validation_function.assert_called_with(schema, sentinel.data)
        assert result is sentinel.data

    @patch('jsonmanager.validation_tools._validate_scalar')
    def test_scalar(self, mock_validate_scalar):
        """ `_validate_scalar` called for non-container values. """
        self.validation_function_test(mock_validate_scalar, type)

    @patch('jsonmanager.validation_tools._validate_dict')
    def test_dict(self, mock_validate_dict):
        """ `_validate_dict` called for `dict` values. """
        self.validation_function_test(mock_validate_dict, dict)

    @patch('jsonmanager.validation_tools._validate_DictOf')
    def test_dict_of(self, mock_validate_DictOf):
        """ `_validate_DictOf` called for `dict` values. """
        self.validation_function_test(mock_validate_DictOf, DictOf)

    @patch('jsonmanager.validation_tools._validate_list')
    def test_list(self, mock_validate_list):
        """ `_validate_list` called for `list` values. """
        self.validation_function_test(mock_validate_list, list)

    @patch('jsonmanager.validation_tools._validate_ListOf')
    def test_list_of(self, mock_validate_ListOf):
        """ `_validate_ListOf` called for `ListOf` values. """
        self.validation_function_test(mock_validate_ListOf, ListOf)

    @patch('jsonmanager.validation_tools._validate_tuple')
    def test_tuple(self, mock_validate_tuple):
        """ `_validate_tuple` called for `tuple` values. """
        self.validation_function_test(mock_validate_tuple, tuple)

class TestValidation(ConfiguredDecoratorTest, unittest.TestCase):
    """ `@validation` decorator. """

    def setUp(self):
        self.configured_decorator = validation
        self.input_processor_callable = validate
        self.output_processor_callable = validate

class TestValidateScalar(unittest.TestCase):
    """ `_validate_scalar` function.
        `schema` should be an expected type.
        `data` should be an instance of the expected type.
        """

    def setUp(self):
        class ExpectedType:
            pass
        self.ExpectedType = ExpectedType

    def test_expected_type_passes(self):
        """ `data` is of the expected type. """
        _validate_scalar(schema=self.ExpectedType, data=self.ExpectedType())

    def test_subclass_passes(self):
        """ `data` is a subclass of the expected type. """
        class SubclassType(self.ExpectedType):
            pass
        _validate_scalar(schema=self.ExpectedType, data=SubclassType())

    def test_none_passes(self):
        """ `data` is `None`. """
        _validate_scalar(schema=self.ExpectedType, data=None)

    def test_wrong_type_raises(self):
        """ `data` is not of the expected type. """
        with self.assertRaises(ValidationError):
            _validate_scalar(schema=self.ExpectedType, data=object())

@patch('jsonmanager.validation_tools.is_mapping')
class TestConfirmMappingType(unittest.TestCase):
    """ `_confirm_mapping_type` function.
        Confirms that `data` is a mapping. """

    def test_passes(self, mock_is_mapping):
        """ `data` is mapping, no exception raised. """
        mock_is_mapping.return_value = True
        _confirm_mapping_type(sentinel.data)
        assert mock_is_mapping.called_with(sentinel.data)

    def test_raises(self, mock_is_mapping):
        """ `data` is not a mapping, exception is raised. """
        mock_is_mapping.return_value = False
        with self.assertRaises(ValidationError):
            _confirm_mapping_type(sentinel.data)
        assert mock_is_mapping.called_with(sentinel.data)

class TestValidateDict(unittest.TestCase):
    """ `_validate_dict` function.
        `schema` should be a mapping of keys to expected types.
        `data` should be a mapping with conforming keys and types.
        """

    @patch('jsonmanager.validation_tools.validate')
    def test_calls_validate(self, mock_validate):
        """ `validate` called for each pair of corresponding values. """
        schema = {
            'a': sentinel.a,
            'b': sentinel.b,
            'c': sentinel.c
            }
        data = {
            'a': sentinel.x,
            'b': sentinel.y,
            'c': sentinel.z
            }

        expected_calls = [
            call(schema[key], data[key]) for key in 'abc'
            ]

        _validate_dict(schema=schema, data=data)

        mock_validate.assert_has_calls(expected_calls, any_order=True)

    @patch('jsonmanager.validation_tools._confirm_mapping_type')
    def test_confirm_mapping_type_called(self, mock_confirm_mapping_type):
        """ `_confirm_mapping_type` is called on `data`. """
        expected = Exception()
        mock_confirm_mapping_type.side_effect = expected
        with self.assertRaises(Exception) as captured:
            _validate_dict(object, sentinel.data)
        assert captured.exception is expected
        mock_confirm_mapping_type.assert_called_with(sentinel.data)

    def test_missing_key_raises(self):
        """ `data` must have all keys that `schema` has. """
        schema = {'a': object}
        data = {}
        with self.assertRaises(ValidationError):
            _validate_dict(schema=schema, data=data)

    def test_extra_key_raises(self):
        """ `data` cannot have any keys that `schema` does not have. """
        schema = {}
        data = {'a': object()}
        with self.assertRaises(ValidationError):
            _validate_dict(schema=schema, data=data)

class TestValidateDictErrorCollection(unittest.TestCase):
    """ `_validate_dict` collects validation errors and returns a common
        `ValidationError` which includes all of the collected errors in the
        `error` attribute.

        Errors collected:
        - Errors raised by `validate`
        - Missing keys
        - Unknown keys
        """

    def structured_error_test(self, expected, error):
        """ Errors raised by `validate` are collected into a dictionary. """
        schema = {'a': sentinel.a, 'b': sentinel.b}
        data = {'a': sentinel.x, 'b': sentinel.y}

        with patch('jsonmanager.validation_tools.validate') as mock_validate:
            mock_validate.side_effect = error
            with self.assertRaises(StructuredValidationError) as captured:
                _validate_dict(schema, data)

        assert captured.exception.error == {'a': expected, 'b': expected}

    def test_structured_error_basic(self):
        """ `ValidationError`s are collected. """
        expected = (sentinel.error_code, sentinel.message)
        error = ValidationError(*expected)
        self.structured_error_test(expected, error)

    def test_structured_error_nested(self):
        """ `StructuredValidationError`s are collected. """
        expected = MagicMock(dict)
        error = StructuredValidationError(expected)
        self.structured_error_test(expected, error)

    def keys_mismatch_test(self, schema, data):
        """ Missing/unknown keys test. """
        with self.assertRaises(ValidationError) as captured:
            _validate_dict(schema, data)

        error = captured.exception.error

        assert set(error.keys()) == set(['a'])
        assert isinstance(error['a'], tuple)

    def test_missing_key_errors(self):
        """ Errors for missing keys are collected. """
        schema = {'a': object}
        data = {}

        self.keys_mismatch_test(schema, data)

    def test_unknown_key_errors(self):
        """ Errors for unknown keys are collected. """
        schema = {}
        data = {'a': object}

        self.keys_mismatch_test(schema, data)

class TestValidateDictOf(unittest.TestCase):
    """ `_validate_DictOf` function. """

    @patch('jsonmanager.validation_tools._validate_dict')
    def test_validate_dict_called(self, mock_validate_dict):
        """ A dictionary schema is constructed with keys from `data`. `data`
            is validated against the constructed dictionary schema. """
        schema = DictOf(sentinel.schema)
        data = {'a': sentinel.a, 'b': sentinel.b, 'c': sentinel.c}

        schema_dict = {
            'a': sentinel.schema,
            'b': sentinel.schema,
            'c': sentinel.schema
            }

        _validate_DictOf(schema, data)

        mock_validate_dict.assert_called_with(schema_dict, data)

    @patch('jsonmanager.validation_tools._confirm_mapping_type')
    def test_confirm_mapping_type_called(self, mock_confirm_mapping_type):
        """ `_confirm_mapping_type` is called on `data`. """
        expected = Exception()
        mock_confirm_mapping_type.side_effect = expected
        with self.assertRaises(Exception) as captured:
            _validate_DictOf(object, sentinel.data)
        assert captured.exception is expected
        mock_confirm_mapping_type.assert_called_with(sentinel.data)

@patch('jsonmanager.validation_tools.is_sequence')
class TestConfirmSequenceType(unittest.TestCase):
    """ `_confirm_sequence_type` function.
        Confirms that `data` is a sequence. """

    def test_passes(self, mock_is_sequence):
        """ `data` is sequence, no exception raised. """
        mock_is_sequence.return_value = True
        _confirm_sequence_type(sentinel.data)
        assert mock_is_sequence.called_with(sentinel.data)

    def test_raises(self, mock_is_sequence):
        """ `data` is not a sequence, exception is raised. """
        mock_is_sequence.return_value = False
        with self.assertRaises(ValidationError):
            _confirm_sequence_type(sentinel.data)
        assert mock_is_sequence.called_with(sentinel.data)

class TestValidateList(unittest.TestCase):
    """ `_validate_list` function.
        `schema` should be a sequence of expected types.
        `data` should be a sequence of instances of the expected types.
        """

    @patch('jsonmanager.validation_tools._validate_dict')
    def test_calls_validate_dict(self, mock_validate_dict):
        """ `schema` and `data` converted to dictionaries, then passed to
            `_validate_dict`. """
        schema = [sentinel.a, sentinel.b, sentinel.c]
        data = [sentinel.x, sentinel.y, sentinel.z]

        schema_dict = {0: sentinel.a, 1: sentinel.b, 2: sentinel.c}
        data_dict = {0: sentinel.x, 1: sentinel.y, 2: sentinel.z}

        _validate_list(schema, data)

        mock_validate_dict.assert_called_with(schema_dict, data_dict)

    @patch('jsonmanager.validation_tools._confirm_sequence_type')
    def test_confirm_sequence_type_called(self, mock_confirm_sequence_type):
        """ `_confirm_sequence_type` is called on `data`. """
        expected = Exception()
        mock_confirm_sequence_type.side_effect = expected
        with self.assertRaises(Exception) as captured:
            _validate_ListOf(object, sentinel.data)
        assert captured.exception is expected
        mock_confirm_sequence_type.assert_called_with(sentinel.data)

    def test_data_too_short_raises(self):
        """ If `schema` has greater length than `data`, an exception is raised.
            """
        schema = [object]
        data = []
        with self.assertRaises(ValidationError):
            _validate_list(schema=schema, data=data)

    def test_data_too_long_raises(self):
        """ If `data` has greater length than `schema`, an exception is raised.
            """
        schema = []
        data = [object()]
        with self.assertRaises(ValidationError):
            _validate_list(schema=schema, data=data)

class TestValidateListOf(unittest.TestCase):
    """ `ListOf` validates `list` data. """

    @patch('jsonmanager.validation_tools._validate_list')
    def test_validate_list_called(self, mock_validate_list):
        """ A list schema is constructed with the same length as `data`. `data`
            is validated against the list schema. """
        schema = ListOf(sentinel.schema)
        data = [sentinel.a, sentinel.b, sentinel.c]

        schema_list = [
            sentinel.schema, sentinel.schema, sentinel.schema
            ]

        _validate_ListOf(schema, data)

        mock_validate_list.assert_called_with(schema_list, data)

    @patch('jsonmanager.validation_tools._confirm_sequence_type')
    def test_confirm_sequence_type_called(self, mock_confirm_sequence_type):
        """ `_confirm_sequence_type` is called on `data`. """
        expected = Exception()
        mock_confirm_sequence_type.side_effect = expected
        with self.assertRaises(Exception) as captured:
            _validate_ListOf(object, sentinel.data)
        assert captured.exception is expected
        mock_confirm_sequence_type.assert_called_with(sentinel.data)

@patch('jsonmanager.validation_tools.validate')
class TestValidateTuple(unittest.TestCase):
    """ `_validate_tuple` function.
        A `tuple` schema type is used to specify form validators. """

    def test_validate_tuple(self, mock_validate):
        """ `data` validated against `schema`.
            Validators are non-class callable objects.
            Each form validator called with `schema` and `data`. """
        validator_0 = MagicMock()
        validator_1 = MagicMock()

        _validate_tuple(
            (sentinel.schema, validator_0, validator_1),
            sentinel.data
            )

        mock_validate.assert_called_with(sentinel.schema, sentinel.data)
        validator_0.assert_called_with(sentinel.schema, sentinel.data)
        validator_1.assert_called_with(sentinel.schema, sentinel.data)

    def test_validator_is_class(self, mock_validate):
        """ When a validator is a class:
            - it is instantiated with no arguments
            - the instance is called. """
        validator_class = MagicMock(type)
        validator_instance = MagicMock()
        validator_class.return_value = validator_instance

        _validate_tuple(
            (sentinel.schema, validator_class),
            sentinel.data
            )

        validator_class.assert_called_with()
        validator_instance.assert_called_with(sentinel.schema, sentinel.data)

    def test_validate_schema_stops_validation(self, mock_validate):
        """ `validate` raises ValidationError.
            Validators are not called. """
        validator = MagicMock()

        mock_validate.side_effect = ValidationError(
            sentinel.error_code, sentinel.message
            )

        with self.assertRaises(ValidationError):
            _validate_tuple(
                (sentinel.schema, validator),
                sentinel.data
                )

        mock_validate.assert_called_with(sentinel.schema, sentinel.data)
        assert not validator.called

    def test_first_validator_stops_validation(self, mock_validate):
        """ First validator raises `ValidationError`.
            Second validator is not called. """
        validator_0 = MagicMock()
        validator_1 = MagicMock()

        validator_0.side_effect = ValidationError(
            sentinel.error_code, sentinel.message
            )

        with self.assertRaises(ValidationError):
            _validate_tuple(
                (sentinel.schema, validator_0, validator_1),
                sentinel.data
                )

        mock_validate.assert_called_with(sentinel.schema, sentinel.data)
        validator_0.assert_called_with(sentinel.schema, sentinel.data)
        assert not validator_1.called
