"""String-like duck types."""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"

from collections import Callable as _Callable
import types as _types

from . import _core as _ducktypes_core
from .. import _converters


def _type_isstringlike(type):
    try:
        string_method = getattr(type, '__unicode__')
    except AttributeError:
        try:
            string_method = getattr(type, '__str__')
        except AttributeError:
            return issubclass(type, _types.StringTypes)
    return isinstance(string_method, _Callable)


hex_intlike = \
    _ducktypes_core.ducktypeclass_fromconverter('hexlike', _converters.hex_int,
                                                type_issubclass=
                                                    _type_isstringlike)


stringlike = \
    _ducktypes_core.ducktypeclass_fromconverter('stringlike',
                                                _converters.string,
                                                type_issubclass=
                                                    _type_isstringlike)
