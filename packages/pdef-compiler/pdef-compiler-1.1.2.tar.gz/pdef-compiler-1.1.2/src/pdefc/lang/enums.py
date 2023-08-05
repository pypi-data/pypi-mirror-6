# encoding: utf-8
import logging
from pdefc.lang.types import Type, TypeEnum, Definition


class Enum(Definition):
    '''Enum definition.'''
    def __init__(self, name, values=None, value_names=None, doc=None, location=None):
        super(Enum, self).__init__(TypeEnum.ENUM, name, doc=doc, location=location)
        self.values = []

        if values and value_names:
            raise ValueError('values and value_names are mutually exclusive')

        if values:
            for value in values:
                self.add_value(value)

        if value_names:
            for name in value_names:
                self.create_value(name)

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<%s %s %s>' % (self.__class__.__name__, self.name, hex(id(self)))

    def add_value(self, value):
        '''Add a value to this enum.'''
        self.values.append(value)
        logging.debug('Added an enum value, enum=%s, value=%s' % (self, value))

    def create_value(self, name):
        '''Create a new enum value by its name, add it to this enum, and return it.'''
        value = EnumValue(name, enum=self)
        self.add_value(value)
        return value

    def get_value(self, name):
        '''Get a value by its name or raise an exception.'''
        for value in self.values:
            if value.name == name:
                return value

    def __contains__(self, enum_value):
        return enum_value in self.values

    def link(self, module):
        errors = super(Enum, self).link(module)

        for value in self.values:
            errors += value.link(self)

        return errors

    def _validate(self):
        errors = []

        names = set()
        for value in self.values:
            if value.name in names:
                errors.append(self._error('%s: duplicate enum value "%s"', self, value.name))

            names.add(value.name)

        return errors


class EnumValue(Type):
    '''Single enum value which has a name and a pointer to the declaring enum.'''
    def __init__(self, name, enum=None, location=None):
        super(EnumValue, self).__init__(TypeEnum.ENUM_VALUE, location=location)
        self.name = name
        self.enum = enum

    def __str__(self):
        if not self.enum:
            return self.name
        return self.enum.name + '.' + self.name

    def __repr__(self):
        return '<%s %s at %s>' % (self.__class__.__name__, self.name, hex(id(self)))

    def link(self, enum):
        if self.enum and not self.enum is enum:
            raise ValueError('Enum value is already linked, value=%s' % self)
        self.enum = enum
        return []
