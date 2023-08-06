import six


integer_type = int
if six.PY3:
    long = None
if six.PY2:
    integer_type = long


def _is_descriptor(obj):
    """Test if an object is a descriptor.
    """

    return (hasattr(obj, '__get__') or
            hasattr(obj, '__set__') or
            hasattr(obj, '__delete__'))


def _is_double_under(name):
    """Test if a key is a __double_underscore__ name.
    """

    return (name[:2] == name[-2:] == '__' and
            name[2:3] != '_' and
            name[-3:-2] != '_' and
            len(name) > 4)


def _is_single_under(name):
    """Test if a key is a _single_underscore_ name.
    """

    return (name[0] == name[-1] == '_' and
            name[1:2] != '_' and
            name[-2:-1] != '_' and
            len(name) > 2)


class _RouteClassAttributeToGetattr(object):
    """Route attribute access on a class to __getattr__.

    This is a descriptor, used to define attributes that act differently when
    accessed through an instance and through a class.  Instance access remains
    normal, but access to an attribute through a class will be routed to the
    class's __getattr__ method; this is done by raising AttributeError.
    """

    def __init__(self, fget=None):
        self.fget = fget

    def __get__(self, instance, ownerclass=None):
        if instance is None:
            raise AttributeError()
        return self.fget(instance)

    def __set__(self, instance, value):
        raise AttributeError("can't set attribute")

    def __delete__(self, instance):
        raise AttributeError("can't delete attribute")


class _BitMaskClassDict(dict):
    """Track bit mask flags ensure flag names and values are not reused.

    BitMaskMeta will use ``_flags`` attribute as the source of flags.
    """

    def __init__(self):
        super(_BitMaskClassDict, self).__init__()
        self._flag_names = set()
        self._flag_values = set()
        self._flags = {}

    def __setitem__(self, key, value):
        """Changes anything not dundered or not a descriptor.

        If a descriptor is added with the same name as an enum member, the name
        is removed from _member_names (this may leave a hole in the numerical
        sequence of values).
        """

        if _is_single_under(key):
            raise ValueError('_names_ are reserved for future BitMask use')
        elif _is_double_under(key):
            pass
        elif key in self._flag_names:
            raise TypeError('Attempted to reuse flag: %r' % key)
        elif not _is_descriptor(value):
            # Ensure that the flag has not already been defined.
            if key in self:
                raise TypeError('Flag already defined as: %r' % self[key])

            # Ensure that the value is a non-negative integer value that is a
            # power of 2.
            if not isinstance(value, six.integer_types):
                raise ValueError('Flag value must be an integer, not %r' %
                                 (type(value)))
            if not value or bool(value & (value - 1)):
                raise ValueError('Flag value must be a power of 2: %d' %
                                 (value))
            value = integer_type(value)
            if value in self._flag_values:
                raise ValueError('Flag with value %d already defined')
            self._flag_names.add(key)
            self._flag_values.add(value)
            self._flags[key] = value
            return
        super(_BitMaskClassDict, self).__setitem__(key, value)


class BitMaskMeta(type):
    """Bit mask meta class.
    """

    def __new__(metacls, cls, bases, classdict):
        # Use _BitMaskClassDict as class dict.
        if not isinstance(classdict, _BitMaskClassDict):
            if not isinstance(classdict, dict):
                raise ValueError('expected classdict to be an instance of '
                                 'dict, but is an instance of %s' %
                                 (type(classdict)))
            original_dict = classdict
            classdict = _BitMaskClassDict()
            for k, v in original_dict.items():
                classdict[k] = v
            del original_dict

        # Create the bit mask class.
        bitmask_cls = super(BitMaskMeta, metacls) \
            .__new__(metacls, cls, bases, classdict)

        # Assign the individual flags.
        bitmask_cls._flag_names_ = set(classdict._flags.keys())
        bitmask_cls._flag_values_ = set(classdict._flags.values())
        bitmask_cls._flag_values_ordered_ = \
            sorted(tuple(classdict._flags.values()))
        bitmask_cls._flag_name_to_value_ = classdict._flags
        bitmask_cls._flag_value_to_name_ = dict([
            (v, k) for k, v in classdict._flags.items()
        ])
        bitmask_cls._valid_mask_ = integer_type(sum(bitmask_cls._flag_values_))

        return bitmask_cls

    def __contains__(cls, flag):
        return isinstance(flag, cls) and flag.value in cls._flag_values_

    def __delattr__(cls, attr):
        if attr in cls._flag_names_:
            raise AttributeError('%s: cannot delete bit mask flag' %
                                 (cls.__name__))
        super(BitMaskMeta, cls).__delattr__(attr)

    def __dir__(self):
        return ['__class__', '__doc__', '__members__', '__module__'] + \
            list(self._flag_names_)

    @property
    def __members__(cls):
        # TODO
        """Returns a mapping of member name->value.

        This mapping lists all enum members, including aliases. Note that this
        is a copy of the internal mapping.
        """

        return cls._member_map_.copy()

    def __getattr__(cls, name):
        """Get the flag matching ``name``.

        We use __getattr__ instead of descriptors or inserting into the enum
        class' __dict__ in order to support `name` and `value` being both
        properties for enum members (which live in the class' __dict__) and
        enum members themselves.
        """

        if _is_double_under(name):
            raise AttributeError(name)
        try:
            return cls(cls._flag_name_to_value_[name])
        except KeyError:
            raise AttributeError(name)

    def __getitem__(cls, name):
        return cls(cls._flag_name_to_value_[name])

    def __iter__(cls):
        return (cls(v) for v in cls._flag_values_ordered_)

    def __reversed__(cls):
        return (cls(v) for v in reversed(cls._flag_values_ordered_))

    def __len__(cls):
        return len(cls._flag_names_)

    def __repr__(cls):
        return "<bit mask %r>" % (cls.__name__)

    def __setattr__(cls, name, value):
        """Block attempts to reassign Enum members.

        A simple assignment to the class namespace only changes one of the
        several possible ways to get an Enum member from the Enum class,
        resulting in an inconsistent Enumeration.
        """

        flag_names = cls.__dict__.get('_flag_names_', set())
        if name in flag_names:
            raise AttributeError('Cannot reassign bit mask flag')
        super(BitMaskMeta, cls).__setattr__(name, value)


_bitmask_dict = {
    '__doc__': """Generic bit mask.

Derive from this class to define new bit masks.""",
    '__slots__': ('_value_', ),
}


def __init__(self, value=integer_type(0)):
    if integer_type(value) & ~(self.__class__._valid_mask_):
        raise ValueError('%d is not a valid %s bit mask value' %
                         (value, self.__class__.__name__))
    self._value_ = integer_type(value)
_bitmask_dict['__init__'] = __init__
del __init__


def __repr__(self):
    return '<%s: %d>' % (
        str(self),
        self._value_
    ) if self._value_ else '<%s: 0>' % (self.__class__.__name__)
_bitmask_dict['__repr__'] = __repr__
del __repr__


def __str__(self):
    names = [
        '%s.%s' % (self.__class__.__name__,
                   self.__class__._flag_value_to_name_[v])
        for v in self.__class__._flag_values_ordered_
        if self._value_ & v
    ]
    return ' | '.join(names)
_bitmask_dict['__str__'] = __str__
del __str__


def __contains__(self, other):
    return isinstance(other, self.__class__) and \
        bool(integer_type(self) & integer_type(other))
_bitmask_dict['__contains__'] = __contains__
del __contains__


def __int__(self):
    return int(self._value_)
_bitmask_dict['__int__'] = __int__
del __int__


if six.PY2:
    def __long__(self):
        return long(self._value_)
    _bitmask_dict['__long__'] = __long__
    del __long__


def __or__(self, other):
    if not isinstance(other, self.__class__):
        raise TypeError('cannot or value of type %r' % (type(other)))
    return self.__class__(self._value_ | other._value_)
_bitmask_dict['__or__'] = __or__
del __or__


def __and__(self, other):
    if not isinstance(other, self.__class__):
        raise TypeError('cannot and value of type %r' % (type(other)))
    return self.__class__(self._value_ & other._value_)
_bitmask_dict['__and__'] = __and__
del __and__


def __xor__(self, other):
    if not isinstance(other, self.__class__):
        raise TypeError('cannot xor value of type %r' % (type(other)))
    return self.__class__(self._value_ ^ other._value_)
_bitmask_dict['__xor__'] = __xor__
del __xor__


def __add__(self, other):
    if not isinstance(other, self.__class__):
        raise TypeError('cannot add value of type %r' % (type(other)))
    return self.__class__(self._value_ | other._value_)
_bitmask_dict['__add__'] = __add__
del __add__


def __sub__(self, other):
    if not isinstance(other, self.__class__):
        raise TypeError('cannot remove value of type %r' % (type(other)))
    return self.__class__(self._value_ & ~(other._value_))
_bitmask_dict['__sub__'] = __sub__
del __sub__


def __ior__(self, other):
    if not isinstance(other, self.__class__):
        raise TypeError('cannot or value of type %r' % (type(other)))
    self._value_ |= other._value_
    return self
_bitmask_dict['__ior__'] = __ior__
del __ior__


def __iand__(self, other):
    if not isinstance(other, self.__class__):
        raise TypeError('cannot and value of type %r' % (type(other)))
    self._value_ &= other._value_
    return self
_bitmask_dict['__iand__'] = __iand__
del __iand__


def __ixor__(self, other):
    if not isinstance(other, self.__class__):
        raise TypeError('cannot xor value of type %r' % (type(other)))
    self._value_ ^= other._value_
    return self
_bitmask_dict['__ixor__'] = __ixor__
del __ixor__


def __iadd__(self, other):
    if not isinstance(other, self.__class__):
        raise TypeError('cannot add value of type %r' % (type(other)))
    self._value_ |= other._value_
    return self
_bitmask_dict['__iadd__'] = __iadd__
del __iadd__


def __isub__(self, other):
    if not isinstance(other, self.__class__):
        raise TypeError('cannot add value of type %r' % (type(other)))
    self._value_ &= ~(other._value_)
    return self
_bitmask_dict['__isub__'] = __isub__
del __isub__


def __eq__(self, other):
    return isinstance(other, self.__class__) and self._value_ == other._value_
_bitmask_dict['__eq__'] = __eq__
del __eq__


def __ne__(self, other):
    return not isinstance(other, self.__class__) or \
        self._value_ != other._value_
_bitmask_dict['__ne__'] = __ne__
del __ne__


def __hash__(self):
    return hash((self.__class__, self._value_))
_bitmask_dict['__hash__'] = __hash__
del __hash__


def __lt__(self, other):
    return (self.__class__, self._value_) < (other.__class__, other._value_)
_bitmask_dict['__lt__'] = __lt__
del __lt__


def __gt__(self, other):
    return (self.__class__, self._value_) > (other.__class__, other._value_)
_bitmask_dict['__gt__'] = __gt__
del __gt__


def __ge__(self, other):
    return (self.__class__, self._value_) >= (other.__class__, other._value_)
_bitmask_dict['__ge__'] = __ge__
del __ge__


def __le__(self, other):
    return (self.__class__, self._value_) <= (other.__class__, other._value_)
_bitmask_dict['__le__'] = __le__
del __le__


def enum_nonzero(self):
    return bool(self._value_)
_bitmask_dict['__nonzero__'] = enum_nonzero
del enum_nonzero


def enum_bool(self):
    return bool(self._value_)
_bitmask_dict['__bool__'] = enum_bool
del enum_bool


def add(self, other):
    if not isinstance(other, self.__class__):
        raise TypeError('cannot add value of type %r' % (type(other)))
    self._value_ |= other._value_
_bitmask_dict['add'] = add
del add


def remove(self, other):
    if not isinstance(other, self.__class__):
        raise TypeError('cannot remove value of type %r' % (type(other)))
    self._value_ &= ~other._value_
_bitmask_dict['remove'] = remove
del remove


@_RouteClassAttributeToGetattr
def name(self):
    flags = self.flags
    if len(flags) != 1:
        raise AttributeError('%r is not a bit mask flag' % (self))
    return self.__class__._flag_value_to_name_[flags[0]._value_]
_bitmask_dict['name'] = name
del name


@_RouteClassAttributeToGetattr
def value(self):
    return self._value_
_bitmask_dict['value'] = value
del value


@_RouteClassAttributeToGetattr
def flags(self):
    return [self.__class__(v)
            for v in self.__class__._flag_values_ordered_
            if self._value_ & v]
_bitmask_dict['flags'] = flags
del flags


BitMask = BitMaskMeta('BitMask', (object, ), _bitmask_dict)
del _bitmask_dict


__all__ = ('BitMask', )
