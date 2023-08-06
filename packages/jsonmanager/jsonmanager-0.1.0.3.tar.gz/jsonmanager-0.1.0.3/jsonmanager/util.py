""" Common tools for both validation and coercion. """

from collections import abc
from functools import wraps

from .exceptions import SchemaError


def select_processor(schema, processor_map):
    """ Select `processor` function from `processor_map`, depending on `schema`
        type. """

    for schema_type, processor in processor_map:
        if isinstance(schema, schema_type):
            return processor

    raise SchemaError(
        "Unknown schema type: `{}`"
        .format(repr(schema))
        )

def is_mapping(value):
    """ Confirm that `value` is a mapping. """
    return isinstance(value, abc.Mapping)

def is_sequence(value):
    """ Confirm that `value` is a sequence, and not a string. """
    return bool(isinstance(value, abc.Sequence) and not isinstance(value, str))

def check_input_schema(schema):
    """ If an input schema is not a dictionary, raise `SchemaError`.
        `None` values are allowed. """
    if not isinstance(schema, dict) and schema is not None:
        raise SchemaError('`input_schema` must be a dictionary.')

def resolve_decorator_schemas(schema, wrapped, schema_name):
    """ Selects either the schema provided as an argument, or the schema stored
        as an attribute on the wrapped callable. """
    if schema is not None:
        return schema

    try:
        return getattr(wrapped, schema_name)
    except AttributeError:
        return None

def process_data(processor, schema, data):
    """ If `schema` is provided:
        - Call `processor`.
        - Return `processor` return value.
        If schema is None:
        - Return `data` unchanged. """
    if schema is None:
        return data
    return processor(schema, data)

def processing_decorator(input_processor, output_processor):
    """ Returns a decorator which adds input/output processing to a wrapped
        callable. """

    def decorator(wrapped=None, *, input_schema=None, output_schema=None):
        """ A decorator.
            Add input/output processing to the wrapped callable. """

        def prepared_decorator(wrapped):
            """ When `input_schema` and/or `output_schema` are passed to the
                decorator as arguments, this is returned to decorate the wrapped
                callable. """
            return decorator(
                wrapped,
                input_schema=input_schema,
                output_schema=output_schema
                )
        if wrapped is None:
            return prepared_decorator

        # Get schemas from wrapped callable attributes, if present.
        resolved_input_schema = resolve_decorator_schemas(
            input_schema, wrapped, 'input_schema'
            )
        resolved_output_schema = resolve_decorator_schemas(
            output_schema, wrapped, 'output_schema'
            )

        check_input_schema(resolved_input_schema)

        @wraps(wrapped)
        def decorated_function(**input_data):
            processed_input_data = process_data(
                input_processor, resolved_input_schema, input_data
                )

            output_data = wrapped(**processed_input_data)

            processed_output_data = process_data(
                output_processor, resolved_output_schema, output_data
                )

            return processed_output_data

        decorated_function.input_schema = resolved_input_schema
        decorated_function.output_schema = resolved_output_schema

        return decorated_function

    return decorator
