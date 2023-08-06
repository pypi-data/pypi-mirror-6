# encoding: utf-8
import logging

import pdefc.lang.collects
from pdefc.lang.common import Located, Validatable
from pdefc.lang.types import Type

try:
    # Python 2.7
    string = basestring
except NameError:
    # Python 3
    string = str


def reference(name_ref_def):
    '''Create a reference from a string name, another reference, a definition or None'''
    if name_ref_def is None:
        return EmptyReference()

    elif isinstance(name_ref_def, string):
        return NameReference(name_ref_def)

    elif isinstance(name_ref_def, Type):
        return Reference(name_ref_def)

    elif isinstance(name_ref_def, Reference):
        return name_ref_def

    raise ValueError('Unsupported type: %r' % name_ref_def)


class Reference(Located, Validatable):
    '''Reference directly references a type.'''
    def __init__(self, type0=None, location=None):
        self._type = type0
        self.location = location

    def __bool__(self):
        return bool(self._type)

    def __nonzero__(self):
        return bool(self._type)

    def dereference(self):
        '''Return a type this references points to or raise ValueError when not linked.'''
        if not self._type:
            raise ValueError('Reference is not linked: %s' % self)
        return self._type

    def link(self, lookup):
        '''Link this reference in a provided callable lookup.'''
        return []

    @property
    def referenced_types(self):
        '''Return a list of all referenced types in this reference.'''
        if not self._type:
            return []
        return [self._type]


class EmptyReference(Reference):
    '''EmptyReference is a sentinel for an absent type. It returns None when dereferenced'''
    def __init__(self, location=None):
        super(EmptyReference, self).__init__(None, location=location)

    def dereference(self):
        return None


class NameReference(Reference):
    '''NameReference references a type by its name.'''
    def __init__(self, name, location=None):
        super(NameReference, self).__init__(None, location=location)
        self.name = name

    def __repr__(self):
        return '<NameReference %r>' % self.name

    def __str__(self):
        return self.name

    def link(self, lookup):
        logging.debug('Linking %s', self)
        self._type = lookup(self.name)
        if self._type:
            return []

        return [self._error('Type not found "%s"', self.name)]


class ListReference(Reference):
    '''ListReference has a child reference for an element, creates a list on linking.'''
    def __init__(self, element, location=None):
        super(ListReference, self).__init__(None, location=location)
        self.element = reference(element)
        self._init_type()

    def __repr__(self):
        return '<ListReference %s>' % self.element

    def __str__(self):
        return 'list<%s>' % self.element

    def _init_type(self):
        if not self.element:
            return
        self._type = pdefc.lang.collects.List(self.element.dereference(), location=self.location)

    def link(self, lookup):
        logging.debug('Linking %s', self)
        errors = self.element.link(lookup)
        if errors:
            return errors

        self._init_type()
        return []

    def _validate(self):
        logging.debug('Validating %s', self)
        if not self._type:
            return []
        return self._type.validate()

    @property
    def referenced_types(self):
        result = super(ListReference, self).referenced_types
        result += self.element.referenced_types
        return result


class SetReference(Reference):
    '''SetReference has a child for an element, creates a set on linking.'''
    def __init__(self, element, location=None):
        super(SetReference, self).__init__(None, location=location)
        self.element = reference(element)
        self._init_type()

    def __repr__(self):
        return '<SetReference %s>' % self.element

    def __str__(self):
        return 'set<%s>' % self.element

    def _init_type(self):
        if not self.element:
            return
        self._type = pdefc.lang.collects.Set(self.element.dereference(), location=self.location)

    def link(self, lookup):
        logging.debug('Linking %s', self)
        errors = self.element.link(lookup)
        if errors:
            return errors

        self._init_type()
        return []

    def _validate(self):
        logging.debug('Validating %s', self)
        if not self._type:
            return []
        return self._type.validate()

    @property
    def referenced_types(self):
        result = super(SetReference, self).referenced_types
        result += self.element.referenced_types
        return result


class MapReference(Reference):
    '''MapReference has children references for a key and a value, creates a map on linking.'''
    def __init__(self, key, value, location=None):
        super(MapReference, self).__init__(None, location=location)
        self.key = reference(key)
        self.value = reference(value)
        self._init_type()

    def __repr__(self):
        return '<MapReference %s, %s>' % (self.key, self.value)

    def __str__(self):
        return 'map<%s, %s>' % (self.key, self.value)

    def _init_type(self):
        if not self.key or not self.value:
            return
        self._type = pdefc.lang.collects.Map(self.key.dereference(), self.value.dereference(),
                                            location=self.location)

    def link(self, lookup):
        logging.debug('Linking %s', self)
        errors0 = self.key.link(lookup)
        errors1 = self.value.link(lookup)
        if errors0 or errors1:
            return errors0 + errors1

        self._init_type()
        return []

    def _validate(self):
        logging.debug('Validation %s', self)
        if not self._type:
            return []
        return self._type.validate()

    @property
    def referenced_types(self):
        result = super(MapReference, self).referenced_types
        result += self.key.referenced_types
        result += self.value.referenced_types
        return result
