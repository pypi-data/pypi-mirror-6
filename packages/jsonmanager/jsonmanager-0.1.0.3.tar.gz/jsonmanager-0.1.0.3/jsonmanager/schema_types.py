""" Special types for schemas. """

AnyType = object

class DictOf:
    """ A dictionary with arbitrary keys. All values must conform to `schema`.
        """
    def __init__(self, schema):
        self.schema = schema

class ListOf:
    """ A list with arbitrary length. All values must conform to `schema`. """
    def __init__(self, schema):
        self.schema = schema
