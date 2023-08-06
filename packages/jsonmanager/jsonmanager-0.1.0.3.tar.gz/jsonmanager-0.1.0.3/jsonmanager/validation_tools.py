""" Tools for validation. """

from .exceptions import (
    ValidationError,
    StructuredValidationError
    )
from .schema_types import (
    DictOf,
    ListOf
    )
from .util import (
    is_mapping,
    is_sequence,
    processing_decorator,
    select_processor
    )


def validate(schema, data):
    """ Call the appropriate validation function, depending on `schema` type.
        If no exception is raised, return `data` unchanged. """
    validation_map = [
        (type,   _validate_scalar),
        (dict,   _validate_dict),
        (DictOf, _validate_DictOf),
        (list,   _validate_list),
        (ListOf, _validate_ListOf),
        (tuple,  _validate_tuple)
        ]

    validation_function = select_processor(schema, validation_map)
    validation_function(schema, data)
    return data

validation = processing_decorator(validate, validate)

def _validate_scalar(schema, data):
    """ `data` must be an instance of `schema` type. """
    if isinstance(data, schema) or data is None:
        return

    raise ValidationError('TYPE', "Not a `{}`.".format(schema.__name__))

def _confirm_mapping_type(data):
    """ Raise `ValidationError` if `data` is not a mapping. """
    if not is_mapping(data):
        raise ValidationError('TYPE', "Not a mapping.")

def _validate_dict(schema, data):
    """ Validate a dictionary.
        Validate each value from `data` against the corresponding `schema`
        value.
        `schema` and `data` must have exactly the same keys.

        Collect all `ValidationError`s raised. Raise a new `ValidationError`
        containing all collected errors. """
    _confirm_mapping_type(data)

    schema_keys = set(schema.keys())
    data_keys = set(data.keys())

    error_dict = {}

    for key in schema_keys & data_keys:
        try:
            validate(schema[key], data[key])
        except ValidationError as exc:
            error_dict[key] = exc.error

    for key in schema_keys - data_keys:
        error_dict[key] = ('MISSING', "Element missing.")

    for key in data_keys - schema_keys:
        error_dict[key] = ('NOT_ALLOWED', "Element not allowed.")

    if error_dict:
        raise StructuredValidationError(error_dict)

def _validate_DictOf(dict_of, data):
    """ Validate a dictionary with arbitrary keys.
        Validate each value from `data` against `dict_of.schema`. """
    _confirm_mapping_type(data)

    schema_dict = {key: dict_of.schema for key in data.keys()}

    _validate_dict(schema_dict, data)

def _confirm_sequence_type(data):
    """ Raise `ValidationError` if `data` is not a sequence, or if `data` is a
        string. """
    if not is_sequence(data):
        raise ValidationError('TYPE', "Not a sequence.")

def _validate_list(schema, data):
    """ Validate a list.
        Validate each value from `data` against the corresponding `schema`
        value.
        `schema` and `data` must have the same length. """
    _confirm_sequence_type(data)

    schema_dict = dict(enumerate(schema))
    data_dict = dict(enumerate(data))

    _validate_dict(schema_dict, data_dict)

def _validate_ListOf(list_of, data):
    """ Validate a list with arbitrary length.
        Validate each value from `data` against `list_of.schema`."""
    _confirm_sequence_type(data)

    schema_list = [list_of.schema for item in data]

    _validate_list(schema_list, data)

def _validate_tuple(schema_tuple, data):
    """ Validate a tuple.
        The first tuple element is `schema`.
        The remaining tuple elements are validators.
        If a validator is a class, instantiate it before calling.
        Pass `schema` and `data` to each validator. """
    schema = schema_tuple[0]
    validators = schema_tuple[1:]

    validate(schema, data)

    for validator in validators:
        if isinstance(validator, type):
            validator = validator()
        validator(schema, data)
