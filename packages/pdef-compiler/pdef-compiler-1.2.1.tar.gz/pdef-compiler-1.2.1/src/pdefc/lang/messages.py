# encoding: utf-8
import logging

from pdefc.lang import references
from pdefc.lang.common import Located, Validatable
from pdefc.lang.types import TypeEnum, Definition


class Message(Definition):
    '''User-defined message.'''
    def __init__(self, name, base=None, discriminator_value=None, declared_fields=None,
                 is_exception=False, doc=None, location=None):
        super(Message, self).__init__(TypeEnum.MESSAGE, name, doc=doc, location=location)

        self.base = base
        self.discriminator_value = discriminator_value
        self._discriminator = None  # Field.

        self.subtypes = []
        self.declared_fields = []
        self.is_exception = is_exception

        if declared_fields:
            for field in declared_fields:
                self.add_field(field)

    @property
    def base(self):
        return self._base.dereference()

    @base.setter
    def base(self, value):
        self._base = references.reference(value)

    @property
    def discriminator_value(self):
        return self._discriminator_value.dereference()

    @discriminator_value.setter
    def discriminator_value(self, value):
        self._discriminator_value = references.reference(value)

    @property
    def discriminator(self):
        '''Return this message discriminator field, base discriminator field, or None.'''
        if self._discriminator:
            return self._discriminator

        return self.base.discriminator if self.base else None

    @property
    def is_polymorphic(self):
        return bool(self.discriminator)

    @property
    def fields(self):
        return self.inherited_fields + self.declared_fields

    @property
    def inherited_fields(self):
        if not self.base:
            return []

        return self.base.fields

    @property
    def inherited_fields(self):
        if not self.base:
            return []

        return self.base.fields

    @property
    def referenced_types(self):
        result = set()
        result.update(self._base.referenced_types)
        result.update(self._discriminator_value.referenced_types)
        result.update(self.subtypes)

        for field in self.fields:
            result.update(field._type.referenced_types)
        
        result.discard(self)
        return result

    def add_field(self, field):
        '''Add a new field to this message and return the field.'''
        self.declared_fields.append(field)

        if field.is_discriminator:
            self._discriminator = field

        logging.debug('%s: added a field "%s"', self, field.name)
        return field

    def create_field(self, name, type0, is_discriminator=False):
        '''Create a new field, add it to this message and return the field.'''
        field = Field(name, type0, is_discriminator=is_discriminator)
        return self.add_field(field)

    def _add_subtype(self, subtype):
        '''Add a new subtype to this message.'''
        if not isinstance(subtype, Message):
            raise ValueError('Must be a message instance, %r' % subtype)

        if subtype is self:
            return

        self.subtypes.append(subtype)
        if self.base and self.base.is_message:
            self.base._add_subtype(subtype)

    def link(self, module):
        errors = super(Message, self).link(module)
        errors += self._base.link(self.lookup)
        errors += self._discriminator_value.link(self.lookup)

        for field in self.declared_fields:
            errors += field.link(self)

        return errors

    def build(self):
        logging.debug('Building %s', self)

        # Add this message to base subtypes.
        if self._discriminator_value and self.base and self.base.is_message:
            self.base._add_subtype(self)

        return []

    def _validate(self):
        logging.debug('Validation %s', self)

        errors = self._validate_base()
        if errors:
            # Cannot validate this message when an invalid base.
            return errors

        errors = []
        if self.discriminator_value:
            errors += self._validate_polymorphic_inheritance()
        else:
            errors += self._validate_simple_inheritance()

        errors += self._validate_subtypes()
        errors += self._validate_fields()
        return errors

    @property
    def _has_circular_inheritance(self):
        base = self.base
        while base:
            if base is self:
                return True

            if base.is_message:
                base = base.base
            else:
                # Cannot proceed, the base is not a message.
                break

        return False

    def _validate_base(self):
        if not self.base:
            return []

        # Prevent circular inheritance before any validation.
        if self._has_circular_inheritance:
            # Cannot proceed when circular inheritance.
            return [self._error('%s: circular inheritance', self)]

        # Validate the base, ignore the errors, they are collected
        # when the base is validated in a module.
        base = self.base
        base.validate()
        if not base.is_valid:
            return [self._error('%s: invalid base %s', self, base)]

        if not base.is_message:
            return [self._error('%s: base must be a message not %s', self, base)]

        errors = []
        if self.is_exception != base.is_exception:
            errors.append(self._error('%s: wrong base type (message/exception), %s', self, base))

        if not self._is_defined_after(base):
            errors.append(self._error('%s: must be declared after its base %s', self, base))

        # base.module can be None in tests.
        if base.module and base.module._depends_on(self.module):
            path = base.module._get_import_path(self.module)
            errors.append(self._error('%s: cannot inherit %s, '
                                      'it is in a dependent module "%s", import path: %s',
                                      self, base, base.module, path))

        return errors

    def _validate_simple_inheritance(self):
        assert not self.discriminator_value

        base = self.base
        if base and base.is_polymorphic:
            return [self._error('%s: discriminator value required, base is polymorphic', self)]

        return []

    def _validate_polymorphic_inheritance(self):
        assert self.discriminator_value

        base = self.base
        value = self.discriminator_value

        if not base:
            return [self._error('%s: discriminator value is present, but no base', self)]

        if not base.is_polymorphic:
            # A present discriminator value requires a polymorphic base.
            return [self._error('%s: base is not polymorphic, '
                                'but the discriminator value is present', self)]

        if self.package and self.package != base.package:
            return [self._error('%s: cannot inherit a polymorphic message from another package',
                                self)]

        # Both the value and the base are present, and the base is polymorphic.
        # The base has been validated before, its discriminator field must valid.
        if value not in base.discriminator.type:
            # The discriminator value is not a base discriminator enum value.
            return [self._error('%s: discriminator value does not match '
                                'the base discriminator type', self)]

        enum = value.enum
        if not self._is_defined_after(enum):
            return [self._error('%s: must be declared after the discriminator type %s', self, enum)]

        # enum.module can be None in tests.
        if enum.module and enum.module._depends_on(self.module):
            path = enum.module._get_import_path(self.module)
            return [self._error('%s: cannot use %s as a discriminator, '
                                'it is in a dependent module "%s", import path: %s',
                                self, enum, enum.module, path)]

        return []

    def _validate_subtypes(self):
        if not self.subtypes:
            return []

        # Prevent duplicate discriminator values in subtypes.
        errors = []
        values = set()
        for subtype in self.subtypes:
            value = subtype.discriminator_value
            if value in values:
                errors.append(self._error('%s: duplicate subtype with a discriminator value "%s"',
                                          self, value.name))
            values.add(value)

        return errors

    def _validate_fields(self):
        errors = []

        # Prevent duplicate field names.
        names = set([field.name for field in self.inherited_fields])
        for field in self.declared_fields:
            if field.name in names:
                errors.append(self._error('%s: duplicate field "%s"', self, field.name))
            names.add(field.name)

        # Prevent multiple discriminator fields.
        discriminator = None
        for field in self.fields:
            if not field.is_discriminator:
                continue

            if discriminator:
                errors.append(self._error('%s: multiple discriminator fields', self))
                break  # One multiple discriminator error is enough.

            discriminator = field

        for field in self.declared_fields:
            errors += field.validate()

        return errors


class Field(Located, Validatable):
    '''Message field.'''
    def __init__(self, name, type0, is_discriminator=False, location=None):
        self.name = name
        self._type = references.reference(type0)
        self.is_discriminator = is_discriminator
        self.location = location

        self.message = None

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<%s %s at %s>' % (self.__class__.__name__, self.name, hex(id(self)))

    @property
    def type(self):
        return self._type.dereference()

    def link(self, message):
        logging.debug('Linking %s', self)

        if self.message:
            raise ValueError('Field is already linked, %s' % self)
        self.message = message

        return self._type.link(message.lookup)

    def _validate(self):
        logging.debug('Validating %s', self)
        errors = []

        if not self.type.is_data_type:
            errors.append(self._error('%s: field must be a data type', self))

        if self.is_discriminator and not self.type.is_enum:
            errors.append(self._error('%s: discriminator field must be an enum', self))

        # Validate the reference (it can be a collection).
        errors += self._type.validate()
        return errors
