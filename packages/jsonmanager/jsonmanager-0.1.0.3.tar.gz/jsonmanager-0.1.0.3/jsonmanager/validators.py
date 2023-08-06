""" Validators for use in schemas. """

import re

from .exceptions import ValidationError

class OneOf:
    """ Rejects values not in `collection`. """

    def __init__(self, *collection):
        self.collection = collection

    def __call__(self, schema, data):
        if data not in self.collection:
            raise ValidationError(
                'one_of',
                'Not a member of the approved collection.'
                )

class Range:
    """ Rejects values not in range. """

    def __init__(self, lowest, highest):
        self.lowest = lowest
        self.highest = highest

    def __call__(self, schema, data):
        if not self.lowest <= data <= self.highest:
            raise ValidationError(
                'range',
                'Not in range: {} - {}'.format(self.lowest, self.highest)
                )

class Regex:
    """ Rejects values that do not match `pattern`. """

    def __init__(self, pattern):
        self.pattern = pattern

    def __call__(self, schema, data):
        if not re.match(self.pattern, data):
            raise ValidationError('regex', 'Did not match pattern.')

class Required:
    """ Rejects `None` and empty string. """

    def __call__(self, schema, data):
        if data is None or data == '':
            raise ValidationError('required', "Required value.")
