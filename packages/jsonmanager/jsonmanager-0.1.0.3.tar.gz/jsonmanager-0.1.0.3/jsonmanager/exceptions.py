""" Exceptions. """

class Error(Exception):
    """ Base class for errors. """

class ValidationError(Error):
    """ `data` does not conform to `schema`. """

    def __init__(self, error_code, message):
        """ Pack `error_code` and `message` into a tuple. Store the tuple as
            `error` attribute.

            `error_code`: a string with no whitespace. A particular validator
                should always use the same `error_code` when raising
                `ValidationError`.

            `message`: a human-readable message describing the reason why
                validation failed.
            """
        error_tuple = (error_code, message)
        Error.__init__(self, error_tuple)
        self.error = error_tuple

class StructuredValidationError(ValidationError):
    """ Raised by `_validate_dict`. `error` is a dictionary of validation errors
        raised by each element of `data` and `schema`. """

    def __init__(self, error_dict):
        """ Store `error_dict` as `error` attribute. """
        if not isinstance(error_dict, dict):
            raise TypeError("`error_dict` must be a dictionary.")

        Error.__init__(self, error_dict)
        self.error = error_dict

class SchemaError(Error):
    """ `schema` is not a valid schema.

        `schema` may only include these things:
        - types (class objects)
        - dictionaries
        - lists
        - `DictOf` and `ListOf` instances
        - tuples composed of one type and several validators
        """