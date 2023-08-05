"""Duck types miscellany."""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"

from collections import Callable as _Callable

from . import _core as _ducktypes_core
from .. import _converters


def _type_isboollike(type):
    try:
        nonzero_method = getattr(type, '__nonzero__')
    except AttributeError:
        return False
    return isinstance(nonzero_method, _Callable)


boollike = _ducktypes_core.ducktypeclass_fromconverter('boollike',
                                                       _converters.bool,
                                                       type_issubclass=
                                                           _type_isboollike)
