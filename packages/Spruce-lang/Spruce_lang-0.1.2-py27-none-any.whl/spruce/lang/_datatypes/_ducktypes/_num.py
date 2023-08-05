"""Numeric duck types."""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"

from collections import Callable as _Callable
import types as _types

from . import _core as _ducktypes_core
from .. import _converters


# float-like variants ---------------------------------------------------------


def _type_isfloatlike(type):
    return issubclass(type,
                      tuple([complex, float, int, long]
                            + list(_types.StringTypes)))


floatlike = _ducktypes_core.ducktypeclass_fromconverter('floatlike',
                                                        _converters.float,
                                                        type_issubclass=
                                                            _type_isfloatlike)


neg_floatlike = \
    _ducktypes_core.ducktypeclass_fromconverter('neg_floatlike',
                                                _converters.neg_float,
                                                bases=(floatlike,))


nonneg_floatlike = \
    _ducktypes_core.ducktypeclass_fromconverter('nonneg_floatlike',
                                                _converters.nonneg_float,
                                                bases=(floatlike,))


nonpos_floatlike = \
    _ducktypes_core.ducktypeclass_fromconverter('nonpos_floatlike',
                                                _converters.nonpos_float,
                                                bases=(floatlike,))


pos_floatlike = \
    _ducktypes_core.ducktypeclass_fromconverter('pos_floatlike',
                                                _converters.pos_float,
                                                bases=(floatlike,))


# int-like variants -----------------------------------------------------------


def _type_isintlike(type):
    try:
        intmethod = getattr(type, '__int__')
    except AttributeError:
        return issubclass(type, _types.StringTypes)
    else:
        return isinstance(intmethod, _Callable)


intlike = _ducktypes_core.ducktypeclass_fromconverter('intlike',
                                                      _converters.int,
                                                      type_issubclass=
                                                          _type_isintlike)


neg_intlike = _ducktypes_core.ducktypeclass_fromconverter('neg_intlike',
                                                          _converters.neg_int,
                                                          bases=(intlike,))


nonneg_intlike = \
    _ducktypes_core.ducktypeclass_fromconverter('nonneg_intlike',
                                                _converters.nonneg_int,
                                                bases=(intlike,))


nonpos_intlike = \
    _ducktypes_core.ducktypeclass_fromconverter('nonpos_intlike',
                                                _converters.nonpos_int,
                                                bases=(intlike,))


pos_intlike = _ducktypes_core.ducktypeclass_fromconverter('pos_intlike',
                                                          _converters.pos_int,
                                                          bases=(intlike,))
