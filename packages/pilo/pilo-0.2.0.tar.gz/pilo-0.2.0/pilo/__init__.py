"""
"""
__version__ = '0.2.0'

__all__ = [
    'NOT_SET',
    'NONE',
    'ERROR',
    'IGNORE',
    'ctx',
    'fields',
    'Field',
    'Form',
    'Source',
    'SourceError',
    'IdentitySource',
    'mime',
    'ParseError',
]


class _Constant(object):

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '{}("{}")'.format(type(self).__name__, self.name)


NOT_SET = _Constant('NOT_SET')

NONE = _Constant('NONE')

ERROR = _Constant('ERROR')

IGNORE = (NONE, ERROR)

from .context import ctx, ContextMixin
from . import source
from .source import Source, IdentitySource, ParseError, ParseError as SourceError
from . import fields
from .fields import Field, FieldError, Form
