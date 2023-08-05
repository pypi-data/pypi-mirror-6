"""Regular-expression-like duck types."""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"

from . import _core as _ducktypes_core
from . import _string as _ducktypes_string
from .. import _converters
from .. import _misc as _datatypes_misc


def _type_isregexlike(type):
    return issubclass(type, _datatypes_misc.regex_class) \
           or _ducktypes_string._type_isstringlike(type)


regexlike = _ducktypes_core.ducktypeclass_fromconverter('regexlike',
                                                        _converters.regex,
                                                        type_issubclass=
                                                            _type_isregexlike)
