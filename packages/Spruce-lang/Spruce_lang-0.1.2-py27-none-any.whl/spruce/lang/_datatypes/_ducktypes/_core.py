"""Duck types core."""

__copyright__ = "Copyright (C) 2014 Ivan D Vasin"
__docformat__ = "restructuredtext"

import __builtin__
import abc as _abc
from collections import Callable as _Callable

from .._annotated import AnnotatedType as _AnnotatedType


def ducktypeclass_fromconverter(classname, converter, bases=(),
                                type_issubclass=None):

    @classmethod
    def _value_isinstance(cls, value):
        try:
            converter(value)
        except (TypeError, ValueError):
            return False
        else:
            return True

    _type_issubclass = None
    if type_issubclass:
        @classmethod
        def _type_issubclass(cls, type):
            return type_issubclass(type)
    elif converter.totype:
        @classmethod
        def _type_issubclass(type):
            return issubclass(type, converter.totype)
    elif any(hasattr(base, '_type_issubclass') for base in bases):
        pass
    else:
        method = None
        for base in bases:
            try:
                method = getattr(base, '_type_issubclass')
            except AttributeError:
                pass
            else:
                if not isinstance(method, _Callable):
                    method = None

        if not method:
            if classname:
                ducktypeclass_description = 'duck type ' + classname
            else:
                ducktypeclass_description = 'a duck type'
            ducktypeclass_description += ' from converter {!r}'\
                                          .format(converter)
            if bases:
                ducktypeclass_description += ' with bases {}'.format(bases)

            raise ValueError('cannot determine a subclass check function for'
                              ' constructing {}'
                              .format(ducktypeclass_description))

    if not classname:
        classname = converter.annotated_totype.__name__ + '_DuckType'

    ducktypeclass_bases = [converter.annotated_totype]
    ducktypeclass_bases.extend(list(bases or (AnnotatedDuckType,)))
    ducktypeclass_bases = tuple(ducktypeclass_bases)

    ducktypeclass_attrs = {'_value_isinstance': _value_isinstance}
    if _type_issubclass:
        ducktypeclass_attrs['_type_issubclass'] = _type_issubclass

    return type(classname, ducktypeclass_bases, ducktypeclass_attrs)


def instance_of(type, displayname=None):

    if displayname is not None:
        def displayname_(cls):
            return displayname
    else:
        def displayname_(cls):
            return 'instance of {!r}'.format(type)
    displayname_.__name__ = 'displayname'
    displayname_ = classmethod(displayname_)

    @classmethod
    def _wrapped_type(cls):
        return type

    classname = type.__name__ + '_Instance'
    class_attrs = {'_wrapped_type': _wrapped_type}
    if displayname_ is not None:
        class_attrs['displayname'] = displayname_
    return __builtin__.type(classname, (InstanceOfType,), class_attrs)


def subclass_of(type, displayname=None):

    if displayname is not None:
        def displayname_(cls):
            return displayname
    else:
        def displayname_(cls):
            return 'subclass of {!r}'.format(type)
    displayname_.__name__ = 'displayname'
    displayname_ = classmethod(displayname_)

    @classmethod
    def _wrapped_type(cls):
        return type

    classname = type.__name__ + '_Subclass'
    class_attrs = {'_wrapped_type': _wrapped_type}
    if displayname_ is not None:
        class_attrs['displayname'] = displayname_
    return __builtin__.type(classname, (SubclassOfType,), class_attrs)


class DuckTypeMeta(_abc.ABCMeta):

    def __instancecheck__(self, value):
        return self._value_isinstance(value)

    def __subclasscheck__(self, type):
        return self._type_issubclass(type)


class AnnotatedDuckType(_AnnotatedType):

    __metaclass__ = DuckTypeMeta

    @classmethod
    @_abc.abstractmethod
    def _type_issubclass(cls, type):
        pass

    @classmethod
    @_abc.abstractmethod
    def _value_isinstance(cls, value):
        pass


class InstanceOfType(AnnotatedDuckType):

    __metaclass__ = DuckTypeMeta

    @classmethod
    def convertible_type_description(cls):
        return repr(cls._wrapped_type())

    @classmethod
    def _type_issubclass(cls, type):
        return issubclass(type, cls._wrapped_type())

    @classmethod
    def _value_isinstance(cls, value):
        return isinstance(value, cls._wrapped_type())

    @classmethod
    @_abc.abstractmethod
    def _wrapped_type(cls):
        pass


class SubclassOfType(AnnotatedDuckType):

    __metaclass__ = DuckTypeMeta

    @classmethod
    def convertible_type_description(cls):
        return 'a metaclass'

    @classmethod
    def convertible_value_description(cls):
        return 'a subclass of {!r}'.format(cls._wrapped_type())

    @classmethod
    def _type_issubclass(cls, type):
        return issubclass(type, __builtin__.type)

    @classmethod
    def _value_isinstance(cls, value):
        try:
            return issubclass(value, cls._wrapped_type())
        except TypeError:
            return False

    @classmethod
    @_abc.abstractmethod
    def _wrapped_type(cls):
        pass
