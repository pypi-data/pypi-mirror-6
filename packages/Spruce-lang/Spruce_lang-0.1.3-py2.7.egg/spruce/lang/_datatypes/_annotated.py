"""Annotated types."""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"

import abc as _abc

from .. import _exc


class AnnotatedType(object):

    __metaclass__ = _abc.ABCMeta

    @classmethod
    def convertible_type_description(cls):
        return None

    @classmethod
    def convertible_value_description(cls):
        if cls.convertible_type_description():
            if any(cls.convertible_type_description().startswith(vowel)
                   for vowel in ('a', 'e', 'i', 'o', 'u')):
                article = 'an'
            else:
                article = 'a'

            return '{} {}'.format(article, cls.convertible_type_description())
        else:
            return None

    @classmethod
    def conversion_type_error(cls, type, message=None):
        return _exc.ConversionTypeError(type, cls.displayname(),
                                        cls.convertible_type_description(),
                                        message)

    @classmethod
    def conversion_value_error(cls, value, message=None):
        return _exc.ConversionValueError(value, cls.displayname(),
                                         cls.convertible_value_description(),
                                         message)

    @classmethod
    @_abc.abstractmethod
    def displayname(cls):
        pass

    @classmethod
    def type_error(cls, type, message=None):
        return _exc.TypeError(type, cls.displayname(),
                              cls.convertible_type_description(), message)

    @classmethod
    def value_error(cls, value, message=None):
        return _exc.ValueError(value, cls.displayname(),
                               cls.convertible_value_description(), message)
